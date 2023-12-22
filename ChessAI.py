import random

knight_scores = [[-50, -40, -30, -30, -30, -30, -40, -50],
                 [-40, -20, 0, 0, 0, 0, -20, -40],
                 [-30, 0, 10, 15, 15, 10, 0, -30],
                 [-30, 5, 15, 20, 20, 15, 5, -30],
                 [-30, 0, 15, 20, 20, 15, 0, -30],
                 [-30, 5, 10, 15, 15, 10, 5, -30],
                 [-40, -20, 0, 5, 5, 0, -20, -40],
                 [-50, -40, -30, -30, -30, -30, -40, -50]]

bishop_scores = [[-20, -10, -10, -10, -10, -10, -10, -20],
                 [-10, 0, 0, 0, 0, 0, 0, -10],
                 [-10, 0, 5, 10, 10, 5, 0, -10],
                 [-10, 5, 5, 10, 10, 5, 5, -10],
                 [-10, 0, 10, 10, 10, 10, 0, -10],
                 [-10, 10, 10, 10, 10, 10, 10, -10],
                 [-10, 5, 0, 0, 0, 0, 5, -10],
                 [-20, -10, -10, -10, -10, -10, -10, -20]]

rook_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
               [5, 10, 10, 10, 10, 10, 10, 5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [0, 0, 5, 5, 5, 5, 0, 0]]

queen_scores = [[-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]]

pawn_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
               [50, 50, 50, 50, 50, 50, 50, 50],
               [10, 10, 20, 30, 30, 20, 10, 10],
               [5, 5, 10, 25, 25, 10, 5, 5],
               [0, 0, 0, 20, 20, 0, 0, 0],
               [5, -5, -10, 0, 0, -10, -5, 5],
               [5, 10, 10, -20, -20, 10, 10, 5],
               [0, 0, 0, 0, 0, 0, 0, 0]]

king_scores = [[-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-20, -30, -30, -40, -40, -30, -30, -20],
               [-10, -20, -20, -20, -20, -20, -20, -10],
               [20, 20, 0, 0, 0, 0, 20, 20],
               [20, 30, 10, 0, 0, 10, 30, 20]]

king_piece_square_table_end_game = [[-50, -40, -30, -20, -20, -30, -40, -50],
                                    [-30, -20, -10, 0, 0, -10, -20, -30],
                                    [-30, -10, 20, 30, 30, 20, -10, -30],
                                    [-30, -10, 30, 40, 40, 30, -10, -30],
                                    [-30, -10, 30, 40, 40, 30, -10, -30],
                                    [-30, -10, 20, 30, 30, 20, -10, -30],
                                    [-30, -30, 0, 0, 0, 0, -30, -30],
                                    [-50, -30, -30, -30, -30, -30, -30, -50]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1],
                         "wK": king_scores,
                         "bK": king_scores[::-1]}

piece_value = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
pieces = ["bB", "bK", "bN", "bp", "bQ", "bR", "wB", "wK", "wN", "wp", "wQ", "wR"]

CHECKMATE = 1000
CASTLE = 10
MOVE_REP_PUNISH = 3
POSITION_WIGHT = .1
STALEMATE = 0
DEPTH = 3  # the moves that the engine looks ahead


def generate_zobrist_keys():
    zobrist_keys = {}

    for row in range(8):
        for col in range(8):
            piece_zobrist_keys = {piece: random.getrandbits(64) for piece in pieces}
            zobrist_keys[(row, col)] = piece_zobrist_keys

    return zobrist_keys

def get_position_zobrist(board, zobrist_keys):
    key = 0

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "--":
                key ^= zobrist_keys[(row, col)][piece]

    return key

def find_random_move(valid_moves):
    return random.choice(valid_moves)


def find_best_move(gamestate, valid_moves):
    global next_move
    next_move = None
    find_move_nega_max_alpha_beta(gamestate, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                                  1 if gamestate.white_to_move else -1)
    return next_move


def find_move_nega_max_alpha_beta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move

    if depth == 0:
        return turn_multiplier * score_board(game_state)

    max_score = -CHECKMATE

    for move in valid_moves:

        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        score = -find_move_nega_max_alpha_beta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        game_state.undoMove()

        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score


# positive score == white is winning, negative score == black is winning
def score_board(gamestate):
    if gamestate.checkmate:
        if gamestate.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE
    elif gamestate.stalemate:
        return STALEMATE

    score = 0
    piece_position_score = 0

    for row in range(len(gamestate.board)):
        for col in range(len(gamestate.board[row])):
            square = gamestate.board[row][col]
            if square != "--":
                color = square[0]
                type = square[1]
                if color == "w":
                    piece_position_score = piece_position_scores["w" + type][row][col]
                elif color == "b":
                    piece_position_score = piece_position_scores["b" + type][row][col]

            if square[0] == "w":
                score += piece_value[square[1]] + piece_position_score * POSITION_WIGHT
                """if len(gamestate.move_log) > 5:
                    if gamestate.move_log[-1] == gamestate.move_log[-5]:
                        score += MOVE_REP_PUNISH"""
            elif square[0] == "b":
                score -= piece_value[square[1]] + piece_position_score * POSITION_WIGHT
                """if len(gamestate.move_log) > 5:
                    if gamestate.move_log[-1] == gamestate.move_log[-5]:
                        score -= MOVE_REP_PUNISH"""

    return score

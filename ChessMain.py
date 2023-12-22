"""
This will be the main driver handling the user input and drawing the current state
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import ChessEngine
import ChessAI

BOARD_WIDTH = 512
BOARD_HEIGHT = 512

MOVE_LOG_WIDTH = 250
MOVE_LOG_HEIGHT = BOARD_HEIGHT

EVAL_BAR_WIDTH = 32
EVAL_BAR_HEIGHT = BOARD_HEIGHT

DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION

MAX_FPS = 30
PIECE_PACKAGE = "neo"
IMAGES = {}

# loading in the images and scaling them to be the size of the square
def load_images():
    pieces = ["bR", "bB", "bN", "bQ", "bK", "bp", "wR", "wB", "wN", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(os.path.join(f"pieces/{PIECE_PACKAGE}", f"{piece}.png")), (SQ_SIZE, SQ_SIZE))

def draw_game_state(win, gamestate, valid_moves, square_selected, move_log_font, eval_font):
    draw_board(win)
    highlight_squares(win, gamestate, valid_moves, square_selected)
    draw_pieces(win, gamestate.board)
    draw_move_log(win, gamestate, move_log_font)
    #draw_eval_bar(win, gamestate, eval_font)

def draw_board(win):
    global colors
    # create 2 colors (the colors of the board)
    colors = ["white", "gray"]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            # if it's a light square its coordinates added up will give no rest when divided by 2 and the same is for black just that it will leave a rest
            # based on that we will choose a color and use that to draw a square
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(win, gamestate, valid_moves, square_selected):
    if square_selected != ():
        row, col = square_selected
        if gamestate.board[row][col][0] == ("w" if gamestate.white_to_move else "b"):  # square selected is a piece of the person which turn it is
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)  # transparency value
            surface.fill(pygame.Color("blue"))
            win.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))
            # highlight valid moves from that square
            surface.fill(pygame.Color("yellow"))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    win.blit(surface, (SQ_SIZE * move.end_col, SQ_SIZE * move.end_row))

def draw_pieces(win, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                win.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE))

def draw_move_log(win, gamestate, move_log_font):
    move_log_rect = pygame.Rect(BOARD_WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    pygame.draw.rect(win, pygame.Color("black"), move_log_rect)

    move_log = gamestate.move_log
    move_texts = []

    padding = 5
    text_y = padding

    for i in range(0, len(move_log), 2):
        move_string = f"{i // 2 + 1}. {str(move_log[i])} "
        if i + 1 < len(move_log):   # black moved
            move_string += str(move_log[i + 1])
        move_texts.append(move_string)

    for i in range(len(move_texts)):
        text_object = move_log_font.render(move_texts[i], True, pygame.Color("Gray"))
        text_loc = move_log_rect.move(padding, text_y)
        win.blit(text_object, text_loc)
        text_y += text_object.get_height()

def draw_eval_bar(win, gamestate, eval_font):
    eval_bar_rect = pygame.Rect(-BOARD_WIDTH, 0, EVAL_BAR_WIDTH, EVAL_BAR_HEIGHT)
    pygame.draw.rect(win, pygame.Color("white"), eval_bar_rect)

    eval = ChessEngine.GameState()
    evaluation_score = eval.evaluate(gamestate.board)

    if evaluation_score < 0:
        text_object = eval_font.render(str(evaluation_score), True, pygame.Color("Black"))
        win.blit(text_object, (732, 500))
    else:
        text_object = eval_font.render(str(evaluation_score), True, pygame.Color("Black"))
        win.blit(text_object, (732, 0))


def animate_move(move, win, board, clock):
    global colors
    delta_row = move.end_row - move.start_row
    delta_col = move.end_col - move.start_col
    frames_per_square = 10   # frames to move one square
    frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

    for frame in range(frame_count + 1):
        row, col = (move.start_row + delta_row * frame / frame_count, move.start_col + delta_col * frame / frame_count)
        draw_board(win)
        draw_pieces(win, board)
        # erase the piece moved from ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pygame.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(win, color, end_square)

        # erase taken piece after animation is done
        if move.piece_captured != "--":
            if move.is_enpassant_move:
                en_passant_row = (move.end_row + 1) if move.piece_captured[0] == "b" else (move.end_row - 1)
                end_square = pygame.Rect(move.end_col * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                win.blit(IMAGES[move.piece_captured], end_square)

        # draw selected piece
        win.blit(IMAGES[move.piece_moved], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(0)

def draw_end_game_text(win, text):
    font = pygame.font.SysFont("Helvitca", 32, True, False)

    text_object = font.render(text, 0, pygame.Color("Gray"))
    text_loc = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    win.blit(text_object, text_loc)

    text_object = font.render(text, 0, pygame.Color("Black"))
    win.blit(text_object, text_loc.move(2, 2))


def main():
    pygame.init()
    win = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
    win.fill(pygame.Color("white"))

    clock = pygame.time.Clock()

    gamestate = ChessEngine.GameState()
    valid_moves = gamestate.getValidMoves()

    zobrist_keys = ChessAI.generate_zobrist_keys()
    print(zobrist_keys, len(zobrist_keys))

    move_made = False  # keeps track of a move being made so that the program doesn't load the valid moves every frame but only when a move is made
    game_over = False
    animate = False

    # will be true when a human is playing and false when an AI is playing
    player_one = False   # representing white
    player_two = False   # representing black

    square_selected = ()  # kep track of last click of user will be a row and a col
    player_clicks = []  # keep track of the player clicks with two tuples. from where to where

    move_log_font = pygame.font.SysFont("Arial", 12, False, False)
    eval_font = pygame.font.SysFont("Arial", 12, False, False)

    load_images()

    rand = 0

    run = True
    while run:
        human_turn = (gamestate.white_to_move and player_one) or (not gamestate.white_to_move and player_two)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = pygame.mouse.get_pos()  # location of mouse (x, y)

                    # gets the square the mouse is on
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    # aka user clicked the same square twice or user clicked mouse log
                    if square_selected == (row, col) or col >= 8:
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)

                    # if he clicked two times move the piece
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gamestate.board)

                        for i in range(len(valid_moves)):
                            # only if a move is valid make it
                            if move == valid_moves[i]:
                                gamestate.makeMove(valid_moves[i])

                                move_made = True
                                animate = True

                                # reset the clicks after a valid move was made
                                square_selected = ()
                                player_clicks = []

                        if not move_made:
                            # if it wasn't a valid move select the most recent one
                            player_clicks = [square_selected]

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gamestate.undoMove()
                    move_made = True
                    animate = False
                    game_over = False

                elif event.key == pygame.K_r:
                    gamestate = ChessEngine.GameState()
                    valid_moves = gamestate.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        # AI logic
        if not game_over and not human_turn:
            AI_move = ChessAI.find_best_move(gamestate, valid_moves)
            if AI_move is None:
                AI_move = ChessAI.find_random_move(valid_moves)
                rand += 1
                print("Random Move: ", rand)
            print(ChessAI.get_position_zobrist(gamestate.board, zobrist_keys))
            gamestate.makeMove(AI_move)
            move_made = True
            animate = True

        # when a valid move was made generate new moves
        if move_made:
            if animate:
                animate_move(gamestate.move_log[-1], win, gamestate.board, clock)
            valid_moves = gamestate.getValidMoves()
            move_made = False
            animate = False

        draw_game_state(win, gamestate, valid_moves, square_selected, move_log_font, eval_font)

        if gamestate.checkmate:
            game_over = True
            text = "Stalemate" if gamestate.stalemate else "Black wins by Checkmate" if gamestate.white_to_move else "White wins by Checkmate"
            draw_end_game_text(win, text)

        if gamestate.move_draw:
            game_over = True
            text = "Draw by 50 Move Rule"
            draw_end_game_text(win, text)

        if gamestate.rep_stalemate:
            game_over = True
            text = "Stalemate by Repetition"
            draw_end_game_text(win, text)

        clock.tick(MAX_FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()

# IDEAS:
# add config to replace color scheme of the board
# improve chess notation (+ for check and = for pawn promotion)
# display which colors turn it is
# highlight last move (in highlight squares)
# turn animations on or off in config
# speed of animation in config
# draws
# highlight king check
# add position evaluation bar
# trash talking
# arrows
# giving out the best move on click
# stalemate on repeated moves (move log)
# move log display fix (off-screen after a number of moves) (add scroll)
# clock / timer
# UI
# fen to board

# AI
# end game maps
# positional rewards
# multiple difficulties for AI
# reward castling
# reward king pos
# attacking and defending squares
# avoid moving back in the next move
# get onto squares that are protected (don't hang your pieces)
# pawn chains
# teach openings
# transpositions for faster evaluation and more depth

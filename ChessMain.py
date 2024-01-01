import datetime

import ChessEngine
import ChessAI
import yaml
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

pygame.init()

# load the config
with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

BOARD_WIDTH = 512
BOARD_HEIGHT = 512

MOVE_LOG_WIDTH = 250
MOVE_LOG_HEIGHT = BOARD_HEIGHT

EVAL_BAR_WIDTH = 32
EVAL_BAR_HEIGHT = BOARD_HEIGHT

DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION

MAX_FPS = cfg["animation"]["max_fps"]
PIECE_PACKAGE = cfg["design"]["piece_set"]
PIECES = {}
IMGS = {}

UI_FONT = pygame.font.SysFont("Arial", 32)
MOVE_LOG_FONT = EVAL_FONT = pygame.font.SysFont("Arial", 12)
FEN_FONT = pygame.font.SysFont("Arial", 10)


class Button:
    def __init__(self, text, x_pos, y_pos, width, height, enabled):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.enabled = enabled
        self.draw()

    def draw(self):
        text = UI_FONT.render(self.text, True, "white")
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.width, self.height))
        win = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
        pygame.draw.rect(win, "black", button_rect, 0, 5)

        win.blit(text, (self.x_pos, self.y_pos))

    def click(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.width, self.height))

        if left_click and button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False


class UI:
    # loading in the images and scaling them to be the size of the square
    def load_pieces(self):
        pieces = ["bR", "bB", "bN", "bQ", "bK", "bp", "wR", "wB", "wN", "wQ", "wK", "wp"]
        for piece in pieces:
            PIECES[piece] = pygame.transform.scale(
                pygame.image.load(os.path.join(f"pieces/{PIECE_PACKAGE}", f"{piece}.png")), (SQ_SIZE, SQ_SIZE))

    def load_images(self):
        images = [image for image in os.listdir("imgs")]
        for img in images:
            IMGS[img] = pygame.image.load(os.path.join("imgs", img))

    def draw_game_state(self, win, gamestate, valid_moves, square_selected, move_log_font, eval_font):
        self.draw_board(win)
        self.highlight_squares(win, gamestate, valid_moves, square_selected)
        self.draw_pieces(win, gamestate.board)
        self.draw_move_log(win, gamestate, move_log_font)
        # draw_eval_bar(win, gamestate, eval_font)

    def draw_board(self, win):
        global colors
        # create 2 colors (the colors of the board)
        colors = [cfg['design']['first_color'], cfg['design']['second_color']]

        for row in range(DIMENSION):
            for col in range(DIMENSION):
                # if it's a light square its coordinates added up will give no rest when divided by 2 and
                # the same is for black just that it will leave a rest
                # based on that we will choose a color and use that to draw a square
                color = colors[(row + col) % 2]
                pygame.draw.rect(win, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def highlight_squares(self, win, gamestate, valid_moves, square_selected):
        if square_selected != ():
            row, col = square_selected
            if gamestate.board[row][col][0] == ("w" if gamestate.white_to_move else "b"):  # square selected is a piece of the person which turn it is
                surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(100)  # transparency value
                surface.fill(cfg["design"]["selection_color"])
                win.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))
                # highlight valid moves from that square
                surface.fill(cfg["design"]["possible_moves_color"])
                for move in valid_moves:
                    if move.start_row == row and move.start_col == col:
                        win.blit(surface, (SQ_SIZE * move.end_col, SQ_SIZE * move.end_row))

    def draw_pieces(self, win, board):
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = board[row][col]
                if piece != "--":
                    win.blit(PIECES[piece], (col * SQ_SIZE, row * SQ_SIZE))

    def draw_move_log(self, win, gamestate, move_log_font):
        move_log_rect = pygame.Rect(BOARD_WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
        pygame.draw.rect(win, pygame.Color("black"), move_log_rect)

        move_log = gamestate.move_log
        move_texts = []

        padding = 5
        text_y = padding

        for i in range(0, len(move_log), 2):
            move_string = f"{i // 2 + 1}. {str(move_log[i])} "
            if i + 1 < len(move_log):  # black moved
                move_string += str(move_log[i + 1])
            move_texts.append(move_string)

        for i in range(len(move_texts)):
            text_object = move_log_font.render(move_texts[i], True, pygame.Color("Gray"))
            text_loc = move_log_rect.move(padding, text_y)
            win.blit(text_object, text_loc)
            text_y += text_object.get_height()

    def draw_eval_bar(self, win, gamestate, eval_font):
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

    def animate_move(self, move, win, board, clock):
        global colors
        delta_row = move.end_row - move.start_row
        delta_col = move.end_col - move.start_col
        frames_per_square = 10  # frames to move one square
        frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

        for frame in range(frame_count + 1):
            row, col = (
            move.start_row + delta_row * frame / frame_count, move.start_col + delta_col * frame / frame_count)
            self.draw_board(win)
            self.draw_pieces(win, board)
            # erase the piece moved from ending square
            color = colors[(move.end_row + move.end_col) % 2]
            end_square = pygame.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(win, color, end_square)

            # erase taken piece after animation is done
            if move.piece_captured != "--":
                if move.is_enpassant_move:
                    en_passant_row = (move.end_row + 1) if move.piece_captured[0] == "b" else (move.end_row - 1)
                    end_square = pygame.Rect(move.end_col * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                    win.blit(PIECES[move.piece_captured], end_square)

            # draw selected piece
            win.blit(PIECES[move.piece_moved], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            pygame.display.flip()
            clock.tick(cfg["animation"]["animation_speed"])

    def draw_end_game_text(self, win, text):
        font = pygame.font.SysFont("Helvitca", 32, True, False)

        text_object = font.render(text, 0, pygame.Color("Gray"))
        text_loc = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                     BOARD_HEIGHT / 2 - text_object.get_height() / 2)
        win.blit(text_object, text_loc)

        text_object = font.render(text, 0, pygame.Color("Black"))
        win.blit(text_object, text_loc.move(2, 2))


class Game:
    def __init__(self):
        self.start_fen = None

    def home(self):
        ui = UI()
        gamestate = ChessEngine.GameState()

        settings_button = Button("settings", 728, 4, 30, 30, True)
        start_button = Button("start", 552, 59, 200, 50, True)

        fen = cfg["game"]["start_fen"]
        fen_rect = pygame.Rect(540, 300, 200, 50)

        ui.load_pieces()
        ui.load_images()

        win = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
        win.fill(pygame.Color("white"))

        run = True
        active = False

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if fen_rect.collidepoint(event.pos):
                        active = True
                    else:
                        active = False

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_BACKSPACE:
                            fen = fen[:-1]
                        else:
                            fen += event.unicode

                if start_button.click():
                    if fen == "None":
                        self.start_fen = None
                    else:
                        self.start_fen = fen
                    return "start"

                if settings_button.click():
                    return "settings"

            ui.draw_board(win)
            ui.draw_move_log(win, gamestate, MOVE_LOG_FONT)
            ui.draw_pieces(win, gamestate.board)

            pygame.draw.rect(win, "white", fen_rect, 1)
            fen_input = FEN_FONT.render(fen, True, "white")

            win.blit(IMGS["settings.png"], (728, 4))
            win.blit(IMGS["play.png"], (552, 59))
            win.blit(fen_input, (fen_rect.x + 10, fen_rect.y + (10 if len(fen) <= 25 else 20)))

            pygame.display.update()

    def settings(self):
        pass

    def main(self):
        win = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
        win.fill(pygame.Color("white"))

        clock = pygame.time.Clock()

        give_up_button = Button("give-up", 620, 300, 125, 20, True)
        flip_board_button = Button("flip-board", 620, 200, 125, 20, True)
        best_move_button = Button("best-move", 620, 100, 125, 20, True)
        # pos_to_fen_button = Button("pos-to-fen", 0, 0, 100, 50, True)

        gamestate = ChessEngine.GameState(fen=self.start_fen)
        ui = UI()
        valid_moves = gamestate.getValidMoves()

        zobrist_keys = ChessAI.generate_zobrist_keys()
        transposition_tale = {}

        move_made = False  # keeps track of a move being made so that the program doesn't load the valid moves every frame but only when a move is made
        game_over = False
        animate = False

        # will be true when a human is playing and false when an AI is playing
        player_one = cfg["game"]["player_one_is_not_ai"]  # representing white
        player_two = cfg["game"]["player_two_is_not_ai"]  # representing black

        square_selected = ()  # kep track of last click of user will be a row and a col
        player_clicks = []  # keep track of the player clicks with two tuples. from where to where

        ui.load_pieces()

        rand = 0

        run = True
        while run:
            human_turn = (gamestate.white_to_move and player_one) or (not gamestate.white_to_move and player_two)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                elif flip_board_button.click():
                    print("flip-board")

                elif give_up_button.click():
                    return "resign"

                elif best_move_button.click():
                    print("Calculating best move...")
                    best_move = ChessAI.find_best_move(gamestate, valid_moves, zobrist_keys, transposition_tale, False)
                    print(f"The best move in this position is {best_move} \n")

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
                start_time = datetime.datetime.now()

                AI_move = ChessAI.find_best_move(gamestate, valid_moves, zobrist_keys, transposition_tale, True)
                if AI_move is None:
                    AI_move = ChessAI.find_random_move(valid_moves)
                    rand += 1
                    print("Random Move Nr.", rand)

                end_time = datetime.datetime.now()
                thinking_time = end_time - start_time

                print(f"This move took {str(thinking_time).split('.')[0]} to calculate. \n")
                gamestate.makeMove(AI_move)
                move_made = True
                animate = True

            # when a valid move was made generate new moves
            if move_made:
                if animate:
                    ui.animate_move(gamestate.move_log[-1], win, gamestate.board, clock)
                valid_moves = gamestate.getValidMoves()
                move_made = False
                animate = False

            if gamestate.checkmate:
                game_over = True
                text = "Stalemate" if gamestate.stalemate else "Black wins by Checkmate" if gamestate.white_to_move else "White wins by Checkmate"
                ui.draw_end_game_text(win, text)

            if gamestate.rep_stalemate:
                game_over = True
                text = "Stalemate by Repetition"
                ui.draw_end_game_text(win, text)

            ui.draw_game_state(win, gamestate, valid_moves, square_selected, MOVE_LOG_FONT, EVAL_FONT)

            win.blit(IMGS["resign.png"], (620, 300))
            win.blit(IMGS["flip_board.png"], (620, 200))
            win.blit(IMGS["best_move.png"], (620, 100))

            clock.tick(MAX_FPS)
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()

    while True:
        if game.home() == "start":
            if game.main() == "resign":
                continue
        else:
            print("Not start")

# IDEAS:
# improve chess notation (+ for check and = for pawn promotion)
# display which colors turn it is
# highlight last move (in highlight squares)
# draws
# highlight king check
# add position evaluation bar
# trash talking
# arrows
# stalemate on repeated moves (move log)
# move log display fix (off-screen after a number of moves) (add scroll)
# clock / timer
# UI
# fen to board (add castling rights and other important things)

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
# forks
# teach openings

"""
This will be the main driver handling the user input and drawing the current state
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import ChessEngine
import ChessAI

WIDTH = 512
HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
IMAGES = {}


# loading in the images and scaling them to be the size of the square
def load_images():
    pieces = ["bR", "bB", "bN", "bQ", "bK", "bP", "wR", "wB", "wN", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(os.path.join("imgs", f"{piece}.png")),
                                               (SQ_SIZE, SQ_SIZE))


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


def draw_pieces(win, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                win.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE))


def draw_game_state(win, gamestate, valid_moves, square_selected):
    draw_board(win)
    highlight_squares(win, gamestate, valid_moves, square_selected)
    draw_pieces(win, gamestate.board)


# highlights moves and pieces selected
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
            win.blit(IMAGES[move.piece_captured], end_square)

        # draw selected piece
        win.blit(IMAGES[move.piece_moved], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(120)


def draw_text(win, text):
    font = pygame.font.SysFont("Helvitca", 32, True, False)

    text_object = font.render(text, 0, pygame.Color("Gray"))
    text_loc = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    win.blit(text_object, text_loc)

    text_object = font.render(text, 0, pygame.Color("Black"))
    win.blit(text_object, text_loc.move(2, 2))


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    win.fill(pygame.Color("white"))

    clock = pygame.time.Clock()

    gamestate = ChessEngine.GameState()
    valid_moves = gamestate.get_valid_moves()

    move_made = False  # keeps track of a move being made so that the program doesn't load the valid moves every frame but only when a move is made
    game_over = False
    animate = False

    # will be true when a human is playing and false when an AI is playing
    player_one = False   # representing white
    player_two = False   # representing black

    square_selected = ()  # kep track of last click of user will be a row and a col
    player_clicks = []  # keep track of the player clicks with two tuples. from where to where

    load_images()

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

                    # aka user clicked the same square twice
                    if square_selected == (row, col):
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
                                print(move.getChessNotation())
                                gamestate.make_move(valid_moves[i])

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
                    gamestate.undo_move()
                    move_made = True
                    animate = False
                elif event.key == pygame.K_r:
                    gamestate = ChessEngine.GameState()
                    valid_moves = gamestate.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

        # AI logic
        if not game_over and not human_turn:
            AI_move = ChessAI.find_random_move(valid_moves)
            gamestate.make_move(AI_move)
            move_made = True
            animate = True

        # when a valid move was made generate new moves
        if move_made:
            if animate:
                animate_move(gamestate.move_log[-1], win, gamestate.board, clock)
            valid_moves = gamestate.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(win, gamestate, valid_moves, square_selected)

        if gamestate.checkmate:
            game_over = True
            if gamestate.white_to_move:
                draw_text(win, "Black wins by Checkmate")
            else:
                draw_text(win, "White wins by Checkmate")
        elif gamestate.stalemate:
            game_over = True
            draw_text(win, "Stalemate")

        clock.tick(MAX_FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()

# IDEAS:
# add config to replace color scheme of the board
# improve chess notation
# display which colors turn it is
# add option for promotion (optional parameter for Move)
# highlight last move (in highlight squares)
# turn animations on or off in config
# speed of animation in config
# multiple difficulties for AI
# draws

# BUGS:
# when moving left knight turns don't switch

"""
This class is used to store all the information of the game and also will determinate legal moves in the current state. It will also keep a move log
"""
import numpy as np


class GameState:
    def __init__(self):
        # board is a 8x8 2D array every element has 2 characters the first one being the colour and the second one being the piece. "--" is an empy space
        self.board = np.array([["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                               ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                               ["--", "--", "--", "--", "--", "--", "--", "--"],
                               ["--", "--", "--", "--", "--", "--", "--", "--"],
                               ["--", "--", "--", "--", "--", "--", "--", "--"],
                               ["--", "--", "--", "--", "--", "--", "--", "--"],
                               ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                               ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
                              )

        self.move_functions = {"P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

        self.white_to_move = True

        self.black_king_loc = (0, 4)
        self.white_king_loc = (7, 4)

        self.in_check = False
        self.pins = []
        self.checks = []

        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = ()  # coordinates for square at which en passant is possible

        self.current_castling_rights = CastlingRights(True, True, True, True)

        self.castle_right_log = [CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        self.move_log = []

    # will not work for pawn promotion, castling and en passant
    def make_move(self, move):
        # leave the square you left blank
        self.board[move.start_row][move.start_col] = "--"
        # put the piece to the next square
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)

        # update kings location if moved
        if move.piece_moved == "wK":
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_loc = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            promoted_piece = input("Promote to Q, R, B, or N: ")
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece

        # en passant
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_col] = "--"

        # update en passant variable
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # copies the rook into new position
                self.board[move.end_row][move.end_col + 1] = "--"  # removes the other rook
            else:  # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # copies the rook into new position
                self.board[move.end_row][move.end_col - 2] = "--"  # removes the other rook

        # castling
        self.update_castle_rights(move)
        self.castle_right_log.append(CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                    self.current_castling_rights.wqs, self.current_castling_rights.bqs))

        self.white_to_move = not self.white_to_move  # reverse the turn aka switch it

    # reverse last move
    def undo_move(self):
        if len(self.move_log) != 0:  # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # swap players
            # update the king's position if needed
            if move.piece_moved == "wK":
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.white_king_loc = (move.start_row, move.start_col)
            # undo en passant move
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            # undo castle rights
            self.castle_right_log.pop()  # get rid of the new castle rights from the move we are undoing
            self.current_castling_rights = self.castle_right_log[
                -1]  # set the current castle rights to the last one in the list
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False

    def inCheck(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move  # switch to opponent's point of view
        opponents_moves = self.get_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    # because you have things such as pins you have to do 2 things.
    # First generate all moves you are allowed to make.
    # Then generate all the possible moves white can make after you made a move because it could be that if you move your king will be in check making that move illegal
    # That is why we will do 2 functions:

    # a function that is considering all the checks
    def get_valid_moves(self):
        temp_castle_rights = CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                            self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # advanced algorithm
        moves = []
        self.in_check, self.pins, self.checks = self.check_pins_and_checks()

        if self.white_to_move:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.get_possible_moves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])

            if len(moves) == 0:
                if self.in_check:
                    self.checkmate = True
                else:
                    # TODO stalemate on repeated moves
                    self.stalemate = True

            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
                self.checkmate = False
                self.stalemate = False

        else:  # not in check - all moves are fine
            moves = self.get_possible_moves()
            if self.white_to_move:
                self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves)
            else:
                self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves)

        self.current_castling_rights = temp_castle_rights
        return moves

    # and a function that is not considering the checks
    def get_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)  # calls appropriate move function based on piece type
        return moves

    # get all possible moves for a given piece at row, col and add them to a list of moves
    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pawn_promotion = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = "b"
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = "w"

        # allowed to 1 square forward if the square is empty
        if self.board[row + move_amount][col] == "--":
            if not piece_pinned or pin_direction == (move_amount, 0):
                if row + move_amount == back_row:
                    pawn_promotion = True
                moves.append(Move((row, col), (row + move_amount, col), self.board, pawn_promotion=pawn_promotion))
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))

        # not allowing to capture over the edges
        if col - 1 >= 0:
            # capture
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    if row + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(
                        Move((row, col), (row + move_amount, col - 1), self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col - 1) == self.en_passant_possible:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board, is_en_passant_move=True))

        if col + 1 <= 7:
            # capture
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    if row + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(
                        Move((row, col), (row + move_amount, col + 1), self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col + 1) == self.en_passant_possible:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board, is_en_passant_move=True))

    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        # represent the directions in which the rook can move
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            # check every position it could possibly move to (somewhere between 1 and 7 squares at a time)
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                # make sure It's still on the board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # it's an empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # it's an enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break  # stopping to move further in this direction
                        else:  # friendly piece
                            break
                else:  # it's not in the range of the board
                    break

    def get_knight_moves(self, row, col, moves):
        piece_pinned = False

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        # get every square the knight can jump onto
        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, 2), (1, -2), (-2, 1), (-1, 2))
        ally_color = "w" if self.white_to_move else "b"

        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]

            # check if the move is still on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    # if the end pieces color is either "-" or "b" when it is whites move you can take it
                    if end_piece[0] != ally_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        # represent the directions in which the rook can move
        directions = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            # check every position it could possibly move to (somewhere between 1 and 7 squares at a time)
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                # make sure It's still on the board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        if end_piece == "--":  # it's an empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # it's an enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break  # stopping to move further in this direction
                        else:  # friendly piece
                            break
                else:  # it's not in the range of the board
                    break

    def get_queen_moves(self, row, col, moves):
        # since a queen is only a rook and a bishop in one piece just take their possible moves from the place the queen stands in
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):

        # get every square the king can go onto
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"

        # for every move he can take
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]

            # check if the move is still on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # if the end pieces color is either "-" or "b" when it is whites move you can take it
                if end_piece[0] != ally_color:
                    # place a king on the end square and see if it goes into check
                    if ally_color == "w":
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.check_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place the king back
                    if ally_color == "w":
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)

    def get_castle_moves(self, row, col, moves):
        if self.square_under_attack(row, col):
            return  # can't castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, col, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, col, moves)

    def get_kingside_castle_moves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))

    def check_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False

        # which king are we looking at. For which one do we want to know if he's in check?
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row, start_col = self.white_king_loc
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row, start_col = self.black_king_loc

        # after that get all the possible moves outward from the king
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        # for each move...
        for j in range(len(directions)):
            # ...go through all directions and then...
            d = directions[j]
            possible_pin = ()
            # ...check for every square in that direction if...
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                # ...the move is still on the board...
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # ... if it is, check if there is an allied piece on the square you are currently checking for pins...
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        # ... then check if that piece is the first one in that direction
                        if possible_pin == ():  # if it is it could be a pin
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # if it is not there cant be any pins in that direction
                            break

                    # ... if it isn't an allied piece...
                    elif end_piece[0] == enemy_color:
                        # ... check what type of piece it is...
                        type = end_piece[1]
                        # from here on there are 5 possible scenarios we need to check for
                        # 1. in straight lines from the king is a rook
                        # 2. diagonally away is a bishop
                        # 3. 1 square diagonally is a pawn
                        # 4. any direction is a queen
                        # 5. any direction 1 square away is a king

                        # so if any of these are true...
                        if (0 <= j <= 3 and type == "R") or (4 <= j <= 7 and type == "B") or (i == 1 and type == "P" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (type == "Q") or (i == 1 and type == "K"):
                            if possible_pin == ():  # ... and there is no pin
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # there is a piece between them
                                pins.append(possible_pin)
                                break

                        else:  # the enemy piece is not putting the king in check
                            break
                else:
                    break  # off board

        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, 2), (1, -2), (-2, 1), (-1, 2))

        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]

            # check if it still on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # check if it is an enemy knight
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))

        return in_check, pins, checks


class Move:
    # convert board to chess notation (rank file notation)
    # keys to values ==> "a" is represented by 0 and 1 is represented by 7
    # in this way the coordinate (0, 0) is equal to its chess notation which is a8
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_col = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    col_to_files = {v: k for k, v in files_to_col.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant_move=False, pawn_promotion=False, is_castle_move=False):
        self.start_row, self.start_col = start_sq
        self.end_row, self.end_col = end_sq

        # piece move = where was it and what was it, piece captured = what did it take (what was there before)
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # pawn promotion
        self.is_pawn_promotion = pawn_promotion

        # en passant
        self.is_en_passant_move = is_en_passant_move

        if self.is_en_passant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        # castling
        self.is_castle_move = is_castle_move

        # generates and id that will be consisting of 4 digits, the first 2 being the start place and the last two the end place
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def getChessNotation(self):
        if self.is_pawn_promotion:
            return self.get_rank_file(self.end_row, self.end_col) + "Q"
        if self.is_castle_move:
            if self.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.is_en_passant_move:
            return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row,
                                                                                                    self.end_col) + " e.p."
        if self.piece_captured != "--":
            if self.piece_moved[1] == "P":
                return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row,
                                                                                                        self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.get_rank_file(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "P":
                return self.get_rank_file(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.col_to_files[col] + self.rows_to_ranks[row]


class CastlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

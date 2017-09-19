from enum import Enum

class MoveDir(Enum):
    LEFT = -1
    RIGHT = 1

class Square(Enum):
    EMPTY = 0
    RED = -1
    BLACK = 1

    def __str__(self):
        if self == self.RED:
            return "X"
        elif self == self.BLACK:
            return "O"
        else:
            return " "

class Player(Enum):
    RED = -1
    BLACK = 1

    def __str__(self):
        return self.name.title()

    @property
    def enemy(self):
        if self == self.RED:
            return self.BLACK
        else:
            return self.RED

    @property
    def my_square(self):
        if self == self.RED:
            return Square.RED
        else:
            return Square.BLACK

class InvalidMove(Exception):
    """Custom exception for invalid moves."""

class MoreJumpsRequired(Exception):
    """Custom exception for when a piece can make a jump,
    but it must keep jumping for the jump sequence to be valid."""

class GameOver(Exception):
    """The game is over because the active player cannot move!"""

def starting_square(x, y):
    """Returns the contents of a given square for the starting board state"""
    if (x + y) % 2 == 0:
        return Square.EMPTY
    elif y < 3:
        return Square.BLACK
    elif y > 4:
        return Square.RED
    else:
        return Square.EMPTY

def make_board(make_square):
    """Returns a board where make_square defines the contents of each square"""
    return tuple(tuple(make_square(x, y) for x in range(8)) for y in range(8))

STARTING_BOARD = make_board(starting_square)

def square_is(location, query, board):
    """Checks if the piece at location equals query. Returns false if location is out of bounds."""
    x, y = location
    if y < 0 or y >= len(board):
        return False
    if x < 0 or x >= len(board[y]):
        return False
    return board[y][x] is query

def do_simple_move(direction, starting_location, player, board):
    """Returns the board that results from player making a simple move in direction with a piece at starting_location"""
    mover_x, mover_y = starting_location
    # Move one square diagonally
    mover_x += direction.value
    mover_y += player.value
    if not square_is((mover_x, mover_y), Square.EMPTY, board):
        raise InvalidMove()

    def next_board_square(x, y):
        if x == mover_x and y == mover_y:
            return player.my_square
        elif x == starting_location[0] and y == starting_location[1]:
            return Square.EMPTY
        else:
            return board[y][x]

    return make_board(next_board_square)

def do_jumps(jumps, starting_location, player, board):
    """Returns the board that results from player making jumps with a piece at starting_location"""
    jumper_x, jumper_y = starting_location
    enemy_piece_locations = []
    for jump in jumps:
        enemy_piece_location = (jumper_x + jump.value, jumper_y + player.value)
        if square_is(enemy_piece_location, player.enemy.my_square, board):
            enemy_piece_locations.append(enemy_piece_location)
        else:
            # If the enemy_piece_location doesn't contain an enemy
            raise InvalidMove()
        # Jump two squares diagonally
        jumper_x += jump.value * 2
        jumper_y += player.value * 2
        if not square_is((jumper_x, jumper_y), Square.EMPTY, board):
            raise InvalidMove()

    def next_board_square(x, y):
        if x == jumper_x and y == jumper_y:
            return player.my_square
        elif x == starting_location[0] and y == starting_location[1]:
            return Square.EMPTY
        elif (x, y) in enemy_piece_locations:
            return Square.EMPTY
        else:
            return board[y][x]

    new_board = make_board(next_board_square)
    if board_has_potential_jumps(new_board, player):
        raise MoreJumpsRequired()
    return new_board

def do_move(move, starting_location, player, board):
    """Returns the board that results from active_player making move with a piece at starting_location"""
    # move might be a simple move or a series of jumps.
    if isinstance(move, MoveDir):
        return do_simple_move(move, starting_location, player, board)
    else:
        return do_jumps(move, starting_location, player, board)

def possible_simple_moves(location, player, board):
    """Returns a list of valid simple moves that the piece at location can make.
    A simple move is a move that's not a jump."""
    valid_moves = []
    moves_to_try = [MoveDir.LEFT, MoveDir.RIGHT]
    for move in moves_to_try:
        try:
            do_simple_move(move, location, player, board)
            # If we get this far it means our move was successful
            valid_moves.append(move)
        except InvalidMove:
            # print(move, "for", location, "and", player, "was invalid!")
            pass
    return valid_moves

def possible_jumps(location, player, board):
    """Returns a list of valid jumps that the piece at location can make."""
    valid_jumps = []
    jumps_to_try = [[MoveDir.LEFT], [MoveDir.RIGHT]]
    while jumps_to_try:
        jumps = jumps_to_try.pop()
        try:
            do_jumps(jumps, location, player, board)
            # If we've gotten this far it means our jumps worked!
            valid_jumps.append(jumps)
        except InvalidMove:
            pass
        except MoreJumpsRequired:
            # If we need to keep jumping this piece, we add more potential jumps to our list that are longer than the original sequence
            jumps_to_try.extend([jumps + [MoveDir.LEFT], jumps + [MoveDir.RIGHT]])
    return valid_jumps

def board_has_potential_jumps(board, active_player):
    """Returns True iff the board has a piece for active_player that can jump over an enemy"""
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x] is active_player.my_square and possible_jumps((x, y), active_player, board):
                return True
    return False

def possible_moves(location, active_player, board):
    """Returns a list of (location, active_player, move) tuples, where move is either
    a MoveDir representing a simple move, or a list of MoveDirs, representing a series of jumps"""
    # WARNING: Does not check for whether another piece must be moved!
    results = []
    jumps = possible_jumps(location, active_player, board)
    if jumps:
        for jump_option in jumps:
            results.append((location, active_player, jump_option))
    else:
        moves = possible_simple_moves(location, active_player, board)
        for move in moves:
            results.append((location, active_player, move))
    return results

def reason_piece_at_location_cant_move(location, active_player, board):
    """Returns either None or a string explaining why location doesn't have a piece active_player can move"""
    if location is None:
        return "You didn't select a piece."
    if board[location[1]][location[0]] == Square.EMPTY:
        return "That square is empty."
    if board[location[1]][location[0]] is not active_player.my_square:
        return "That piece doesn't belong to {}.".format(active_player)
    must_jump = board_has_potential_jumps(board, active_player)
    this_piece_jumps = possible_jumps(location, active_player, board)
    if must_jump and not this_piece_jumps:
        return "{} must jump, and that piece is not a valid jumper.".format(active_player)
    this_piece_simple_moves = possible_simple_moves(location, active_player, board)
    if not this_piece_simple_moves and not this_piece_jumps:
        return "That piece has no valid moves."
    return None

def locations_of_pieces_with_valid_moves(active_player, board):
    """Returns a list of (x,y) tuples for each location on the board that has a piece active_player can move"""
    results = []
    for y in range(len(board)):
        for x in range(len(board[y])):
            if reason_piece_at_location_cant_move((x, y), active_player, board) is None:
                results.append((x, y))
    return results

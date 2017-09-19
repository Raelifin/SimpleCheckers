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

X_CHARS = "hgfedcba"

class InvalidLocationString(Exception):
    """Custom exception for when player input doesn't parse into a board location."""

class InvalidMove(Exception):
    """Custom exception for invalid moves."""

class MoreJumpsRequired(Exception):
    """Custom exception for when a piece can make a jump,
    but it must keep jumping for the jump sequence to be valid."""

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

STARTING_BOARD = tuple(tuple(starting_square(x, y) for x in range(8)) for y in range(8))

def next_board(next_square_function, board):
    return tuple(tuple(next_square_function(x, y) for x in range(len(board[y]))) for y in range(len(board)))

def parse_location_from_str(s):
    # TODO Provide better feedback about reasons for problems.
    s = s.strip()
    if len(s) != 2:
        raise InvalidLocationString()
    x_char = s[0]
    if x_char not in X_CHARS:
        raise InvalidLocationString()
    x = X_CHARS.index(x_char)
    try:
        y = int(s[1]) - 1
    except ValueError:
        raise InvalidLocationString()
    if y < 0 or y > 7:
        raise InvalidLocationString()
    return (x, y)

def print_board(board):
    print()
    for y in range(len(board)):
        row = board[y]
        print("{}|{}".format(y + 1, "".join([str(square) for square in row])))
    print("  " + X_CHARS)
    print()

def square_is(location, query, board):
    """Checks if the piece at location equals query. Returns false if location is out of bounds."""
    x, y = location
    if y < 0 or y >= len(board):
        return False
    if x < 0 or x >= len(board[y]):
        return False
    return board[y][x] is query

def do_simple_move(direction, starting_location, player, board):
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

    return next_board(next_board_square, board)

def do_jumps(jumps, starting_location, player, board):
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

    new_board = next_board(next_board_square, board)
    if board_has_potential_jumps(new_board, player):
        raise MoreJumpsRequired()
    return new_board

def do_move(move, starting_location, player, board):
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
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x] is active_player.my_square and possible_jumps((x, y), active_player, board):
                return True
    return False

def can_move_piece_at_location(location, active_player, board, print_reasons=False):
    if location is None:
        return False  # Don't even bother giving a reason
    if board[location[1]][location[0]] == Square.EMPTY:
        if print_reasons:
            print("That square is empty.")
        return False
    if board[location[1]][location[0]] is not active_player.my_square:
        if print_reasons:
            print("That piece doesn't belong to {}.".format(active_player))
        return False
    must_jump = board_has_potential_jumps(board, active_player)
    this_piece_jumps = possible_jumps(location, active_player, board)
    if must_jump and not this_piece_jumps:
        if print_reasons:
            print("{} must jump, and that piece is not a valid jumper.".format(active_player))
        return False
    this_piece_simple_moves = possible_simple_moves(location, active_player, board)
    if not this_piece_simple_moves and not this_piece_jumps:
        if print_reasons:
            print("That piece has no valid moves.")
        return False
    return True

def possible_moves(location, active_player, board):
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

def pretty_location_str(location):
    x, y = location
    return X_CHARS[x] + str(y + 1)

def pretty_move_str(move):
    location, player, move_specifics = move
    if isinstance(move_specifics, MoveDir):
        new_x = location[0] + move_specifics.value
        new_y = location[1] + player.value
        return pretty_location_str(location) + " -> " + pretty_location_str((new_x, new_y))
    else:
        # Is a sequence of jumps!
        s = pretty_location_str(location)
        x, y = location
        for jump in move_specifics:
            # Jump two squares diagonally
            x += jump.value * 2
            y += player.value
            s += " -> " + pretty_location_str((x, y))
        return s

def get_choice_from_stdin(options, option_to_str):
    # TODO: Add the ability to say nevermind by selecting "0"
    print("Valid options are:")
    for i in range(len(options)):
        print("\t{}: {}".format(i + 1, option_to_str(options[i])))
    while True:
        try:
            integer = int(input("> "))
        except ValueError:
            print("That's not a valid number.")
        if integer < 1 or integer > len(options):
            print("Please input a number in the range 1 to {}.".format(len(options)))
        else:
            return options[integer - 1]

def get_move_from_stdin(active_player, board):
    print("Select a piece to move.")
    location_of_piece_to_move = None
    while not can_move_piece_at_location(location_of_piece_to_move, active_player, board, print_reasons=True):
        try:
            location_of_piece_to_move = parse_location_from_str(input("> "))
        except InvalidLocationString:
            print("That's not a valid square. Try something like \"h6\"...")
    options = possible_moves(location_of_piece_to_move, active_player, board)
    return get_choice_from_stdin(options, pretty_move_str)

def main():
    board = STARTING_BOARD
    active_player = Player.RED

    print("Welcome to checkers!")
    print("X = Red's pieces")
    print("O = Black's pieces")
    print("The rules have been simplified for your convenience! Good luck!")

    while True:
        print_board(board)
        print("{}'s turn".format(active_player))
        piece_loc, player, move = get_move_from_stdin(active_player, board)

        board = do_move(move, piece_loc, player, board)
        active_player = active_player.enemy

if __name__ == '__main__':
    main()

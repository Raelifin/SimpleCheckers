from enum import Enum

class Player(Enum):
    RED = -1
    BLACK = 1

    def __str__(self):
        return self.name.title()

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

X_CHARS = "hgfedcba"

class InvalidLocationString(Exception):
    """Custom exception for when player input doesn't parse into a board location."""

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

def show_board(board):
    print()
    for y in range(len(board)):
        row = board[y]
        print("{}|{}".format(y + 1, "".join([str(square) for square in row])))
    print("  " + X_CHARS)
    print()

def can_move_piece_at_location(location, active_player, board, print_reasons=False):
    if location is None:
        return False  # Don't even bother giving a reason
    if board[location[1]][location[0]] == Square.EMPTY:
        if print_reasons:
            print("That square is empty.")
        return False
    if board[location[1]][location[0]].value != active_player.value:
        if print_reasons:
            print("That piece doesn't belong to {}.".format(active_player))
        return False
    return True

def get_move_from_stdin(active_player, board):
    print("Select a piece to move.")
    location_of_piece_to_move = None
    while not can_move_piece_at_location(location_of_piece_to_move, active_player, board, print_reasons=True):
        try:
            location_of_piece_to_move = parse_location_from_str(input("> "))
        except InvalidLocationString:
            print("That's not a valid square. Try something like \"h6\"...")
    print(location_of_piece_to_move)

def main():
    board = STARTING_BOARD
    active_player = Player.RED

    print("Welcome to checkers!")
    print("X = Red's pieces")
    print("O = Black's pieces")
    print("The rules have been simplified for your convenience! Good luck!")

    show_board(board)
    print("{}'s turn".format(active_player))
    move = get_move_from_stdin(active_player, board)

if __name__ == '__main__':
    main()

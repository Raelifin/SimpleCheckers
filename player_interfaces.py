import random

from game import MoveDir, Player, GameOver
from game import reason_piece_at_location_cant_move, locations_of_pieces_with_valid_moves, possible_moves

X_CHARS = "hgfedcba"

def print_board(board):
    """Prints a nice version of the board to StdOut"""
    print()
    for y in range(len(board)):
        row = board[y]
        print("{}|{}".format(y + 1, "".join([str(square) for square in row])))
    print("  " + X_CHARS)
    print()

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

# <DEFUNCT>
class InvalidLocationString(Exception):
    """Custom exception for when player input doesn't parse into a board location."""

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

def get_move_from_stdin_old_style(active_player, board):
    location_of_piece_to_move = None
    reason_cant_move = "Select a piece to move."
    while reason_cant_move:
        print(reason_cant_move)
        try:
            location_of_piece_to_move = parse_location_from_str(input("> "))
            reason_cant_move = reason_piece_at_location_cant_move(location_of_piece_to_move, active_player, board)
        except InvalidLocationString:
            reason_cant_move = "That's not a valid square. Try something like \"h6\"..."
    options = possible_moves(location_of_piece_to_move, active_player, board)
    return get_choice_from_stdin(options, pretty_move_str)
# </DEFUNCT

def get_move_from_stdin(active_player, board):
    piece_location_options = locations_of_pieces_with_valid_moves(active_player, board)
    if not piece_location_options:
        raise GameOver()
    location_of_piece_to_move = get_choice_from_stdin(piece_location_options, pretty_location_str)
    move_options = possible_moves(location_of_piece_to_move, active_player, board)
    return get_choice_from_stdin(move_options, pretty_move_str)

def get_move_randomly(active_player, board):
    piece_location_options = locations_of_pieces_with_valid_moves(active_player, board)
    if not piece_location_options:
        raise GameOver()
    location_of_piece_to_move = random.choice(piece_location_options)
    move_options = possible_moves(location_of_piece_to_move, active_player, board)
    return random.choice(move_options)

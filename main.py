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

def show_board(board):
    for y in range(len(board)):
        row = board[y]
        print("{}|{}".format(y + 1, "".join([str(square) for square in row])))
    print("  hgfedcba")

starting_board = [[starting_square(x, y) for x in range(8)] for y in range(8)]
active_player = Player.RED

show_board(starting_board)
print()
print("{}'s turn".format(active_player))

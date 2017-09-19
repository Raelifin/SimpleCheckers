from game import STARTING_BOARD
from game import Player
from game import do_move

from player_interfaces import print_board, get_move_from_stdin

def main():
    board = STARTING_BOARD
    active_player = Player.RED

    print()
    print("Welcome to checkers!")
    print()
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

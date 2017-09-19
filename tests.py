from game import STARTING_BOARD
from game import Player, GameOver
from game import do_move

from player_interfaces import get_move_randomly

def test_random_moves_get_game_over():
    num_games = 20
    num_moves = 500

    for _ in range(num_games):
        board = STARTING_BOARD
        active_player = Player.RED
        try:
            for _ in range(num_moves):
                piece_loc, player, move = get_move_randomly(active_player, board)
                board = do_move(move, piece_loc, player, board)
                active_player = active_player.enemy
            assert False, "Game did not finish with {} random moves!".format(num_moves)
        except GameOver:
            pass
    assert True

if __name__ == '__main__':
    print("Use nosetests to run this file! (Or python3 -m \"nose\")")

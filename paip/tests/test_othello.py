import unittest
import random
from paip.othello import *

class MoveTests(unittest.TestCase):
    def setUp(self):
        b = initial_board()
        # fig. 18.2a from PAIP p.598
        b[33:35] = [WHITE, BLACK]
        b[43:46] = [WHITE, WHITE, BLACK]
        b[52:57] = [WHITE, WHITE, WHITE, WHITE, BLACK]
        b[64:66] = [BLACK, WHITE]
        self.board = b
        
    def test_is_valid(self):
        self.assertTrue(is_valid(27))
        self.assertFalse(is_valid(30))
        self.assertFalse(is_valid(49))
        self.assertFalse(is_valid(-2))
        self.assertFalse(is_valid(124))
        self.assertFalse(is_valid('foo'))

    def test_find_bracketing_piece_none(self):
        square = 63
        self.assertEqual(None, find_bracket(63, WHITE, self.board, UP))
        self.assertEqual(None, find_bracket(63, WHITE, self.board, DOWN_RIGHT))
        self.assertEqual(None, find_bracket(63, WHITE, self.board, DOWN))
        self.assertEqual(None, find_bracket(63, WHITE, self.board, DOWN_LEFT))
        self.assertEqual(None, find_bracket(63, WHITE, self.board, LEFT))
        self.assertEqual(None, find_bracket(63, WHITE, self.board, UP_LEFT))
        
    def test_find_bracket(self):
        square = 42
        self.assertEqual(45, find_bracket(42, BLACK, self.board, RIGHT))
        self.assertEqual(64, find_bracket(42, BLACK, self.board, DOWN_RIGHT))

    def test_is_legal_false_not_empty(self):
        self.assertFalse(is_legal(64, WHITE, self.board))
    
    def test_is_legal_false_no_bracket(self):
        self.assertFalse(is_legal(42, WHITE, self.board))
    
    def test_is_legal(self):
        self.assertTrue(is_legal(42, BLACK, self.board))

    def test_make_flips_none(self):
        b1, b2 = self.board, list(self.board)
        make_flips(42, WHITE, b2, RIGHT)
        self.assertEqual(b1, b2)
    
    def test_make_flips(self):
        b1, b2 = self.board, list(self.board)
        make_flips(42, BLACK, b2, RIGHT)
        b1[43:45] = [BLACK, BLACK]
        self.assertEqual(b1, b2)
    
    def test_make_move(self):
        b1, b2 = self.board, list(self.board)
        make_move(42, BLACK, b2)
        b1[42] = BLACK
        b1[43:45] = [BLACK, BLACK]
        b1[53] = BLACK
        self.assertEqual(b1, b2)


class GameTests(unittest.TestCase):
    def setUp(self):
        self.board = initial_board()
        for sq in squares():
            self.board[sq] = WHITE
        self.board[11] = EMPTY
        self.board[88] = BLACK
    
    def test_any_legal_move_false(self):
        self.assertFalse(any_legal_move(WHITE, self.board))
    
    def test_any_legal_move(self):
        self.assertTrue(any_legal_move(BLACK, self.board))
    
    def test_next_player_repeat(self):
        self.assertEqual(BLACK, next_player(self.board, BLACK))
    
    def test_next_player_none(self):
        self.board[11] = WHITE
        self.assertEqual(None, next_player(self.board, BLACK))
    
    def test_next_player(self):
        self.assertEqual(BLACK, next_player(self.board, WHITE))

    def test_get_move_invalid(self):
        strategy = lambda player, board: -23
        self.assertRaises(IllegalMoveError, get_move, strategy, BLACK, self.board)
    
    def test_get_move_illegal(self):
        strategy = lambda player, board: 11
        self.assertRaises(IllegalMoveError, get_move, strategy, WHITE, self.board)
    
    def test_get_move(self):
        strategy = lambda player, board: 11
        self.assertEqual(11, get_move(strategy, BLACK, self.board))

    def test_score(self):
        make_move(11, BLACK, self.board)
        self.assertEqual(8 - 56, score(BLACK, self.board))

    def test_play(self):
        player_accesses = []
        def random_strategy(player, board):
            player_accesses.append(player)
            legal = [sq for sq in squares() if is_legal(sq, player, board)]
            return random.choice(legal)
        board, score = play(random_strategy, random_strategy)

        # check that no moves remain
        self.assertFalse(any_legal_move(BLACK, board))
        self.assertFalse(any_legal_move(WHITE, board))
        
        # check that both players had a turn
        self.assertTrue(BLACK in player_accesses)
        self.assertTrue(WHITE in player_accesses)


class StrategyTests(unittest.TestCase):
    def setUp(self):
        b = initial_board()
        #       1 2 3 4 5 6 7 8
        #     1 . . . . . . . .
        #     2 . . . . . . . .
        #     3 . . o @ . o . .
        #     4 . . o o @ @ . .
        #     5 . o o o o @ . .
        #     6 . . . @ o . . .
        #     7 . . . . . . . .
        #     8 . . . . . . . .
        b[33:37] = [WHITE, BLACK, EMPTY, WHITE]
        b[43:47] = [WHITE, WHITE, BLACK, BLACK]
        b[52:57] = [WHITE, WHITE, WHITE, WHITE, BLACK]
        b[64:66] = [BLACK, WHITE]
        self.board = b

    def test_maximizer(self):
        self.assertEqual(51, maximizer(score)(BLACK, self.board))
        self.assertEqual(47, maximizer(score)(WHITE, self.board))

    def test_weighted_score(self):
        score = weighted_score(BLACK, self.board)
        expected = 5 * 3 - (6 * 3 - 5 + 2 * 15)
        self.assertEqual(expected, score)
        self.assertEqual(-score, weighted_score(WHITE, self.board))

    def test_final_value(self):
        self.assertEqual(MIN_VALUE, final_value(BLACK, self.board))
        self.assertEqual(MAX_VALUE, final_value(WHITE, self.board))

    def test_minimax_leaf(self):
        val = score(BLACK, self.board)
        self.assertEqual((val, None), minimax(BLACK, self.board, 0, score))
        self.assertEqual((-val, None), minimax(WHITE, self.board, 0, score))
    
    def test_minimax_game_over(self):
        result, outcome = play(random_strategy, random_strategy)
        if outcome == 0:
            val_black, val_white = 0, 0
        else:
            val_black = MAX_VALUE if outcome > 0 else MIN_VALUE
            val_white = -val_black
        self.assertEqual((val_black, None), minimax(BLACK, result, 20, score))
        self.assertEqual((val_white, None), minimax(WHITE, result, 20, score))
    
    def test_minimax_pass(self):
        # remove all black pieces so black has no moves
        for sq in squares():
            if self.board[sq] == BLACK:
                self.board[sq] = EMPTY
        # result:
        #       1 2 3 4 5 6 7 8
        #     1 . . . . . . . .
        #     2 . . . . . . . .
        #     3 . . o . . o . .
        #     4 . . o o . . . .
        #     5 . o o o o . . .
        #     6 . . . . o . . .
        #     7 . . . . . . . .
        #     8 . . . . . . . .

        # leave one move for white
        self.board[57:59] = [BLACK, WHITE]
        # result:
        #       1 2 3 4 5 6 7 8
        #     1 . . . . . . . .
        #     2 . . . . . . . .
        #     3 . . o . . o . .
        #     4 . . o o . . . .
        #     5 . o o o o . @ o
        #     6 . . . . o . . .
        #     7 . . . . . . . .
        #     8 . . . . . . . .
        
        accesses = []
        def evaluate(player, board):
            accesses.append(player)
            return score(player, board)
        self.assertEqual(0, len(accesses))
        self.assertEqual((MIN_VALUE, None), minimax(BLACK, self.board, 20, evaluate))
    
    def test_minimax(self):
        board = initial_board()
        for sq in squares():
            board[sq] = EMPTY
        
        #       1 2 3 4 5 6 7 8
        #     1 . . . . . . . .
        #     2 . . . . . . . .
        #     3 . . . . . . . .
        #     4 . . . . . . . .
        #     5 . . . . . . . .
        #     6 . . . . . . . .
        #     7 . @ @ @ o @ . .
        #     8 . . . . . . . .
        board[72:77] = [BLACK, BLACK, BLACK, WHITE, BLACK]
        accesses = []
        def evaluate(player, board):
            accesses.append(player)
            return score(player, board)
        self.assertEqual((MAX_VALUE, 71), minimax(WHITE, board, 20, evaluate))
        self.assertEqual(0, len(accesses))

    def test_alphabeta(self):
        board = initial_board()
        for sq in squares():
            board[sq] = EMPTY
        
        #       1 2 3 4 5 6 7 8
        #     1 . @ o . . . . .
        #     2 . . . . . . . .
        #     3 . @ o o o . . .
        #     4 . . . . . . . .
        #     5 . @ o o o o o .
        #     6 . . . . . . . .
        #     7 . @ o o . . . .
        #     8 . . . . . . . .
        board[12:14] = [BLACK, WHITE]
        board[32:35] = [BLACK, WHITE, WHITE, WHITE]
        board[52:56] = [BLACK, WHITE, WHITE, WHITE, WHITE, WHITE]
        board[72:77] = [BLACK, WHITE, WHITE]
            
        # 1. 14, value -4, below alpha, ignore
        # 2. 36, value 0, above alpha, update alpha
        # 3. 58, value 4, above alpha, update alpha
        # 2. 75, value -2, alpha above beta, ignore and break
        expected_values = [4, 0, -4]
        
        values = []
        def evaluate(player, board):
            val = score(player, board)
            values.append(val)
            return val
        self.assertEqual((4, 58), alphabeta(BLACK, board, -1, 3, 1, evaluate))
        self.assertEqual(expected_values, values)

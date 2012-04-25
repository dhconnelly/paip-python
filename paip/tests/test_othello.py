import unittest
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

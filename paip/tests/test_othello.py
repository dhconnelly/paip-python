import unittest
from paip.othello import *

class BoardTests(unittest.TestCase):
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

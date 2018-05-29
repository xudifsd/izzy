#!/usr/bin/env python
# Tue May 29 10:58:36 CST 2018

import chess

import unittest
import logging

log = logging.getLogger("chess_test")

class TestTable(unittest.TestCase):
    """ case for chess table """

    def test_get_out_of_bound(self):
        table = chess.Table(5, 5)
        self.assertEquals(chess.Table.EMPTY, table.get(0, 0))
        self.assertEquals(chess.Table.EMPTY, table.get(4, 4))
        self.assertEquals(None, table.get(4, 5))
        self.assertEquals(None, table.get(5, 1))
        self.assertEquals(None, table.get(-1, -1))

    def test_set_value(self):
        table = chess.Table(5, 5)
        self.assertTrue(table.set(0, 0, chess.Table.WHITE))
        self.assertFalse(table.set(0, 0, chess.Table.BLACK))
        self.assertEquals(chess.Table.WHITE, table.get(0, 0))

        self.assertEquals(chess.Table.EMPTY, table.get(0, 1))

        self.assertTrue(table.set(0, 1, chess.Table.BLACK))
        self.assertFalse(table.set(0, 1, chess.Table.WHITE))
        self.assertEquals(chess.Table.BLACK, table.get(0, 1))

        self.assertFalse(table.set(0, 2, chess.Table.EMPTY))
        self.assertEquals(chess.Table.EMPTY, table.get(0, 2))

    def test_upper_left_to_lower_right_is_finished(self):
        # upper right
        table = chess.Table(10, 6)
        self.assertTrue(table.set(0, 1, chess.Table.WHITE))
        self.assertTrue(table.set(1, 2, chess.Table.WHITE))
        self.assertTrue(table.set(2, 3, chess.Table.WHITE))
        self.assertTrue(table.set(3, 4, chess.Table.WHITE))
        self.assertTrue(table.set(4, 5, chess.Table.WHITE))
        self.assertTrue(table.is_finished())

        # lower left
        table = chess.Table(10, 6)
        self.assertTrue(table.set(1, 0, chess.Table.WHITE))
        self.assertTrue(table.set(2, 1, chess.Table.WHITE))
        self.assertTrue(table.set(3, 2, chess.Table.WHITE))
        self.assertTrue(table.set(4, 3, chess.Table.WHITE))
        self.assertTrue(table.set(5, 4, chess.Table.WHITE))
        self.assertTrue(table.is_finished())

    def test_lower_left_to_upper_right_is_finished(self):
        # upper left
        table = chess.Table(10, 6)
        self.assertTrue(table.set(4, 0, chess.Table.WHITE))
        self.assertTrue(table.set(3, 1, chess.Table.WHITE))
        self.assertTrue(table.set(2, 2, chess.Table.WHITE))
        self.assertTrue(table.set(1, 3, chess.Table.WHITE))
        self.assertTrue(table.set(0, 4, chess.Table.WHITE))
        self.assertTrue(table.is_finished())

        # lower right
        table = chess.Table(10, 6)
        self.assertTrue(table.set(9, 1, chess.Table.WHITE))
        self.assertTrue(table.set(8, 2, chess.Table.WHITE))
        self.assertTrue(table.set(7, 3, chess.Table.WHITE))
        self.assertTrue(table.set(6, 4, chess.Table.WHITE))
        self.assertTrue(table.set(5, 5, chess.Table.WHITE))
        self.assertTrue(table.is_finished())

    def test_row_wise_is_finished(self):
        table = chess.Table(10, 10)
        self.assertTrue(table.set(0, 1, chess.Table.BLACK))
        self.assertTrue(table.set(0, 2, chess.Table.BLACK))
        self.assertTrue(table.set(0, 3, chess.Table.BLACK))
        self.assertTrue(table.set(0, 4, chess.Table.BLACK))
        self.assertTrue(table.set(0, 5, chess.Table.BLACK))
        self.assertTrue(table.is_finished())

    def test_column_wise_is_finished(self):
        table = chess.Table(10, 10)
        self.assertTrue(table.set(1, 5, chess.Table.BLACK))
        self.assertTrue(table.set(2, 5, chess.Table.BLACK))
        self.assertTrue(table.set(3, 5, chess.Table.BLACK))
        self.assertTrue(table.set(4, 5, chess.Table.BLACK))
        self.assertTrue(table.set(5, 5, chess.Table.BLACK))
        self.assertTrue(table.is_finished())

    def test_different_type_in_middle_is_unfinished(self):
        table = chess.Table(10, 6)
        self.assertTrue(table.set(0, 1, chess.Table.WHITE))
        self.assertTrue(table.set(1, 2, chess.Table.WHITE))
        self.assertTrue(table.set(2, 3, chess.Table.BLACK))
        self.assertTrue(table.set(3, 4, chess.Table.WHITE))
        self.assertTrue(table.set(4, 5, chess.Table.WHITE))
        self.assertFalse(table.is_finished())

        table = chess.Table(10, 6)
        self.assertTrue(table.set(1, 0, chess.Table.WHITE))
        self.assertTrue(table.set(2, 1, chess.Table.WHITE))
        self.assertTrue(table.set(3, 2, chess.Table.BLACK))
        self.assertTrue(table.set(4, 3, chess.Table.WHITE))
        self.assertTrue(table.set(5, 4, chess.Table.WHITE))
        self.assertFalse(table.is_finished())

        table = chess.Table(10, 6)
        self.assertTrue(table.set(4, 0, chess.Table.WHITE))
        self.assertTrue(table.set(3, 1, chess.Table.WHITE))
        self.assertTrue(table.set(2, 2, chess.Table.WHITE))
        self.assertTrue(table.set(1, 3, chess.Table.WHITE))
        self.assertTrue(table.set(0, 4, chess.Table.BLACK))
        self.assertFalse(table.is_finished())

        table = chess.Table(10, 6)
        self.assertTrue(table.set(9, 1, chess.Table.BLACK))
        self.assertTrue(table.set(8, 2, chess.Table.WHITE))
        self.assertTrue(table.set(7, 3, chess.Table.WHITE))
        self.assertTrue(table.set(6, 4, chess.Table.WHITE))
        self.assertTrue(table.set(5, 5, chess.Table.WHITE))
        self.assertFalse(table.is_finished())

        table = chess.Table(10, 10)
        self.assertTrue(table.set(0, 1, chess.Table.BLACK))
        self.assertTrue(table.set(0, 2, chess.Table.WHITE))
        self.assertTrue(table.set(0, 3, chess.Table.BLACK))
        self.assertTrue(table.set(0, 4, chess.Table.BLACK))
        self.assertTrue(table.set(0, 5, chess.Table.BLACK))
        self.assertFalse(table.is_finished())

        table = chess.Table(10, 10)
        self.assertTrue(table.set(1, 5, chess.Table.BLACK))
        self.assertTrue(table.set(2, 5, chess.Table.BLACK))
        self.assertTrue(table.set(3, 5, chess.Table.BLACK))
        self.assertTrue(table.set(4, 5, chess.Table.WHITE))
        self.assertTrue(table.set(5, 5, chess.Table.BLACK))
        self.assertFalse(table.is_finished())

if __name__ == '__main__':
    unittest.main()

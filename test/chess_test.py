#!/usr/bin/env python
# Tue May 29 10:58:36 CST 2018

import chess

import unittest
import logging

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

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(thread)d : %(levelname)s : %(message)s',
                        level=logging.DEBUG)

    unittest.main()

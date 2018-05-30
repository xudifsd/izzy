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


class TestSession(unittest.TestCase):
    """ case for session """

    def _build_unfinished_test_session(self):
        result = chess.Session("a", "b", True, False)
        result.move(1, 2)
        result.move(1, 3)
        result.move(2, 3)
        result.move(2, 4)
        result.move(3, 4)
        result.move(3, 5)
        result.move(4, 5)
        result.move(4, 6)
        return result

    def _build_finished_test_session(self):
        result = self._build_unfinished_test_session()
        result.move(5, 6)
        return result

    def _assert_session_equals(self, s1, s2):
        self.assertEquals(s1.players, s2.players)
        self.assertEquals(s1.current, s2.current)

        self.assertEquals(s1.table.row, s2.table.row)
        self.assertEquals(s1.table.col, s2.table.col)
        self.assertEquals(s1.table.data, s2.table.data)

        self.assertEquals(len(s1.history), len(s2.history))

        for i in xrange(len(s1.history)):
            h1 = s1.history[i]
            h2 = s2.history[i]
            self.assertEquals(h1.row, h2.row)
            self.assertEquals(h1.col, h2.col)
            self.assertEquals(h1.author, h2.author)
            self.assertEquals(h1.timestamp, h2.timestamp)
            self.assertEquals(h1.is_ai, h2.is_ai)


    def test_can_not_serialize_unfinished_session(self):
        self.assertEquals(None, self._build_unfinished_test_session().serialize())

    def test_serialize_and_deserialize(self):
        finished_session = self._build_finished_test_session()
        self.assertNotEquals(None, finished_session.serialize())

        returned_session = chess.Session.deserialize(finished_session.serialize())

        self._assert_session_equals(finished_session, returned_session)

    def test_get_winner(self):
        self.assertEquals(None, self._build_unfinished_test_session().get_winner())
        self.assertEquals("a", self._build_finished_test_session().get_winner())

    def test_get_curret_player_name(self):
        self.assertEquals("a", self._build_unfinished_test_session().get_current_player_name())
        self.assertEquals("b", self._build_finished_test_session().get_current_player_name())

if __name__ == '__main__':
    unittest.main()

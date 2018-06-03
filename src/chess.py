#!/usr/bin/env python
# Mon May 28 18:55:57 CST 2018

import datetime
import time

import logging

log = logging.getLogger("chess")

import session_pb2

class Table(object):
    """ table represent a chess table, only 3 value are valid: 0, 1, 2"""

    EMPTY, BLACK, WHITE = range(3)

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.data = 0

    def _bit_offset(self, row, col):
        return 2 * ((row * self.row) + col)

    def set(self, row, col, type):
        """ return True on success """
        if type != Table.BLACK and type != Table.WHITE:
            log.debug("invalid type %d", type)
            return False
        if self.get(row, col) != Table.EMPTY:
            log.debug("position %d,%d has been occupied or invalid", row, col)
            return False

        self.data |= type << self._bit_offset(row, col)
        return True

    def get(self, row, col):
        """ return None on invalid """
        if row < 0 or row >= self.row:
            log.debug("row %d invalid", row)
            return None
        if col < 0 or col >= self.col:
            log.debug("col %d invalid", col)
            return None

        bit_pos = self._bit_offset(row, col)

        return (self.data & (3 << bit_pos)) >> bit_pos

    def is_finished(self):
        """ check if game is finished """

        class Checker(object):
            """ check if has continual occurance of same type """
            def __init__(self):
                self.last_type = 0
                self.num = 0

            def reset(self):
                self.last_type = 0
                self.num = 0

            def is_win(self, type):
                if type == Table.EMPTY:
                    self.reset()
                else:
                    if self.last_type == type:
                        self.num += 1
                        if self.num == 5:
                            return True
                    else:
                        self.last_type = type
                        self.num = 1
                return False

        checker = Checker()

        # check row wise
        for row in xrange(self.row):
            checker.reset()
            for col in xrange(self.col):
                if checker.is_win(self.get(row, col)):
                    return True

        checker.reset()

        # check column wise
        for col in xrange(self.col):
            checker.reset()
            for row in xrange(self.row):
                if checker.is_win(self.get(row, col)):
                    return True

        checker.reset()

        # check upper left to lower right wise
        for delta in xrange(-self.col + 1, self.row):
            if delta <= 0:
                row, col = 0, abs(delta)
            else:
                row, col = delta, 0

            checker.reset()
            while row < self.row and col < self.col and row > -1 and col > -1:
                if checker.is_win(self.get(row, col)):
                    return True
                row += 1
                col += 1

        # check lower left to upper right wise
        for delta in xrange(0, self.row + self.col - 2):
            if delta < self.row:
                row, col = delta, 0
            else:
                row, col = self.row - 1, delta - self.row

            checker.reset()
            while row < self.row and col < self.col and row > -1 and col > -1:
                if checker.is_win(self.get(row, col)):
                    return True
                row -= 1
                col += 1

        return False

    def to_array(self):
        result = []
        for row in xrange(self.row):
            row_array = []
            for col in xrange(self.col):
                row_array.append(self.get(row, col))
            result.append(row_array)
        return result

    def to_ascii(self):
        buf = []

        row_buf = []
        for col in xrange(-1, self.col):
            if col < 0:
                row_buf.append("  ")
            else:
                row_buf.append("%2s" % (col))
        buf.append("|".join(row_buf))

        row_buf = []
        for _ in xrange(-1, self.col):
            row_buf.append("__")
        buf.append("|".join(row_buf))

        for row in xrange(self.row):
            row_buf = []
            for col in xrange(-1, self.col):
                if col < 0:
                    row_buf.append("  ")
                else:
                    val = self.get(row, col)
                    if val == Table.EMPTY:
                        row_buf.append("  ")
                    elif val == Table.BLACK:
                        row_buf.append("**")
                    else:
                        row_buf.append("##")
            buf.append("|".join(row_buf))

            row_buf = []
            for col in xrange(-1, self.col):
                if col < 0:
                    row_buf.append("%2s" % (row))
                else:
                    val = self.get(row, col)
                    if val == Table.EMPTY:
                        row_buf.append("__")
                    elif val == Table.BLACK:
                        row_buf.append("**")
                    else:
                        row_buf.append("##")

            buf.append("|".join(row_buf))
        return "\n".join(buf)


class Move(object):
    """ move made by someone """

    def __init__(self, row, col, author, timestamp, is_ai):
        self.row = row
        self.col = col
        self.author = author
        self.timestamp = timestamp
        self.is_ai = is_ai


class Session(object):
    """ represent a session of a game """
    TABLE_SIZE = 15

    MOVE_OK, MOVE_INVALID, MOVE_NOT_PLAYER, MOVE_NOT_YOUR_TURN = range(4)

    def __init__(self, player1_name, player2_name, player1_is_ai, player2_is_ai):
        self.players = [player1_name, player2_name]
        self.types = [Table.BLACK, Table.WHITE]
        self.current = 0
        self.table = Table(Session.TABLE_SIZE, Session.TABLE_SIZE)
        self.history = []

    def get_current_player_name(self):
        return self.players[self.current]

    def move(self, row, col, player=None, timestamp=None):
        """ return move status """

        current_type = self.types[self.current]
        if player is None:
            player_name = self.players[self.current]
        else:
            if player not in self.players:
                return Session.MOVE_NOT_PLAYER
            elif player != self.players[self.current]:
                return Session.MOVE_NOT_YOUR_TURN
            else:
                player_name = player

        if not self.table.is_finished() and self.table.set(row, col, current_type):
            self.current += 1
            self.current %= 2
            if timestamp is None:
                timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

            self.history.append(Move(row, col, player_name, timestamp, False))
            return Session.MOVE_OK

        return Session.MOVE_INVALID

    def get_winner(self):
        """ check if last move win the game """
        if self.table.is_finished():
            return self.history[-1].author

        return None

    def get_table_ascii(self):
        return self.table.to_ascii()

    def serialize(self):
        """ return None on not finished """
        if self.get_winner() is None:
            return None

        session = session_pb2.Session()
        session.player1 = self.players[0]
        session.player2 = self.players[1]
        session.player1_is_ai = False
        session.player2_is_ai = False

        for move in self.history:
            m = session.moves.add()
            m.row = move.row
            m.col = move.col
            m.timestamp = move.timestamp

        return session.SerializeToString()

    @classmethod
    def deserialize(cls, data):
        """ from binary """
        session = session_pb2.Session()
        session.ParseFromString(data)

        result = cls(session.player1, session.player2, session.player1_is_ai, session.player2_is_ai)

        players = [session.player1, session.player2]
        i = 0

        for move in session.moves:
            result.move(move.row, move.col, players[i], move.timestamp)
            i += 1
            i %= 2

        return result


if __name__ == '__main__':
    pass

#!/usr/bin/env python
# Mon May 28 18:55:57 CST 2018

import datetime
import time

import logging

log = logging.getLogger("chess")

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

    def to_ascii(self):
        buf = []

        for row in xrange(self.row):
            row_buf = []
            for col in xrange(self.col):
                val = self.get(row, col)
                if val == Table.EMPTY:
                    row_buf.append("_")
                elif val == Table.BLACK:
                    row_buf.append("*")
                else:
                    row_buf.append("#")

            buf.append("|".join(row_buf))
        return "\n".join(buf)


class Move(object):
    """ move made by someone """

    def __init__(self, row, col, author, timestamp):
        self.row = row
        self.col = col
        self.author = author
        self.timestamp = timestamp


class Session(object):
    """ represent a session of a game """
    TABLE_SIZE = 15

    def __init__(self, player1_name, player2_name):
        self.players = [player1_name, player2_name]
        self.types = [Table.BLACK, Table.WHITE]
        self.current = 0
        self.table = Table(Session.TABLE_SIZE, Session.TABLE_SIZE)
        self.history = []

    def get_current_player_name(self):
        return self.players[self.current]

    def move(self, row, col):
        """ return True on success """

        current_type = self.types[self.current]
        player_name = self.players[self.current]

        if self.table.set(row, col, current_type):
            self.current += 1
            self.current %= 2
            timestamp = time.mktime(datetime.datetime.now().timetuple())

            self.history.append(Move(row, col, player_name, timestamp))
            return True

        return False

    def get_winner(self):
        """ check if last move win the game """
        if self.table.is_finished():
            return self.history[-1].author

        return None

    def get_table_ascii(self):
        return self.table.to_ascii()


def commandline_interface():
    player1_name = raw_input("please input first player's name: ")
    player2_name = raw_input("please input second player's name: ")

    session = Session(player1_name, player2_name)
    has_error = False

    while session.get_winner() is None:
        if not has_error:
            print session.get_table_ascii()

        prompt = "%s please make a move 'row, col': " % (session.get_current_player_name())
        row_col = raw_input(prompt)
        parts = row_col.split(",")

        if len(parts) != 2:
            print "move should be seperated by `,`, but get " + row_col
            has_error = True
            continue

        try:
            row = int(parts[0])
            col = int(parts[1])
        except ValueError as e:
            print "row or col is not a number " + row_col
            has_error = True
            continue

        if not session.move(row, col):
            print "invalid move " + row_col
            has_error = True
            continue

        has_error = False

    print "%s is winner" % (session.get_winner())


if __name__ == '__main__':
    commandline_interface()
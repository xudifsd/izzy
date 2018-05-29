#!/usr/bin/env python
# Mon May 28 18:55:57 CST 2018

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

if __name__ == '__main__':
    pass

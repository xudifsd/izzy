#!/usr/bin/env python
# Tue May 29 20:13:50 CST 2018

import sys
import argparse
import datetime
import time

import chess
import persist

SAVE_TARGET = "data/sessions.data"

def play(store_path):
    player1_name = raw_input("please input first player's name: ")
    player2_name = raw_input("please input second player's name: ")

    session = chess.Session(player1_name, player2_name)
    has_error = False

    while session.get_winner() is None:
        if not has_error:
            print session.get_table_ascii()

        prompt = "%s, please make a move 'row, col': " % (session.get_current_player_name())
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

    print "%s is winner, saving" % (session.get_winner())

    if append_to_store(store_path, session.serialize()):
        print "saving success"
    else:
        print "saving failed"


def replay_session(src):
    """ replay alread saved sessions """
    for data in persist.iterate_over_store(SAVE_TARGET):
        session = chess.Session.deserialize(data)

        # for display
        table = chess.Table(chess.Session.TABLE_SIZE, chess.Session.TABLE_SIZE)

        types = [chess.Table.BLACK, chess.Table.WHITE]
        i = 0

        for move in session.history:
            table.set(move.row, move.col, types[i])
            i += 1
            i %= 2

            date = datetime.datetime.fromtimestamp(move.timestamp)

            print "%s(is_ai=%r) make move in %d,%d in %s" % (move.author, move.is_ai, move.row, move.col, date.isoformat())
            print table.to_ascii()
            time.sleep(1)

        print "-" * 100


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--play", help="play Gomoku", action="store_true")
    parser.add_argument("-r", "--replay", help="replay old sessions", action="store_true")

    args = parser.parse_args()

    if args.play:
        play(SAVE_TARGET)
    elif args.replay:
        replay_session(SAVE_TARGET)
    else:
        parser.print_help()
        sys.exit(1)

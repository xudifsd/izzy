#!/usr/bin/env python
# Tue May 29 20:13:50 CST 2018

import chess

def commandline_interface():
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

    session.save()

def read():
    chess.Session.replay()

if __name__ == '__main__':
    commandline_interface()
    #read()

#!/usr/bin/env python
# Sun Jun 3 19:50:34 CST 2018

""" ai part of this project, credit goes to <Make Your Own Neural Network> """

import numpy
import scipy.special
import scipy.misc
import logging
import threading

log = logging.getLogger("izzy")

import chess

class Neuron(object):
    def __init__(self, wih, who, activation_fn, learning_rate):
        self.wih = wih
        self.who = who
        self.activation_fn = activation_fn
        self.learning_rate = learning_rate

    @classmethod
    def empty(cls, input_num, hidden_num, output_num, learning_rate):
        # weights between input and hidden
        wih = numpy.random.normal(0.0, pow(input_num, -0.5), (hidden_num, input_num))
        # weights between hidden and output
        who = numpy.random.normal(0.0, pow(hidden_num, -0.5), (output_num, hidden_num))

        activation_fn = lambda x: scipy.special.expit(x)

        return cls(wih, who, activation_fn, learning_rate)

    def train(self, inputs_list, targets_list):
        inputs = numpy.array(inputs_list, ndmin=2).T
        targets = numpy.array(targets_list, ndmin=2).T

        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_fn(hidden_inputs)

        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_fn(final_inputs)

        output_errors = targets - final_outputs
        hidden_errors = numpy.dot(self.who.T, output_errors)

        self.who += self.learning_rate * numpy.dot((output_errors * final_outputs * (1.0 - final_outputs)), numpy.transpose(hidden_outputs))

        self.wih += self.learning_rate * numpy.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), numpy.transpose(inputs))


    def query(self, inputs_list):
        inputs = numpy.array(inputs_list, ndmin=2).T

        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_fn(hidden_inputs)

        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_fn(final_inputs)

        return final_outputs

    def copy(self):
        return Neuron(self.wih, self.who, self.activation_fn, self.learning_rate)


def flatten(array):
    return [subitem for sublist in array for subitem in sublist]


class Izzy(object):
    HIDDEN_NUM = 400
    LEARNING_RATE = 0.7

    def __init__(self, slot_num, neural):
        self.lock = threading.RLock()
        self.slot_num = slot_num
        self.neural = neural

    @classmethod
    def new(cls):
        slot_num = chess.Session.TABLE_SIZE * chess.Session.TABLE_SIZE
        neural = Neuron.empty(slot_num, Izzy.HIDDEN_NUM, slot_num, Izzy.LEARNING_RATE)
        return cls(slot_num, neural)

    def scale_inputs(self, inputs):
        return (numpy.asfarray(inputs) / 4.0 * 0.99) + 0.01

    def train(self, sessions):
        with self.lock:
            for session in sessions:
                if session.get_winner() is None:
                    log.warn("session should finished before can be used as training data")
                    continue

                winning_moves = (len(session.history) - 1) % 2

                for offset, move in enumerate(session.history):
                    inputs = flatten(move.before_moved_table.to_array())
                    scaled_input = self.scale_inputs(inputs)

                    targets = [0.01] * self.slot_num

                    if offset % 2 == winning_moves:
                        targets[move.row * chess.Session.TABLE_SIZE + move.col] = 0.99
                    else:
                        if move.is_ai:
                            log.debug("skip ai's move if it's not winner")
                            continue
                        targets[move.row * chess.Session.TABLE_SIZE + move.col] = 0.88

                    self.neural.train(scaled_input, targets)

    def query(self, session):
        inputs = flatten(session.table.to_array())
        scaled_input = self.scale_inputs(inputs)
        result = flatten(self.neural.query(scaled_input))

        # remove that can not be placed
        for offset, slot_val in enumerate(inputs):
            if slot_val != chess.Table.EMPTY:
                result[offset] = 0.0

        pos = int(numpy.argmax(result))
        row = pos / chess.Session.TABLE_SIZE
        col = pos % chess.Session.TABLE_SIZE
        log.debug("place %d,%d(%d) with confidence %f", row, col, pos, result[pos])
        return row, col

    def copy(self):
        with self.lock:
            return Izzy(self.slot_num, self.neural.copy())


if __name__ == '__main__':
    pass

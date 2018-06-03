#!/usr/bin/env python
# Wed May 30 15:37:57 CST 2018

import struct
import zlib
import threading
import logging
import time
from Queue import Queue
from Queue import Empty

log = logging.getLogger("persist")


# format: [len of compressed data][compressed data][len of compressed data][compressed data]...

def append_to_store(path, data):
    """ append data to the end of store, return True on success """
    sessions = []

    with open(path, "ab") as f:
        compressed = zlib.compress(data)

        f.write(struct.pack("i", len(compressed)))
        f.write(compressed)

    return True


def iterate_over_store(path):
    """ iterate over data store """
    with open(path, "rb") as f:
        while True:
            data = f.read(4)
            if data == "":
                break

            length, = struct.unpack("i", data)
            data = f.read(length)
            decompressed = zlib.decompress(data)

            yield decompressed


class PersistManager(object):
    def __init__(self, path):
        self.path = path
        self.running = True
        self.queue = Queue()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.run, args=(),
                name="persist-manager")
        self.thread.start()

    def persist(self, val):
        self.queue.put(val)

    def run(self):
        while self.running:
            try:
                val = self.queue.get(False)
                append_to_store(self.path, val)
                log.info("appended val to store %s", self.path)
            except Empty:
                time.sleep(0.5)

    def join(self):
        while not self.queue.empty():
            time.sleep(0.2)

        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None



if __name__ == '__main__':
    pass

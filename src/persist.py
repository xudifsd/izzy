#!/usr/bin/env python
# Wed May 30 15:37:57 CST 2018

import struct
import zlib

# format: [len of compressed data][compressed data][len of compressed data][compressed data]...

def append_to_store(path, data):
    """ append data to the end of store, return True on success """
    sessions = []

    with open(target, "ab") as f:
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


if __name__ == '__main__':
    pass

#!/usr/bin/env python
#-*- encoding:utf-8 -*-

# Wed May 30 16:46:28 CST 2018

import tempfile
import unittest
import logging

log = logging.getLogger("persist_test")

import persist

class TestPersist(unittest.TestCase):
    """ case for chess table """

    data = [
        "True Colors",
        "アンジェラ・アキ",
        "",
        "同じ色に染れない僕は独り いつも無口",
        "果てない闇の深淵に立って",
        "途方に暮れる時もある",
        "Can you see my true colors shining through?",
        "ありのままの 僕でいいのか",
        "問いかけても 心の中",
        "色あせた 自分の 声が",
        "こだましている",
        "",
        "同じ色に染まらない君はなぜか いつも笑顔だ",
        "痛みがわかる人の優しさで",
        "僕にそっと つぶやいた",
        "I see your true colors shining through",
        "ありのままの 君が好きだよ",
        "恐れずに 上を向いて",
        "君だけの 可能性が",
        "光っている",
        "",
        "like a rainbow, like a rainbow",
        "",
        "in a world full of people you can lose sight of it all",
        "and the darkness inside you can make you feel so small",
        "涙は未来の宝石だから",
        "泣いたぶんだけ 価値がある",
        "I see your true colors shining through",
        "I see your true colors and that's why I love you",
        "So don't be afraid to let them show",
        "Your true colors your true colors are beautiful",
        "I see your true colors shining through",
        "ありのままの君でいいから",
        "恐れずに 上を向いて",
        "明日の 君だけの 可能性が 光っている",
        "Like a rainbow",
        "Like a rainbow",
        ]

    def test_iterate_over_store(self):
        with tempfile.NamedTemporaryFile() as f:
            f_name = f.name

            for d in TestPersist.data:
                persist.append_to_store(f_name, d)

            for offset, readback in enumerate(persist.iterate_over_store(f_name)):
                self.assertEquals(TestPersist.data[offset], readback)

    def test_append_while_read(self):
        with tempfile.NamedTemporaryFile() as f:
            f_name = f.name

            data = ["a", "b", "c", "d"]

            persist.append_to_store(f_name, data[0])

            for offset, readback in enumerate(persist.iterate_over_store(f_name)):
                if offset + 1 != len(data):
                    persist.append_to_store(f_name, data[offset + 1])

            self.assertEquals(len(data) - 1, offset)

if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Store files in ZIP archives"""

from .common import PostProcessor
from .. import util


class MangaPlusDRMPP(PostProcessor):
    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        print("init")

        job.register_hooks({
            "file": self.process, "finalize": self.finalize
        }, options)

    def process(self, pathfmt):
        print("process")
        print(pathfmt)

    def finalize(self, pathfmt, status):
        print(pathfmt)
        print(status)
        print("done!")

    # algorithm borrowed from:
    # https://github.com/tachiyomiorg/tachiyomi-extensions/blob/b1dfa393779606aef653087360d511140fdcdb2b/src/all/mangaplus/src/eu/kanade/tachiyomi/extension/all/mangaplus/MangaPlus.kt#L382-L391
    def _decode_image(encryption_key, image_bytes):
        def chunked(size, source):
            for i in range(0, len(source), size):
                yield source[i:i+size]

        key_stream = [int(bit, 16) for bit in chunked(2, encryption_key)]

        image_bytes = [bool(byte) ^ bool(key_stream[i % len(key_stream)])
                       for i, byte in enumerate(image_bytes)]

        return image_bytes


__postprocessor__ = MangaPlusDRMPP

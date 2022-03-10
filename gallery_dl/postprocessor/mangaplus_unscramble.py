# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
# Copyright 2022 Merilynn Bandy
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Remove DRM on downloads from https://mangaplus.shueisha.co.jp"""

from .common import PostProcessor
from pathlib import Path


class MangaPlusUnscramblePP(PostProcessor):
    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        job.register_hooks({"file": self.process}, options)

    def process(self, pathfmt):
        encryption_key = pathfmt.kwdict['encryption_key']

        in_path = Path(pathfmt.temppath)
        out_path = Path(pathfmt.realpath)

        with open(in_path, "rb") as in_file, open(out_path, "wb") as out_file:
            image_bytes = in_file.read()

            decoded = self._decode_image(encryption_key, image_bytes)

            out_file.write(decoded)

        # delete file at pathfmt.temppath when done
        pathfmt.delete = True

    # algorithm borrowed from:
    # https://github.com/tachiyomiorg/tachiyomi-extensions/blob/b1dfa393779606aef653087360d511140fdcdb2b/src/all/mangaplus/src/eu/kanade/tachiyomi/extension/all/mangaplus/MangaPlus.kt#L382-L391
    @staticmethod
    def _decode_image(encryption_key: str, image_bytes: bytes):
        """Shifts bytes on an image to undo MangaPlus DRM"""
        def chunked(size, source):
            for i in range(0, len(source), size):
                yield source[i:i+size]

        key_stream = [int(bit, 16) for bit in chunked(2, encryption_key)]

        buffer = [byte ^ key_stream[i % len(key_stream)]
                  for i, byte in enumerate(image_bytes)]

        return bytes(buffer)


__postprocessor__ = MangaPlusUnscramblePP

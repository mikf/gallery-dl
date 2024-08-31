# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Compute file hash digests"""

from .common import PostProcessor
import hashlib


class HashPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        self.chunk_size = options.get("chunk-size", 32768)
        self.filename = options.get("filename")

        hashes = options.get("hashes")
        if isinstance(hashes, dict):
            self.hashes = list(hashes.items())
        elif isinstance(hashes, str):
            self.hashes = []
            for h in hashes.split(","):
                name, sep, key = h.partition(":")
                self.hashes.append((key if sep else name, name))
        elif hashes:
            self.hashes = hashes
        else:
            self.hashes = (("md5", "md5"), ("sha1", "sha1"))

        events = options.get("event")
        if events is None:
            events = ("file",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

    def run(self, pathfmt):
        hashes = [
            (key, hashlib.new(name))
            for key, name in self.hashes
        ]

        size = self.chunk_size
        with self._open(pathfmt) as fp:
            while True:
                data = fp.read(size)
                if not data:
                    break
                for _, h in hashes:
                    h.update(data)

        for key, h in hashes:
            pathfmt.kwdict[key] = h.hexdigest()

        if self.filename:
            pathfmt.build_path()

    def _open(self, pathfmt):
        try:
            return open(pathfmt.temppath, "rb")
        except OSError:
            return open(pathfmt.realpath, "rb")


__postprocessor__ = HashPP

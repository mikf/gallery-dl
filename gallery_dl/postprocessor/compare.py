# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Compare versions of the same file and replace/enumerate them on mismatch"""

from .common import PostProcessor
from .. import text, util, output, exception
import os


class ComparePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        if options.get("shallow"):
            self._compare = self._compare_size
        self._equal_exc = self._equal_cnt = 0

        equal = options.get("equal")
        if equal:
            equal, _, emax = equal.partition(":")
            self._equal_max = text.parse_int(emax)
            if equal == "abort":
                self._equal_exc = exception.StopExtraction
            elif equal == "terminate":
                self._equal_exc = exception.TerminateExtraction
            elif equal == "exit":
                self._equal_exc = SystemExit

        job.register_hooks({"file": (
            self.enumerate
            if options.get("action") == "enumerate" else
            self.replace
        )}, options)

    def replace(self, pathfmt):
        try:
            if self._compare(pathfmt.realpath, pathfmt.temppath):
                return self._equal(pathfmt)
        except OSError:
            pass
        self._equal_cnt = 0

    def enumerate(self, pathfmt):
        num = 1
        try:
            while not self._compare(pathfmt.realpath, pathfmt.temppath):
                pathfmt.prefix = prefix = format(num) + "."
                pathfmt.kwdict["extension"] = prefix + pathfmt.extension
                pathfmt.build_path()
                num += 1
            return self._equal(pathfmt)
        except OSError:
            pass
        self._equal_cnt = 0

    def _compare(self, f1, f2):
        return self._compare_size(f1, f2) and self._compare_content(f1, f2)

    @staticmethod
    def _compare_size(f1, f2):
        return os.stat(f1).st_size == os.stat(f2).st_size

    @staticmethod
    def _compare_content(f1, f2):
        size = 16384
        with open(f1, "rb") as fp1, open(f2, "rb") as fp2:
            while True:
                buf1 = fp1.read(size)
                buf2 = fp2.read(size)
                if buf1 != buf2:
                    return False
                if not buf1:
                    return True

    def _equal(self, pathfmt):
        if self._equal_exc:
            self._equal_cnt += 1
            if self._equal_cnt >= self._equal_max:
                util.remove_file(pathfmt.temppath)
                output.stderr_write("\n")
                raise self._equal_exc()
        pathfmt.delete = True


__postprocessor__ = ComparePP

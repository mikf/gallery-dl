# -*- coding: utf-8 -*-

# Copyright 2020-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Compare versions of the same file and replace/enumerate them on mismatch"""

from .common import PostProcessor
from .. import text, util, exception
import sys
import os


class ComparePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        if options.get("shallow"):
            self._compare = self._compare_size

        action = options.get("action")
        if action == "enumerate":
            job.register_hooks({"file": self.enumerate}, options)
        else:
            job.register_hooks({"file": self.compare}, options)
            action, _, smax = action.partition(":")
            self._skipmax = text.parse_int(smax)
            self._skipexc = self._skipcnt = 0
            if action == "abort":
                self._skipexc = exception.StopExtraction
            elif action == "terminate":
                self._skipexc = exception.TerminateExtraction
            elif action == "exit":
                self._skipexc = sys.exit

    def compare(self, pathfmt):
        try:
            if self._compare(pathfmt.realpath, pathfmt.temppath):
                if self._skipexc:
                    self._skipcnt += 1
                    if self._skipcnt >= self._skipmax:
                        util.remove_file(pathfmt.temppath)
                        print()
                        raise self._skipexc()
                pathfmt.delete = True
            else:
                self._skipcnt = 0
        except OSError:
            pass

    def enumerate(self, pathfmt):
        num = 1
        try:
            while not self._compare(pathfmt.realpath, pathfmt.temppath):
                pathfmt.prefix = str(num) + "."
                pathfmt.set_extension(pathfmt.extension, False)
                num += 1
            pathfmt.delete = True
        except OSError:
            pass

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


__postprocessor__ = ComparePP

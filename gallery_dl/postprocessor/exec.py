# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Execute processes"""

from .common import PostProcessor
from .. import util
import subprocess
import shlex


class ExecPP(PostProcessor):

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)

        args = options["command"]

        if isinstance(args, str):
            self.args = util.Formatter(args.replace("{}", "{_temppath}"))
            self.shell = True
            self._format = self._format_args_string
        else:
            for i, arg in enumerate(args):
                if "{}" in arg:
                    args[i] = arg.replace("{}", "{_temppath}")
            self.args = [util.Formatter(arg) for arg in args]
            self.shell = False
            self._format = self._format_args_list

        if options.get("async", False):
            self._exec = self._exec_async

    def run(self, pathfmt):
        kwdict = pathfmt.kwdict
        kwdict["_directory"] = pathfmt.realdirectory
        kwdict["_filename"] = pathfmt.filename
        kwdict["_temppath"] = pathfmt.temppath
        kwdict["_path"] = pathfmt.realpath
        self._exec(self._format(kwdict))

    def _format_args_list(self, kwdict):
        return [arg.format_map(kwdict) for arg in self.args]

    def _format_args_string(self, kwdict):
        return self.args.format_map(_quote(kwdict))

    def _exec(self, args):
        retcode = subprocess.Popen(args, shell=self.shell).wait()
        if retcode:
            self.log.warning(
                "executing '%s' returned with non-zero exit status (%d)",
                " ".join(args) if isinstance(args, list) else args, retcode)

    def _exec_async(self, args):
        subprocess.Popen(args, shell=self.shell)


def _quote(kwdict):
    """Create a copy of 'kwdict' and apply shlex.quote to its string values"""
    kwdict = kwdict.copy()
    for key, value in kwdict.items():
        cls = value.__class__
        if cls is str:
            kwdict[key] = shlex.quote(value)
        elif cls is list:
            kwdict[key] = shlex.quote(", ".join(value))
        elif cls is dict:
            kwdict[key] = _quote(value)
    return kwdict


__postprocessor__ = ExecPP

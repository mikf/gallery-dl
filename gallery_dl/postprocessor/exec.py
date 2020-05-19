# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Execute processes"""

from .common import PostProcessor
from .. import util
import subprocess


if util.WINDOWS:
    def quote(s):
        return '"' + s.replace('"', '\\"') + '"'
else:
    from shlex import quote


class ExecPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        args = options["command"]
        final = options.get("final", False)

        if isinstance(args, str):
            if final:
                self._format = self._format_args_directory
            else:
                self._format = self._format_args_path
            if "{}" not in args:
                args += " {}"
            self.args = args
            self.shell = True
        else:
            self._format = self._format_args_list
            self.args = [util.Formatter(arg) for arg in args]
            self.shell = False

        if final:
            self.run_after = PostProcessor.run_after
        else:
            self.run_final = PostProcessor.run_final

        if options.get("async", False):
            self._exec = self._exec_async

    def run_after(self, pathfmt):
        self._exec(self._format(pathfmt))

    def run_final(self, pathfmt, status):
        if status == 0:
            self._exec(self._format(pathfmt))

    def _format_args_path(self, pathfmt):
        return self.args.replace("{}", quote(pathfmt.realpath))

    def _format_args_directory(self, pathfmt):
        return self.args.replace("{}", quote(pathfmt.realdirectory))

    def _format_args_list(self, pathfmt):
        kwdict = pathfmt.kwdict
        kwdict["_directory"] = pathfmt.realdirectory
        kwdict["_filename"] = pathfmt.filename
        kwdict["_path"] = pathfmt.realpath
        return [arg.format_map(kwdict) for arg in self.args]

    def _exec(self, args):
        self.log.debug("Running '%s'", args)
        retcode = subprocess.Popen(args, shell=self.shell).wait()
        if retcode:
            self.log.warning(
                "Executing '%s' returned with non-zero exit status (%d)",
                " ".join(args) if isinstance(args, list) else args, retcode)

    def _exec_async(self, args):
        subprocess.Popen(args, shell=self.shell)


__postprocessor__ = ExecPP

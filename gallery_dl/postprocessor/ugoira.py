# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Convert pixiv ugoira to webm"""

from .common import PostProcessor
from .. import util
import subprocess
import tempfile
import zipfile


class UgoiraPP(PostProcessor):

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)
        self.extension = options.get("extension") or "webm"
        self.ffmpeg = options.get("ffmpeg-location") or "ffmpeg"
        self.args = options.get("ffmpeg-args")
        self.delete = not options.get("keep-files", False)

    def run(self, pathfmt):
        if (pathfmt.keywords["extension"] != "zip" or
                "frames" not in pathfmt.keywords):
            return

        framelist = [
            (frame["file"], frame["delay"] / 1000)
            for frame in pathfmt.keywords["frames"]
        ]
        if self.extension != "gif":
            # repeat the last frame to prevent it from only being
            # displayed for a very short amount of time
            framelist.append(framelist[-1])

        with tempfile.TemporaryDirectory() as tempdir:
            # extract frames
            with zipfile.ZipFile(pathfmt.temppath) as zfile:
                zfile.extractall(tempdir)

            # write ffconcat file
            ffconcat = tempdir + "/ffconcat.txt"
            with open(ffconcat, "w") as file:
                file.write("ffconcat version 1.0\n")
                for name, duration in framelist:
                    file.write("file '{}'\n".format(name))
                    file.write("duration {}\n".format(duration))

            # invoke ffmpeg
            pathfmt.set_extension(self.extension)
            args = [util.expand_path(self.ffmpeg), "-i", ffconcat]
            if self.args:
                args += self.args
            args.append(pathfmt.realpath)
            subprocess.Popen(args).wait()

        if self.delete:
            pathfmt.delete = True
        else:
            pathfmt.set_extension("zip")


__postprocessor__ = UgoiraPP

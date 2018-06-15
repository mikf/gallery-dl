# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Convert pixiv ugoira to webm"""

from .common import PostProcessor
import subprocess
import tempfile
import zipfile


class UgoiraPP(PostProcessor):

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)

    def run(self, pathfmt):
        if pathfmt.keywords["extension"] != "txt":
            return

        framelist = []

        # get frames and their durations
        with pathfmt.open("r") as file:
            for line in file:
                name, _, duration = line.partition(" ")
                framelist.append((name, int(duration.rstrip())))
            # list the last frame twice to prevent it from only being
            # displayed for a very short time
            framelist.append((name, int(duration.rstrip())))

        with tempfile.TemporaryDirectory() as tempdir:
            # extract frames
            pathfmt.set_extension("zip")
            with zipfile.ZipFile(pathfmt.realpath) as zfile:
                zfile.extractall(tempdir)

            # write ffconcat file
            ffconcat = tempdir + "/ffconcat.txt"
            with open(ffconcat, "w") as file:
                file.write("ffconcat version 1.0\n")
                for name, duration in framelist:
                    file.write("file '{}'\n".format(name))
                    file.write("duration {}\n".format(duration / 1000))

            # invoke ffmpeg
            pathfmt.set_extension("webm")
            args = ["ffmpeg", "-i", ffconcat, pathfmt.realpath]
            subprocess.Popen(args).wait()

        # mark framelist file for deletion
        pathfmt.delete = True


__postprocessor__ = UgoiraPP

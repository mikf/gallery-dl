# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Convert Pixiv Ugoira to WebM"""

from .common import PostProcessor
from .. import util
import collections
import subprocess
import tempfile
import zipfile
import os


class UgoiraPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        self.extension = options.get("extension") or "webm"
        self.args = options.get("ffmpeg-args") or ()
        self.twopass = options.get("ffmpeg-twopass", False)
        self.output = options.get("ffmpeg-output", True)
        self.delete = not options.get("keep-files", False)

        ffmpeg = options.get("ffmpeg-location")
        self.ffmpeg = util.expand_path(ffmpeg) if ffmpeg else "ffmpeg"

        rate = options.get("framerate", "auto")
        if rate != "auto":
            self.calculate_framerate = lambda _: (None, rate)

        if options.get("libx264-prevent-odd", True):
            # get last video-codec argument
            vcodec = None
            for index, arg in enumerate(self.args):
                arg, _, stream = arg.partition(":")
                if arg == "-vcodec" or arg in ("-c", "-codec") and (
                        not stream or stream.partition(":")[0] in ("v", "V")):
                    vcodec = self.args[index + 1]
            # use filter when using libx264/5
            self.prevent_odd = (
                vcodec in ("libx264", "libx265") or
                not vcodec and self.extension.lower() in ("mp4", "mkv"))
        else:
            self.prevent_odd = False

    def prepare(self, pathfmt):
        self._frames = None

        if pathfmt.extension != "zip":
            return

        if "frames" in pathfmt.kwdict:
            self._frames = pathfmt.kwdict["frames"]
        elif "pixiv_ugoira_frame_data" in pathfmt.kwdict:
            self._frames = pathfmt.kwdict["pixiv_ugoira_frame_data"]["data"]
        else:
            return

        if self.delete:
            pathfmt.set_extension(self.extension)

    def run(self, pathfmt):
        if not self._frames:
            return

        rate_in, rate_out = self.calculate_framerate(self._frames)

        with tempfile.TemporaryDirectory() as tempdir:
            # extract frames
            with zipfile.ZipFile(pathfmt.temppath) as zfile:
                zfile.extractall(tempdir)

            # write ffconcat file
            ffconcat = tempdir + "/ffconcat.txt"
            with open(ffconcat, "w") as file:
                file.write("ffconcat version 1.0\n")
                for frame in self._frames:
                    file.write("file '{}'\n".format(frame["file"]))
                    file.write("duration {}\n".format(frame["delay"] / 1000))
                if self.extension != "gif":
                    # repeat the last frame to prevent it from only being
                    # displayed for a very short amount of time
                    file.write("file '{}'\n".format(self._frames[-1]["file"]))

            # collect command-line arguments
            args = [self.ffmpeg]
            if rate_in:
                args += ("-r", str(rate_in))
            args += ("-i", ffconcat)
            if rate_out:
                args += ("-r", str(rate_out))
            if self.prevent_odd:
                args += ("-vf", "crop=iw-mod(iw\\,2):ih-mod(ih\\,2)")
            if self.args:
                args += self.args
            self.log.debug("ffmpeg args: %s", args)

            # invoke ffmpeg
            pathfmt.set_extension(self.extension)
            try:
                if self.twopass:
                    if "-f" not in args:
                        args += ("-f", self.extension)
                    args += ("-passlogfile", tempdir + "/ffmpeg2pass", "-pass")
                    self._exec(args + ["1", "-y", os.devnull])
                    self._exec(args + ["2", pathfmt.realpath])
                else:
                    args.append(pathfmt.realpath)
                    self._exec(args)
            except OSError as exc:
                print()
                self.log.error("Unable to invoke FFmpeg (%s: %s)",
                               exc.__class__.__name__, exc)
                pathfmt.realpath = pathfmt.temppath
            else:
                if self.delete:
                    pathfmt.delete = True
                else:
                    pathfmt.set_extension("zip")

    def _exec(self, args):
        out = None if self.output else subprocess.DEVNULL
        return subprocess.Popen(args, stdout=out, stderr=out).wait()

    @staticmethod
    def calculate_framerate(framelist):
        counter = collections.Counter(frame["delay"] for frame in framelist)
        fps = "1000/{}".format(min(counter))
        return (fps, None) if len(counter) == 1 else (None, fps)


__postprocessor__ = UgoiraPP

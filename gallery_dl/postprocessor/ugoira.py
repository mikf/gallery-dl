# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
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
        self.repeat = options.get("repeat-last-frame", True)

        ffmpeg = options.get("ffmpeg-location")
        self.ffmpeg = util.expand_path(ffmpeg) if ffmpeg else "ffmpeg"

        rate = options.get("framerate", "auto")
        if rate != "auto":
            self.calculate_framerate = lambda _: (None, rate)

        if options.get("ffmpeg-demuxer") == "image2":
            self._process = self._image2
        else:
            self._process = self._concat

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

        job.register_hooks(
            {"prepare": self.prepare, "file": self.convert}, options)

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

    def convert(self, pathfmt):
        if not self._frames:
            return

        with tempfile.TemporaryDirectory() as tempdir:
            # extract frames
            try:
                with zipfile.ZipFile(pathfmt.temppath) as zfile:
                    zfile.extractall(tempdir)
            except FileNotFoundError:
                pathfmt.realpath = pathfmt.temppath
                return

            # process frames and collect command-line arguments
            args = self._process(tempdir)
            if self.args:
                args += self.args
            self.log.debug("ffmpeg args: %s", args)

            # invoke ffmpeg
            pathfmt.set_extension(self.extension)
            try:
                if self.twopass:
                    if "-f" not in self.args:
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

    def _concat(self, path):
        ffconcat = path + "/ffconcat.txt"

        content = ["ffconcat version 1.0"]
        append = content.append
        for frame in self._frames:
            append("file '{}'\nduration {}".format(
                frame["file"], frame["delay"] / 1000))
        if self.repeat:
            append("file '{}'".format(frame["file"]))
        append("")

        with open(ffconcat, "w") as file:
            file.write("\n".join(content))

        rate_in, rate_out = self.calculate_framerate(self._frames)
        args = [self.ffmpeg, "-f", "concat"]
        if rate_in:
            args += ("-r", str(rate_in))
        args += ("-i", ffconcat)
        if rate_out:
            args += ("-r", str(rate_out))
        return args

    def _image2(self, path):
        path += "/"

        # adjust frame mtime values
        ts = 0
        for frame in self._frames:
            os.utime(path + frame["file"], ns=(ts, ts))
            ts += frame["delay"] * 1000000

        return [
            self.ffmpeg,
            "-f", "image2",
            "-ts_from_file", "2",
            "-pattern_type", "sequence",
            "-i", "{}%06d.{}".format(
                path.replace("%", "%%"), frame["file"].rpartition(".")[2]),
        ]

    def _exec(self, args):
        out = None if self.output else subprocess.DEVNULL
        return subprocess.Popen(args, stdout=out, stderr=out).wait()

    @staticmethod
    def calculate_framerate(framelist):
        counter = collections.Counter(frame["delay"] for frame in framelist)
        fps = "1000/{}".format(min(counter))
        return (fps, None) if len(counter) == 1 else (None, fps)


__postprocessor__ = UgoiraPP

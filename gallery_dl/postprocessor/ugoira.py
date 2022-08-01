# -*- coding: utf-8 -*-

# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Convert Pixiv Ugoira to WebM"""

from .common import PostProcessor
from .. import util
import subprocess
import tempfile
import zipfile
import shutil
import os

try:
    from math import gcd
except ImportError:
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a


class UgoiraPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        self.extension = options.get("extension") or "webm"
        self.args = options.get("ffmpeg-args") or ()
        self.twopass = options.get("ffmpeg-twopass", False)
        self.output = options.get("ffmpeg-output", True)
        self.delete = not options.get("keep-files", False)
        self.repeat = options.get("repeat-last-frame", True)
        self.mtime = options.get("mtime", True)

        ffmpeg = options.get("ffmpeg-location")
        self.ffmpeg = util.expand_path(ffmpeg) if ffmpeg else "ffmpeg"

        mkvmerge = options.get("mkvmerge-location")
        self.mkvmerge = util.expand_path(mkvmerge) if mkvmerge else "mkvmerge"

        demuxer = options.get("ffmpeg-demuxer")
        if demuxer is None or demuxer == "auto":
            if self.extension in ("webm", "mkv") and (
                    mkvmerge or shutil.which("mkvmerge")):
                demuxer = "mkvmerge"
            else:
                demuxer = "concat"

        if demuxer == "mkvmerge":
            self._process = self._process_mkvmerge
            self._finalize = self._finalize_mkvmerge
        elif demuxer == "image2":
            self._process = self._process_image2
            self._finalize = None
        else:
            self._process = self._process_concat
            self._finalize = None
        self.log.debug("using %s demuxer", demuxer)

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
            pathfmt.set_extension(self.extension)
            args = self._process(pathfmt, tempdir)
            if self.args:
                args += self.args

            # ensure target directory exists
            os.makedirs(pathfmt.realdirectory, exist_ok=True)

            # invoke ffmpeg
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
                if self._finalize:
                    self._finalize(pathfmt, tempdir)
            except OSError as exc:
                print()
                self.log.error("Unable to invoke FFmpeg (%s: %s)",
                               exc.__class__.__name__, exc)
                pathfmt.realpath = pathfmt.temppath
            except Exception:
                pathfmt.realpath = pathfmt.temppath
            else:
                if self.mtime:
                    mtime = pathfmt.kwdict.get("_mtime")
                    if mtime:
                        util.set_mtime(pathfmt.realpath, mtime)
                if self.delete:
                    pathfmt.delete = True
                else:
                    pathfmt.set_extension("zip")

    def _exec(self, args):
        self.log.debug(args)
        out = None if self.output else subprocess.DEVNULL
        retcode = subprocess.Popen(args, stdout=out, stderr=out).wait()
        if retcode:
            print()
            self.log.error("Non-zero exit status when running %s (%s)",
                           args, retcode)
            raise ValueError()
        return retcode

    def _process_concat(self, pathfmt, tempdir):
        rate_in, rate_out = self.calculate_framerate(self._frames)
        args = [self.ffmpeg, "-f", "concat"]
        if rate_in:
            args += ("-r", str(rate_in))
        args += ("-i", self._write_ffmpeg_concat(tempdir))
        if rate_out:
            args += ("-r", str(rate_out))
        return args

    def _process_image2(self, pathfmt, tempdir):
        tempdir += "/"
        frames = self._frames

        # add extra frame if necessary
        if self.repeat and not self._delay_is_uniform(frames):
            last = frames[-1]
            delay_gcd = self._delay_gcd(frames)
            if last["delay"] - delay_gcd > 0:
                last["delay"] -= delay_gcd

                self.log.debug("non-uniform delays; inserting extra frame")
                last_copy = last.copy()
                frames.append(last_copy)
                name, _, ext = last_copy["file"].rpartition(".")
                last_copy["file"] = "{:>06}.{}".format(int(name)+1, ext)
                shutil.copyfile(tempdir + last["file"],
                                tempdir + last_copy["file"])

        # adjust frame mtime values
        ts = 0
        for frame in frames:
            os.utime(tempdir + frame["file"], ns=(ts, ts))
            ts += frame["delay"] * 1000000

        return [
            self.ffmpeg,
            "-f", "image2",
            "-ts_from_file", "2",
            "-pattern_type", "sequence",
            "-i", "{}%06d.{}".format(
                tempdir.replace("%", "%%"),
                frame["file"].rpartition(".")[2]
            ),
        ]

    def _process_mkvmerge(self, pathfmt, tempdir):
        self._realpath = pathfmt.realpath
        pathfmt.realpath = tempdir + "/temp." + self.extension

        return [
            self.ffmpeg,
            "-f", "image2",
            "-pattern_type", "sequence",
            "-i", "{}/%06d.{}".format(
                tempdir.replace("%", "%%"),
                self._frames[0]["file"].rpartition(".")[2]
            ),
        ]

    def _finalize_mkvmerge(self, pathfmt, tempdir):
        args = [
            self.mkvmerge,
            "-o", pathfmt.path,  # mkvmerge does not support "raw" paths
            "--timecodes", "0:" + self._write_mkvmerge_timecodes(tempdir),
        ]
        if self.extension == "webm":
            args.append("--webm")
        args += ("=", pathfmt.realpath)

        pathfmt.realpath = self._realpath
        self._exec(args)

    def _write_ffmpeg_concat(self, tempdir):
        content = ["ffconcat version 1.0"]
        append = content.append

        for frame in self._frames:
            append("file '{}'\nduration {}".format(
                frame["file"], frame["delay"] / 1000))
        if self.repeat:
            append("file '{}'".format(frame["file"]))
        append("")

        ffconcat = tempdir + "/ffconcat.txt"
        with open(ffconcat, "w") as file:
            file.write("\n".join(content))
        return ffconcat

    def _write_mkvmerge_timecodes(self, tempdir):
        content = ["# timecode format v2"]
        append = content.append

        delay_sum = 0
        for frame in self._frames:
            append(str(delay_sum))
            delay_sum += frame["delay"]
        append(str(delay_sum))
        append("")

        timecodes = tempdir + "/timecodes.tc"
        with open(timecodes, "w") as file:
            file.write("\n".join(content))
        return timecodes

    def calculate_framerate(self, frames):
        uniform = self._delay_is_uniform(frames)
        if uniform:
            return ("1000/{}".format(frames[0]["delay"]), None)
        return (None, "1000/{}".format(self._delay_gcd(frames)))

    @staticmethod
    def _delay_gcd(frames):
        result = frames[0]["delay"]
        for f in frames:
            result = gcd(result, f["delay"])
        return result

    @staticmethod
    def _delay_is_uniform(frames):
        delay = frames[0]["delay"]
        for f in frames:
            if f["delay"] != delay:
                return False
        return True


__postprocessor__ = UgoiraPP

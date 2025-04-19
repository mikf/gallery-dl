# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Convert Pixiv Ugoira to WebM"""

from .common import PostProcessor
from .. import util, output
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
        self.args = options.get("ffmpeg-args") or ()
        self.twopass = options.get("ffmpeg-twopass", False)
        self.output = options.get("ffmpeg-output", "error")
        self.delete = not options.get("keep-files", False)
        self.repeat = options.get("repeat-last-frame", True)
        self.metadata = options.get("metadata", True)
        self.mtime = options.get("mtime", True)
        self.skip = options.get("skip", True)
        self.uniform = self._convert_zip = self._convert_files = False

        ffmpeg = options.get("ffmpeg-location")
        self.ffmpeg = util.expand_path(ffmpeg) if ffmpeg else "ffmpeg"

        mkvmerge = options.get("mkvmerge-location")
        self.mkvmerge = util.expand_path(mkvmerge) if mkvmerge else "mkvmerge"

        ext = options.get("extension")
        mode = options.get("mode") or options.get("ffmpeg-demuxer")
        if mode is None or mode == "auto":
            if ext in (None, "webm", "mkv") and (
                    mkvmerge or shutil.which("mkvmerge")):
                mode = "mkvmerge"
            else:
                mode = "concat"

        if mode == "mkvmerge":
            self._process = self._process_mkvmerge
            self._finalize = self._finalize_mkvmerge
        elif mode == "image2":
            self._process = self._process_image2
            self._finalize = None
        elif mode == "archive":
            if ext is None:
                ext = "zip"
            self._convert_impl = self.convert_to_archive
            self._tempdir = util.NullContext
        else:
            self._process = self._process_concat
            self._finalize = None
        self.extension = "webm" if ext is None else ext
        self.log.debug("using %s demuxer", mode)

        rate = options.get("framerate", "auto")
        if rate == "uniform":
            self.uniform = True
        elif rate != "auto":
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

        self.args_pp = args = []
        if isinstance(self.output, str):
            args += ("-hide_banner", "-loglevel", self.output)
        if self.prevent_odd:
            args += ("-vf", "crop=iw-mod(iw\\,2):ih-mod(ih\\,2)")

        job.register_hooks({
            "prepare": self.prepare,
            "file"   : self.convert_from_zip,
            "after"  : self.convert_from_files,
        }, options)

    def prepare(self, pathfmt):
        self._convert_zip = self._convert_files = False
        if "_ugoira_frame_data" not in pathfmt.kwdict:
            self._frames = None
            return

        self._frames = pathfmt.kwdict["_ugoira_frame_data"]
        if pathfmt.extension == "zip":
            self._convert_zip = True
            if self.delete:
                pathfmt.set_extension(self.extension)
                pathfmt.build_path()
        else:
            index = pathfmt.kwdict.get("_ugoira_frame_index")
            if index is None:
                return

            pathfmt.build_path()
            frame = self._frames[index].copy()
            frame["index"] = index
            frame["path"] = pathfmt.realpath
            frame["ext"] = pathfmt.extension

            if not index:
                self._files = [frame]
            else:
                self._files.append(frame)
                if len(self._files) >= len(self._frames):
                    self._convert_files = True

    def convert_from_zip(self, pathfmt):
        if not self._convert_zip:
            return
        self._zip_source = True

        with self._tempdir() as tempdir:
            if tempdir:
                try:
                    with zipfile.ZipFile(pathfmt.temppath) as zfile:
                        zfile.extractall(tempdir)
                except FileNotFoundError:
                    pathfmt.realpath = pathfmt.temppath
                    return
                except Exception as exc:
                    pathfmt.realpath = pathfmt.temppath
                    self.log.error(
                        "%s: Unable to extract frames from %s (%s: %s)",
                        pathfmt.kwdict.get("id"), pathfmt.filename,
                        exc.__class__.__name__, exc)
                    return self.log.debug("", exc_info=exc)

            if self.convert(pathfmt, tempdir):
                pathfmt.delete = self.delete

    def convert_from_files(self, pathfmt):
        if not self._convert_files:
            return
        self._zip_source = False

        with tempfile.TemporaryDirectory() as tempdir:
            for frame in self._files:

                # update frame filename extension
                frame["file"] = name = "{}.{}".format(
                    frame["file"].partition(".")[0], frame["ext"])

                if tempdir:
                    # move frame into tempdir
                    try:
                        self._copy_file(frame["path"], tempdir + "/" + name)
                    except OSError as exc:
                        self.log.debug("Unable to copy frame %s (%s: %s)",
                                       name, exc.__class__.__name__, exc)
                        return

            pathfmt.kwdict["num"] = 0
            self._frames = self._files
            if self.convert(pathfmt, tempdir):
                self.log.info(pathfmt.filename)
                if self.delete:
                    self.log.debug("Deleting frames")
                    for frame in self._files:
                        util.remove_file(frame["path"])

    def convert(self, pathfmt, tempdir):
        pathfmt.set_extension(self.extension)
        pathfmt.build_path()
        if self.skip and pathfmt.exists():
            return True

        return self._convert_impl(pathfmt, tempdir)

    def convert_to_animation(self, pathfmt, tempdir):
        # process frames and collect command-line arguments
        args = self._process(pathfmt, tempdir)
        if self.args_pp:
            args += self.args_pp
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
            output.stderr_write("\n")
            self.log.error("Unable to invoke FFmpeg (%s: %s)",
                           exc.__class__.__name__, exc)
            self.log.debug("", exc_info=exc)
            pathfmt.realpath = pathfmt.temppath
        except Exception as exc:
            output.stderr_write("\n")
            self.log.error("%s: %s", exc.__class__.__name__, exc)
            self.log.debug("", exc_info=exc)
            pathfmt.realpath = pathfmt.temppath
        else:
            if self.mtime:
                mtime = pathfmt.kwdict.get("_mtime")
                if mtime:
                    util.set_mtime(pathfmt.realpath, mtime)
            return True

    def convert_to_archive(self, pathfmt, tempdir):
        frames = self._frames

        if self.metadata:
            if isinstance(self.metadata, str):
                metaname = self.metadata
            else:
                metaname = "animation.json"
            framedata = util.json_dumps([
                {"file": frame["file"], "delay": frame["delay"]}
                for frame in frames
            ]).encode()

        if self._zip_source:
            self.delete = False
            if self.metadata:
                with zipfile.ZipFile(pathfmt.temppath, "a") as zfile:
                    zinfo = zipfile.ZipInfo(metaname)
                    if self.mtime:
                        zinfo.date_time = zfile.infolist()[0].date_time
                    with zfile.open(zinfo, "w") as fp:
                        fp.write(framedata)
        else:
            if self.mtime:
                dt = pathfmt.kwdict["date_url"] or pathfmt.kwdict["date"]
                mtime = (dt.year, dt.month, dt.day,
                         dt.hour, dt.minute, dt.second)
            with zipfile.ZipFile(pathfmt.realpath, "w") as zfile:
                for frame in frames:
                    zinfo = zipfile.ZipInfo.from_file(
                        frame["path"], frame["file"])
                    if self.mtime:
                        zinfo.date_time = mtime
                    with open(frame["path"], "rb") as src, \
                            zfile.open(zinfo, "w") as dst:
                        shutil.copyfileobj(src, dst, 1024*8)
                if self.metadata:
                    zinfo = zipfile.ZipInfo(metaname)
                    if self.mtime:
                        zinfo.date_time = mtime
                    with zfile.open(zinfo, "w") as fp:
                        fp.write(framedata)

        return True

    _convert_impl = convert_to_animation
    _tempdir = tempfile.TemporaryDirectory

    def _exec(self, args):
        self.log.debug(args)
        out = None if self.output else subprocess.DEVNULL
        retcode = util.Popen(args, stdout=out, stderr=out).wait()
        if retcode:
            output.stderr_write("\n")
            self.log.error("Non-zero exit status when running %s (%s)",
                           args, retcode)
            raise ValueError()
        return retcode

    def _copy_file(self, src, dst):
        shutil.copyfile(src, dst)

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
        with open(ffconcat, "w") as fp:
            fp.write("\n".join(content))
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
        with open(timecodes, "w") as fp:
            fp.write("\n".join(content))
        return timecodes

    def calculate_framerate(self, frames):
        if self._delay_is_uniform(frames):
            return ("1000/{}".format(frames[0]["delay"]), None)

        if not self.uniform:
            gcd = self._delay_gcd(frames)
            if gcd >= 10:
                return (None, "1000/{}".format(gcd))

        return (None, None)

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

# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for URLs requiring youtube-dl support"""

from .common import DownloaderBase
from .. import text
import os


class YoutubeDLDownloader(DownloaderBase):
    scheme = "ytdl"

    def __init__(self, job):
        module = __import__(self.config("module") or "youtube_dl")

        DownloaderBase.__init__(self, job)
        extractor = job.extractor

        retries = self.config("retries", extractor._retries)
        options = {
            "format": self.config("format") or None,
            "ratelimit": text.parse_bytes(self.config("rate"), None),
            "retries": retries+1 if retries >= 0 else float("inf"),
            "socket_timeout": self.config("timeout", extractor._timeout),
            "nocheckcertificate": not self.config("verify", extractor._verify),
            "nopart": not self.part,
            "updatetime": self.config("mtime", True),
            "proxy": extractor.session.proxies.get("http"),
            "min_filesize": text.parse_bytes(
                self.config("filesize-min"), None),
            "max_filesize": text.parse_bytes(
                self.config("filesize-max"), None),
        }

        raw_options = self.config("raw-options")
        if raw_options:
            options.update(raw_options)

        self.progress = self.config("progress", 3.0)
        if self.progress is not None:
            options["progress_hooks"] = (self._progress_hook,)

        if self.config("logging", True):
            options["logger"] = self.log
        self.forward_cookies = self.config("forward-cookies", False)

        self.outtmpl = self.config("outtmpl")
        if self.outtmpl == "default":
            self.outtmpl = module.DEFAULT_OUTTMPL

        self.ytdl = module.YoutubeDL(options)

    def download(self, url, pathfmt):
        kwdict = pathfmt.kwdict

        ytdl = kwdict.pop("_ytdl_instance", None)
        if ytdl:
            if self.progress is not None and not ytdl._progress_hooks:
                ytdl.add_progress_hook(self._progress_hook)
        else:
            ytdl = self.ytdl
            if self.forward_cookies:
                set_cookie = ytdl.cookiejar.set_cookie
                for cookie in self.session.cookies:
                    set_cookie(cookie)

        info_dict = kwdict.pop("_ytdl_info_dict", None)
        if not info_dict:
            try:
                info_dict = ytdl.extract_info(url[5:], download=False)
            except Exception:
                return False

        if "entries" in info_dict:
            index = kwdict.get("_ytdl_index")
            if index is None:
                return self._download_playlist(ytdl, pathfmt, info_dict)
            else:
                info_dict = info_dict["entries"][index]

        extra = kwdict.get("_ytdl_extra")
        if extra:
            info_dict.update(extra)

        return self._download_video(ytdl, pathfmt, info_dict)

    def _download_video(self, ytdl, pathfmt, info_dict):
        if "url" in info_dict:
            text.nameext_from_url(info_dict["url"], pathfmt.kwdict)

        formats = info_dict.get("requested_formats")
        if formats and not compatible_formats(formats):
            info_dict["ext"] = "mkv"

        if self.outtmpl:
            self._set_outtmpl(ytdl, self.outtmpl)
            pathfmt.filename = filename = ytdl.prepare_filename(info_dict)
            pathfmt.extension = info_dict["ext"]
            pathfmt.path = pathfmt.directory + filename
            pathfmt.realpath = pathfmt.temppath = (
                pathfmt.realdirectory + filename)
        else:
            pathfmt.set_extension(info_dict["ext"])

        if pathfmt.exists():
            pathfmt.temppath = ""
            return True
        if self.part and self.partdir:
            pathfmt.temppath = os.path.join(
                self.partdir, pathfmt.filename)

        self._set_outtmpl(ytdl, pathfmt.temppath.replace("%", "%%"))

        self.out.start(pathfmt.path)
        try:
            ytdl.process_info(info_dict)
        except Exception:
            self.log.debug("Traceback", exc_info=True)
            return False
        return True

    def _download_playlist(self, ytdl, pathfmt, info_dict):
        pathfmt.set_extension("%(playlist_index)s.%(ext)s")
        self._set_outtmpl(ytdl, pathfmt.realpath)

        for entry in info_dict["entries"]:
            ytdl.process_info(entry)
        return True

    def _progress_hook(self, info):
        if info["status"] == "downloading" and \
                info["elapsed"] >= self.progress:
            self.out.progress(
                info["total_bytes"],
                info["downloaded_bytes"],
                int(info["speed"]),
            )

    @staticmethod
    def _set_outtmpl(ytdl, outtmpl):
        try:
            ytdl.outtmpl_dict["default"] = outtmpl
        except AttributeError:
            ytdl.params["outtmpl"] = outtmpl


def compatible_formats(formats):
    """Returns True if 'formats' are compatible for merge"""
    video_ext = formats[0].get("ext")
    audio_ext = formats[1].get("ext")

    if video_ext == "webm" and audio_ext == "webm":
        return True

    exts = ("mp3", "mp4", "m4a", "m4p", "m4b", "m4r", "m4v", "ismv", "isma")
    return video_ext in exts and audio_ext in exts


__downloader__ = YoutubeDLDownloader

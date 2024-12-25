# -*- coding: utf-8 -*-

# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for URLs requiring youtube-dl support"""

from .common import DownloaderBase
from .. import ytdl, text
import os


class YoutubeDLDownloader(DownloaderBase):
    scheme = "ytdl"

    def __init__(self, job):
        DownloaderBase.__init__(self, job)

        extractor = job.extractor
        retries = self.config("retries", extractor._retries)
        self.ytdl_opts = {
            "retries": retries+1 if retries >= 0 else float("inf"),
            "socket_timeout": self.config("timeout", extractor._timeout),
            "nocheckcertificate": not self.config("verify", extractor._verify),
            "proxy": self.proxies.get("http") if self.proxies else None,
        }

        self.ytdl_instance = None
        self.forward_cookies = self.config("forward-cookies", True)
        self.progress = self.config("progress", 3.0)
        self.outtmpl = self.config("outtmpl")

    def download(self, url, pathfmt):
        kwdict = pathfmt.kwdict

        ytdl_instance = kwdict.pop("_ytdl_instance", None)
        if not ytdl_instance:
            ytdl_instance = self.ytdl_instance
            if not ytdl_instance:
                try:
                    module = ytdl.import_module(self.config("module"))
                except (ImportError, SyntaxError) as exc:
                    self.log.error("Cannot import module '%s'",
                                   getattr(exc, "name", ""))
                    self.log.debug("", exc_info=exc)
                    self.download = lambda u, p: False
                    return False
                self.ytdl_instance = ytdl_instance = ytdl.construct_YoutubeDL(
                    module, self, self.ytdl_opts)
                if self.outtmpl == "default":
                    self.outtmpl = module.DEFAULT_OUTTMPL
            if self.forward_cookies:
                self.log.debug("Forwarding cookies to %s",
                               ytdl_instance.__module__)
                set_cookie = ytdl_instance.cookiejar.set_cookie
                for cookie in self.session.cookies:
                    set_cookie(cookie)

        if self.progress is not None and not ytdl_instance._progress_hooks:
            ytdl_instance.add_progress_hook(self._progress_hook)

        info_dict = kwdict.pop("_ytdl_info_dict", None)
        if not info_dict:
            url = url[5:]
            try:
                manifest = kwdict.pop("_ytdl_manifest", None)
                if manifest:
                    info_dict = self._extract_manifest(
                        ytdl_instance, url, manifest)
                else:
                    info_dict = self._extract_info(ytdl_instance, url)
            except Exception as exc:
                self.log.debug("", exc_info=exc)
                self.log.warning("%s: %s", exc.__class__.__name__, exc)

            if not info_dict:
                return False

        if "entries" in info_dict:
            index = kwdict.get("_ytdl_index")
            if index is None:
                return self._download_playlist(
                    ytdl_instance, pathfmt, info_dict)
            else:
                info_dict = info_dict["entries"][index]

        extra = kwdict.get("_ytdl_extra")
        if extra:
            info_dict.update(extra)

        return self._download_video(ytdl_instance, pathfmt, info_dict)

    def _download_video(self, ytdl_instance, pathfmt, info_dict):
        if "url" in info_dict:
            text.nameext_from_url(info_dict["url"], pathfmt.kwdict)

        formats = info_dict.get("requested_formats")
        if formats and not compatible_formats(formats):
            info_dict["ext"] = "mkv"
        elif "ext" not in info_dict:
            try:
                info_dict["ext"] = info_dict["formats"][0]["ext"]
            except LookupError:
                info_dict["ext"] = "mp4"

        if self.outtmpl:
            self._set_outtmpl(ytdl_instance, self.outtmpl)
            pathfmt.filename = filename = \
                ytdl_instance.prepare_filename(info_dict)
            pathfmt.extension = info_dict["ext"]
            pathfmt.path = pathfmt.directory + filename
            pathfmt.realpath = pathfmt.temppath = (
                pathfmt.realdirectory + filename)
        else:
            pathfmt.set_extension(info_dict["ext"])
            pathfmt.build_path()

        if pathfmt.exists():
            pathfmt.temppath = ""
            return True
        if self.part and self.partdir:
            pathfmt.temppath = os.path.join(
                self.partdir, pathfmt.filename)

        self._set_outtmpl(ytdl_instance, pathfmt.temppath.replace("%", "%%"))

        self.out.start(pathfmt.path)
        try:
            ytdl_instance.process_info(info_dict)
        except Exception as exc:
            self.log.debug("", exc_info=exc)
            return False
        return True

    def _download_playlist(self, ytdl_instance, pathfmt, info_dict):
        pathfmt.set_extension("%(playlist_index)s.%(ext)s")
        pathfmt.build_path()
        self._set_outtmpl(ytdl_instance, pathfmt.realpath)

        for entry in info_dict["entries"]:
            ytdl_instance.process_info(entry)
        return True

    def _extract_info(self, ytdl, url):
        return ytdl.extract_info(url, download=False)

    def _extract_manifest(self, ytdl, url, manifest):
        extr = ytdl.get_info_extractor("Generic")
        video_id = extr._generic_id(url)

        if manifest == "hls":
            try:
                formats, subtitles = extr._extract_m3u8_formats_and_subtitles(
                    url, video_id, "mp4")
            except AttributeError:
                formats = extr._extract_m3u8_formats(url, video_id, "mp4")
                subtitles = None

        elif manifest == "dash":
            try:
                formats, subtitles = extr._extract_mpd_formats_and_subtitles(
                    url, video_id)
            except AttributeError:
                formats = extr._extract_mpd_formats(url, video_id)
                subtitles = None

        else:
            self.log.error("Unsupported manifest type '%s'", manifest)
            return None

        info_dict = {
            "id"       : video_id,
            "title"    : video_id,
            "formats"  : formats,
            "subtitles": subtitles,
        }
        #  extr._extra_manifest_info(info_dict, url)
        return ytdl.process_ie_result(info_dict, download=False)

    def _progress_hook(self, info):
        if info["status"] == "downloading" and \
                info["elapsed"] >= self.progress:
            total = info.get("total_bytes") or info.get("total_bytes_estimate")
            speed = info.get("speed")
            self.out.progress(
                None if total is None else int(total),
                info["downloaded_bytes"],
                int(speed) if speed else 0,
            )

    @staticmethod
    def _set_outtmpl(ytdl_instance, outtmpl):
        try:
            ytdl_instance._parse_outtmpl
        except AttributeError:
            try:
                ytdl_instance.outtmpl_dict["default"] = outtmpl
            except AttributeError:
                ytdl_instance.params["outtmpl"] = outtmpl
        else:
            ytdl_instance.params["outtmpl"] = {"default": outtmpl}


def compatible_formats(formats):
    """Returns True if 'formats' are compatible for merge"""
    video_ext = formats[0].get("ext")
    audio_ext = formats[1].get("ext")

    if video_ext == "webm" and audio_ext == "webm":
        return True

    exts = ("mp3", "mp4", "m4a", "m4p", "m4b", "m4r", "m4v", "ismv", "isma")
    return video_ext in exts and audio_ext in exts


__downloader__ = YoutubeDLDownloader

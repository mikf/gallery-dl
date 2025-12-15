# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for URLs requiring youtube-dl support"""

from .common import DownloaderBase
from .. import ytdl, text
from xml.etree import ElementTree
from http.cookiejar import Cookie
import os


class YoutubeDLDownloader(DownloaderBase):
    scheme = "ytdl"

    def __init__(self, job):
        DownloaderBase.__init__(self, job)

        extractor = job.extractor
        self.retries = self.config("retries", extractor._retries)
        self.ytdl_opts = {
            "retries": self.retries+1 if self.retries >= 0 else float("inf"),
            "socket_timeout": self.config("timeout", extractor._timeout),
            "nocheckcertificate": not self.config("verify", extractor._verify),
            "proxy": self.proxies.get("http") if self.proxies else None,
            "ignoreerrors": True,
        }

        self.ytdl_instance = None
        self.rate_dyn = None
        self.forward_cookies = self.config("forward-cookies", True)
        self.progress = self.config("progress", 3.0)
        self.outtmpl = self.config("outtmpl")

    def download(self, url, pathfmt):
        kwdict = pathfmt.kwdict
        tries = 0

        if ytdl_instance := kwdict.pop("_ytdl_instance", None):
            # 'ytdl' extractor
            self._prepare(ytdl_instance)
            info_dict = kwdict.pop("_ytdl_info_dict")
        else:
            # other extractors
            ytdl_instance = self.ytdl_instance
            if not ytdl_instance:
                try:
                    module = ytdl.import_module(self.config("module"))
                except (ImportError, SyntaxError) as exc:
                    if exc.__context__:
                        self.log.error("Cannot import yt-dlp or youtube-dl")
                    else:
                        self.log.error("Cannot import module '%s'",
                                       getattr(exc, "name", ""))
                    self.log.traceback(exc)
                    self.download = lambda u, p: False
                    return False

                try:
                    ytdl_version = module.version.__version__
                except Exception:
                    ytdl_version = ""
                self.log.debug("Using %s version %s", module, ytdl_version)

                self.ytdl_instance = ytdl_instance = ytdl.construct_YoutubeDL(
                    module, self, self.ytdl_opts)
                if self.outtmpl == "default":
                    self.outtmpl = module.DEFAULT_OUTTMPL
                self._prepare(ytdl_instance)

            if self.forward_cookies:
                self.log.debug("Forwarding cookies to %s",
                               ytdl_instance.__module__)
                set_cookie = ytdl_instance.cookiejar.set_cookie
                for cookie in self.session.cookies:
                    set_cookie(cookie)

            url = url[5:]
            manifest = kwdict.get("_ytdl_manifest")
            while True:
                tries += 1
                self.error = None
                try:
                    if manifest is None:
                        info_dict = self._extract_url(
                            ytdl_instance, url)
                    else:
                        info_dict = self._extract_manifest(
                            ytdl_instance, url, kwdict)
                except Exception as exc:
                    self.log.traceback(exc)
                    cls = exc.__class__
                    if cls.__module__ == "builtins":
                        tries = False
                    msg = f"{cls.__name__}: {exc}"
                else:
                    if self.error is not None:
                        msg = self.error
                    elif not info_dict:
                        msg = "Empty 'info_dict' data"
                    else:
                        break

                if tries:
                    self.log.error("%s (%s/%s)", msg, tries, self.retries+1)
                else:
                    self.log.error(msg)
                    return False
                if tries > self.retries:
                    return False

        if extra := kwdict.get("_ytdl_extra"):
            info_dict.update(extra)

        while True:
            tries += 1
            self.error = None
            try:
                if "entries" in info_dict:
                    success = self._download_playlist(
                        ytdl_instance, pathfmt, info_dict)
                else:
                    success = self._download_video(
                        ytdl_instance, pathfmt, info_dict)
            except Exception as exc:
                self.log.traceback(exc)
                cls = exc.__class__
                if cls.__module__ == "builtins":
                    tries = False
                msg = f"{cls.__name__}: {exc}"
            else:
                if self.error is not None:
                    msg = self.error
                elif not success:
                    msg = "Error"
                else:
                    break

            if tries:
                self.log.error("%s (%s/%s)", msg, tries, self.retries+1)
            else:
                self.log.error(msg)
                return False
            if tries > self.retries:
                return False
        return True

    def _extract_url(self, ytdl, url):
        return ytdl.extract_info(url, download=False)

    def _extract_manifest(self, ytdl, url, kwdict):
        extr = ytdl.get_info_extractor("Generic")
        video_id = extr._generic_id(url)

        if cookies := kwdict.get("_ytdl_manifest_cookies"):
            if isinstance(cookies, dict):
                cookies = cookies.items()
            set_cookie = ytdl.cookiejar.set_cookie
            for name, value in cookies:
                set_cookie(Cookie(
                    0, name, value, None, False,
                    "", False, False, "/", False,
                    False, None, False, None, None, {},
                ))

        type = kwdict["_ytdl_manifest"]
        data = kwdict.get("_ytdl_manifest_data")
        headers = kwdict.get("_ytdl_manifest_headers")
        if type == "hls":
            if data is None:
                try:
                    fmts, subs = extr._extract_m3u8_formats_and_subtitles(
                        url, video_id, "mp4", headers=headers)
                except AttributeError:
                    fmts = extr._extract_m3u8_formats(
                        url, video_id, "mp4", headers=headers)
                    subs = None
            else:
                try:
                    fmts, subs = extr._parse_m3u8_formats_and_subtitles(
                        data, url, "mp4", headers=headers)
                except AttributeError:
                    fmts = extr._parse_m3u8_formats(
                        data, url, "mp4", headers=headers)
                    subs = None

        elif type == "dash":
            if data is None:
                try:
                    fmts, subs = extr._extract_mpd_formats_and_subtitles(
                        url, video_id, headers=headers)
                except AttributeError:
                    fmts = extr._extract_mpd_formats(
                        url, video_id, headers=headers)
                    subs = None
            else:
                if isinstance(data, str):
                    data = ElementTree.fromstring(data)
                try:
                    fmts, subs = extr._parse_mpd_formats_and_subtitles(
                        data, mpd_id="dash")
                except AttributeError:
                    fmts = extr._parse_mpd_formats(
                        data, mpd_id="dash")
                    subs = None

        else:
            raise ValueError(f"Unsupported manifest type '{type}'")

        if headers:
            for fmt in fmts:
                fmt["http_headers"] = headers

        info_dict = {
            "extractor": "",
            "id"       : video_id,
            "title"    : video_id,
            "formats"  : fmts,
            "subtitles": subs,
        }
        return ytdl.process_ie_result(info_dict, download=False)

    def _download_video(self, ytdl_instance, pathfmt, info_dict):
        if "url" in info_dict:
            if "filename" in pathfmt.kwdict:
                pathfmt.kwdict["extension"] = \
                    text.ext_from_url(info_dict["url"])
            else:
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

        if self.rate_dyn is not None:
            # static ratelimits are set in ytdl.construct_YoutubeDL
            ytdl_instance.params["ratelimit"] = self.rate_dyn()

        self.out.start(pathfmt.path)
        if self.part:
            pathfmt.kwdict["extension"] = pathfmt.prefix
            filename = pathfmt.build_filename(pathfmt.kwdict)
            pathfmt.kwdict["extension"] = info_dict["ext"]
            if self.partdir:
                path = os.path.join(self.partdir, filename)
            else:
                path = pathfmt.realdirectory + filename
            path = path.replace("%", "%%") + "%(ext)s"
        else:
            path = pathfmt.realpath.replace("%", "%%")

        self._set_outtmpl(ytdl_instance, path)
        ytdl_instance.process_info(info_dict)
        pathfmt.temppath = info_dict.get("filepath") or info_dict["_filename"]
        return True

    def _download_playlist(self, ytdl_instance, pathfmt, info_dict):
        pathfmt.kwdict["extension"] = pathfmt.prefix
        filename = pathfmt.build_filename(pathfmt.kwdict)
        pathfmt.kwdict["extension"] = pathfmt.extension
        path = pathfmt.realdirectory + filename
        path = path.replace("%", "%%") + "%(playlist_index)s.%(ext)s"
        self._set_outtmpl(ytdl_instance, path)

        status = False
        for entry in info_dict["entries"]:
            if not entry:
                continue
            if self.rate_dyn is not None:
                ytdl_instance.params["ratelimit"] = self.rate_dyn()
            try:
                ytdl_instance.process_info(entry)
                status = True
            except Exception as exc:
                self.log.traceback(exc)
                self.log.error("%s: %s", exc.__class__.__name__, exc)
        return status

    def _prepare(self, ytdl_instance):
        if "__gdl_initialize" not in ytdl_instance.params:
            return

        del ytdl_instance.params["__gdl_initialize"]
        if self.progress is not None:
            ytdl_instance.add_progress_hook(self._progress_hook)
        if rlf := ytdl_instance.params.pop("__gdl_ratelimit_func", False):
            self.rate_dyn = rlf
        ytdl_instance.params["logger"] = LoggerAdapter(self, ytdl_instance)

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

    def _set_outtmpl(self, ytdl_instance, outtmpl):
        try:
            ytdl_instance._parse_outtmpl
        except AttributeError:
            try:
                ytdl_instance.outtmpl_dict["default"] = outtmpl
            except AttributeError:
                ytdl_instance.params["outtmpl"] = outtmpl
        else:
            ytdl_instance.params["outtmpl"] = {"default": outtmpl}


class LoggerAdapter():
    __slots__ = ("obj", "log")

    def __init__(self, obj, ytdl_instance):
        self.obj = obj
        self.log = ytdl_instance.params.get("logger")

    def debug(self, msg):
        if self.log is not None:
            if msg[0] == "[":
                msg = msg[msg.find("]")+2:]
            self.log.debug(msg)

    def warning(self, msg):
        if self.log is not None:
            if "WARNING:" in msg:
                msg = msg[msg.find(" ")+1:]
            self.log.warning(msg)

    def error(self, msg):
        if "ERROR:" in msg:
            msg = msg[msg.find(" ")+1:]
        self.obj.error = msg


def compatible_formats(formats):
    """Returns True if 'formats' are compatible for merge"""
    video_ext = formats[0].get("ext")
    audio_ext = formats[1].get("ext")

    if video_ext == "webm" and audio_ext == "webm":
        return True

    exts = ("mp3", "mp4", "m4a", "m4p", "m4b", "m4r", "m4v", "ismv", "isma")
    return video_ext in exts and audio_ext in exts


__downloader__ = YoutubeDLDownloader

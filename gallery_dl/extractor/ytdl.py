# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for sites supported by youtube-dl"""

from .common import Extractor, Message
from .. import text, config, exception


class YoutubeDLExtractor(Extractor):
    """Generic extractor for youtube-dl supported URLs"""
    category = "ytdl"
    directory_fmt = ("{category}", "{subcategory}")
    filename_fmt = "{title}-{id}.{extension}"
    archive_fmt = "{extractor_key} {id}"
    pattern = r"ytdl:(.*)"
    test = ("ytdl:https://www.youtube.com/watch?v=BaW_jenozKc&t=1s&end=9",)

    def __init__(self, match):
        # import main youtube_dl module
        module_name = self.ytdl_module_name = config.get(
            ("extractor", "ytdl"), "module") or "youtube_dl"
        module = __import__(module_name)

        # find suitable youtube_dl extractor
        self.ytdl_url = url = match.group(1)
        generic = config.interpolate(("extractor", "ytdl"), "generic", True)
        if generic == "force":
            self.ytdl_ie_key = "Generic"
            self.force_generic_extractor = True
        else:
            for ie in module.extractor.gen_extractor_classes():
                if ie.suitable(url):
                    self.ytdl_ie_key = ie.ie_key()
                    break
            if not generic and self.ytdl_ie_key == "Generic":
                raise exception.NoExtractorError()
            self.force_generic_extractor = False

        # set subcategory to youtube_dl extractor's key
        self.subcategory = self.ytdl_ie_key
        Extractor.__init__(self, match)

    def items(self):
        # import subcategory module
        ytdl_module = __import__(
            config.get(("extractor", "ytdl", self.subcategory), "module") or
            self.ytdl_module_name)
        self.log.debug("Using %s", ytdl_module)

        # construct YoutubeDL object
        options = {
            "format"                 : self.config("format"),
            "retries"                : self._retries,
            "socket_timeout"         : self._timeout,
            "nocheckcertificate"     : not self._verify,
            "proxy"                  : self.session.proxies.get("http"),
            "force_generic_extractor": self.force_generic_extractor,
            "nopart"                 : not self.config("part", True),
            "updatetime"             : self.config("mtime", True),
            "ratelimit"              : text.parse_bytes(
                self.config("rate"), None),
            "min_filesize"           : text.parse_bytes(
                self.config("filesize-min"), None),
            "max_filesize"           : text.parse_bytes(
                self.config("filesize-max"), None),
        }

        raw_options = self.config("raw-options")
        if raw_options:
            options.update(raw_options)
        if self.config("logging", True):
            options["logger"] = self.log
        options["extract_flat"] = "in_playlist"

        username, password = self._get_auth_info()
        if username:
            options["username"], options["password"] = username, password
        del username, password

        ytdl = ytdl_module.YoutubeDL(options)

        # transfer cookies to ytdl
        cookies = self.session.cookies
        if cookies:
            set_cookie = self.ytdl.cookiejar.set_cookie
            for cookie in self.session.cookies:
                set_cookie(cookie)

        # extract youtube_dl info_dict
        info_dict = ytdl._YoutubeDL__extract_info(
            self.ytdl_url,
            ytdl.get_info_extractor(self.ytdl_ie_key),
            False, {}, True)

        if "entries" in info_dict:
            results = self._process_entries(ytdl, info_dict["entries"])
        else:
            results = (info_dict,)

        # yield results
        for info_dict in results:
            info_dict["extension"] = None
            info_dict["_ytdl_info_dict"] = info_dict
            info_dict["_ytdl_instance"] = ytdl

            url = "ytdl:" + (info_dict.get("url") or
                             info_dict.get("webpage_url") or
                             self.ytdl_url)

            yield Message.Directory, info_dict
            yield Message.Url, url, info_dict

    def _process_entries(self, ytdl, entries):
        for entry in entries:
            if entry.get("_type") in ("url", "url_transparent"):
                info_dict = ytdl.extract_info(
                    entry["url"], False,
                    ie_key=entry.get("ie_key"))
                if "entries" in info_dict:
                    yield from self._process_entries(
                        ytdl, info_dict["entries"])
                else:
                    yield info_dict
            else:
                yield entry


if config.get(("extractor", "ytdl"), "enabled"):
    # make 'ytdl:' prefix optional
    YoutubeDLExtractor.pattern = r"(?:ytdl:)?(.*)"

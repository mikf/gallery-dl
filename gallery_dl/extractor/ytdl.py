# -*- coding: utf-8 -*-

# Copyright 2021-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for sites supported by youtube-dl"""

from .common import Extractor, Message
from .. import ytdl, config, exception


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
        ytdl_module = ytdl.import_module(config.get(
            ("extractor", "ytdl"), "module"))
        self.ytdl_module_name = ytdl_module.__name__

        # find suitable youtube_dl extractor
        self.ytdl_url = url = match.group(1)
        generic = config.interpolate(("extractor", "ytdl"), "generic", True)
        if generic == "force":
            self.ytdl_ie_key = "Generic"
            self.force_generic_extractor = True
        else:
            for ie in ytdl_module.extractor.gen_extractor_classes():
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
        ytdl_module = ytdl.import_module(
            config.get(("extractor", "ytdl", self.subcategory), "module") or
            self.ytdl_module_name)
        self.log.debug("Using %s", ytdl_module)

        # construct YoutubeDL object
        extr_opts = {
            "extract_flat"           : "in_playlist",
            "force_generic_extractor": self.force_generic_extractor,
        }
        user_opts = {
            "retries"                : self._retries,
            "socket_timeout"         : self._timeout,
            "nocheckcertificate"     : not self._verify,
        }

        if self._proxies:
            user_opts["proxy"] = self._proxies.get("http")

        username, password = self._get_auth_info()
        if username:
            user_opts["username"], user_opts["password"] = username, password
        del username, password

        ytdl_instance = ytdl.construct_YoutubeDL(
            ytdl_module, self, user_opts, extr_opts)

        # transfer cookies to ytdl
        cookies = self.session.cookies
        if cookies:
            set_cookie = ytdl_instance.cookiejar.set_cookie
            for cookie in cookies:
                set_cookie(cookie)

        # extract youtube_dl info_dict
        try:
            info_dict = ytdl_instance._YoutubeDL__extract_info(
                self.ytdl_url,
                ytdl_instance.get_info_extractor(self.ytdl_ie_key),
                False, {}, True)
        except ytdl_module.utils.YoutubeDLError:
            raise exception.StopExtraction("Failed to extract video data")

        if not info_dict:
            return
        elif "entries" in info_dict:
            results = self._process_entries(
                ytdl_module, ytdl_instance, info_dict["entries"])
        else:
            results = (info_dict,)

        # yield results
        for info_dict in results:
            info_dict["extension"] = None
            info_dict["_ytdl_info_dict"] = info_dict
            info_dict["_ytdl_instance"] = ytdl_instance

            url = "ytdl:" + (info_dict.get("url") or
                             info_dict.get("webpage_url") or
                             self.ytdl_url)

            yield Message.Directory, info_dict
            yield Message.Url, url, info_dict

    def _process_entries(self, ytdl_module, ytdl_instance, entries):
        for entry in entries:
            if not entry:
                continue
            elif entry.get("_type") in ("url", "url_transparent"):
                try:
                    info_dict = ytdl_instance.extract_info(
                        entry["url"], False,
                        ie_key=entry.get("ie_key"))
                except ytdl_module.utils.YoutubeDLError:
                    continue

                if not info_dict:
                    continue
                elif "entries" in info_dict:
                    yield from self._process_entries(
                        ytdl_module, ytdl_instance, info_dict["entries"])
                else:
                    yield info_dict
            else:
                yield entry


if config.get(("extractor", "ytdl"), "enabled"):
    # make 'ytdl:' prefix optional
    YoutubeDLExtractor.pattern = r"(?:ytdl:)?(.*)"

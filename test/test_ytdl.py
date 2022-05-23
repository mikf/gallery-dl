#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import ytdl, util, config  # noqa E402


class Test_CommandlineArguments(unittest.TestCase):
    module_name = "youtube_dl"

    @classmethod
    def setUpClass(cls):
        try:
            cls.module = __import__(cls.module_name)
        except ImportError:
            raise unittest.SkipTest("cannot import module '{}'".format(
                cls.module_name))
        cls.default = ytdl.parse_command_line(cls.module, [])

    def test_ignore_errors(self):
        self._("--ignore-errors" , "ignoreerrors", True)
        self._("--abort-on-error", "ignoreerrors", False)

    def test_default_search(self):
        self._(["--default-search", "foo"] , "default_search", "foo")

    def test_mark_watched(self):
        self._("--mark-watched"   , "mark_watched", True)
        self._("--no-mark-watched", "mark_watched", False)

    def test_proxy(self):
        self._(["--proxy", "socks5://127.0.0.1:1080/"],
               "proxy", "socks5://127.0.0.1:1080/")
        self._(["--cn-verification-proxy", "https://127.0.0.1"],
               "cn_verification_proxy", "https://127.0.0.1")
        self._(["--geo-verification-proxy", "127.0.0.1"],
               "geo_verification_proxy", "127.0.0.1")

    def test_network_options(self):
        self._(["--socket-timeout", "3.5"],
               "socket_timeout", 3.5)
        self._(["--source-address", "127.0.0.1"],
               "source_address", "127.0.0.1")
        self._("-4"          , "source_address", "0.0.0.0")
        self._("--force-ipv4", "source_address", "0.0.0.0")
        self._("-6"          , "source_address", "::")
        self._("--force-ipv6", "source_address", "::")

    def test_thumbnail_options(self):
        self._("--write-thumbnail", "writethumbnail", True)
        self._("--write-all-thumbnails", "write_all_thumbnails", True)

    def test_authentication_options(self):
        self._(["-u"        , "foo"], "username", "foo")
        self._(["--username", "foo"], "username", "foo")

        self._(["-p"        , "bar"], "password", "bar")
        self._(["--password", "bar"], "password", "bar")

        self._(["--ap-mso"     , "mso"], "ap_mso", "mso")
        self._(["--ap-username", "foo"], "ap_username", "foo")
        self._(["--ap-password", "bar"], "ap_password", "bar")

        self._(["-2"         , "pass"], "twofactor", "pass")
        self._(["--twofactor", "pass"], "twofactor", "pass")

        self._(["--video-password", "pass"], "videopassword", "pass")

        self._("-n"     , "usenetrc", True)
        self._("--netrc", "usenetrc", True)

    def test_subtitle_options(self):
        self._("--write-sub"     , "writesubtitles"   , True)
        self._("--write-auto-sub", "writeautomaticsub", True)

        self._(["--sub-format", "best"], "subtitlesformat", "best")
        self._(["--sub-langs", "en,ru"], "subtitleslangs", ["en", "ru"])

    def test_retries(self):
        inf = float("inf")

        self._(["--retries", "5"], "retries", 5)
        self._(["--retries", "inf"], "retries", inf)
        self._(["--retries", "infinite"], "retries", inf)
        self._(["--fragment-retries", "8"], "fragment_retries", 8)
        self._(["--fragment-retries", "inf"], "fragment_retries", inf)
        self._(["--fragment-retries", "infinite"], "fragment_retries", inf)

    def test_geo_bypass(self):
        self._("--geo-bypass", "geo_bypass", True)
        self._("--no-geo-bypass", "geo_bypass", False)
        self._(["--geo-bypass-country", "EN"], "geo_bypass_country", "EN")
        self._(["--geo-bypass-ip-block", "198.51.100.14/24"],
               "geo_bypass_ip_block", "198.51.100.14/24")

    def test_headers(self):
        headers = self.module.std_headers

        self.assertNotEqual(headers["User-Agent"], "Foo/1.0")
        self._(["--user-agent", "Foo/1.0"])
        self.assertEqual(headers["User-Agent"], "Foo/1.0")

        self.assertNotIn("Referer", headers)
        self._(["--referer", "http://example.org/"])
        self.assertEqual(headers["Referer"], "http://example.org/")

        self.assertNotEqual(headers["Accept"], "*/*")
        self.assertNotIn("DNT", headers)
        self._([
            "--add-header", "accept:*/*",
            "--add-header", "dnt:1",
        ])
        self.assertEqual(headers["accept"], "*/*")
        self.assertEqual(headers["dnt"], "1")

    def test_extract_audio(self):
        opts = self._(["--extract-audio"])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "best",
            "preferredquality": "5",
            "nopostoverwrites": False,
        })

        opts = self._([
            "--extract-audio",
            "--audio-format", "opus",
            "--audio-quality", "9",
            "--no-post-overwrites",
        ])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
            "preferredquality": "9",
            "nopostoverwrites": True,
        })

    def test_recode_video(self):
        opts = self._(["--recode-video", " mkv "])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mkv",
        })

    def test_subs(self):
        opts = self._(["--convert-subs", "srt"])
        conv = {"key": "FFmpegSubtitlesConvertor", "format": "srt"}
        if self.module_name == "yt_dlp":
            conv["when"] = "before_dl"
        self.assertEqual(opts["postprocessors"][0], conv)

    def test_embed(self):
        subs = {"key": "FFmpegEmbedSubtitle"}
        thumb = {"key": "EmbedThumbnail", "already_have_thumbnail": False}
        if self.module_name == "yt_dlp":
            subs["already_have_subtitle"] = False

        opts = self._(["--embed-subs", "--embed-thumbnail"])
        self.assertEqual(opts["postprocessors"], [subs, thumb])

        thumb["already_have_thumbnail"] = True
        if self.module_name == "yt_dlp":
            subs["already_have_subtitle"] = True
            thumb["already_have_thumbnail"] = "all"

        opts = self._([
            "--embed-thumbnail",
            "--embed-subs",
            "--write-sub",
            "--write-all-thumbnails",
        ])
        self.assertEqual(opts["postprocessors"], [subs, thumb])

    def test_metadata(self):
        opts = self._("--add-metadata")
        self.assertEqual(opts["postprocessors"][0], {"key": "FFmpegMetadata"})

    def test_metadata_from_title(self):
        opts = self._(["--metadata-from-title", "%(artist)s - %(title)s"])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "MetadataFromTitle",
            "titleformat": "%(artist)s - %(title)s",
        })

    def test_xattr(self):
        self._("--xattr-set-filesize", "xattr_set_filesize", True)

        opts = self._("--xattrs")
        self.assertEqual(opts["postprocessors"][0], {"key": "XAttrMetadata"})

    def test_noop(self):
        cmdline = [
            "--update",
            "--dump-user-agent",
            "-F",
            "--list-formats",
            "--list-extractors",
            "--list-thumbnails",
            "--list-subs",
            "--ap-list-mso",
            "--extractor-descriptions",
            "--ignore-config",
        ]

        if self.module_name != "yt_dlp":
            cmdline.extend((
                "--dump-json",
                "--dump-single-json",
                "--config-location", "~",
            ))

        result = self._(cmdline)
        result["daterange"] = self.default["daterange"]
        self.assertEqual(result, self.default)

    def _(self, cmdline, option=util.SENTINEL, expected=None):
        if isinstance(cmdline, str):
            cmdline = [cmdline]
        result = ytdl.parse_command_line(self.module, cmdline)
        if option is not util.SENTINEL:
            self.assertEqual(result[option], expected, option)
        return result


class Test_CommandlineArguments_YtDlp(Test_CommandlineArguments):
    module_name = "yt_dlp"

    def test_retries_extractor(self):
        inf = float("inf")

        self._(["--extractor-retries", "5"], "extractor_retries", 5)
        self._(["--extractor-retries", "inf"], "extractor_retries", inf)
        self._(["--extractor-retries", "infinite"], "extractor_retries", inf)

    def test_remuxs_video(self):
        opts = self._(["--remux-video", " mkv "])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mkv",
        })

    def test_metadata(self):
        opts = self._(["--embed-metadata",
                       "--no-embed-chapters",
                       "--embed-info-json"])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "FFmpegMetadata",
            "add_chapters": False,
            "add_metadata": True,
            "add_infojson": True,
        })

    def test_metadata_from_title(self):
        opts = self._(["--metadata-from-title", "%(artist)s - %(title)s"])
        self.assertEqual(opts["postprocessors"][0], {
            "key": "MetadataParser",
            "when": "pre_process",
            "actions": [self.module.MetadataFromFieldPP.to_action(
                "title:%(artist)s - %(title)s")],
        })


if __name__ == "__main__":
    unittest.main(warnings="ignore")

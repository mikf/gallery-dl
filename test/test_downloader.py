#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import Mock, MagicMock, patch

import re
import base64
import logging
import os.path
import tempfile
import threading
import http.server


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import downloader, extractor, output, config, util  # noqa E402


class MockDownloaderModule(Mock):
    __downloader__ = "mock"


class FakeJob():

    def __init__(self):
        self.extractor = extractor.find("test:")
        self.pathfmt = util.PathFormat(self.extractor)
        self.out = output.NullOutput()
        self.get_logger = logging.getLogger


class TestDownloaderModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # allow import of ytdl downloader module without youtube_dl installed
        sys.modules["youtube_dl"] = MagicMock()

    @classmethod
    def tearDownClass(cls):
        del sys.modules["youtube_dl"]

    def tearDown(self):
        downloader._cache.clear()

    def test_find(self):
        cls = downloader.find("http")
        self.assertEqual(cls.__name__, "HttpDownloader")
        self.assertEqual(cls.scheme  , "http")

        cls = downloader.find("https")
        self.assertEqual(cls.__name__, "HttpDownloader")
        self.assertEqual(cls.scheme  , "http")

        cls = downloader.find("text")
        self.assertEqual(cls.__name__, "TextDownloader")
        self.assertEqual(cls.scheme  , "text")

        cls = downloader.find("ytdl")
        self.assertEqual(cls.__name__, "YoutubeDLDownloader")
        self.assertEqual(cls.scheme  , "ytdl")

        self.assertEqual(downloader.find("ftp"), None)
        self.assertEqual(downloader.find("foo"), None)
        self.assertEqual(downloader.find(1234) , None)
        self.assertEqual(downloader.find(None) , None)

    @patch("builtins.__import__")
    def test_cache(self, import_module):
        import_module.return_value = MockDownloaderModule()
        downloader.find("http")
        downloader.find("text")
        downloader.find("ytdl")
        self.assertEqual(import_module.call_count, 3)
        downloader.find("http")
        downloader.find("text")
        downloader.find("ytdl")
        self.assertEqual(import_module.call_count, 3)

    @patch("builtins.__import__")
    def test_cache_http(self, import_module):
        import_module.return_value = MockDownloaderModule()
        downloader.find("http")
        downloader.find("https")
        self.assertEqual(import_module.call_count, 1)

    @patch("builtins.__import__")
    def test_cache_https(self, import_module):
        import_module.return_value = MockDownloaderModule()
        downloader.find("https")
        downloader.find("http")
        self.assertEqual(import_module.call_count, 1)


class TestDownloaderBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        cls.fnum = 0
        config.set((), "base-directory", cls.dir.name)
        cls.job = FakeJob()

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()
        config.clear()

    @classmethod
    def _prepare_destination(cls, content=None, part=True, extension=None):
        name = "file-{}".format(cls.fnum)
        cls.fnum += 1

        kwdict = {
            "category"   : "test",
            "subcategory": "test",
            "filename"   : name,
            "extension"  : extension,
        }

        pathfmt = cls.job.pathfmt
        pathfmt.set_directory(kwdict)
        pathfmt.set_filename(kwdict)

        if content:
            mode = "w" + ("b" if isinstance(content, bytes) else "")
            with pathfmt.open(mode) as file:
                file.write(content)

        return pathfmt

    def _run_test(self, url, input, output,
                  extension, expected_extension=None):
        pathfmt = self._prepare_destination(input, extension=extension)
        success = self.downloader.download(url, pathfmt)

        # test successful download
        self.assertTrue(success, "downloading '{}' failed".format(url))

        # test content
        mode = "r" + ("b" if isinstance(output, bytes) else "")
        with pathfmt.open(mode) as file:
            content = file.read()
        self.assertEqual(content, output)

        # test filename extension
        self.assertEqual(
            pathfmt.extension,
            expected_extension,
        )
        self.assertEqual(
            os.path.splitext(pathfmt.realpath)[1][1:],
            expected_extension,
        )


class TestHTTPDownloader(TestDownloaderBase):

    @classmethod
    def setUpClass(cls):
        TestDownloaderBase.setUpClass()
        cls.downloader = downloader.find("http")(cls.job)

        port = 8088
        cls.address = "http://127.0.0.1:{}".format(port)
        cls._jpg = cls.address + "/image.jpg"
        cls._png = cls.address + "/image.png"
        cls._gif = cls.address + "/image.gif"

        server = http.server.HTTPServer(("", port), HttpRequestHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.downloader.minsize = self.downloader.maxsize = None

    def test_http_download(self):
        self._run_test(self._jpg, None, DATA_JPG, "jpg", "jpg")
        self._run_test(self._png, None, DATA_PNG, "png", "png")
        self._run_test(self._gif, None, DATA_GIF, "gif", "gif")

    def test_http_offset(self):
        self._run_test(self._jpg, DATA_JPG[:123], DATA_JPG, "jpg", "jpg")
        self._run_test(self._png, DATA_PNG[:12] , DATA_PNG, "png", "png")
        self._run_test(self._gif, DATA_GIF[:1]  , DATA_GIF, "gif", "gif")

    def test_http_extension(self):
        self._run_test(self._jpg, None, DATA_JPG, None, "jpg")
        self._run_test(self._png, None, DATA_PNG, None, "png")
        self._run_test(self._gif, None, DATA_GIF, None, "gif")

    def test_http_adjust_extension(self):
        self._run_test(self._jpg, None, DATA_JPG, "png", "jpg")
        self._run_test(self._png, None, DATA_PNG, "gif", "png")
        self._run_test(self._gif, None, DATA_GIF, "jpg", "gif")

    def test_http_filesize_min(self):
        pathfmt = self._prepare_destination(None, extension=None)
        self.downloader.minsize = 100
        with self.assertLogs(self.downloader.log, "WARNING"):
            success = self.downloader.download(self._gif, pathfmt)
        self.assertFalse(success)

    def test_http_filesize_max(self):
        pathfmt = self._prepare_destination(None, extension=None)
        self.downloader.maxsize = 100
        with self.assertLogs(self.downloader.log, "WARNING"):
            success = self.downloader.download(self._jpg, pathfmt)
        self.assertFalse(success)


class TestTextDownloader(TestDownloaderBase):

    @classmethod
    def setUpClass(cls):
        TestDownloaderBase.setUpClass()
        cls.downloader = downloader.find("text")(cls.job)

    def test_text_download(self):
        self._run_test("text:foobar", None, "foobar", "txt", "txt")

    def test_text_offset(self):
        self._run_test("text:foobar", "foo", "foobar", "txt", "txt")

    def test_text_empty(self):
        self._run_test("text:", None, "", "txt", "txt")


class HttpRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/image.jpg":
            content_type = "image/jpeg"
            output = DATA_JPG
        elif self.path == "/image.png":
            content_type = "image/png"
            output = DATA_PNG
        elif self.path == "/image.gif":
            content_type = "image/gif"
            output = DATA_GIF
        else:
            self.send_response(404)
            self.wfile.write(self.path.encode())
            return

        headers = {
            "Content-Type": content_type,
            "Content-Length": len(output),
        }

        if "Range" in self.headers:
            status = 206

            match = re.match(r"bytes=(\d+)-", self.headers["Range"])
            start = int(match.group(1))

            headers["Content-Range"] = "bytes {}-{}/{}".format(
                start, len(output)-1, len(output))
            output = output[start:]
        else:
            status = 200

        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(output)


DATA_JPG = base64.standard_b64decode("""
/9j/4AAQSkZJRgABAQEASABIAAD/2wBD
AAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB
AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB
AQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEB
AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB
AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB
AQEBAQEBAQEBAQEBAQH/wAARCAABAAED
AREAAhEBAxEB/8QAFAABAAAAAAAAAAAA
AAAAAAAACv/EABQQAQAAAAAAAAAAAAAA
AAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAA
AAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAA
AP/aAAwDAQACEQMRAD8AfwD/2Q==""")


DATA_PNG = base64.standard_b64decode("""
iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB
CAAAAAA6fptVAAAACklEQVQIHWP4DwAB
AQEANl9ngAAAAABJRU5ErkJggg==""")


DATA_GIF = base64.standard_b64decode("""
R0lGODdhAQABAIAAAP///////ywAAAAA
AQABAAACAkQBADs=""")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import base64
import os.path
import tempfile
import unittest
import threading
import http.server

import gallery_dl.downloader as downloader
import gallery_dl.extractor as extractor
import gallery_dl.config as config
from gallery_dl.downloader.common import DownloaderBase
from gallery_dl.output import NullOutput
from gallery_dl.util import PathFormat


class TestDownloaderBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extractor = extractor.find("test:")
        cls.dir = tempfile.TemporaryDirectory()
        cls.fnum = 0
        config.set(("base-directory",), cls.dir.name)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()
        config.clear()

    @classmethod
    def _prepare_destination(cls, content=None, part=True, extension=None):
        name = "file-{}".format(cls.fnum)
        cls.fnum += 1

        kwdict = {
            "category": "test",
            "subcategory": "test",
            "filename": name,
            "extension": extension,
        }
        pathfmt = PathFormat(cls.extractor)
        pathfmt.set_directory(kwdict)
        pathfmt.set_keywords(kwdict)

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
            pathfmt.keywords["extension"],
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
        cls.downloader = downloader.find("http")(cls.extractor, NullOutput())

        port = 8088
        cls.address = "http://127.0.0.1:{}".format(port)
        cls._jpg = cls.address + "/image.jpg"
        cls._png = cls.address + "/image.png"
        cls._gif = cls.address + "/image.gif"

        server = http.server.HTTPServer(("", port), HttpRequestHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()

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


class TestTextDownloader(TestDownloaderBase):

    @classmethod
    def setUpClass(cls):
        TestDownloaderBase.setUpClass()
        cls.downloader = downloader.find("text")(cls.extractor, NullOutput())

    def test_text_download(self):
        self._run_test("text:foobar", None, "foobar", "txt", "txt")

    def test_text_offset(self):
        self._run_test("text:foobar", "foo", "foobar", "txt", "txt")

    def test_text_extension(self):
        self._run_test("text:foobar", None, "foobar", None, "txt")

    def test_text_empty(self):
        self._run_test("text:", None, "", "txt", "txt")


class FakeDownloader(DownloaderBase):
    scheme = "fake"

    def __init__(self, extractor, output):
        DownloaderBase.__init__(self, extractor, output)

    def connect(self, url, offset):
        pass

    def receive(self, file):
        pass

    def reset(self):
        pass

    def get_extension(self):
        pass

    @staticmethod
    def _check_extension(file, pathfmt):
        pass


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

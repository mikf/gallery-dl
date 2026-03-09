#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import Mock, MagicMock, patch

import re
import logging
import os.path
import binascii
import tempfile
import threading
import http.server

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import downloader, extractor, output, config, path  # noqa E402
from gallery_dl.downloader import http as http_downloader  # noqa E402
from gallery_dl.downloader.http import MIME_TYPES, SIGNATURE_CHECKS # noqa E402


class MockDownloaderModule(Mock):
    __downloader__ = "mock"


class FakeJob():

    def __init__(self):
        self.extractor = extractor.find("generic:https://example.org/")
        self.extractor.initialize()
        self.pathfmt = path.PathFormat(self.extractor)
        self.out = output.NullOutput()
        self.get_logger = logging.getLogger


class TestDownloaderModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # allow import of ytdl downloader module without youtube_dl installed
        cls._orig_ytdl = sys.modules.get("youtube_dl")
        sys.modules["youtube_dl"] = MagicMock()

    @classmethod
    def tearDownClass(cls):
        if cls._orig_ytdl:
            sys.modules["youtube_dl"] = cls._orig_ytdl
        else:
            del sys.modules["youtube_dl"]

    def setUp(self):
        downloader._cache.clear()

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


class TestDownloaderConfig(unittest.TestCase):

    def setUp(self):
        config.clear()

    def tearDown(self):
        config.clear()

    def test_default_http(self):
        job = FakeJob()
        extr = job.extractor
        dl = downloader.find("http")(job)

        self.assertEqual(dl.adjust_extension, True)
        self.assertEqual(dl.chunk_size, 32768)
        self.assertEqual(dl.metadata, None)
        self.assertEqual(dl.progress, 3.0)
        self.assertEqual(dl.validate, True)
        self.assertEqual(dl.headers, None)
        self.assertEqual(dl.minsize, None)
        self.assertEqual(dl.maxsize, None)
        self.assertEqual(dl.mtime, True)
        self.assertEqual(dl.rate, None)
        self.assertEqual(dl.part, True)
        self.assertEqual(dl.partdir, None)
        self.assertEqual(dl._aria2c, False)

        self.assertIs(dl.interval_429, extr._interval_429)
        self.assertIs(dl.retry_codes, extr._retry_codes)
        self.assertIs(dl.retries, extr._retries)
        self.assertIs(dl.timeout, extr._timeout)
        self.assertIs(dl.proxies, extr._proxies)
        self.assertIs(dl.verify, extr._verify)

    def test_config_http(self):
        config.set((), "rate", 42)
        config.set((), "mtime", False)
        config.set((), "headers", {"foo": "bar"})
        config.set(("downloader",), "retries", -1)
        config.set(("downloader", "http"), "filesize-min", "10k")
        config.set(("extractor", "generic"), "verify", False)
        config.set(("extractor", "generic", "example.org"), "timeout", 10)
        config.set(("extractor", "generic", "http"), "part", False)
        config.set(
            ("extractor", "generic", "example.org", "http"), "headers", {})

        job = FakeJob()
        dl = downloader.find("http")(job)

        self.assertEqual(dl.headers, {"foo": "bar"})
        self.assertEqual(dl.minsize, 10240)
        self.assertEqual(dl.retries, float("inf"))
        self.assertEqual(dl.timeout, 10)
        self.assertEqual(dl.verify, False)
        self.assertEqual(dl.mtime, False)
        self.assertEqual(dl.rate(), 42)
        self.assertEqual(dl.part, False)


class TestHTTPDownloaderAria2c(unittest.TestCase):
    """Tests for the aria2c backend option of HttpDownloader."""

    def setUp(self):
        config.clear()
        self.job = FakeJob()
        self.dl = downloader.find("http")(self.job)
        # Enable a fake aria2c path so _can_use_aria2c can return True.
        self.dl._aria2c = "aria2c"

    def tearDown(self):
        config.clear()

    # ------------------------------------------------------------------
    # _can_use_aria2c eligibility checks
    # ------------------------------------------------------------------

    def _can(self, **kwdict):
        return self.dl._can_use_aria2c(kwdict)

    def _prepare_aria2c_download(self, tmpdir, extension="jpg", name="aria2c"):
        config.set((), "base-directory", tmpdir)
        job = FakeJob()
        dl = downloader.find("http")(job)
        dl._aria2c = "aria2c"

        kwdict = {
            "category"   : "test",
            "subcategory": "test",
            "filename"   : name,
            "extension"  : extension,
        }
        pathfmt = job.pathfmt
        pathfmt.set_directory(kwdict)
        pathfmt.set_filename(kwdict)
        pathfmt.build_path()

        return dl, pathfmt

    def test_aria2c_config_false_by_default(self):
        dl = downloader.find("http")(self.job)
        self.assertEqual(dl._aria2c, False)

    def test_aria2c_config_true_becomes_string(self):
        config.set(("downloader", "http"), "aria2c", True)
        dl = downloader.find("http")(self.job)
        self.assertEqual(dl._aria2c, "aria2c")

    def test_aria2c_config_custom_path(self):
        config.set(("downloader", "http"), "aria2c", "/usr/local/bin/aria2c")
        dl = downloader.find("http")(self.job)
        self.assertEqual(dl._aria2c, "/usr/local/bin/aria2c")

    def test_can_use_aria2c_simple_get(self):
        self.assertTrue(self._can(extension="jpg"))

    def test_can_use_aria2c_no_aria2c(self):
        self.dl._aria2c = False
        self.assertFalse(self._can(extension="jpg"))

    def test_can_use_aria2c_non_get_method(self):
        self.assertFalse(self._can(extension="jpg", _http_method="POST"))

    def test_can_use_aria2c_with_data(self):
        self.assertFalse(self._can(extension="jpg", _http_data=b"body"))

    def test_can_use_aria2c_with_validate(self):
        self.assertFalse(self._can(extension="jpg",
                                   _http_validate=lambda r: True))

    def test_can_use_aria2c_with_retry(self):
        self.assertFalse(self._can(extension="jpg",
                                   _http_retry=lambda r: False))

    def test_can_use_aria2c_with_expected_status(self):
        self.assertFalse(self._can(extension="jpg",
                                   _http_expected_status=(202,)))

    def test_can_use_aria2c_with_segmented(self):
        self.assertFalse(self._can(extension="jpg", _http_segmented=True))

    def test_can_use_aria2c_metadata_enabled(self):
        self.dl.metadata = "http_headers"
        self.assertFalse(self._can(extension="jpg"))

    def test_can_use_aria2c_no_extension(self):
        # When extension is unknown, MIME type must come from the response
        self.assertFalse(self._can(extension=""))
        self.assertFalse(self._can())

    # ------------------------------------------------------------------
    # Fallback when aria2c binary is not found
    # ------------------------------------------------------------------

    def test_aria2c_fallback_on_not_found(self):
        """FileNotFoundError from subprocess falls back to built-in."""
        import tempfile
        import threading
        import http.server as _http

        # Spin up a tiny server returning a known payload
        payload = DATA["jpg"]
        addr_holder = []

        class Handler(_http.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Length", len(payload))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *a):
                pass

        srv = _http.HTTPServer(("127.0.0.1", 0), Handler)
        addr_holder.append(srv.server_address)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        host, port = addr_holder[0]
        url = f"http://{host}:{port}/img.jpg"

        with tempfile.TemporaryDirectory() as tmpdir:
            config.set((), "base-directory", tmpdir)
            job = FakeJob()
            dl = downloader.find("http")(job)
            dl._aria2c = "/nonexistent/aria2c"

            kwdict = {
                "category"   : "test",
                "subcategory": "test",
                "filename"   : "fallback",
                "extension"  : "jpg",
            }
            pf = job.pathfmt
            pf.set_directory(kwdict)
            pf.set_filename(kwdict)
            pf.build_path()

            with self.assertLogs(dl.log, "WARNING"):
                result = dl.download(url, pf)

        self.assertTrue(result)
        self.assertIsNone(dl._aria2c,
                          "aria2c should be disabled after fallback")

    @patch.object(http_downloader.subprocess, "run")
    def test_aria2c_forwards_matching_cookies_and_timeout(self, run):
        captured = {}

        def side_effect(cmd, capture_output):
            captured["cmd"] = cmd
            outdir = next(arg[6:] for arg in cmd if arg.startswith("--dir="))
            outfile = next(arg[6:] for arg in cmd if arg.startswith("--out="))
            os.makedirs(outdir, exist_ok=True)
            with open(os.path.join(outdir, outfile), "wb") as fp:
                fp.write(DATA["jpg"])
            return Mock(returncode=0, stderr=b"")

        run.side_effect = side_effect

        with tempfile.TemporaryDirectory() as tmpdir:
            dl, pathfmt = self._prepare_aria2c_download(tmpdir)
            dl.timeout = 7
            dl.session.cookies.set("good", "1", domain="example.org", path="/")
            dl.session.cookies.set("bad", "2", domain="invalid.example",
                                   path="/")

            result = dl.download("https://example.org/file.jpg", pathfmt)

        self.assertTrue(result)
        headers = [
            arg for arg in captured["cmd"]
            if arg.startswith("--header=")
        ]
        self.assertIn("--header=Cookie: good=1", headers)
        self.assertNotIn("--header=Cookie: bad=2", headers)
        self.assertIn("--timeout=7", captured["cmd"])
        self.assertIn("--connect-timeout=7", captured["cmd"])

    @patch.object(http_downloader.subprocess, "run")
    def test_aria2c_removes_invalid_html_download(self, run):
        def side_effect(cmd, capture_output):
            outdir = next(arg[6:] for arg in cmd if arg.startswith("--dir="))
            outfile = next(arg[6:] for arg in cmd if arg.startswith("--out="))
            os.makedirs(outdir, exist_ok=True)
            with open(os.path.join(outdir, outfile), "wb") as fp:
                fp.write(DATA["html"])
            return Mock(returncode=0, stderr=b"")

        run.side_effect = side_effect

        with tempfile.TemporaryDirectory() as tmpdir:
            dl, pathfmt = self._prepare_aria2c_download(
                tmpdir, name="invalid_html_as_jpg")
            partpath = pathfmt.realpath + ".part"

            with self.assertLogs(dl.log, "WARNING") as log_info:
                result = dl.download("https://example.org/file.jpg", pathfmt)

            self.assertFalse(result)
            self.assertEqual(log_info.output[-1],
                             "WARNING:downloader.http:HTML response")
            self.assertFalse(os.path.exists(partpath))
            self.assertEqual(pathfmt.temppath, "")


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
        name = f"file-{cls.fnum}"
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
        pathfmt.build_path()

        if content:
            mode = "wb" if isinstance(content, bytes) else "w"
            with pathfmt.open(mode) as fp:
                fp.write(content)

        return pathfmt

    def _run_test(self, url, input, output,
                  extension, expected_extension=None):
        pathfmt = self._prepare_destination(input, extension=extension)
        success = self.downloader.download(url, pathfmt)

        # test successful download
        self.assertTrue(success, f"downloading '{url}' failed")

        # test content
        mode = "rb" if isinstance(output, bytes) else "r"
        with pathfmt.open(mode) as fp:
            content = fp.read()
        self.assertEqual(content, output)

        # test filename extension
        self.assertEqual(
            pathfmt.extension,
            expected_extension,
            content[0:16],
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

        host = "127.0.0.1"
        port = 0  # select random not-in-use port

        try:
            server = http.server.HTTPServer((host, port), HttpRequestHandler)
        except OSError as exc:
            raise unittest.SkipTest(
                f"cannot spawn local HTTP server ({exc})")

        host, port = server.server_address
        cls.address = f"http://{host}:{port}"
        threading.Thread(target=server.serve_forever, daemon=True).start()

    def _run_test(self, ext, input, output,
                  extension, expected_extension=None):
        TestDownloaderBase._run_test(
            self, f"{self.address}/{ext}", input, output,
            extension, expected_extension)

    def tearDown(self):
        self.downloader.minsize = self.downloader.maxsize = None

    def test_http_download(self):
        self._run_test("jpg", None, DATA["jpg"], "jpg", "jpg")
        self._run_test("png", None, DATA["png"], "png", "png")
        self._run_test("gif", None, DATA["gif"], "gif", "gif")

    def test_http_offset(self):
        self._run_test("jpg", DATA["jpg"][:123], DATA["jpg"], "jpg", "jpg")
        self._run_test("png", DATA["png"][:12] , DATA["png"], "png", "png")
        self._run_test("gif", DATA["gif"][:1]  , DATA["gif"], "gif", "gif")

    def test_http_extension(self):
        self._run_test("jpg", None, DATA["jpg"], None, "jpg")
        self._run_test("png", None, DATA["png"], None, "png")
        self._run_test("gif", None, DATA["gif"], None, "gif")

    def test_http_adjust_extension(self):
        self._run_test("jpg", None, DATA["jpg"], "png", "jpg")
        self._run_test("png", None, DATA["png"], "gif", "png")
        self._run_test("gif", None, DATA["gif"], "jpg", "gif")

    def test_http_filesize_min(self):
        url = f"{self.address}/gif"
        pathfmt = self._prepare_destination(None, extension=None)
        self.downloader.minsize = 100
        with self.assertLogs(self.downloader.log, "WARNING"):
            success = self.downloader.download(url, pathfmt)
        self.assertTrue(success)
        self.assertEqual(pathfmt.temppath, "")

    def test_http_filesize_max(self):
        url = f"{self.address}/jpg"
        pathfmt = self._prepare_destination(None, extension=None)
        self.downloader.maxsize = 100
        with self.assertLogs(self.downloader.log, "WARNING"):
            success = self.downloader.download(url, pathfmt)
        self.assertTrue(success)
        self.assertEqual(pathfmt.temppath, "")

    def test_http_empty(self):
        url = f"{self.address}/~NUL"
        pathfmt = self._prepare_destination(None, extension=None)
        with self.assertLogs(self.downloader.log, "WARNING") as log_info:
            success = self.downloader.download(url, pathfmt)
        self.assertFalse(success)
        self.assertEqual(log_info.output[0],
                         "WARNING:downloader.http:Empty file")


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
        try:
            output = DATA[self.path[1:]]
        except KeyError:
            self.send_response(404)
            self.wfile.write(self.path.encode())
            return

        headers = {"Content-Length": len(output)}

        if "Range" in self.headers:
            status = 206

            match = re.match(r"bytes=(\d+)-", self.headers["Range"])
            start = int(match[1])

            headers["Content-Range"] = \
                f"bytes {start}-{len(output) - 1}/{len(output)}"
            output = output[start:]
        else:
            status = 200

        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(output)


SAMPLES = {
    ("jpg" , binascii.a2b_base64(
        "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
        "AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEB"
        "AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
        "AQEBAQEBAQEBAQEBAQH/wAARCAABAAEDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAA"
        "AAAAAAAACv/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAA"
        "AAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AfwD/2Q==")),
    ("png" , binascii.a2b_base64(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVQIHWP4DwAB"
        "AQEANl9ngAAAAABJRU5ErkJggg==")),
    ("gif" , binascii.a2b_base64(
        "R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=")),
    ("bmp" , b"BM"),
    ("webp", b"RIFF????WEBP"),
    ("avif", b"????ftypavif"),
    ("avif", b"????ftypavis"),
    ("heic", b"????ftypheic"),
    ("heic", b"????ftypheim"),
    ("heic", b"????ftypheis"),
    ("heic", b"????ftypheix"),
    ("svg" , b"<?xml"),
    ("html", b"<!DOCTYPE html><html>...</html>"),
    ("html", b"  \n  \n\r\t\n  <!DOCTYPE html><html>...</html>"),
    ("ico" , b"\x00\x00\x01\x00"),
    ("cur" , b"\x00\x00\x02\x00"),
    ("psd" , b"8BPS"),
    ("mp4" , b"????ftypmp4"),
    ("mp4" , b"????ftypavc1"),
    ("mp4" , b"????ftypiso3"),
    ("m4v" , b"????ftypM4V"),
    ("mov" , b"????ftypqt  "),
    ("webm", b"\x1A\x45\xDF\xA3"),
    ("ogg" , b"OggS"),
    ("wav" , b"RIFF????WAVE"),
    ("mp3" , b"ID3"),
    ("mp3" , b"\xFF\xFB"),
    ("mp3" , b"\xFF\xF3"),
    ("mp3" , b"\xFF\xF2"),
    ("aac" , b"\xFF\xF9"),
    ("aac" , b"\xFF\xF1"),
    ("m3u8", b"#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=200000"),
    ("mpd" , b'<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"'),
    ("zip" , b"PK\x03\x04"),
    ("zip" , b"PK\x05\x06"),
    ("zip" , b"PK\x07\x08"),
    ("rar" , b"Rar!\x1A\x07"),
    ("rar" , b"\x52\x61\x72\x21\x1A\x07"),
    ("7z"  , b"\x37\x7A\xBC\xAF\x27\x1C"),
    ("pdf" , b"%PDF-"),
    ("swf" , b"FWS"),
    ("swf" , b"CWS"),
    ("blend", b"BLENDER-v303RENDH"),
    ("obj" , b"# Blender v3.2.0 OBJ File: 'foo.blend'"),
    ("clip", b"CSFCHUNK\x00\x00\x00\x00"),
    ("~NUL", b""),
}


DATA = {}

for ext, content in SAMPLES:
    if ext not in DATA:
        DATA[ext] = content

for idx, (_, content) in enumerate(SAMPLES):
    DATA[f"S{idx:>02}"] = content


# reverse mime types mapping
MIME_TYPES = {
    ext: mtype
    for mtype, ext in MIME_TYPES.items()
}


def generate_tests():
    def generate_test(idx, ext, content):
        def test(self):
            self._run_test(f"S{idx:>02}", None, content, "bin", ext)
        test.__name__ = f"test_http_ext_{idx:>02}_{ext}"
        return test

    for idx, (ext, content) in enumerate(SAMPLES):
        if ext[0].isalnum():
            test = generate_test(idx, ext, content)
            setattr(TestHTTPDownloader, test.__name__, test)


generate_tests()
if __name__ == "__main__":
    unittest.main()

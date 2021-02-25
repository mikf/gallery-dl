# -*- coding: utf-8 -*-

# Copyright 2014-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// URLs"""

import time
import mimetypes
from requests.exceptions import RequestException, ConnectionError, Timeout
from .common import DownloaderBase
from .. import text, util

from ssl import SSLError
try:
    from OpenSSL.SSL import Error as OpenSSLError
except ImportError:
    OpenSSLError = SSLError


class HttpDownloader(DownloaderBase):
    scheme = "http"

    def __init__(self, job):
        DownloaderBase.__init__(self, job)
        extractor = job.extractor
        self.chunk_size = 16384
        self.downloading = False

        self.adjust_extension = self.config("adjust-extensions", True)
        self.headers = self.config("headers")
        self.minsize = self.config("filesize-min")
        self.maxsize = self.config("filesize-max")
        self.retries = self.config("retries", extractor._retries)
        self.timeout = self.config("timeout", extractor._timeout)
        self.verify = self.config("verify", extractor._verify)
        self.mtime = self.config("mtime", True)
        self.rate = self.config("rate")

        if self.retries < 0:
            self.retries = float("inf")
        if self.minsize:
            minsize = text.parse_bytes(self.minsize)
            if not minsize:
                self.log.warning(
                    "Invalid minimum file size (%r)", self.minsize)
            self.minsize = minsize
        if self.maxsize:
            maxsize = text.parse_bytes(self.maxsize)
            if not maxsize:
                self.log.warning(
                    "Invalid maximum file size (%r)", self.maxsize)
            self.maxsize = maxsize
        if self.rate:
            rate = text.parse_bytes(self.rate)
            if rate:
                if rate < self.chunk_size:
                    self.chunk_size = rate
                self.rate = rate
                self.receive = self._receive_rate
            else:
                self.log.warning("Invalid rate limit (%r)", self.rate)

    def download(self, url, pathfmt):
        try:
            return self._download_impl(url, pathfmt)
        except Exception:
            print()
            raise
        finally:
            # remove file from incomplete downloads
            if self.downloading and not self.part:
                util.remove_file(pathfmt.temppath)

    def _download_impl(self, url, pathfmt):
        response = None
        tries = 0
        msg = ""

        if self.part:
            pathfmt.part_enable(self.partdir)

        while True:
            if tries:
                if response:
                    response.close()
                    response = None
                self.log.warning("%s (%s/%s)", msg, tries, self.retries+1)
                if tries > self.retries:
                    return False
                time.sleep(tries)

            tries += 1
            headers = {"Accept": "*/*"}
            file_header = None

            # check for .part file
            file_size = pathfmt.part_size()
            if file_size:
                headers["Range"] = "bytes={}-".format(file_size)
            # general headers
            if self.headers:
                headers.update(self.headers)
            # file-specific headers
            extra = pathfmt.kwdict.get("_http_headers")
            if extra:
                headers.update(extra)

            # connect to (remote) source
            try:
                response = self.session.request(
                    "GET", url, stream=True, headers=headers,
                    timeout=self.timeout, verify=self.verify)
            except (ConnectionError, Timeout) as exc:
                msg = str(exc)
                continue
            except Exception as exc:
                self.log.warning(exc)
                return False

            # check response
            code = response.status_code
            if code == 200:  # OK
                offset = 0
                size = response.headers.get("Content-Length")
            elif code == 206:  # Partial Content
                offset = file_size
                size = response.headers["Content-Range"].rpartition("/")[2]
            elif code == 416 and file_size:  # Requested Range Not Satisfiable
                break
            else:
                msg = "'{} {}' for '{}'".format(code, response.reason, url)
                if code == 429 or 500 <= code < 600:  # Server Error
                    continue
                self.log.warning(msg)
                return False

            # check for invalid responses
            validate = pathfmt.kwdict.get("_http_validate")
            if validate and not validate(response):
                self.log.warning("Invalid response")
                return False

            # set missing filename extension from MIME type
            if not pathfmt.extension:
                pathfmt.set_extension(self._find_extension(response))
                if pathfmt.exists():
                    pathfmt.temppath = ""
                    return True

            # check file size
            size = text.parse_int(size, None)
            if size is not None:
                if self.minsize and size < self.minsize:
                    self.log.warning(
                        "File size smaller than allowed minimum (%s < %s)",
                        size, self.minsize)
                    return False
                if self.maxsize and size > self.maxsize:
                    self.log.warning(
                        "File size larger than allowed maximum (%s > %s)",
                        size, self.maxsize)
                    return False

            content = response.iter_content(self.chunk_size)

            # check filename extension against file header
            if self.adjust_extension and not offset and \
                    pathfmt.extension in FILE_SIGNATURES:
                try:
                    file_header = next(
                        content if response.raw.chunked
                        else response.iter_content(16), b"")
                except (RequestException, SSLError, OpenSSLError) as exc:
                    msg = str(exc)
                    print()
                    continue
                if self._adjust_extension(pathfmt, file_header) and \
                        pathfmt.exists():
                    pathfmt.temppath = ""
                    return True

            # set open mode
            if not offset:
                mode = "w+b"
                if file_size:
                    self.log.debug("Unable to resume partial download")
            else:
                mode = "r+b"
                self.log.debug("Resuming download at byte %d", offset)

            # download content
            self.downloading = True
            with pathfmt.open(mode) as fp:
                if file_header:
                    fp.write(file_header)
                elif offset:
                    if self.adjust_extension and \
                            pathfmt.extension in FILE_SIGNATURES:
                        self._adjust_extension(pathfmt, fp.read(16))
                    fp.seek(offset)

                self.out.start(pathfmt.path)
                try:
                    self.receive(fp, content)
                except (RequestException, SSLError, OpenSSLError) as exc:
                    msg = str(exc)
                    print()
                    continue

                # check file size
                if size and fp.tell() < size:
                    msg = "file size mismatch ({} < {})".format(
                        fp.tell(), size)
                    print()
                    continue

            break

        self.downloading = False
        if self.mtime:
            pathfmt.kwdict.setdefault(
                "_mtime", response.headers.get("Last-Modified"))
        else:
            pathfmt.kwdict["_mtime"] = None

        return True

    @staticmethod
    def receive(fp, content):
        write = fp.write
        for data in content:
            write(data)

    def _receive_rate(self, fp, content):
        rt = self.rate
        t1 = time.time()

        for data in content:
            fp.write(data)

            t2 = time.time()           # current time
            actual = t2 - t1           # actual elapsed time
            expected = len(data) / rt  # expected elapsed time

            if actual < expected:
                # sleep if less time elapsed than expected
                time.sleep(expected - actual)
                t1 = time.time()
            else:
                t1 = t2

    def _find_extension(self, response):
        """Get filename extension from MIME type"""
        mtype = response.headers.get("Content-Type", "image/jpeg")
        mtype = mtype.partition(";")[0]

        if "/" not in mtype:
            mtype = "image/" + mtype

        if mtype in MIME_TYPES:
            return MIME_TYPES[mtype]

        ext = mimetypes.guess_extension(mtype, strict=False)
        if ext:
            return ext[1:]

        self.log.warning("Unknown MIME type '%s'", mtype)
        return "bin"

    @staticmethod
    def _adjust_extension(pathfmt, file_header):
        """Check filename extension against file header"""
        sig = FILE_SIGNATURES[pathfmt.extension]
        if not file_header.startswith(sig):
            for ext, sig in FILE_SIGNATURES.items():
                if file_header.startswith(sig):
                    pathfmt.set_extension(ext)
                    return True
        return False


MIME_TYPES = {
    "image/jpeg"    : "jpg",
    "image/jpg"     : "jpg",
    "image/png"     : "png",
    "image/gif"     : "gif",
    "image/bmp"     : "bmp",
    "image/x-bmp"   : "bmp",
    "image/x-ms-bmp": "bmp",
    "image/webp"    : "webp",
    "image/svg+xml" : "svg",
    "image/ico"     : "ico",
    "image/icon"    : "ico",
    "image/x-icon"  : "ico",
    "image/vnd.microsoft.icon" : "ico",
    "image/x-photoshop"        : "psd",
    "application/x-photoshop"  : "psd",
    "image/vnd.adobe.photoshop": "psd",

    "video/webm": "webm",
    "video/ogg" : "ogg",
    "video/mp4" : "mp4",

    "audio/wav"  : "wav",
    "audio/x-wav": "wav",
    "audio/webm" : "webm",
    "audio/ogg"  : "ogg",
    "audio/mpeg" : "mp3",

    "application/zip"  : "zip",
    "application/x-zip": "zip",
    "application/x-zip-compressed": "zip",
    "application/rar"  : "rar",
    "application/x-rar": "rar",
    "application/x-rar-compressed": "rar",
    "application/x-7z-compressed" : "7z",

    "application/pdf"  : "pdf",
    "application/x-pdf": "pdf",
    "application/x-shockwave-flash": "swf",

    "application/ogg": "ogg",
    "application/octet-stream": "bin",
}

# https://en.wikipedia.org/wiki/List_of_file_signatures
FILE_SIGNATURES = {
    "jpg" : b"\xFF\xD8\xFF",
    "png" : b"\x89PNG\r\n\x1A\n",
    "gif" : (b"GIF87a", b"GIF89a"),
    "bmp" : b"BM",
    "webp": b"RIFF",
    "svg" : b"<?xml",
    "ico" : b"\x00\x00\x01\x00",
    "cur" : b"\x00\x00\x02\x00",
    "psd" : b"8BPS",
    "webm": b"\x1A\x45\xDF\xA3",
    "ogg" : b"OggS",
    "wav" : b"RIFF",
    "mp3" : (b"\xFF\xFB", b"\xFF\xF3", b"\xFF\xF2", b"ID3"),
    "zip" : (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    "rar" : b"\x52\x61\x72\x21\x1A\x07",
    "7z"  : b"\x37\x7A\xBC\xAF\x27\x1C",
    "pdf" : b"%PDF-",
    "swf" : (b"CWS", b"FWS"),
    # check 'bin' files against all other file signatures
    "bin" : b"\x00\x00\x00\x00\x00\x00\x00\x00",
}

__downloader__ = HttpDownloader

# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os
import time
import logging
from .. import config, util, exception
from requests.exceptions import RequestException
from ssl import SSLError


class DownloaderBase():
    """Base class for downloaders"""
    scheme = ""
    retries = 1

    def __init__(self, extractor, output):
        self.session = extractor.session
        self.out = output
        self.log = logging.getLogger("downloader." + self.scheme)
        self.downloading = False
        self.part = self.config("part", True)
        self.partdir = self.config("part-directory")

        if self.partdir:
            self.partdir = util.expand_path(self.partdir)
            os.makedirs(self.partdir, exist_ok=True)

    def config(self, key, default=None):
        """Interpolate config value for 'key'"""
        return config.interpolate(("downloader", self.scheme, key), default)

    def download(self, url, pathfmt):
        """Download the resource at 'url' and write it to a file-like object"""
        try:
            return self.download_impl(url, pathfmt)
        except Exception:
            print()
            raise
        finally:
            # remove file from incomplete downloads
            if self.downloading and not self.part:
                try:
                    os.remove(pathfmt.temppath)
                except (OSError, AttributeError):
                    pass

    def download_impl(self, url, pathfmt):
        """Actual implementaion of the download process"""
        adj_ext = None
        tries = 0
        msg = ""

        if self.part:
            pathfmt.part_enable(self.partdir)

        while True:
            self.reset()
            if tries:
                self.log.warning("%s (%d/%d)", msg, tries, self.retries)
                if tries >= self.retries:
                    return False
                time.sleep(tries)
            tries += 1

            # check for .part file
            filesize = pathfmt.part_size()

            # connect to (remote) source
            try:
                offset, size = self.connect(url, filesize)
            except exception.DownloadRetry as exc:
                msg = exc
                continue
            except exception.DownloadComplete:
                break
            except Exception as exc:
                self.log.warning(exc)
                return False

            # check response
            if not offset:
                mode = "w+b"
                if filesize:
                    self.log.info("Unable to resume partial download")
            else:
                mode = "r+b"
                self.log.info("Resuming download at byte %d", offset)

            # set missing filename extension
            if not pathfmt.has_extension:
                pathfmt.set_extension(self.get_extension())
                if pathfmt.exists():
                    pathfmt.temppath = ""
                    return True

            self.out.start(pathfmt.path)
            self.downloading = True
            with pathfmt.open(mode) as file:
                if offset:
                    file.seek(offset)

                # download content
                try:
                    self.receive(file)
                except (RequestException, SSLError) as exc:
                    msg = exc
                    print()
                    continue

                # check filesize
                if size and file.tell() < size:
                    msg = "filesize mismatch ({} < {})".format(
                        file.tell(), size)
                    continue

                # check filename extension
                adj_ext = self._check_extension(file, pathfmt)

            break

        self.downloading = False
        if adj_ext:
            pathfmt.set_extension(adj_ext)
        return True

    def connect(self, url, offset):
        """Connect to 'url' while respecting 'offset' if possible

        Returns a 2-tuple containing the actual offset and expected filesize.
        If the returned offset-value is greater than zero, all received data
        will be appended to the existing .part file.
        Return '0' as second tuple-field to indicate an unknown filesize.
        """

    def receive(self, file):
        """Write data to 'file'"""

    def reset(self):
        """Reset internal state / cleanup"""

    def get_extension(self):
        """Return a filename extension appropriate for the current request"""

    @staticmethod
    def _check_extension(file, pathfmt):
        """Check filename extension against fileheader"""
        extension = pathfmt.keywords["extension"]
        if extension in FILETYPE_CHECK:
            file.seek(0)
            header = file.read(8)
            if len(header) >= 8 and not FILETYPE_CHECK[extension](header):
                for ext, check in FILETYPE_CHECK.items():
                    if ext != extension and check(header):
                        return ext
        return None


FILETYPE_CHECK = {
    "jpg": lambda h: h[0:2] == b"\xff\xd8",
    "png": lambda h: h[0:8] == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a",
    "gif": lambda h: h[0:4] == b"GIF8" and h[5] == 97,
}

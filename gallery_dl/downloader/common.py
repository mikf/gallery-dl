# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os
import os.path
import logging
import time


class DownloaderBase():
    """Base class for downloaders"""
    retries = 1
    mode = "b"

    def __init__(self, session, output):
        self.session = session
        self.out = output
        self.log = logging.getLogger("download")

    def download(self, url, pathfmt):
        """Download the resource at 'url' and write it to a file-like object"""
        tries = 0
        msg = ""

        if not pathfmt.has_extension:
            pathfmt.set_extension("part", False)
            partpath = pathfmt.realpath
        else:
            partpath = pathfmt.realpath + ".part"

        while True:
            if tries:
                self.out.error(pathfmt.path, msg, tries, self.retries)
                if tries >= self.retries:
                    return False
                time.sleep(1)
            tries += 1
            self.reset()

            # check for .part file
            filesize = 0
            if os.path.isfile(partpath):
                try:
                    filesize = os.path.getsize(partpath)
                except OSError:
                    pass

            # connect to (remote) source
            try:
                offset, size = self.connect(url, filesize)
            except Exception as exc:
                msg = exc
                continue

            # check response
            if not offset:
                mode = "w" + self.mode
                if filesize:
                    self.log.info("Unable to resume partial download")
            elif offset == -1:
                break  # early finish
            else:
                mode = "a" + self.mode
                self.log.info("Resuming download at byte %d", offset)

            # set missing filename extension
            if not pathfmt.has_extension:
                pathfmt.set_extension(self.get_extension())
                if pathfmt.exists():
                    self.out.skip(pathfmt.path)
                    return True

            self.out.start(pathfmt.path)
            with open(partpath, mode) as file:
                # download content
                try:
                    self.receive(file)
                except OSError:
                    raise
                except Exception as exc:
                    msg = exc
                    continue

                # check filesize
                if size and file.tell() < size:
                    msg = "filesize mismatch ({} < {})".format(
                        file.tell(), size)
                    continue
            break

        os.rename(partpath, pathfmt.realpath)
        self.out.success(pathfmt.path, tries)
        return True

    def connect(self, url, offset):
        """Connect to 'url' while respecting 'offset' if possible

        Returns a 2-tuple containing the actual offset and expected filesize.
        If the returned offset-value is greater than zero, all received data
        will be appended to the existing .part file. If it is '-1', the
        download will finish early and be considered successfull.
        Return '0' as second tuple-field to indicate an unknown filesize.
        """

    def receive(self, file):
        """Write data to 'file'"""

    def reset(self):
        """Reset internal state / cleanup"""

    def get_extension(self):
        """Return a filename extension appropriate for the current request"""

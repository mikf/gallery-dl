# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys

from .extractor.common import Extractor, Message
from .job import DownloadJob
from . import util, version

REPOS = {
    "stable": "mikf/gallery-dl",
    "dev"   : "gdl-org/builds",
}

BINARIES = {
    "stable": {
        "windows"    : "gallery-dl.exe",
        "windows_x86": "gallery-dl.exe",
        "linux"      : "gallery-dl.bin",
    },
    "dev": {
        "windows"    : "gallery-dl_windows.exe",
        "windows_x86": "gallery-dl_windows_x86.exe",
        "linux"      : "gallery-dl_ubuntu",
        "macos"      : "gallery-dl_macos",
    },
}


class UpdateJob(DownloadJob):

    def handle_url(self, url, kwdict):
        if not url:
            self.extractor.log.info("Up to date (%s)", version.__version__)
            return

        self.extractor.log.info(
            "Updating from %s to %s",
            version.__version__, kwdict["tag_name"])

        path_old = sys.executable + ".old"
        path_new = sys.executable + ".new"
        directory, filename = os.path.split(sys.executable)

        pathfmt = self.pathfmt
        pathfmt.extension = "new"
        pathfmt.filename = filename
        pathfmt.temppath = path_new
        pathfmt.realpath = pathfmt.path = sys.executable
        pathfmt.realdirectory = pathfmt.directory = directory

        self._newline = True
        if not self.download(url):
            self.status |= 4
            return self._error("Failed to download %s", filename or url)

        if not util.WINDOWS:
            try:
                mask = os.stat(sys.executable).st_mode
            except OSError:
                mask = 0o755
                self._warning("Unable to get file permission bits")

        try:
            os.replace(sys.executable, path_old)
        except OSError:
            return self._error("Unable to move current executable")

        try:
            pathfmt.finalize()
        except OSError:
            self._error("Unable to overwrite current executable")
            return os.replace(path_old, sys.executable)

        if util.WINDOWS:
            import atexit
            import subprocess

            cmd = 'ping 127.0.0.1 -n 5 -w 1000 & del /F "{}"'.format(path_old)
            atexit.register(
                util.Popen, cmd, shell=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )

        else:
            try:
                os.unlink(path_old)
            except OSError:
                self._warning("Unable to delete old executable")

            try:
                os.chmod(sys.executable, mask)
            except OSError:
                self._warning("Unable to restore file permission bits")

        self.out.success(pathfmt.path)

    def _warning(self, msg, *args):
        if self._newline:
            self._newline = False
            print()
        self.extractor.log.warning(msg, *args)

    def _error(self, msg, *args):
        if self._newline:
            self._newline = False
            print()
        self.status |= 1
        self.extractor.log.error(msg, *args)


class UpdateExtractor(Extractor):
    category = "update"
    root = "https://github.com"
    root_api = "https://api.github.com"
    pattern = r"update(?:(.+))?"

    def items(self):
        repo, _, binary = version.__variant__.partition("/")
        tag = "latest"

        url = "{}/repos/{}/releases/{}".format(
            self.root_api, REPOS[repo], tag)
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": util.USERAGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        data = self.request(url, headers=headers).json()

        yield Message.Directory, data

        tag = data["tag_name"]
        url = "{}/{}/releases/download/{}/{}".format(
            self.root, REPOS[repo], tag, BINARIES[repo][binary])

        if tag[0] == "v":
            data["tag_name"] = tag = tag[1:]
            if tag == version.__version__:
                url = ""
        else:
            if version.__version__.endswith(":" + tag):
                url = ""

        yield Message.Url, url, data

# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import re
import sys

from .extractor.common import Extractor, Message
from .job import DownloadJob
from . import util, version, output, exception

REPOS = {
    "stable" : "mikf/gallery-dl",
    "dev"    : "gdl-org/builds",
    "nightly": "gdl-org/builds",
    "master" : "gdl-org/builds",
}

BINARIES_STABLE = {
    "windows"    : "gallery-dl.exe",
    "windows_x64": "gallery-dl.exe",
    "windows_x86": "gallery-dl_x86.exe",
    "linux"      : "gallery-dl.bin",
}
BINARIES_DEV = {
    "windows"    : "gallery-dl_windows.exe",
    "windows_x64": "gallery-dl_windows.exe",
    "windows_x86": "gallery-dl_windows_x86.exe",
    "linux"      : "gallery-dl_linux",
    "macos"      : "gallery-dl_macos",
}
BINARIES = {
    "stable" : BINARIES_STABLE,
    "dev"    : BINARIES_DEV,
    "nightly": BINARIES_DEV,
    "master" : BINARIES_DEV,
}


class UpdateJob(DownloadJob):

    def handle_url(self, url, kwdict):
        if not self._check_update(kwdict):
            if kwdict["_check"]:
                self.status |= 1
            return self.extractor.log.info(
                "gallery-dl is up to date (%s)", version.__version__)

        if kwdict["_check"]:
            return self.extractor.log.info(
                "A new release is available: %s -> %s",
                version.__version__, kwdict["tag_name"])

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
            return self._error("Failed to download %s", url.rpartition("/")[2])

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

    def _check_update(self, kwdict):
        if kwdict["_exact"]:
            return True

        tag = kwdict["tag_name"]

        if tag[0] == "v":
            kwdict["tag_name"] = tag = tag[1:]
            ver, _, dev = version.__version__.partition("-")

            version_local = [int(v) for v in ver.split(".")]
            version_remote = [int(v) for v in tag.split(".")]

            if dev:
                version_local[-1] -= 0.5
            if version_local >= version_remote:
                return False

        elif version.__version__.endswith(":" + tag):
            return False

        return True

    def _warning(self, msg, *args):
        if self._newline:
            self._newline = False
            output.stderr_write("\n")
        self.extractor.log.warning(msg, *args)

    def _error(self, msg, *args):
        if self._newline:
            self._newline = False
            output.stderr_write("\n")
        self.status |= 1
        self.extractor.log.error(msg, *args)


class UpdateExtractor(Extractor):
    category = "update"
    root = "https://github.com"
    root_api = "https://api.github.com"
    pattern = r"update(?::(.+))?"

    def items(self):
        tag = "latest"
        check = exact = False

        variant = version.__variant__ or "stable/windows"
        repo, _, binary = variant.partition("/")

        target = self.groups[0]
        if target == "latest":
            pass
        elif target == "check":
            check = True
        else:
            channel, sep, target = target.partition("@")
            if sep:
                repo = channel
                tag = target
                exact = True
            elif channel in REPOS:
                repo = channel
            else:
                tag = channel
                exact = True

            if re.match(r"\d\.\d+\.\d+", tag):
                tag = "v" + tag

        try:
            path_repo = REPOS[repo or "stable"]
        except KeyError:
            raise exception.StopExtraction("Invalid channel '%s'", repo)

        path_tag = tag if tag == "latest" else "tags/" + tag
        url = "{}/repos/{}/releases/{}".format(
            self.root_api, path_repo, path_tag)
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": util.USERAGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        data = self.request(url, headers=headers, notfound="tag").json()
        data["_check"] = check
        data["_exact"] = exact

        if binary == "linux" and \
                repo != "stable" and \
                data["tag_name"] <= "2024.05.28":
            binary_name = "gallery-dl_ubuntu"
        else:
            binary_name = BINARIES[repo][binary]

        url = "{}/{}/releases/download/{}/{}".format(
            self.root, path_repo, data["tag_name"], binary_name)

        yield Message.Directory, data
        yield Message.Url, url, data

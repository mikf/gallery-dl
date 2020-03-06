#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build a standalone executable using PyInstaller"""

import PyInstaller.__main__
import util
import os

PyInstaller.__main__.run([
    "--onefile",
    "--console",
    "--name", "gallery-dl." + ("exe" if os.name == "nt" else "bin"),
    "--additional-hooks-dir", util.path("scripts"),
    "--distpath", util.path("dist"),
    "--workpath", util.path("build"),
    "--specpath", util.path("build"),
    util.path("gallery_dl", "__main__.py"),
])

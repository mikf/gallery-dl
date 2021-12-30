# -*- coding: utf-8 -*-

from gallery_dl import extractor, downloader, postprocessor

hiddenimports = [
    package.__name__ + "." + module
    for package in (extractor, downloader, postprocessor)
    for module in package.modules
]

hiddenimports.append("yt_dlp")

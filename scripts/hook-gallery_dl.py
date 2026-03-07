# -*- coding: utf-8 -*-

from gallery_dl import extractor, downloader, postprocessor

hiddenimports = [
    package.__name__ + "." + module
    for package in (extractor, downloader, postprocessor)
    for module in package.modules
]

hiddenimports.append("yt_dlp")
hiddenimports.append("81d243bd2c585b0f4821__mypyc")

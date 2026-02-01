# -*- coding: utf-8 -*-

from gallery_dl import extractor, downloader, postprocessor
import os

hiddenimports = [
    f"{package.__name__}.{module}"
    for package in (extractor, downloader, postprocessor)
    for module in package.modules
]

base = extractor.__name__ + ".utils."
path = os.path.join(extractor.__path__[0], "utils")
hiddenimports.extend(
    base + file[:-3]
    for file in os.listdir(path)
    if not file.startswith("__")
)

hiddenimports.append("yt_dlp")

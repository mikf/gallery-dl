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

mypyc = "81d243bd2c585b0f4821__mypyc"
try:
    from importlib.metadata import files
    for file in files("charset_normalizer"):
        if "__mypyc" in file.name:
            mypyc = file.name.partition(".")[0]
            break
except Exception:
    pass
hiddenimports.append(mypyc)

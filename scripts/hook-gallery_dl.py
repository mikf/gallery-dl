# -*- coding: utf-8 -*-

from gallery_dl import extractor, downloader, postprocessor

hiddenimports = [
    package.__name__ + "." + module
    for package in (extractor, downloader, postprocessor)
    for module in package.modules
]

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

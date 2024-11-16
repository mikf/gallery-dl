from gallery_dl import downloader
from gallery_dl import extractor
from gallery_dl import postprocessor

hiddenimports = [
    package.__name__ + "." + module
    for package in (extractor, downloader, postprocessor)
    for module in package.modules
]

hiddenimports.append("yt_dlp")

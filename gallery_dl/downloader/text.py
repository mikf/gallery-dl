from .common import BasicDownloader

class Downloader(BasicDownloader):

    def __init__(self, extr):
        BasicDownloader.__init__(self)

    def download_impl(self, url, file):
        file.write(bytes(url[7:], "utf-8"))
        return 0

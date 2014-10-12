import os
import sys
import importlib

class DownloadManager():

    def __init__(self, opts, conf):
        self.opts = opts
        self.conf = conf
        self.downloaders = {}

    def add(self, extr):
        if self.opts.dest:
            dest = self.opts.dest
        elif extr.category in self.conf:
            dest = self.conf[extr.category].get("destination", "/tmp/")
        else:
            dest = self.conf["general"].get("destination", "/tmp/")
        dest = os.path.join(dest, extr.category, extr.directory)
        os.makedirs(dest, exist_ok=True)

        for url, filename in extr:
            path = os.path.join(dest, filename)
            if os.path.exists(path):
                self.print_skip(path)
                continue
            dl = self.get_downloader(extr, url)
            self.print_start(path)
            tries = dl.download(url, path)
            self.print_success(path, tries)

    def get_downloader(self, extr, url):
        end   = url.find("://")
        proto = url[:end] if end != -1 else "http"
        if proto not in self.downloaders:
            # import downloader
            module = importlib.import_module("."+proto, __package__)
            self.downloaders[proto] = module.Downloader
        return self.downloaders[proto](extr)

    @staticmethod
    def print_start(path):
        print(path, end="")
        sys.stdout.flush()

    @staticmethod
    def print_skip(path):
        print("\033[2m", path, "\033[0m", sep="")

    @staticmethod
    def print_success(path, tries):
        if tries == 0:
            print("\r", end="")
        print("\r\033[1;32m", path, "\033[0m", sep="")

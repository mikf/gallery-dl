from .common import BasicDownloader
import time
import requests

class Downloader(BasicDownloader):

    def __init__(self, extr):
        BasicDownloader.__init__(self)
        self.session = extr.session

    def download_impl(self, url, file):
        tries = 0
        while True:
            # try to connect to remote source
            try:
                response = self.session.get(url, stream=True, verify=True)
            except requests.exceptions.ConnectionError as e:
                tries += 1
                self.print_error(file, e, tries, self.max_tries)
                time.sleep(1)
                if tries == self.max_tries:
                    raise
                continue

            # reject error-status-codes
            if response.status_code != requests.codes.ok:
                tries += 1
                self.print_error(file, 'HTTP status "{} {}"'.format(
                    response.status_code, response.reason), tries, self.max_tries)
                if response.status_code == 404:
                    return self.max_tries
                time.sleep(1)
                if tries == 5:
                    response.raise_for_status()
                continue

            # everything ok -- proceed to download
            break

        for data in response.iter_content(16384):
            file.write(data)
        return tries

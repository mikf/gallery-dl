from .common import AsyncExtractor
from ..util import filename_from_url
import xml.etree.ElementTree as ET
import urllib.parse

class BooruExtractor(AsyncExtractor):

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.tags      = urllib.parse.unquote(match.group(1))
        self.category  = "booru"
        self.params    = {"tags": self.tags}
        self.page      = "page"
        self.directory = self.tags.replace("/", "_")

    def images(self):
        self.update_page(reset=True)
        while True:
            root = ET.fromstring(
                self.request(self.api_url, verify=True, params=self.params).text
            )
            if len(root) == 0:
                return
            for item in root:
                url  = item.attrib["file_url"]
                name = "{}_{}".format(self.category, filename_from_url(url))
                yield url, name
            self.update_page()

    def update_page(self, reset=False):
        # Override this method in derived classes if necessary.
        # It is usually enough to adjust the 'page' attribute
        if reset is False:
            self.params[self.page] += 1
        else:
            self.params[self.page]  = 1

class Extractor(BooruExtractor):

    def __init__(self, match, config):
        BooruExtractor.__init__(self, match, config)
        self.category = "gelbooru"
        self.api_url  = "http://gelbooru.com/"
        self.params   = {"page":"dapi", "s":"post", "q":"index", "tags":self.tags}

    def update_page(self, reset=False):
        if reset is False:
            self.params["pid"] += 1
        else:
            self.params["pid"]  = 0

from .common import AsyncExtractor
from ..util import filename_from_url
import xml.etree.ElementTree as ET
import json
import urllib.parse

class BooruExtractor(AsyncExtractor):

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.tags      = urllib.parse.unquote(match.group(1))
        self.category  = "booru"
        self.params    = {"tags": self.tags}
        self.page      = "page"
        self.directory = self.tags.replace("/", "_")

    def update_page(self, reset=False):
        # Override this method in derived classes if necessary.
        # It is usually enough to adjust the 'page' attribute
        if reset is False:
            self.params[self.page] += 1
        else:
            self.params[self.page]  = 1

class JSONBooruExtractor(BooruExtractor):

    def images(self):
        self.update_page(reset=True)
        while True:
            images = json.loads(
                self.request(self.api_url, verify=True, params=self.params).text
            )
            if len(images) == 0:
                return
            for img in images:
                url  = urllib.parse.urljoin(self.api_url, img["file_url"])
                name = "{}_{}".format(self.category, filename_from_url(url))
                yield url, name
            self.update_page()

class XMLBooruExtractor(BooruExtractor):

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

class Extractor(JSONBooruExtractor):

    def __init__(self, match, config):
        JSONBooruExtractor.__init__(self, match, config)
        self.category = "danbooru"
        self.api_url  = "https://danbooru.donmai.us/posts.json"

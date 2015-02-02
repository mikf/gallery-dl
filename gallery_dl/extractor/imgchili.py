from .common import BasicExtractor
from ..util import filename_from_url
import re

class Extractor(BasicExtractor):

    def __init__(self, match, config):
        BasicExtractor.__init__(self, config)
        self.url  = match.group(0)
        self.page = self.request(self.url).text;
        self.category = "imgchili"

        title = self.get_title()
        pos   = self.url.rindex("/")
        self.directory = title + " - " + self.url[pos+1:]

    def images(self):
        pattern = r' src="http://t(\d+\.imgchili.net/[^"]+)"'
        for match in re.finditer(pattern, self.page):
            url = "http://i" + match.group(1)
            yield url, filename_from_url(url)

    def get_title(self):
        return self.extract(self.page, "<h1>", "</h1>")[0]

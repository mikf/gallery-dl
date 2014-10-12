from .common import AsyncExtractor
from ..util import filename_from_url

class Extractor(AsyncExtractor):

    url = "https://chan.sankakucomplex.com/"

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.tags      = match.group(1)
        self.category  = "sankaku"
        self.directory = self.tags.replace("/", "_")
        self.enable_useragent()

    def images(self):
        needle = ' src="//c.sankakucomplex.com/data/preview/'
        params = {"tags": self.tags, "page":1}
        while True:
            text  = self.request(self.url, params=params).text
            print(text)
            return
            pos   = 0
            found = 0
            while True:
                try:
                    url, pos = self.extract(text, needle, '"', pos)
                    found += 1
                    print("https://cs.sankakucomplex.com/data/" + url)
                    yield ("https://cs.sankakucomplex.com/data/" + url,
                           "%s_%s" % (self.category, filename_from_url(url)))
                except:
                    break
            if found == 0:
                break
            params["page"] += 1

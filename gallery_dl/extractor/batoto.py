from .common import AsyncExtractor
from ..util import filename_from_url
from urllib.parse import unquote

class Extractor(AsyncExtractor):

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.url = "https://bato.to/read/_/" + match.group(1) + "/_/1"
        self.category = "batoto"
        self.directory = match.group(1)

    def images(self):
        next_url = self.url
        while next_url:
            text = self.request(next_url).text
            pos  = text.find('<div id="full_image"')

            next_url, pos = self.extract(text, '<a href="', '"', pos)
            url, pos = self.extract(text, 'src="', '"', pos)
            name = unquote( filename_from_url(url) )
            yield url, name

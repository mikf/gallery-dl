from .gelbooru import BooruExtractor

class Extractor(BooruExtractor):

    def __init__(self, match, config):
        BooruExtractor.__init__(self, match, config)
        self.category = "e621"
        self.api_url  = "https://e621.net/post/index.xml"

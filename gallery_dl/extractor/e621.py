from .danbooru import JSONBooruExtractor

class Extractor(JSONBooruExtractor):

    def __init__(self, match, config):
        JSONBooruExtractor.__init__(self, match, config)
        self.category = "e621"
        self.api_url  = "https://e621.net/post/index.json"

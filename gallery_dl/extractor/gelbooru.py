from .danbooru import XMLBooruExtractor

class Extractor(XMLBooruExtractor):

    def __init__(self, match, config):
        XMLBooruExtractor.__init__(self, match, config)
        self.category = "gelbooru"
        self.api_url  = "http://gelbooru.com/"
        self.params   = {"page":"dapi", "s":"post", "q":"index", "tags":self.tags}

    def update_page(self, reset=False):
        if reset is False:
            self.params["pid"] += 1
        else:
            self.params["pid"]  = 0

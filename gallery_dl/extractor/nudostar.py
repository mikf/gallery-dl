# -*- coding: utf-8 -*-


from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?nudostar\.tv"

class NudostarExtractor(Extractor):
    category = "nudostar"
    pattern = BASE_PATTERN
    # sampleurl = "https://nudostar.tv/models/megan-bitchell/343/"

    def items(self):
        url = text.ensure_http_scheme(self.url)
        data = text.nameext_from_url(url, {"url": url})
        print(f'*** Debug:: Data is {data}')
        yield Message.Directory, data
        yield Message.Url, url, data
        
        
        
        
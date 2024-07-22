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
        page = self.request(text.ensure_http_scheme(url)).text
        self.log.debug(f"Variable url is currently set to {url}")
        
        testtext = text.extract(page, '<div class="block-video"', '#343">')
        self.log.debug(f"Text extracted is {testtext}")
    
        extractedfurther = text.extract(testtext, '<img src=', 'alt=')
        self.log.debug(f"extractedfurther is {extractedfurther}")

        html_removed = text.remove_html(testtext)
        self.log.debug(f"Text html_removed is {html_removed}")

        data = text.nameext_from_url(url, {"url": url})
        self.log.debug(f"Data is {data}")


        yield Message.Directory, data
        yield Message.Url, url, data
        
        
        
        
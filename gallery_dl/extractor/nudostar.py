# -*- coding: utf-8 -*-


from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?nudostar\.tv"

class NudostarExtractor(Extractor):
    category = "nudostar"
    pattern = BASE_PATTERN + r"/models/([^&#/]+)*/(\w*)/"
    # sampleurl = "https://nudostar.tv/models/megan-bitchell/343/"

    def items(self):
        url = text.ensure_http_scheme(self.url)

      <img src = ("https://nudostar.tv/contents/"

                  "l/e/leena-1/1000/leena-1_0107.jpg")

        yield Message.Directory, data
        yield Message.Url, url, data




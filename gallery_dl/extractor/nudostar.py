# -*- coding: utf-8 -*-


from .common import Extractor, Message, GalleryExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?nudostar\.tv"


class NudostarGalleryExtractor(GalleryExtractor):
    """Extractor for Nudostar albums"""
    category = "nudostar"
    pattern = BASE_PATTERN + r"/models/([^&#/]+)*/"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{gallery_id}")

    def __init__(self, match):
        url = match.group(0)

        ## Stopped here - Need to figure out how to get unique pages from here.

        GalleryExtractor.__init__(self, match, url)




class _NudostarExtractor(Extractor):
    """Extractor for Nudostar Images"""
    category = "nudostar"
    directory_fmt = ("{category}", "{user_id}")
    pattern = BASE_PATTERN + r"/models/([^&#/]+)*/(\w*)/"

    # sampleurl = "https://nudostar.tv/models/megan-bitchell/343/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id, self.image_id = match.groups()

    def items(self):
        pagetext = self.request(self.url, notfound=self.subcategory).text

        url_regex = r'<a href=\"https://nudostar\.tv/models/[^&#]+\s+<img src=\"([^&\"]+)\"'

        match = re.search(url_regex, pagetext)
        imageURL = match.group(1)
        data = text.nameext_from_url(imageURL, {"url": imageURL})
        data["extension"] = text.ext_from_url(imageURL)
        data["filename"] = self.user_id + '-' + self.image_id
        data["user_id"] = self.user_id

        yield Message.Directory, data
        yield Message.Url, imageURL, data

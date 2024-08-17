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
        self.root = text.root_from_url(match.group(0))
        self.gallery_url = match.group(0)
        print(f"Gallery URL detected; Attempting to access {self.gallery_url} with root {self.root}")
        GalleryExtractor.__init__(self, match, self.gallery_url)


    def metadata(self, page):
        """Return a dict with general metadata about the Gallery

        This gets called by this line in GalleryExtractor:
            data = self.metadata(page)
        """
        pass

    def images(self, page):
        """Return a list of all (image-url, metadata)-tuples

        This gets called by this line in GalleryExtractor:
            imgs = self.images(page)
        """
        urllist = []
        url_pattern = re.compile(BASE_PATTERN + r"/models/([^&#/]+)*/(\w*)/")
        for match in url_pattern.finditer(page):
            url = match.group(1)
            urllist.append(url)
        return [(image, None) for image in urllist]


class _NudostarExtractor(Extractor):
    """Extractor for Nudostar Images"""
    category = "nudostar"
    directory_fmt = ("{category}", "{user_id}")
    pattern = BASE_PATTERN + r"/models/([^&#/]+)*/(\w*)/"
    # sampleurl = "https://nudostar.tv/models/megan-bitchell/343/"

    def __init__(self, match):
        self.log.debug("Initializing NudostarExtractor Class")
        Extractor.__init__(self, match)
        self.user_id, self.image_id = match.groups()

    def items(self):
        """Return a list of all (image-url, metadata)-tuples"""
        pagetext = self.request(self.url, notfound=self.subcategory).text
        self.log.debug(f"Image page URL detected - accessing  {self.url}")
        url_regex = r'<a href=\"https://nudostar\.tv/models/[^&#]+\s+<img src=\"([^&\"]+)\"'
        match = re.search(url_regex, pagetext)
        imageURL = match.group(1)
        data = text.nameext_from_url(imageURL, {"url": imageURL})
        data["extension"] = text.ext_from_url(imageURL)
        data["filename"] = self.user_id + '-' + self.image_id
        data["user_id"] = self.user_id

        self.log.debug(f"Image matched. Attempting to download {data}")

        yield Message.Directory, data
        yield Message.Url, imageURL, data

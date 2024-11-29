# -*- coding: utf-8 -*-
from .common import Extractor, Message, GalleryExtractor
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?nudostar\.tv"


class NudostarGalleryExtractor(GalleryExtractor):
    """Extractor for Nudostar albums"""
    pattern = BASE_PATTERN + r"/models/([\w-]*)/$"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        self.gallery_url = match.group(0)
        print(f"Gallery URL detected; Attempting to access {self.gallery_url} with root {self.root}")
        GalleryExtractor.__init__(self, match, self.gallery_url)

    def images(self, page):
        """Return a list of all (image-url, None) tuples"""
        urllist = []
        for image_page_url in text.extract_iter(page, '<div class="item">', 'title='):
            page_url = text.extract(image_page_url, '="', '"')[0]
            # Create a match object for the image extractor
            image_match = re.match(NudostarExtractor.pattern, page_url)
            if image_match:
                # Create an instance of the image extractor
                image_extractor = NudostarExtractor(image_match)
                # Get the items from the extractor
                for message_type, url, metadata in image_extractor.items():
                    if message_type == Message.Url:
                        urllist.append((url, metadata))
                        break  # We only want the first URL from each page

        print(f"URL List is {urllist}")
        return urllist

    def metadata(self, page):
        """Return metadata dictionary"""
        model = self.gallery_url.split("/models/")[1].split("/")[0]
        return {
            "gallery_id": model,
            "title": model,
        }


class NudostarExtractor(Extractor):
    """Extractor for Nudostar Images"""
    category = "nudostar"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{filename}.{extension}"
    pattern = BASE_PATTERN + r"/models/([^&#/]+)*/(\w*)/"
    # sampleurl = "https://nudostar.tv/models/megan-bitchell/343/"

    # TODO: page head/title has some good metadata for alternate names?

    def __init__(self, match):
        print("Initializing NudostarExtractor Class")
        Extractor.__init__(self, match)
        self.user_id, self.image_id = match.groups()

    def items(self):
        """Return a list of all (image-url, metadata)-tuples"""
        pagetext = self.request(self.url, notfound=self.subcategory).text
        print(f"Image page URL detected - accessing  {self.url}")
        url_regex = r'<a href=\"https://nudostar\.tv/models/[^&#]+\s+<img src=\"([^&\"]+)\"'
        match = re.search(url_regex, pagetext)
        imageURL = match.group(1)
        data = text.nameext_from_url(imageURL, {"url": imageURL})
        data["extension"] = text.ext_from_url(imageURL)
        data["filename"] = self.user_id + '-' + self.image_id
        data["user_id"] = self.user_id

        print(f"Image matched. Attempting to download {data}")

        yield Message.Directory, data
        yield Message.Url, imageURL, data

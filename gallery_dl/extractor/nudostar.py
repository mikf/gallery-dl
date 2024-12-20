# -*- coding: utf-8 -*-
import re
from .common import Extractor, Message, GalleryExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?nudostar\.tv"


class NudostarGalleryExtractor(GalleryExtractor):
    """Extractor for Nudostar albums"""
    category = "nudostar"
    pattern = BASE_PATTERN + r"/models/([\w-]*)/$"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{filename}.{extension}"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        self.gallery_url = match.group(0)
        GalleryExtractor.__init__(self, match, self.gallery_url)

    def images(self, page):
        """Return a list of all (image-url, None) tuples"""
        url_list = []
        while True:  # Loop to handle all pages
            # Process current page's images
            for image_page_url in text.extract_iter(
                    page, '<div class="item">', 'title='):
                page_url = text.extract(image_page_url, '="', '"')[0]
                # Create a match object for the image extractor
                image_match = re.match(NudostarExtractor.pattern, page_url)
                if image_match:
                    # Create an instance of the image extractor
                    image_extractor = NudostarExtractor(image_match)
                    image_extractor.session = self.session  # Share our session
                    image_extractor.initialize()  # Initialize the extractor
                    # Get the items from the extractor
                    for item in image_extractor.items():
                        if item[0] == Message.Url:
                            message_type, url, metadata = item
                            url_list.append((url, metadata))
                            break  # We only want the first URL from each page

            # Look for next page
            next_page = text.extract(
                page, '<li class="next"><a href="', '"')[0]
            if not next_page:
                break  # No more pages

            # Get the next page's content
            page = self.request(next_page).text
        return url_list

    def metadata(self, page):
        """Return metadata dictionary"""
        model = self.gallery_url.split("/models/")[1].split("/")[0]
        return {
            "gallery_id": model,
            "title": model,
            "user_id": model,
        }


class NudostarExtractor(Extractor):
    """Extractor for Nudostar Images"""
    category = "nudostar"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{filename}.{extension}"
    pattern = (
        BASE_PATTERN +
        r"/models/([^&#/]+)*/(\w*)/"
    )
    # Sample URL: "https://nudostar.tv/models/megan-bitchell/343/"

    # TODO: page head/title has some good metadata for alternate names?

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id, self.image_id = match.groups()

    def items(self):
        """Return a list of all (image-url, metadata)-tuples"""
        pagetext = self.request(self.url, notfound=self.subcategory).text
        url_regex = (
            r'<a href=\"https://nudostar\.tv/models/[^&#]+'
            r'\s+<img src=\"([^&\"]+)\"'
        )
        match = re.search(url_regex, pagetext)
        image_url = match.group(1)
        data = text.nameext_from_url(image_url, {"url": image_url})
        data["extension"] = text.ext_from_url(image_url)
        data["filename"] = f"{self.user_id}-{self.image_id}"
        data["user_id"] = self.user_id

        yield Message.Directory, data
        yield Message.Url, image_url, data

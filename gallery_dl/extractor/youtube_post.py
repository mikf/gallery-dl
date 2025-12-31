# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://www.youtube.com/ community posts"""

from .common import Extractor, Message
from .. import util


class YoutubePostExtractor(Extractor):
    """Extractor for YouTube community posts"""

    category = "youtube"
    subcategory = "post"
    root = "https://www.youtube.com"
    directory_fmt = ("{category}",)
    filename_fmt = "{post_id}_{num}.{extension}"
    archive_fmt = "{post_id}_{num}"
    pattern = r"(?:https?://)?(?:www\.)?youtube\.com/post/(?P<post_id>[A-Za-z0-9_-]+)"
    example = "https://www.youtube.com/post/aB9_-Q3bT71kP2fGx8LmN3sR0YcUdVeWqZ5-"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.post_id = match.group("post_id")

    def items(self):
        # Start with version message
        yield Message.Version, 1

        # Make request to the YouTube post URL
        url = f"https://www.youtube.com/post/{self.post_id}"
        response = self.request(url)

        yt_initial_data_re = util.re(R"var ytInitialData = (\{[\s\S]*?\});")
        match = yt_initial_data_re.search(response.text)
        if match is None:
            self.log.warning("No ytInitialData found")
            return

        # For now, just extract basic metadata
        data = {
            "post_id": self.post_id,
            # "uploader": "",
            # "title": "",
            "url": url,
        }

        yield Message.Directory, data

        # Extract ggpht.com image base URLs (up to and incl. '=') from ytInitialData script
        # Example: "url":"https://yt3.ggpht.com/AAAA...=s960-c-fcrop64=1,...."
        # We only keep the stable prefix ending at the first '=' to later append size params
        pattern = util.re(r"https://[^\"'\s]+\.ggpht\.com/[A-Za-z0-9_-]+?=")
        image_urls = pattern.findall(match.group(1))

        # Process each found URL: append s0?imgmax=0 and yield as jobs
        for i, img_url in enumerate(image_urls):
            modified_url = img_url + "s0?imgmax=0"

            img_data = data.copy()
            img_data.update(
                {
                    "num": i,
                    "extension": "",  # will be inferred from URL/MIME
                    "url": modified_url,
                }
            )

            yield Message.Url, modified_url, img_data

# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://twitter.com/"""

from .common import Extractor, Message
from .. import text


class TwitterExtractor(Extractor):
    """Base class for twitter extractors"""
    category = "twitter"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{retweet_id}_{num}"
    root = "https://twitter.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.user = match.group(1)
        self.retweets = self.config("retweets", True)
        self.videos = self.config("videos", False)

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, self.metadata()

        for tweet in self.tweets():
            data = self._data_from_tweet(tweet)
            if not self.retweets and data["retweet_id"]:
                continue

            images = text.extract_iter(
                tweet, 'data-image-url="', '"')
            for data["num"], url in enumerate(images, 1):
                text.nameext_from_url(url, data)
                yield Message.Url, url + ":orig", data

            if self.videos and "-videoContainer" in tweet:
                data["num"] = 1
                url = "ytdl:{}/{}/status/{}".format(
                    self.root, data["user"], data["tweet_id"])
                yield Message.Url, url, data

    def metadata(self):
        """Return general metadata"""
        return {"user": self.user}

    def tweets(self):
        """Yield HTML content of all relevant tweets"""

    @staticmethod
    def _data_from_tweet(tweet):
        data = text.extract_all(tweet, (
            ("tweet_id"  , 'data-tweet-id="'   , '"'),
            ("retweet_id", 'data-retweet-id="' , '"'),
            ("retweeter" , 'data-retweeter="'  , '"'),
            ("user"      , 'data-screen-name="', '"'),
            ("username"  , 'data-name="'       , '"'),
            ("user_id"   , 'data-user-id="'    , '"'),
        ))[0]
        for key in ("tweet_id", "retweet_id", "user_id"):
            data[key] = text.parse_int(data[key])
        data["retweeter"] = data["retweeter"] or ""
        return data

    def _tweets_from_api(self, url):
        params = {
            "include_available_features": "1",
            "include_entities": "1",
            "reset_error_state": "false",
            "lang": "en",
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-Twitter-Active-User": "yes",
            "Referer": "{}/{}".format(self.root, self.user)
        }

        while True:
            data = self.request(url, params=params, headers=headers).json()
            if "inner" in data:
                data = data["inner"]

            for tweet in text.extract_iter(
                    data["items_html"], '<div class="tweet ', '\n</li>'):
                yield tweet

            if not data["has_more_items"]:
                return
            params["max_position"] = text.extract(
                tweet, 'data-tweet-id="', '"')[0]


class TwitterTimelineExtractor(TwitterExtractor):
    """Extractor for all images from a user's timeline"""
    subcategory = "timeline"
    pattern = [r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+)/?$"]
    test = [("https://twitter.com/PicturesEarth", {
        "range": "1-40",
        "url": "2f4d51cbba81e56c1c755677b3ad58fc167c9771",
        "keyword": "cbae53b6f4ba133078bb13c95dbd3cbb4fa40b9f",
    })]

    def tweets(self):
        url = "{}/i/profiles/show/{}/timeline/tweets".format(
            self.root, self.user)
        return self._tweets_from_api(url)


class TwitterMediaExtractor(TwitterExtractor):
    """Extractor for all images from a user's Media Tweets"""
    subcategory = "media"
    pattern = [r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+)/media(?!\w)"]
    test = [("https://twitter.com/PicturesEarth/media", {
        "range": "1-40",
        "url": "2f4d51cbba81e56c1c755677b3ad58fc167c9771",
    })]

    def tweets(self):
        url = "{}/i/profiles/show/{}/media_timeline".format(
            self.root, self.user)
        return self._tweets_from_api(url)


class TwitterTweetExtractor(TwitterExtractor):
    """Extractor for images from individual tweets"""
    subcategory = "tweet"
    pattern = [r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+)/status/(\d+)"]
    test = [
        ("https://twitter.com/PicturesEarth/status/672897688871018500", {
            "url": "d9e68d41301d2fe382eb27711dea28366be03b1a",
            "keyword": "46c8e739a892000848a8a2184da91346c9cbe4bf",
            "content": "a1f2f04cb2d8df24b1afa7a39910afda23484342",
        }),
        ("https://twitter.com/perrypumas/status/894001459754180609", {
            "url": "c8a262a9698cb733fb27870f5a8f75faf77d79f6",
            "keyword": "7729cd3ff16a5647b0b5ffdec9d428c91eedafbe",
        }),
    ]

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        self.tweet_id = match.group(2)

    def metadata(self):
        return {"user": self.user, "tweet_id": self.tweet_id}

    def tweets(self):
        url = "{}/{}/status/{}".format(self.root, self.user, self.tweet_id)
        page = self.request(url).text
        return (text.extract(
            page, '<div class="tweet ', '<ul class="stats')[0],)

# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://twitter.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import re


class TwitterExtractor(Extractor):
    """Base class for twitter extractors"""
    category = "twitter"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{retweet_id}_{num}"
    root = "https://twitter.com"
    sizes = (":orig", ":large", ":medium", ":small")

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.retweets = self.config("retweets", True)
        self.content = self.config("content", False)
        self.videos = self.config("videos", False)

        if self.content:
            self._emoji_sub = re.compile(
                r'<img class="Emoji [^>]+ alt="([^"]+)"[^>]*>').sub

    def items(self):
        self.login()
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
                urls = [url + size for size in self.sizes]
                yield Message.Urllist, urls, data

            if self.videos and "-videoContainer" in tweet:
                data["num"] = 1
                data["extension"] = None
                url = "ytdl:{}/{}/status/{}".format(
                    self.root, data["user"], data["tweet_id"])
                yield Message.Url, url, data

    def metadata(self):
        """Return general metadata"""
        return {"user": self.user}

    def tweets(self):
        """Yield HTML content of all relevant tweets"""

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        page = self.request(self.root + "/login").text
        pos = page.index('name="authenticity_token"')
        token = text.extract(page, 'value="', '"', pos-80)[0]

        url = self.root + "/sessions"
        data = {
            "session[username_or_email]": username,
            "session[password]"         : password,
            "authenticity_token"        : token,
            "ui_metrics"                : '{"rf":{},"s":""}',
            "scribe_log"                : "",
            "redirect_after_login"      : "",
            "remember_me"               : "1",
        }
        response = self.request(url, method="POST", data=data)

        if "/error" in response.url:
            raise exception.AuthenticationError()
        return self.session.cookies

    def _data_from_tweet(self, tweet):
        extr = text.extract_from(tweet)
        data = {
            "tweet_id"  : text.parse_int(extr('data-tweet-id="'  , '"')),
            "retweet_id": text.parse_int(extr('data-retweet-id="', '"')),
            "retweeter" : extr('data-retweeter="'  , '"'),
            "user"      : extr('data-screen-name="', '"'),
            "username"  : extr('data-name="'       , '"'),
            "user_id"   : text.parse_int(extr('data-user-id="'   , '"')),
            "date"      : text.parse_timestamp(extr('data-time="', '"')),
        }
        if self.content:
            content = extr('<div class="js-tweet-text-container">', '\n</div>')
            if '<img class="Emoji ' in content:
                content = self._emoji_sub(r"\1", content)
            content = text.unescape(text.remove_html(content, "", ""))
            cl, _, cr = content.rpartition("pic.twitter.com/")
            data["content"] = cl if cl and len(cr) < 16 else content
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

            position = text.parse_int(text.extract(
                tweet, 'data-tweet-id="', '"')[0])
            if "max_position" in params and position >= params["max_position"]:
                return
            params["max_position"] = position


class TwitterTimelineExtractor(TwitterExtractor):
    """Extractor for all images from a user's timeline"""
    subcategory = "timeline"
    pattern = (r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+)/?(?:$|[?#])")
    test = (
        ("https://twitter.com/supernaturepics", {
            "range": "1-40",
            "url": "0106229d408f4111d9a52c8fd2ad687f64842aa4",
            "keyword": "7210d679606240405e0cf62cbc67596e81a7a250",
        }),
        ("https://mobile.twitter.com/supernaturepics?p=i"),
    )

    def tweets(self):
        url = "{}/i/profiles/show/{}/timeline/tweets".format(
            self.root, self.user)
        return self._tweets_from_api(url)


class TwitterMediaExtractor(TwitterExtractor):
    """Extractor for all images from a user's Media Tweets"""
    subcategory = "media"
    pattern = (r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+)/media(?!\w)")
    test = (
        ("https://twitter.com/supernaturepics/media", {
            "range": "1-40",
            "url": "0106229d408f4111d9a52c8fd2ad687f64842aa4",
        }),
        ("https://mobile.twitter.com/supernaturepics/media#t"),
    )

    def tweets(self):
        url = "{}/i/profiles/show/{}/media_timeline".format(
            self.root, self.user)
        return self._tweets_from_api(url)


class TwitterTweetExtractor(TwitterExtractor):
    """Extractor for images from individual tweets"""
    subcategory = "tweet"
    pattern = (r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+|i/web)/status/(\d+)")
    test = (
        ("https://twitter.com/supernaturepics/status/604341487988576256", {
            "url": "0e801d2f98142dd87c3630ded9e4be4a4d63b580",
            "keyword": "1b8afb93cc04a9f44d89173f8facc61c3a6caf91",
            "content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",
        }),
        # 4 images
        ("https://twitter.com/perrypumas/status/894001459754180609", {
            "url": "c8a262a9698cb733fb27870f5a8f75faf77d79f6",
            "keyword": "43d98ab448193f0d4f30aa571a4b6bda9b6a5692",
        }),
        # video
        ("https://twitter.com/perrypumas/status/1065692031626829824", {
            "options": (("videos", True),),
            "pattern": r"ytdl:https://twitter.com/perrypumas/status/\d+",
        }),
        # content with emoji, newlines, hashtags (#338)
        ("https://twitter.com/yumi_san0112/status/1151144618936823808", {
            "options": (("content", True),),
            "keyword": "b13b6c4cd0b0c15b2ea7685479e7fedde3c47b9e",
        }),
        # Reply to another tweet (#403)
        ("https://twitter.com/tyson_hesse/status/1103767554424598528", {
            "options": (("videos", True),),
            "pattern": r"ytdl:https://twitter.com/.*/1103767554424598528$",
        }),
        # /i/web/ URL
        ("https://twitter.com/i/web/status/1155074198240292865", {
            "pattern": r"https://pbs.twimg.com/media/EAel0vUUYAAZ4Bq.jpg:orig",
        }),
    )

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        self.tweet_id = match.group(2)

    def metadata(self):
        return {"user": self.user, "tweet_id": self.tweet_id}

    def tweets(self):
        self.session.cookies.clear()
        url = "{}/i/web/status/{}".format(self.root, self.tweet_id)
        page = self.request(url).text
        end = page.index('class="js-tweet-stats-container')
        beg = page.rindex('<div class="tweet ', 0, end)
        return (page[beg:end],)

# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Nitter instances"""

from .common import BaseExtractor, Message
from .. import text


class NitterExtractor(BaseExtractor):
    """Base class for nitter extractors"""
    basecategory = "nitter"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{num}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.user = match.group(match.lastindex)

    def items(self):
        for tweet_html in self.tweets():
            tweet = self._tweet_from_html(tweet_html)

            attachments_html = tweet.pop("_attach", "")
            if attachments_html:
                attachments = list(text.extract_iter(
                    attachments_html, 'href="', '"'))
                attachments.extend(text.extract_iter(
                    attachments_html, 'data-url="', '"'))
            else:
                attachments = ()
            tweet["count"] = len(attachments)

            yield Message.Directory, tweet
            for tweet["num"], url in enumerate(attachments, 1):
                if url[0] == "/":
                    url = self.root + url
                if "/video/" in url:
                    url = "ytdl:" + url
                    tweet["filename"] = url.rpartition(
                        "%2F")[2].partition(".")[0]
                    tweet["extension"] = "mp4"
                else:
                    text.nameext_from_url(url, tweet)
                yield Message.Url, url, tweet

    def _tweet_from_html(self, html):
        extr = text.extract_from(html)
        user = {
            "name": extr('class="fullname" href="/', '"'),
            "nick": extr('title="', '"'),
        }
        extr('<span class="tweet-date', '')
        link = extr('href="', '"')
        return {
            "user": user,
            "date": text.parse_datetime(
                extr('title="', '"'), "%b %d, %Y · %I:%M %p %Z"),
            "tweet_id": link.rpartition("/")[2].partition("#")[0],
            "content": extr('class="tweet-content', "</div").partition(">")[2],
            "_attach": extr('class="attachments', 'class="tweet-stats'),
            "comments": text.parse_int(extr(
                'class="icon-comment', '</div>').rpartition(">")[2]),
            "retweets": text.parse_int(extr(
                'class="icon-retweet', '</div>').rpartition(">")[2]),
            "quotes"  : text.parse_int(extr(
                'class="icon-quote', '</div>').rpartition(">")[2]),
            "likes"   : text.parse_int(extr(
                'class="icon-heart', '</div>').rpartition(">")[2]),
        }

    def _pagination(self, path):
        base_url = url = self.root + path

        while True:
            page = self.request(url).text

            yield from page.split('<div class="timeline-item')[1:]

            more = text.extr(page, '<div class="show-more"><a href="?', '"')
            if not more:
                return
            url = base_url + "?" + text.unescape(more)


BASE_PATTERN = NitterExtractor.update({
    "nitter.net": {
        "root": "https://nitter.net",
        "pattern": r"nitter\.net",
    },
    "nitter.lacontrevoie.fr": {
        "root": "https://nitter.lacontrevoie.fr",
        "pattern": r"nitter\.lacontrevoie\.fr",
    },
    "nitter.pussthecat.org": {
        "root": "https://nitter.pussthecat.org",
        "pattern": r"nitter\.pussthecat\.org",
    },
    "nitter.1d4.us": {
        "root": "https://nitter.1d4.us",
        "pattern": r"nitter\.1d4\.us",
    },
    "nitter.kavin.rocks": {
        "root": "https://nitter.kavin.rocks",
        "pattern": r"nitter\.kavin\.rocks",
    },
    "nitter.unixfox.eu": {
        "root": "https://nitter.unixfox.eu",
        "pattern": r"nitter\.unixfox\.eu",
    },
})


class NitterTweetsExtractor(NitterExtractor):
    subcategory = "tweets"
    pattern = BASE_PATTERN + r"/([^/?#]+)(?:/tweets)?(?:$|\?|#)"
    test = (
        ("https://nitter.net/supernaturepics", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
            "count": 20,
            "keyword": {
                "comments": int,
                "content": str,
                "count": 1,
                "date": "type:datetime",
                "likes": int,
                "quotes": int,
                "retweets": int,
                "tweet_id": r"re:\d+",
                "user": {
                    "name": "supernaturepics",
                    "nick": "Nature Pictures"
                },
            },
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics"),
        ("https://nitter.pussthecat.org/supernaturepics"),
        ("https://nitter.1d4.us/supernaturepics"),
        ("https://nitter.kavin.rocks/supernaturepics"),
        ("https://nitter.unixfox.eu/supernaturepics"),
    )

    def tweets(self):
        return self._pagination("/" + self.user)


class NitterRepliesExtractor(NitterExtractor):
    subcategory = "replies"
    pattern = BASE_PATTERN + r"/([^/?#]+)/with_replies"
    test = (
        ("https://nitter.net/supernaturepics/with_replies", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics/with_replies"),
        ("https://nitter.pussthecat.org/supernaturepics/with_replies"),
        ("https://nitter.1d4.us/supernaturepics/with_replies"),
        ("https://nitter.kavin.rocks/supernaturepics/with_replies"),
        ("https://nitter.unixfox.eu/supernaturepics/with_replies"),
    )

    def tweets(self):
        return self._pagination("/" + self.user + "/with_replies")


class NitterMediaExtractor(NitterExtractor):
    subcategory = "media"
    pattern = BASE_PATTERN + r"/([^/?#]+)/media"
    test = (
        ("https://nitter.net/supernaturepics/media", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics/media"),
        ("https://nitter.pussthecat.org/supernaturepics/media"),
        ("https://nitter.1d4.us/supernaturepics/media"),
        ("https://nitter.kavin.rocks/supernaturepics/media"),
        ("https://nitter.unixfox.eu/supernaturepics/media"),
    )

    def tweets(self):
        return self._pagination("/" + self.user + "/media")


class NitterSearchExtractor(NitterExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/([^/?#]+)/search"
    test = (
        ("https://nitter.net/supernaturepics/search", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics/search"),
        ("https://nitter.pussthecat.org/supernaturepics/search"),
        ("https://nitter.1d4.us/supernaturepics/search"),
        ("https://nitter.kavin.rocks/supernaturepics/search"),
        ("https://nitter.unixfox.eu/supernaturepics/search"),
    )

    def tweets(self):
        return self._pagination("/" + self.user + "/search")


class NitterTweetExtractor(NitterExtractor):
    """Extractor for nitter tweets"""
    subcategory = "tweet"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{num}"
    pattern = BASE_PATTERN + r"/[^/?#]+/status/(\d+)"
    test = (
        ("https://nitter.net/supernaturepics/status/604341487988576256", {
            "url": "3f2b64e175bf284aa672c3bb53ed275e470b919a",
            "content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",
        }),
        # 4 images
        ("https://nitter.lacontrevoie.fr/i/status/894001459754180609", {
            "url": "9c51b3a4a1114535eb9b168bba97ad95db0d59ff",
        }),
        # video
        ("https://nitter.pussthecat.org/i/status/1065692031626829824", {
            "pattern": r"ytdl:https://nitter.pussthecat.org/video"
                       r"/B875137EDC8FF/https%3A%2F%2Fvideo.twimg.com%2F"
                       r"ext_tw_video%2F1065691868439007232%2Fpu%2Fpl%2F"
                       r"nv8hUQC1R0SjhzcZ.m3u8%3Ftag%3D5",
        }),
        # content with emoji, newlines, hashtags (#338)
        ("https://nitter.1d4.us/playpokemon/status/1263832915173048321", {
            "keyword": {"content": (
                r"re:Gear up for #PokemonSwordShieldEX with special Mystery "
                "Gifts! \n\nYou’ll be able to receive four Galarian form "
                "Pokémon with Hidden Abilities, plus some very useful items. "
                "It’s our \\(Mystery\\) Gift to you, Trainers! \n\n❓🎁➡️ "
            )},
        }),
        # Nitter tweet (#890)
        ("https://nitter.kavin.rocks/ed1conf/status/1163841619336007680", {
            "url": "e115bd1c86c660064e392b05269bbcafcd8c8b7a",
            "content": "f29501e44d88437fe460f5c927b7543fda0f6e34",
        }),
    )

    def tweets(self):
        url = "{}/i/status/{}".format(self.root, self.user)
        return (self.request(url).text,)

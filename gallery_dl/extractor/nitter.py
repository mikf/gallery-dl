# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Nitter instances"""

from .common import BaseExtractor, Message
from .. import text
import binascii


class NitterExtractor(BaseExtractor):
    """Base class for nitter extractors"""
    basecategory = "nitter"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{num}"

    def __init__(self, match):
        self.cookiedomain = self.root.partition("://")[2]
        BaseExtractor.__init__(self, match)

        lastindex = match.lastindex
        self.user = match.group(lastindex)
        self.user_id = match.group(lastindex + 1)
        self.user_obj = None

    def items(self):
        retweets = self.config("retweets", False)
        videos = self.config("videos", True)
        if videos:
            ytdl = (videos == "ytdl")
            videos = True
            self._cookiejar.set("hlsPlayback", "on", domain=self.cookiedomain)

        for tweet in self.tweets():

            if not retweets and tweet["retweet"]:
                self.log.debug("Skipping %s (retweet)", tweet["tweet_id"])
                continue

            attachments = tweet.pop("_attach", "")
            if attachments:
                files = []
                append = files.append

                for url in text.extract_iter(
                        attachments, 'href="', '"'):

                    if "/i/broadcasts/" in url:
                        self.log.debug(
                            "Skipping unsupported broadcast '%s'", url)
                        continue

                    if "/enc/" in url:
                        name = binascii.a2b_base64(url.rpartition(
                            "/")[2]).decode().rpartition("/")[2]
                    else:
                        name = url.rpartition("%2F")[2]

                    if url[0] == "/":
                        url = self.root + url
                    file = {"url": url, "_http_retry": _retry_on_404}
                    file["filename"], _, file["extension"] = \
                        name.rpartition(".")
                    append(file)

                if videos and not files:
                    if ytdl:
                        append({
                            "url": "ytdl:{}/i/status/{}".format(
                                self.root, tweet["tweet_id"]),
                            "extension": None,
                        })
                    else:
                        for url in text.extract_iter(
                                attachments, 'data-url="', '"'):

                            if "/enc/" in url:
                                name = binascii.a2b_base64(url.rpartition(
                                    "/")[2]).decode().rpartition("/")[2]
                            else:
                                name = url.rpartition("%2F")[2]

                            if url[0] == "/":
                                url = self.root + url
                            append({
                                "url"      : "ytdl:" + url,
                                "filename" : name.rpartition(".")[0],
                                "extension": "mp4",
                            })

                        for url in text.extract_iter(
                                attachments, '<source src="', '"'):
                            append(text.nameext_from_url(url, {"url": url}))

            else:
                files = ()
            tweet["count"] = len(files)

            yield Message.Directory, tweet
            for tweet["num"], file in enumerate(files, 1):
                url = file["url"]
                file.update(tweet)
                yield Message.Url, url, file

    def _tweet_from_html(self, html):
        extr = text.extract_from(html)
        author = {
            "name": extr('class="fullname" href="/', '"'),
            "nick": extr('title="', '"'),
        }
        extr('<span class="tweet-date', '')
        link = extr('href="', '"')
        return {
            "author"  : author,
            "user"    : self.user_obj or author,
            "date"    : text.parse_datetime(
                extr('title="', '"'), "%b %d, %Y · %I:%M %p %Z"),
            "tweet_id": link.rpartition("/")[2].partition("#")[0],
            "content": extr('class="tweet-content', "</div").partition(">")[2],
            "_attach" : extr('class="attachments', 'class="tweet-stats'),
            "comments": text.parse_int(extr(
                'class="icon-comment', '</div>').rpartition(">")[2]),
            "retweets": text.parse_int(extr(
                'class="icon-retweet', '</div>').rpartition(">")[2]),
            "quotes"  : text.parse_int(extr(
                'class="icon-quote', '</div>').rpartition(">")[2]),
            "likes"   : text.parse_int(extr(
                'class="icon-heart', '</div>').rpartition(">")[2]),
            "retweet" : 'class="retweet-header' in html,
            "quoted"  : False,
        }

    def _tweet_from_quote(self, html):
        extr = text.extract_from(html)
        author = {
            "name": extr('class="fullname" href="/', '"'),
            "nick": extr('title="', '"'),
        }
        extr('<span class="tweet-date', '')
        link = extr('href="', '"')
        return {
            "author"  : author,
            "user"    : self.user_obj or author,
            "date"    : text.parse_datetime(
                extr('title="', '"'), "%b %d, %Y · %I:%M %p %Z"),
            "tweet_id": link.rpartition("/")[2].partition("#")[0],
            "content" : extr('class="quote-text', "</div").partition(">")[2],
            "_attach" : extr('class="attachments', '''
                </div>'''),
            "retweet" : False,
            "quoted"  : True,
        }

    def _user_from_html(self, html):
        extr = text.extract_from(html, html.index('class="profile-tabs'))
        banner = extr('class="profile-banner"><a href="', '"')

        try:
            if "/enc/" in banner:
                uid = binascii.a2b_base64(banner.rpartition(
                    "/")[2]).decode().split("/")[4]
            else:
                uid = banner.split("%2F")[4]
        except Exception:
            uid = 0

        return {
            "id"              : uid,
            "profile_banner"  : self.root + banner if banner else "",
            "profile_image"   : self.root + extr(
                'class="profile-card-avatar" href="', '"'),
            "nick"            : extr('title="', '"'),
            "name"            : extr('title="@', '"'),
            "description"     : extr('<p dir="auto">', '<'),
            "date"            : text.parse_datetime(
                extr('class="profile-joindate"><span title="', '"'),
                "%I:%M %p - %d %b %Y"),
            "statuses_count"  : text.parse_int(extr(
                'class="profile-stat-num">', '<').replace(",", "")),
            "friends_count"   : text.parse_int(extr(
                'class="profile-stat-num">', '<').replace(",", "")),
            "followers_count" : text.parse_int(extr(
                'class="profile-stat-num">', '<').replace(",", "")),
            "favourites_count": text.parse_int(extr(
                'class="profile-stat-num">', '<').replace(",", "")),
            "verified"        : 'title="Verified account"' in html,
        }

    def _extract_quote(self, html):
        html, _, quote = html.partition('class="quote')
        if quote:
            quote, _, tail = quote.partition('class="tweet-published')
            return (html + tail, quote)
        return (html, None)

    def _pagination(self, path):
        quoted = self.config("quoted", False)

        if self.user_id:
            self.user = self.request(
                "{}/i/user/{}".format(self.root, self.user_id),
                allow_redirects=False,
            ).headers["location"].rpartition("/")[2]
        base_url = url = "{}/{}{}".format(self.root, self.user, path)

        while True:
            tweets_html = self.request(url).text.split(
                '<div class="timeline-item')

            if self.user_obj is None:
                self.user_obj = self._user_from_html(tweets_html[0])

            for html, quote in map(self._extract_quote, tweets_html[1:]):
                yield self._tweet_from_html(html)
                if quoted and quote:
                    yield self._tweet_from_quote(quote)

            more = text.extr(
                tweets_html[-1], '<div class="show-more"><a href="?', '"')
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
    "nitter.it": {
        "root": "https://nitter.it",
        "pattern": r"nitter\.it",
    },
})

USER_PATTERN = BASE_PATTERN + r"/(i(?:/user/|d:)(\d+)|[^/?#]+)"


class NitterTweetsExtractor(NitterExtractor):
    subcategory = "tweets"
    pattern = USER_PATTERN + r"(?:/tweets)?(?:$|\?|#)"
    test = (
        ("https://nitter.net/supernaturepics", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
            "count": 20,
            "keyword": {
                "author": {
                    "name": "supernaturepics",
                    "nick": "Nature Pictures"
                },
                "comments": int,
                "content": str,
                "count": 1,
                "date": "type:datetime",
                "likes": int,
                "quotes": int,
                "retweets": int,
                "tweet_id": r"re:\d+",
                "user": {
                    "date": "dt:2015-01-12 10:25:00",
                    "description": "The very best nature pictures.",
                    "favourites_count": int,
                    "followers_count": int,
                    "friends_count": int,
                    "id": "2976459548",
                    "name": "supernaturepics",
                    "nick": "Nature Pictures",
                    "profile_banner": "https://nitter.net/pic/https%3A%2F%2Fpb"
                                      "s.twimg.com%2Fprofile_banners%2F2976459"
                                      "548%2F1421058583%2F1500x500",
                    "profile_image": "https://nitter.net/pic/pbs.twimg.com%2Fp"
                                     "rofile_images%2F554585280938659841%2FFLV"
                                     "AlX18.jpeg",
                    "statuses_count": 1568,
                    "verified": False,
                },
            },
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics", {
            "url": "54f4b55f2099dcc248f3fb7bfacf1349e08d8e2d",
            "pattern": r"https://nitter\.lacontrevoie\.fr/pic/orig"
                       r"/media%2FCGMNYZvW0AIVoom\.jpg",
            "range": "1",
        }),
        ("https://nitter.1d4.us/supernaturepics", {
            "range": "1",
            "keyword": {"user": {"id": "2976459548"}},
        }),
        ("https://nitter.kavin.rocks/id:2976459548"),
        ("https://nitter.unixfox.eu/supernaturepics"),
    )

    def tweets(self):
        return self._pagination("")


class NitterRepliesExtractor(NitterExtractor):
    subcategory = "replies"
    pattern = USER_PATTERN + r"/with_replies"
    test = (
        ("https://nitter.net/supernaturepics/with_replies", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics/with_replies"),
        ("https://nitter.1d4.us/supernaturepics/with_replies"),
        ("https://nitter.kavin.rocks/id:2976459548/with_replies"),
        ("https://nitter.unixfox.eu/i/user/2976459548/with_replies"),
    )

    def tweets(self):
        return self._pagination("/with_replies")


class NitterMediaExtractor(NitterExtractor):
    subcategory = "media"
    pattern = USER_PATTERN + r"/media"
    test = (
        ("https://nitter.net/supernaturepics/media", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.kavin.rocks/id:2976459548/media", {
            "pattern": r"https://nitter\.kavin\.rocks/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics/media"),
        ("https://nitter.1d4.us/supernaturepics/media"),
        ("https://nitter.unixfox.eu/i/user/2976459548/media"),
    )

    def tweets(self):
        return self._pagination("/media")


class NitterSearchExtractor(NitterExtractor):
    subcategory = "search"
    pattern = USER_PATTERN + r"/search"
    test = (
        ("https://nitter.net/supernaturepics/search", {
            "pattern": r"https://nitter\.net/pic/orig"
                       r"/media%2F[\w-]+\.(jpg|png)$",
            "range": "1-20",
        }),
        ("https://nitter.lacontrevoie.fr/supernaturepics/search"),
        ("https://nitter.1d4.us/supernaturepics/search"),
        ("https://nitter.kavin.rocks/id:2976459548/search"),
        ("https://nitter.unixfox.eu/i/user/2976459548/search"),
    )

    def tweets(self):
        return self._pagination("/search")


class NitterTweetExtractor(NitterExtractor):
    """Extractor for nitter tweets"""
    subcategory = "tweet"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{num}"
    pattern = BASE_PATTERN + r"/(i/web|[^/?#]+)/status/(\d+())"
    test = (
        ("https://nitter.net/supernaturepics/status/604341487988576256", {
            "url": "3f2b64e175bf284aa672c3bb53ed275e470b919a",
            "content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",
            "keyword": {
                "comments": 19,
                "content": "Big Wedeene River, Canada",
                "count": 1,
                "date": "dt:2015-05-29 17:40:00",
                "extension": "jpg",
                "filename": "CGMNYZvW0AIVoom",
                "likes": int,
                "num": 1,
                "quotes": 10,
                "retweets": int,
                "tweet_id": "604341487988576256",
                "url": "https://nitter.net/pic/orig"
                       "/media%2FCGMNYZvW0AIVoom.jpg",
                "user": {
                    "name": "supernaturepics",
                    "nick": "Nature Pictures",
                },
            },
        }),
        # 4 images
        ("https://nitter.lacontrevoie.fr/i/status/894001459754180609", {
            "url": "9c51b3a4a1114535eb9b168bba97ad95db0d59ff",
        }),
        # video
        ("https://nitter.lacontrevoie.fr/i/status/1065692031626829824", {
            "pattern": r"ytdl:https://nitter\.lacontrevoie\.fr/video"
                       r"/[0-9A-F]{10,}/https%3A%2F%2Fvideo.twimg.com%2F"
                       r"ext_tw_video%2F1065691868439007232%2Fpu%2Fpl%2F"
                       r"nv8hUQC1R0SjhzcZ.m3u8%3Ftag%3D5",
            "keyword": {
                "extension": "mp4",
                "filename": "nv8hUQC1R0SjhzcZ",
            },
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
        # Reply to deleted tweet (#403, #838)
        ("https://nitter.unixfox.eu/i/web/status/1170041925560258560", {
            "pattern": r"https://nitter\.unixfox\.eu/pic/orig"
                       r"/media%2FEDzS7VrU0AAFL4_\.jpg",
        }),
        # "quoted" option (#854)
        ("https://nitter.net/StobiesGalaxy/status/1270755918330896395", {
            "options": (("quoted", True),),
            "pattern": r"https://nitter\.net/pic/orig/media%2FEa[KG].+\.jpg",
            "count": 8,
        }),
        # quoted tweet (#526, #854)
        ("https://nitter.1d4.us/StobiesGalaxy/status/1270755918330896395", {
            "pattern": r"https://nitter\.1d4\.us/pic/orig"
                       r"/enc/bWVkaWEvRWFL\w+LmpwZw==",
            "keyword": {"filename": r"re:EaK.{12}"},
            "count": 4,
        }),
        # deleted quote tweet (#2225)
        ("https://nitter.lacontrevoie.fr/i/status/1460044411165888515", {
            "count": 0,
        }),
        # "Misleading" content
        ("https://nitter.lacontrevoie.fr/i/status/1486373748911575046", {
            "count": 4,
        }),
        # age-restricted (#2354)
        ("https://nitter.unixfox.eu/mightbecurse/status/1492954264909479936", {
            "keyword": {"date": "dt:2022-02-13 20:10:00"},
            "count": 1,
        }),
        # broadcast
        ("https://nitter.it/POTUS/status/1639409307878928384", {
            "count": 0,
        })
    )

    def tweets(self):
        url = "{}/i/status/{}".format(self.root, self.user)
        html = text.extr(self.request(url).text, 'class="main-tweet', '''\
                </div>
              </div></div></div>''')
        html, quote = self._extract_quote(html)
        tweet = self._tweet_from_html(html)
        if quote and self.config("quoted", False):
            quoted = self._tweet_from_quote(quote)
            quoted["user"] = tweet["user"]
            return (tweet, quoted)
        return (tweet,)


def _retry_on_404(response):
    return response.status_code == 404

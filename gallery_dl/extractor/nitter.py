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
        self.cookies_domain = self.root.partition("://")[2]
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
            self.cookies.set("hlsPlayback", "on", domain=self.cookies_domain)

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
                            if url[0] == "/":
                                url = self.root + url
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
                tweet = self._tweet_from_html(html)
                if not tweet["date"]:
                    continue
                yield tweet
                if quoted and quote:
                    yield self._tweet_from_quote(quote)

            more = text.extr(
                tweets_html[-1], '<div class="show-more"><a href="?', '"')
            if not more:
                return
            url = base_url + "?" + text.unescape(more)


BASE_PATTERN = NitterExtractor.update({
})

USER_PATTERN = BASE_PATTERN + r"/(i(?:/user/|d:)(\d+)|[^/?#]+)"


class NitterTweetsExtractor(NitterExtractor):
    subcategory = "tweets"
    pattern = USER_PATTERN + r"(?:/tweets)?(?:$|\?|#)"
    example = "https://nitter.net/USER"

    def tweets(self):
        return self._pagination("")


class NitterRepliesExtractor(NitterExtractor):
    subcategory = "replies"
    pattern = USER_PATTERN + r"/with_replies"
    example = "https://nitter.net/USER/with_replies"

    def tweets(self):
        return self._pagination("/with_replies")


class NitterMediaExtractor(NitterExtractor):
    subcategory = "media"
    pattern = USER_PATTERN + r"/media"
    example = "https://nitter.net/USER/media"

    def tweets(self):
        return self._pagination("/media")


class NitterSearchExtractor(NitterExtractor):
    subcategory = "search"
    pattern = USER_PATTERN + r"/search"
    example = "https://nitter.net/USER/search"

    def tweets(self):
        return self._pagination("/search")


class NitterTweetExtractor(NitterExtractor):
    """Extractor for nitter tweets"""
    subcategory = "tweet"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{num}"
    pattern = BASE_PATTERN + r"/(i/web|[^/?#]+)/status/(\d+())"
    example = "https://nitter.net/USER/status/12345"

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

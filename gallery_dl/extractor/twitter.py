# -*- coding: utf-8 -*-

# Copyright 2016-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://twitter.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache, memcache
import json
import re


class TwitterExtractor(Extractor):
    """Base class for twitter extractors"""
    category = "twitter"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{retweet_id}_{num}"
    cookiedomain = ".twitter.com"
    root = "https://twitter.com"
    sizes = (":orig", ":large", ":medium", ":small")
    user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64; "
                  "Trident/7.0; rv:11.0) like Gecko")

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self._user_dict = None
        self.logged_in = False
        self.retweets = self.config("retweets", True)
        self.twitpic = self.config("twitpic", False)
        self.content = self.config("content", False)
        self.videos = self.config("videos", True)

        if self.content:
            self._emoji_sub = re.compile(
                r'<img class="Emoji [^>]+ alt="([^"]+)"[^>]*>').sub

    def items(self):
        self.login()
        metadata = self.metadata()
        yield Message.Version, 1

        for tweet in self.tweets():
            data = self._data_from_tweet(tweet)
            if not data or not self.retweets and data["retweet_id"]:
                continue
            data.update(metadata)

            if self.videos and "-videoContainer" in tweet:
                yield Message.Directory, data

                if self.videos == "ytdl":
                    data["extension"] = None
                    url = "ytdl:{}/i/web/status/{}".format(
                        self.root, data["tweet_id"])
                else:
                    url = self._video_from_tweet(data["tweet_id"])
                    if not url:
                        continue
                    ext = text.ext_from_url(url)
                    if ext == "m3u8":
                        url = "ytdl:" + url
                        data["extension"] = "mp4"
                        data["_ytdl_extra"] = {"protocol": "m3u8_native"}
                    else:
                        data["extension"] = ext
                data["num"] = 1
                yield Message.Url, url, data

            elif "data-image-url=" in tweet:
                yield Message.Directory, data

                images = text.extract_iter(
                    tweet, 'data-image-url="', '"')
                for data["num"], url in enumerate(images, 1):
                    text.nameext_from_url(url, data)
                    urls = [url + size for size in self.sizes]
                    yield Message.Urllist, urls, data

            if self.twitpic and "//twitpic.com/" in tweet:
                urls = [
                    url for url in text.extract_iter(
                        tweet, 'data-expanded-url="', '"')
                    if "//twitpic.com/" in url
                ]

                if "num" not in data:
                    if urls:
                        yield Message.Directory, data
                    data["num"] = 0

                for data["num"], url in enumerate(urls, data["num"]+1):
                    response = self.request(url, fatal=False)
                    if response.status_code >= 400:
                        continue
                    url = text.extract(
                        response.text, 'name="twitter:image" value="', '"')[0]
                    yield Message.Url, url, text.nameext_from_url(url, data)

    def metadata(self):
        """Return general metadata"""
        return {}

    def tweets(self):
        """Yield HTML content of all relevant tweets"""

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))
            self.logged_in = True

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        headers = {"User-Agent": self.user_agent}
        page = self.request(self.root + "/login", headers=headers).text
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
        response = self.request(url, method="POST", headers=headers, data=data)
        if "/error" in response.url:
            raise exception.AuthenticationError()

        return {
            cookie.name: cookie.value
            for cookie in self.session.cookies
            if cookie.domain and "twitter.com" in cookie.domain
        }

    def _data_from_tweet(self, tweet):
        extr = text.extract_from(tweet)
        data = {
            "tweet_id"  : text.parse_int(extr('data-tweet-id="'  , '"')),
            "retweet_id": text.parse_int(extr('data-retweet-id="', '"')),
            "retweeter" : extr('data-retweeter="'  , '"'),
            "author"    : {
                "name"  : extr('data-screen-name="', '"'),
                "nick"  : text.unescape(extr('data-name="'       , '"')),
                "id"    : text.parse_int(extr('data-user-id="'   , '"')),
            },
        }

        if not self._user_dict:
            if data["retweet_id"]:
                for user in json.loads(text.unescape(extr(
                        'data-reply-to-users-json="', '"'))):
                    if user["screen_name"] == data["retweeter"]:
                        break
                else:
                    self.log.warning("Unable to extract user info")
                    return None
                self._user_dict = {
                    "name": user["screen_name"],
                    "nick": text.unescape(user["name"]),
                    "id"  : text.parse_int(user["id_str"]),
                }
            else:
                self._user_dict = data["author"]

        data["user"] = self._user_dict
        data["date"] = text.parse_timestamp(extr('data-time="', '"'))

        if self.content:
            content = extr('<div class="js-tweet-text-container">', '\n</div>')
            if '<img class="Emoji ' in content:
                content = self._emoji_sub(r"\1", content)
            content = text.unescape(text.remove_html(content, "", ""))
            cl, _, cr = content.rpartition("pic.twitter.com/")
            data["content"] = cl if cl and len(cr) < 16 else content

        if extr('<div class="QuoteTweet', '>'):
            data["retweet_id"] = text.parse_int(extr('data-item-id="', '"'))
            data["retweeter"] = data["user"]["name"]
            data["author"] = {
                "name"  : extr('data-screen-name="', '"'),
                "id"    : text.parse_int(extr('data-user-id="'   , '"')),
                "nick"  : text.unescape(extr(
                    'QuoteTweet-fullname', '<').partition('>')[2]),
            }

        return data

    def _video_from_tweet(self, tweet_id):
        url = "https://api.twitter.com/1.1/videos/tweet/config/{}.json".format(
            tweet_id)
        cookies = None
        headers = {
            "Origin"       : self.root,
            "Referer"      : "{}/i/web/status/{}".format(self.root, tweet_id),
            "x-csrf-token" : self.session.cookies.get("ct0"),
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekM"
                             "xqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28N"
                             "HfOPqkca3qaAxGfsyKCs0wRbw",
        }

        if self.logged_in:
            headers["x-twitter-auth-type"] = "OAuth2Session"
        else:
            token = _guest_token(self, headers)
            cookies = {"gt": token}
            headers["x-guest-token"] = token

        response = self.request(
            url, cookies=cookies, headers=headers, fatal=None)

        if response.status_code == 429 or \
                response.headers.get("x-rate-limit-remaining") == "0":
            if self.logged_in:
                reset = response.headers.get("x-rate-limit-reset")
                self.wait(until=reset, reason="rate limit reset")
            else:
                _guest_token.invalidate()
            return self._video_from_tweet(tweet_id)

        elif response.status_code >= 400:
            self.log.warning("Unable to fetch video data for %s ('%s %s')",
                             tweet_id, response.status_code, response.reason)
            return None

        return response.json()["track"]["playbackUrl"]

    def _tweets_from_api(self, url, max_position=None):
        params = {
            "include_available_features": "1",
            "include_entities": "1",
            "max_position": max_position,
            "reset_error_state": "false",
            "lang": "en",
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-Twitter-Active-User": "yes",
            "Referer": self.root + "/",
        }

        while True:
            data = self.request(url, params=params, headers=headers).json()
            if "inner" in data:
                data = data["inner"]

            for tweet in text.extract_iter(
                    data["items_html"], '<div class="tweet ', '\n</li>'):
                yield tweet

            if data.get("min_position") is None:
                if data["has_more_items"] and "min_position" not in data:
                    pass
                else:
                    return

            if "min_position" in data:
                position = data["min_position"]
                if position == max_position or position is None:
                    return
            else:
                position = text.parse_int(text.extract(
                    tweet, 'data-tweet-id="', '"')[0])
                if max_position and position >= max_position:
                    return
            params["max_position"] = max_position = position


class TwitterTimelineExtractor(TwitterExtractor):
    """Extractor for all images from a user's timeline"""
    subcategory = "timeline"
    pattern = (r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/(?!search)([^/?&#]+)/?(?:$|[?#])")
    test = (
        ("https://twitter.com/supernaturepics", {
            "range": "1-40",
            "url": "0106229d408f4111d9a52c8fd2ad687f64842aa4",
            "keyword": "37f4d35affd733d458d3b235b4a55f619a86f794",
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
               r"/(?!search)([^/?&#]+)/media(?!\w)")
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


class TwitterSearchExtractor(TwitterExtractor):
    """Extractor for all images from a search timeline"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = (r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/search/?\?(?:[^&#]+&)*q=([^&#]+)")
    test = ("https://twitter.com/search?q=nature", {
        "range": "1-40",
        "count": 40,
    })

    def metadata(self):
        return {"search": self.user}

    def tweets(self):
        url = "{}/i/search/timeline?f=tweets&q={}".format(
            self.root, self.user)
        return self._tweets_from_api(url, "-1")


class TwitterTweetExtractor(TwitterExtractor):
    """Extractor for images from individual tweets"""
    subcategory = "tweet"
    pattern = (r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com"
               r"/([^/?&#]+|i/web)/status/(\d+)")
    test = (
        ("https://twitter.com/supernaturepics/status/604341487988576256", {
            "url": "0e801d2f98142dd87c3630ded9e4be4a4d63b580",
            "keyword": "3fa3623e8d9a204597238e2f1f6433da19c63b4a",
            "content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",
        }),
        # 4 images
        ("https://twitter.com/perrypumas/status/894001459754180609", {
            "url": "c8a262a9698cb733fb27870f5a8f75faf77d79f6",
            "keyword": "49165725116ac52193a3861e8f5534e47a706b62",
        }),
        # video
        ("https://twitter.com/perrypumas/status/1065692031626829824", {
            "options": (("videos", True),),
            "pattern": r"ytdl:https://video.twimg.com/ext_tw_video/.*.m3u8",
        }),
        # content with emoji, newlines, hashtags (#338)
        ("https://twitter.com/yumi_san0112/status/1151144618936823808", {
            "options": (("content", True),),
            "keyword": {"content": (
                "re:晴、お誕生日おめでとう🎉！\n実は下の名前が同じなので結構親近感ある"
                "アイドルです✨\n今年の晴ちゃんめちゃくちゃ可愛い路線攻めてるから、そろ"
                "そろまたかっこいい晴が見たいですねw\n#結城晴生誕祭2019\n#結城晴生誕祭"
            )},
        }),
        # Reply to another tweet (#403)
        ("https://twitter.com/tyson_hesse/status/1103767554424598528", {
            "options": (("videos", "ytdl"),),
            "pattern": r"ytdl:https://twitter.com/i/web.+/1103767554424598528",
        }),
        # /i/web/ URL
        ("https://twitter.com/i/web/status/1155074198240292865", {
            "pattern": r"https://pbs.twimg.com/media/EAel0vUUYAAZ4Bq.jpg:orig",
        }),
        # quoted tweet (#526)
        ("https://twitter.com/Pistachio/status/1222690391817932803", {
            "pattern": r"https://pbs\.twimg\.com/media/EPfMfDUU8AAnByO\.jpg",
            "keyword": {
                "author": {"name": "Afro_Herper", "id": 786047748508221440},
                "user"  : {"name": "Pistachio"  , "id": 3533231},
            },
        }),
        # TwitPic embeds (#579)
        ("https://twitter.com/i/web/status/112900228289540096", {
            "options": (("twitpic", True),),
            "pattern": r"https://\w+.cloudfront.net/photos/large/\d+.jpg",
            "count": 3,
        }),
    )

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        self.tweet_id = match.group(2)

    def tweets(self):
        url = "{}/i/web/status/{}".format(self.root, self.tweet_id)
        cookies = {"app_shell_visited": "1"}
        headers = {"User-Agent": self.user_agent, "Referer": url}

        response = self.request(url, cookies=cookies, headers=headers)
        if response.history and response.url == self.root + "/":
            raise exception.AuthorizationError()
        page = response.text

        end = page.index('class="js-tweet-stats-container')
        beg = page.rindex('<div class="tweet ', 0, end)
        return (page[beg:end],)


class TwitterBookmarkExtractor(TwitterExtractor):
    """Extractor for bookmarked tweets"""
    subcategory = "bookmark"
    pattern = r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com/i/bookmarks()"
    test = ("https://twitter.com/i/bookmarks",)

    def items(self):
        self.login()
        if not self.logged_in:
            raise exception.AuthorizationError("Login required")
        for cookie in self.session.cookies:
            cookie.expires = None

        url = "https://api.twitter.com/2/timeline/bookmark.json"
        params = {
            "include_profile_interstitial_type": "1",
            "include_blocking": "1",
            "include_blocked_by": "1",
            "include_followed_by": "1",
            "include_want_retweets": "1",
            "include_mute_edge": "1",
            "include_can_dm": "1",
            "include_can_media_tag": "1",
            "skip_status": "1",
            "cards_platform": "Web-12",
            "include_cards": "1",
            "include_composer_source": "true",
            "include_ext_alt_text": "true",
            "include_reply_count": "1",
            "tweet_mode": "extended",
            "include_entities": "true",
            "include_user_entities": "true",
            "include_ext_media_color": "true",
            "include_ext_media_availability": "true",
            "send_error_codes": "true",
            "simple_quoted_tweets": "true",
            "count": "100",
            "cursor": None,
            "ext": "mediaStats%2CcameraMoment",
        }
        headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejR"
                             "COuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu"
                             "4FA33AGWWjCpTnA",
            "Origin": self.root,
            "Referer": self.root + "/i/bookmarks",
            "x-csrf-token": self.session.cookies.get("ct0"),
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
        }

        while True:
            response = self.request(
                url, params=params, headers=headers, fatal=False)
            if response.status_code >= 400:
                raise exception.StopExtraction(response.text)
            data = response.json()
            tweets = data["globalObjects"]["tweets"]

            if not tweets:
                return
            for tweet_id, tweet_data in tweets.items():
                tweet_url = "{}/i/web/status/{}".format(self.root, tweet_id)
                tweet_data["_extractor"] = TwitterTweetExtractor
                yield Message.Queue, tweet_url, tweet_data

            inst = data["timeline"]["instructions"][0]
            for entry in inst["addEntries"]["entries"]:
                if entry["entryId"].startswith("cursor-bottom-"):
                    params["cursor"] = \
                        entry["content"]["operation"]["cursor"]["value"]
                    break


@memcache()
def _guest_token(extr, headers):
    return extr.request(
        "https://api.twitter.com/1.1/guest/activate.json",
        method="POST", headers=headers,
    ).json().get("guest_token")

# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://twitter.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import json

BASE_PATTERN = (
    r"(?:https?://)?(?:www\.|mobile\.)?"
    r"(?:twitter\.com|nitter\.net)"
)


class TwitterExtractor(Extractor):
    """Base class for twitter extractors"""
    category = "twitter"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{retweet_id}_{num}"
    cookiedomain = ".twitter.com"
    cookienames = ("auth_token",)
    root = "https://twitter.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.textonly = self.config("text-tweets", False)
        self.retweets = self.config("retweets", False)
        self.replies = self.config("replies", True)
        self.twitpic = self.config("twitpic", False)
        self.pinned = self.config("pinned", False)
        self.quoted = self.config("quoted", False)
        self.videos = self.config("videos", True)
        self.cards = self.config("cards", True)
        self._user_cache = {}
        self._init_sizes()

    def _init_sizes(self):
        size = self.config("size")
        if size is None:
            self._size_image = "orig"
            self._size_fallback = ("4096x4096", "large", "medium", "small")
        else:
            if isinstance(size, str):
                size = size.split(",")
            self._size_image = size[0]
            self._size_fallback = size[1:]

    def items(self):
        self.login()
        self.api = TwitterAPI(self)
        metadata = self.metadata()

        for tweet in self.tweets():

            if "legacy" in tweet:
                data = tweet["legacy"]
            else:
                data = tweet

            if not self.retweets and "retweeted_status_id_str" in data:
                self.log.debug("Skipping %s (retweet)", data["id_str"])
                continue
            if not self.quoted and "quoted_by_id_str" in data:
                self.log.debug("Skipping %s (quoted tweet)", data["id_str"])
                continue
            if "in_reply_to_user_id_str" in data and (
                not self.replies or (
                    self.replies == "self" and
                    data["in_reply_to_user_id_str"] != data["user_id_str"]
                )
            ):
                self.log.debug("Skipping %s (reply)", data["id_str"])
                continue

            files = []
            if "extended_entities" in data:
                self._extract_media(
                    data, data["extended_entities"]["media"], files)
            if "card" in tweet and self.cards:
                self._extract_card(tweet, files)
            if self.twitpic:
                self._extract_twitpic(data, files)
            if not files and not self.textonly:
                continue

            tdata = self._transform_tweet(tweet)
            tdata.update(metadata)
            yield Message.Directory, tdata
            for tdata["num"], file in enumerate(files, 1):
                file.update(tdata)
                url = file.pop("url")
                if "extension" not in file:
                    text.nameext_from_url(url, file)
                yield Message.Url, url, file

    def _extract_media(self, tweet, entities, files):
        for media in entities:
            width = media["original_info"].get("width", 0)
            height = media["original_info"].get("height", 0)

            if "video_info" in media:
                if self.videos == "ytdl":
                    files.append({
                        "url": "ytdl:{}/i/web/status/{}".format(
                            self.root, tweet["id_str"]),
                        "width"    : width,
                        "height"   : height,
                        "extension": None,
                    })
                elif self.videos:
                    video_info = media["video_info"]
                    variant = max(
                        video_info["variants"],
                        key=lambda v: v.get("bitrate", 0),
                    )
                    files.append({
                        "url"     : variant["url"],
                        "width"   : width,
                        "height"  : height,
                        "bitrate" : variant.get("bitrate", 0),
                        "duration": video_info.get(
                            "duration_millis", 0) / 1000,
                    })
            elif "media_url_https" in media:
                url = media["media_url_https"]
                base, _, fmt = url.rpartition(".")
                base += "?format=" + fmt + "&name="
                files.append(text.nameext_from_url(url, {
                    "url"      : base + self._size_image,
                    "width"    : width,
                    "height"   : height,
                    "_fallback": self._image_fallback(base),
                }))
            else:
                files.append({"url": media["media_url"]})

    def _image_fallback(self, base):
        for fmt in self._size_fallback:
            yield base + fmt

    def _extract_card(self, tweet, files):
        card = tweet["card"]
        if "legacy" in card:
            card = card["legacy"]
        name = card["name"]

        if name in ("summary", "summary_large_image"):
            bvals = card["binding_values"]
            if isinstance(bvals, list):
                bvals = {
                    bval["key"]: bval["value"]
                    for bval in card["binding_values"]
                }
            for prefix in ("photo_image_full_size_",
                           "summary_photo_image_",
                           "thumbnail_image_"):
                for size in ("original", "x_large", "large", "small"):
                    key = prefix + size
                    if key in bvals:
                        value = bvals[key].get("image_value")
                        if value and "url" in value:
                            base, sep, size = value["url"].rpartition("&name=")
                            if sep:
                                base += sep
                                value["url"] = base + self._size_image
                                value["_fallback"] = self._image_fallback(base)
                            files.append(value)
                            return
        elif name == "unified_card":
            bvals = card["binding_values"]
            if isinstance(bvals, list):
                for bval in card["binding_values"]:
                    if bval["key"] == "unified_card":
                        bval = bval["value"]["string_value"]
                        break
            else:
                bval = bvals["unified_card"]["string_value"]
            data = json.loads(bval)
            if data.get("type") == "image_carousel_website":
                self._extract_media(
                    tweet, data["media_entities"].values(), files)
                return

        if self.cards == "ytdl":
            tweet_id = tweet.get("rest_id") or tweet["id_str"]
            url = "ytdl:{}/i/web/status/{}".format(self.root, tweet_id)
            files.append({"url": url})

    def _extract_twitpic(self, tweet, files):
        for url in tweet["entities"].get("urls", ()):
            url = url["expanded_url"]
            if "//twitpic.com/" in url and "/photos/" not in url:
                response = self.request(url, fatal=False)
                if response.status_code >= 400:
                    continue
                url = text.extract(
                    response.text, 'name="twitter:image" value="', '"')[0]
                if url:
                    files.append({"url": url})

    def _transform_tweet(self, tweet):
        if "core" in tweet:
            user = self._transform_user(
                tweet["core"]["user_results"]["result"])
        else:
            user = self._transform_user(tweet["user"])

        if "legacy" in tweet:
            tweet = tweet["legacy"]

        entities = tweet["entities"]
        tdata = {
            "tweet_id"      : text.parse_int(tweet["id_str"]),
            "retweet_id"    : text.parse_int(
                tweet.get("retweeted_status_id_str")),
            "quote_id"      : text.parse_int(
                tweet.get("quoted_status_id_str")),
            "reply_id"      : text.parse_int(
                tweet.get("in_reply_to_status_id_str")),
            "date"          : text.parse_datetime(
                tweet["created_at"], "%a %b %d %H:%M:%S %z %Y"),
            "user"          : user,
            "lang"          : tweet["lang"],
            "favorite_count": tweet["favorite_count"],
            "quote_count"   : tweet["quote_count"],
            "reply_count"   : tweet["reply_count"],
            "retweet_count" : tweet["retweet_count"],
        }

        hashtags = entities.get("hashtags")
        if hashtags:
            tdata["hashtags"] = [t["text"] for t in hashtags]

        mentions = entities.get("user_mentions")
        if mentions:
            tdata["mentions"] = [{
                "id": text.parse_int(u["id_str"]),
                "name": u["screen_name"],
                "nick": u["name"],
            } for u in mentions]

        content = tweet["full_text"]
        urls = entities.get("urls")
        if urls:
            for url in urls:
                content = content.replace(url["url"], url["expanded_url"])
        txt, _, tco = content.rpartition(" ")
        tdata["content"] = txt if tco.startswith("https://t.co/") else content

        if "in_reply_to_screen_name" in tweet:
            tdata["reply_to"] = tweet["in_reply_to_screen_name"]
        if "quoted_by_id_str" in tweet:
            tdata["quote_by"] = text.parse_int(tweet["quoted_by_id_str"])

        if "author" in tweet:
            tdata["author"] = self._transform_user(tweet["author"])
        else:
            tdata["author"] = tdata["user"]

        return tdata

    def _transform_user(self, user):
        try:
            return self._user_cache[user.get("rest_id") or user["id_str"]]
        except KeyError:
            pass

        uid = user.get("rest_id") or user["id_str"]
        if "legacy" in user:
            user = user["legacy"]
        entities = user["entities"]

        self._user_cache[uid] = udata = {
            "id"              : text.parse_int(uid),
            "name"            : user["screen_name"],
            "nick"            : user["name"],
            "location"        : user["location"],
            "date"            : text.parse_datetime(
                user["created_at"], "%a %b %d %H:%M:%S %z %Y"),
            "verified"        : user.get("verified", False),
            "profile_banner"  : user.get("profile_banner_url", ""),
            "profile_image"   : user.get(
                "profile_image_url_https", "").replace("_normal.", "."),
            "favourites_count": user["favourites_count"],
            "followers_count" : user["followers_count"],
            "friends_count"   : user["friends_count"],
            "listed_count"    : user["listed_count"],
            "media_count"     : user["media_count"],
            "statuses_count"  : user["statuses_count"],
        }

        descr = user["description"]
        urls = entities["description"].get("urls")
        if urls:
            for url in urls:
                descr = descr.replace(url["url"], url["expanded_url"])
        udata["description"] = descr

        if "url" in entities:
            url = entities["url"]["urls"][0]
            udata["url"] = url.get("expanded_url") or url.get("url")

        return udata

    def _users_result(self, users):
        userfmt = self.config("users")
        if not userfmt or userfmt == "timeline":
            cls = TwitterTimelineExtractor
            fmt = (self.root + "/i/user/{rest_id}").format_map
        elif userfmt == "media":
            cls = TwitterMediaExtractor
            fmt = (self.root + "/id:{rest_id}/media").format_map
        else:
            cls = None
            fmt = userfmt.format_map

        for user in users:
            user["_extractor"] = cls
            yield Message.Queue, fmt(user), user

    def metadata(self):
        """Return general metadata"""
        return {}

    def tweets(self):
        """Yield all relevant tweet objects"""

    def login(self):
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if username:
                self._update_cookies(self._login_impl(username, password))

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        token = util.generate_token()
        self.session.cookies.clear()
        self.request(self.root + "/login")

        url = self.root + "/sessions"
        cookies = {
            "_mb_tk": token,
        }
        data = {
            "redirect_after_login"      : "/",
            "remember_me"               : "1",
            "authenticity_token"        : token,
            "wfa"                       : "1",
            "ui_metrics"                : "{}",
            "session[username_or_email]": username,
            "session[password]"         : password,
        }
        response = self.request(
            url, method="POST", cookies=cookies, data=data)

        if "/account/login_verification" in response.url:
            raise exception.AuthenticationError(
                "Login with two-factor authentication is not supported")

        cookies = {
            cookie.name: cookie.value
            for cookie in self.session.cookies
        }

        if "/error" in response.url or "auth_token" not in cookies:
            raise exception.AuthenticationError()
        return cookies


class TwitterTimelineExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's timeline"""
    subcategory = "timeline"
    pattern = (BASE_PATTERN + r"/(?!search)(?:([^/?#]+)/?(?:$|[?#])"
               r"|i(?:/user/|ntent/user\?user_id=)(\d+))")
    test = (
        ("https://twitter.com/supernaturepics", {
            "range": "1-40",
            "url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",
        }),
        # suspended account (#2216)
        ("https://twitter.com/realDonaldTrump", {
            "exception": exception.NotFoundError,
        }),
        ("https://mobile.twitter.com/supernaturepics?p=i"),
        ("https://www.twitter.com/id:2976459548"),
        ("https://twitter.com/i/user/2976459548"),
        ("https://twitter.com/intent/user?user_id=2976459548"),
    )

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        user_id = match.group(2)
        if user_id:
            self.user = "id:" + user_id

    def tweets(self):
        return self.api.user_tweets(self.user)


class TwitterRepliesExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's timeline including replies"""
    subcategory = "replies"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/with_replies(?!\w)"
    test = (
        ("https://twitter.com/supernaturepics/with_replies", {
            "range": "1-40",
            "url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",
        }),
        ("https://mobile.twitter.com/supernaturepics/with_replies#t"),
        ("https://www.twitter.com/id:2976459548/with_replies"),
    )

    def tweets(self):
        return self.api.user_tweets_and_replies(self.user)


class TwitterMediaExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's Media timeline"""
    subcategory = "media"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/media(?!\w)"
    test = (
        ("https://twitter.com/supernaturepics/media", {
            "range": "1-40",
            "url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",
        }),
        ("https://mobile.twitter.com/supernaturepics/media#t"),
        ("https://www.twitter.com/id:2976459548/media"),
    )

    def tweets(self):
        return self.api.user_media(self.user)


class TwitterLikesExtractor(TwitterExtractor):
    """Extractor for liked tweets"""
    subcategory = "likes"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/likes(?!\w)"
    test = ("https://twitter.com/supernaturepics/likes",)

    def metadata(self):
        return {"user_likes": self.user}

    def tweets(self):
        return self.api.user_likes(self.user)


class TwitterBookmarkExtractor(TwitterExtractor):
    """Extractor for bookmarked tweets"""
    subcategory = "bookmark"
    pattern = BASE_PATTERN + r"/i/bookmarks()"
    test = ("https://twitter.com/i/bookmarks",)

    def tweets(self):
        return self.api.user_bookmarks()


class TwitterListExtractor(TwitterExtractor):
    """Extractor for Twitter lists"""
    subcategory = "list"
    pattern = BASE_PATTERN + r"/i/lists/(\d+)/?$"
    test = ("https://twitter.com/i/lists/784214683683127296", {
        "range": "1-40",
        "count": 40,
        "archive": False,
    })

    def tweets(self):
        return self.api.list_latest_tweets_timeline(self.user)


class TwitterListMembersExtractor(TwitterExtractor):
    """Extractor for members of a Twitter list"""
    subcategory = "list-members"
    pattern = BASE_PATTERN + r"/i/lists/(\d+)/members"
    test = ("https://twitter.com/i/lists/784214683683127296/members",)

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).list_members(self.user))


class TwitterFollowingExtractor(TwitterExtractor):
    """Extractor for followed users"""
    subcategory = "following"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/following(?!\w)"
    test = (
        ("https://twitter.com/supernaturepics/following"),
        ("https://www.twitter.com/id:2976459548/following"),
    )

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).user_following(self.user))


class TwitterSearchExtractor(TwitterExtractor):
    """Extractor for Twitter search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?(?:[^&#]+&)*q=([^&#]+)"
    test = ("https://twitter.com/search?q=nature", {
        "range": "1-40",
        "count": 40,
        "archive": False,
    })

    def metadata(self):
        return {"search": text.unquote(self.user)}

    def tweets(self):
        return self.api.search_adaptive(text.unquote(self.user))


class TwitterEventExtractor(TwitterExtractor):
    """Extractor for Tweets from a Twitter Event"""
    subcategory = "event"
    directory_fmt = ("{category}", "Events",
                     "{event[id]} {event[short_title]}")
    pattern = BASE_PATTERN + r"/i/events/(\d+)"
    test = ("https://twitter.com/i/events/1484669206993903616", {
        "range": "1-20",
        "count": ">5",
    })

    def metadata(self):
        return {"event": self.api.live_event(self.user)}

    def tweets(self):
        return self.api.live_event_timeline(self.user)


class TwitterTweetExtractor(TwitterExtractor):
    """Extractor for images from individual tweets"""
    subcategory = "tweet"
    pattern = BASE_PATTERN + r"/([^/?#]+|i/web)/status/(\d+)"
    test = (
        ("https://twitter.com/supernaturepics/status/604341487988576256", {
            "url": "88a40f7d25529c2501c46f2218f9e0de9aa634b4",
            "content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",
        }),
        # 4 images
        ("https://twitter.com/perrypumas/status/894001459754180609", {
            "url": "3a2a43dc5fb79dd5432c701d8e55e87c4e551f47",
        }),
        # video
        ("https://twitter.com/perrypumas/status/1065692031626829824", {
            "pattern": r"https://video.twimg.com/ext_tw_video/.+\.mp4\?tag=5",
        }),
        # content with emoji, newlines, hashtags (#338)
        ("https://twitter.com/playpokemon/status/1263832915173048321", {
            "keyword": {"content": (
                r"re:Gear up for #PokemonSwordShieldEX with special Mystery "
                "Gifts! \n\nYou’ll be able to receive four Galarian form "
                "Pokémon with Hidden Abilities, plus some very useful items. "
                "It’s our \\(Mystery\\) Gift to you, Trainers! \n\n❓🎁➡️ "
            )},
        }),
        # Reply to deleted tweet (#403, #838)
        ("https://twitter.com/i/web/status/1170041925560258560", {
            "pattern": r"https://pbs.twimg.com/media/EDzS7VrU0AAFL4_",
        }),
        # 'replies' option (#705)
        ("https://twitter.com/i/web/status/1170041925560258560", {
            "options": (("replies", False),),
            "count": 0,
        }),
        # 'replies' to self (#1254)
        ("https://twitter.com/i/web/status/1424882930803908612", {
            "options": (("replies", "self"),),
            "count": 4,
            "keyword": {"user": {
                "description": "re:business email-- rhettaro.bloom@gmail.com "
                               "patreon- http://patreon.com/Princecanary",
                "url": "http://princecanary.tumblr.com",
            }},
        }),
        ("https://twitter.com/i/web/status/1424898916156284928", {
            "options": (("replies", "self"),),
            "count": 0,
        }),
        # "quoted" option (#854)
        ("https://twitter.com/StobiesGalaxy/status/1270755918330896395", {
            "options": (("quoted", True),),
            "pattern": r"https://pbs\.twimg\.com/media/Ea[KG].+=jpg",
            "count": 8,
        }),
        # quoted tweet (#526, #854)
        ("https://twitter.com/StobiesGalaxy/status/1270755918330896395", {
            "pattern": r"https://pbs\.twimg\.com/media/EaK.+=jpg",
            "count": 4,
        }),
        # TwitPic embeds (#579)
        ("https://twitter.com/i/web/status/112900228289540096", {
            "options": (("twitpic", True), ("cards", False)),
            "pattern": r"https://\w+.cloudfront.net/photos/large/\d+.jpg",
            "count": 3,
        }),
        # Nitter tweet (#890)
        ("https://nitter.net/ed1conf/status/1163841619336007680", {
            "url": "4a9ea898b14d3c112f98562d0df75c9785e239d9",
            "content": "f29501e44d88437fe460f5c927b7543fda0f6e34",
        }),
        # Twitter card (#1005)
        ("https://twitter.com/billboard/status/1306599586602135555", {
            "options": (("cards", True),),
            "pattern": r"https://pbs.twimg.com/card_img/\d+/",
        }),
        # unified_card with image_carousel_website
        ("https://twitter.com/doax_vv_staff/status/1479438945662685184", {
            "options": (("cards", True),),
            "pattern": r"https://pbs\.twimg\.com/media/F.+=png",
            "count": 6,
        }),
        # unified_card without type
        ("https://twitter.com/i/web/status/1466183847628865544", {
            "count": 0,
        }),
        # original retweets (#1026)
        ("https://twitter.com/jessica_3978/status/1296304589591810048", {
            "options": (("retweets", "original"),),
            "count": 2,
            "keyword": {
                "tweet_id"  : 1296296016002547713,
                "retweet_id": 1296296016002547713,
                "date"      : "dt:2020-08-20 04:00:28",
            },
        }),
        # all Tweets from a conversation (#1319)
        ("https://twitter.com/BlankArts_/status/1323314488611872769", {
            "options": (("conversations", True),),
            "count": ">= 50",
        }),
        # retweet with missing media entities (#1555)
        ("https://twitter.com/morino_ya/status/1392763691599237121", {
            "options": (("retweets", True),),
            "count": 4,
        }),
        # deleted quote tweet (#2225)
        ("https://twitter.com/i/web/status/1460044411165888515", {
            "count": 0,
        }),
        # "Misleading" content
        ("https://twitter.com/i/web/status/1486373748911575046", {
            "count": 4,
        }),
    )

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        self.tweet_id = match.group(2)

    def tweets(self):
        if self.config("conversations", False):
            return self.api.tweet_detail(self.tweet_id)

        tweets = []
        tweet_id = self.tweet_id
        for tweet in self.api.tweet_detail(tweet_id):
            if tweet["rest_id"] == tweet_id or \
                    tweet.get("_retweet_id_str") == tweet_id:
                tweets.append(tweet)

                tweet_id = tweet["legacy"].get("quoted_status_id_str")
                if not tweet_id:
                    break
        return tweets


class TwitterImageExtractor(Extractor):
    category = "twitter"
    subcategory = "image"
    pattern = r"https?://pbs\.twimg\.com/media/([\w-]+)(?:\?format=|\.)(\w+)"
    test = (
        ("https://pbs.twimg.com/media/EqcpviCVoAAG-QG?format=jpg&name=orig", {
            "options": (("size", "4096x4096,orig"),),
            "url": "cb3042a6f6826923da98f0d2b66c427e9385114c",
        }),
        ("https://pbs.twimg.com/media/EqcpviCVoAAG-QG.jpg:orig"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.id, self.fmt = match.groups()
        TwitterExtractor._init_sizes(self)

    def items(self):
        base = "https://pbs.twimg.com/media/{}?format={}&name=".format(
            self.id, self.fmt)

        data = {
            "filename": self.id,
            "extension": self.fmt,
            "_fallback": TwitterExtractor._image_fallback(self, base),
        }

        yield Message.Directory, data
        yield Message.Url, base + self._size_image, data


class TwitterAPI():

    def __init__(self, extractor):
        self.extractor = extractor

        self.root = "https://twitter.com/i/api"
        self.headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejR"
                             "COuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu"
                             "4FA33AGWWjCpTnA",
            "x-guest-token": None,
            "x-twitter-auth-type": None,
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "x-csrf-token": None,
            "Referer": "https://twitter.com/",
        }
        self.params = {
            "include_profile_interstitial_type": "1",
            "include_blocking": "1",
            "include_blocked_by": "1",
            "include_followed_by": "1",
            "include_want_retweets": "1",
            "include_mute_edge": "1",
            "include_can_dm": "1",
            "include_can_media_tag": "1",
            "include_ext_has_nft_avatar": "1",
            "skip_status": "1",
            "cards_platform": "Web-12",
            "include_cards": "1",
            "include_ext_alt_text": "true",
            "include_quote_count": "true",
            "include_reply_count": "1",
            "tweet_mode": "extended",
            "include_entities": "true",
            "include_user_entities": "true",
            "include_ext_media_color": "true",
            "include_ext_media_availability": "true",
            "include_ext_sensitive_media_warning": "true",
            "send_error_codes": "true",
            "simple_quoted_tweet": "true",
            "count": "100",
            "cursor": None,
            "ext": "mediaStats,highlightedLabel,hasNftAvatar,"
                   "voiceInfo,superFollowMetadata",
        }
        self.variables = {
            "includePromotedContent": False,
            "withSuperFollowsUserFields": True,
            "withBirdwatchPivots": False,
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
            "withV2Timeline": False,
            "__fs_interactive_text": False,
            "__fs_dont_mention_me_view_api_enabled": False,
        }

        self._nsfw_warning = True
        self._json_dumps = json.JSONEncoder(separators=(",", ":")).encode
        self._user = None

        cookies = extractor.session.cookies
        cookiedomain = extractor.cookiedomain

        # CSRF
        csrf_token = cookies.get("ct0", domain=cookiedomain)
        if not csrf_token:
            csrf_token = util.generate_token()
            cookies.set("ct0", csrf_token, domain=cookiedomain)
        self.headers["x-csrf-token"] = csrf_token

        if cookies.get("auth_token", domain=cookiedomain):
            # logged in
            self.headers["x-twitter-auth-type"] = "OAuth2Session"
        else:
            # guest
            guest_token = self._guest_token()
            cookies.set("gt", guest_token, domain=cookiedomain)
            self.headers["x-guest-token"] = guest_token

    def tweet_detail(self, tweet_id):
        endpoint = "/graphql/ItejhtHVxU7ksltgMmyaLA/TweetDetail"
        variables = {
            "focalTweetId": tweet_id,
            "with_rux_injections": False,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withBirdwatchNotes": False,
        }
        return self._pagination_tweets(
            endpoint, variables, ("threaded_conversation_with_injections",))

    def user_tweets(self, screen_name):
        endpoint = "/graphql/WZT7sCTrLvSOaWOXLDsWbQ/UserTweets"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "withQuickPromoteEligibilityTweetFields": True,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_tweets_and_replies(self, screen_name):
        endpoint = "/graphql/t4wEKVulW4Mbv1P0kgxTEw/UserTweetsAndReplies"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "withCommunity": True,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_media(self, screen_name):
        endpoint = "/graphql/nRybED9kRbN-TOWioHq1ng/UserMedia"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_likes(self, screen_name):
        endpoint = "/graphql/9MSTt44HoGjVFSg_u3rHDw/Likes"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_bookmarks(self):
        endpoint = "/graphql/uKP9v_I31k0_VSBmlpq2Xg/Bookmarks"
        variables = {
            "count": 100,
        }
        return self._pagination_tweets(
            endpoint, variables, ("bookmark_timeline", "timeline"))

    def list_latest_tweets_timeline(self, list_id):
        endpoint = "/graphql/z3l-EHlx-fyg8OvGO4JN8A/ListLatestTweetsTimeline"
        variables = {
            "listId": list_id,
            "count": 100,
        }
        return self._pagination_tweets(
            endpoint, variables, ("list", "tweets_timeline", "timeline"))

    def search_adaptive(self, query):
        endpoint = "/2/search/adaptive.json"
        params = self.params.copy()
        params["q"] = query
        params["tweet_search_mode"] = "live"
        params["query_source"] = "typed_query"
        params["pc"] = "1"
        params["spelling_corrections"] = "1"
        return self._pagination_legacy(endpoint, params)

    def live_event_timeline(self, event_id):
        endpoint = "/2/live_event/timeline/{}.json".format(event_id)
        params = self.params.copy()
        params["timeline_id"] = "recap"
        params["urt"] = "true"
        params["get_annotations"] = "true"
        return self._pagination_legacy(endpoint, params)

    def live_event(self, event_id):
        endpoint = "/1.1/live_event/1/{}/timeline.json".format(event_id)
        params = self.params.copy()
        params["count"] = "0"
        params["urt"] = "true"
        return (self._call(endpoint, params)
                ["twitter_objects"]["live_events"][event_id])

    def list_by_rest_id(self, list_id):
        endpoint = "/graphql/BWEhzAk7k8TwbU4lKH2dpw/ListByRestId"
        params = {"variables": self._json_dumps({
            "listId": list_id,
            "withSuperFollowsUserFields": True,
        })}
        try:
            return self._call(endpoint, params)["data"]["list"]
        except KeyError:
            raise exception.NotFoundError("list")

    def list_members(self, list_id):
        endpoint = "/graphql/snESM0DPs3c7M1SBm4rvVw/ListMembers"
        variables = {
            "listId": list_id,
            "count": 100,
            "withSafetyModeUserFields": True,
        }
        return self._pagination_users(
            endpoint, variables, ("list", "members_timeline", "timeline"))

    def user_following(self, screen_name):
        endpoint = "/graphql/mIwX8GogcobVlRwlgpHNYA/Following"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
        }
        return self._pagination_users(endpoint, variables)

    def user_by_rest_id(self, rest_id):
        endpoint = "/graphql/I5nvpI91ljifos1Y3Lltyg/UserByRestId"
        params = {"variables": self._json_dumps({
            "userId": rest_id,
            "withSafetyModeUserFields": True,
            "withSuperFollowsUserFields": True,
        })}
        return self._call(endpoint, params)["data"]["user"]["result"]

    def user_by_screen_name(self, screen_name):
        endpoint = "/graphql/7mjxD3-C6BxitPMVQ6w0-Q/UserByScreenName"
        params = {"variables": self._json_dumps({
            "screen_name": screen_name,
            "withSafetyModeUserFields": True,
            "withSuperFollowsUserFields": True,
        })}
        return self._call(endpoint, params)["data"]["user"]["result"]

    def _user_id_by_screen_name(self, screen_name):
        if screen_name.startswith("id:"):
            self._user = util.SENTINEL
            return screen_name[3:]

        user = ()
        try:
            user = self._user = self.user_by_screen_name(screen_name)
            return user["rest_id"]
        except KeyError:
            if "unavailable_message" in user:
                raise exception.NotFoundError("{} ({})".format(
                    user["unavailable_message"].get("text"),
                    user.get("reason")), False)
            else:
                raise exception.NotFoundError("user")

    @cache(maxage=3600)
    def _guest_token(self):
        root = "https://api.twitter.com"
        endpoint = "/1.1/guest/activate.json"
        return str(self._call(endpoint, None, root, "POST")["guest_token"])

    def _call(self, endpoint, params, root=None, method="GET"):
        if root is None:
            root = self.root

        while True:
            response = self.extractor.request(
                root + endpoint, method=method, params=params,
                headers=self.headers, fatal=None)

            # update 'x-csrf-token' header (#1170)
            csrf_token = response.cookies.get("ct0")
            if csrf_token:
                self.headers["x-csrf-token"] = csrf_token

            if response.status_code < 400:
                # success
                return response.json()

            if response.status_code == 429:
                # rate limit exceeded
                until = response.headers.get("x-rate-limit-reset")
                seconds = None if until else 60
                self.extractor.wait(until=until, seconds=seconds)
                continue

            # error
            try:
                data = response.json()
                errors = ", ".join(e["message"] for e in data["errors"])
            except ValueError:
                errors = response.text
            except Exception:
                errors = data.get("errors", "")

            raise exception.StopExtraction(
                "%s %s (%s)", response.status_code, response.reason, errors)

    def _pagination_legacy(self, endpoint, params):
        original_retweets = (self.extractor.retweets == "original")

        while True:
            cursor = tweet = None
            data = self._call(endpoint, params)

            instr = data["timeline"]["instructions"]
            if not instr:
                return
            tweet_ids = []
            tweets = data["globalObjects"]["tweets"]
            users = data["globalObjects"]["users"]

            # collect tweet IDs and cursor value
            for entry in instr[0]["addEntries"]["entries"]:
                entry_startswith = entry["entryId"].startswith

                if entry_startswith(("tweet-", "sq-I-t-")):
                    tweet_ids.append(
                        entry["content"]["item"]["content"]["tweet"]["id"])

                elif entry_startswith("homeConversation-"):
                    tweet_ids.extend(
                        entry["content"]["timelineModule"]["metadata"]
                        ["conversationMetadata"]["allTweetIds"][::-1])

                elif entry_startswith(("cursor-bottom-", "sq-cursor-bottom")):
                    cursor = entry["content"]["operation"]["cursor"]
                    if not cursor.get("stopOnEmptyResponse", True):
                        # keep going even if there are no tweets
                        tweet = True
                    cursor = cursor["value"]

                elif entry_startswith("conversationThread-"):
                    tweet_ids.extend(
                        item["entryId"][6:]
                        for item in entry["content"]["timelineModule"]["items"]
                        if item["entryId"].startswith("tweet-")
                    )

            # process tweets
            for tweet_id in tweet_ids:
                try:
                    tweet = tweets[tweet_id]
                except KeyError:
                    self.extractor.log.debug("Skipping %s (deleted)", tweet_id)
                    continue

                if "retweeted_status_id_str" in tweet:
                    retweet = tweets.get(tweet["retweeted_status_id_str"])
                    if original_retweets:
                        if not retweet:
                            continue
                        retweet["retweeted_status_id_str"] = retweet["id_str"]
                        retweet["_retweet_id_str"] = tweet["id_str"]
                        tweet = retweet
                    elif retweet:
                        tweet["author"] = users[retweet["user_id_str"]]
                        if "extended_entities" in retweet and \
                                "extended_entities" not in tweet:
                            tweet["extended_entities"] = \
                                retweet["extended_entities"]
                tweet["user"] = users[tweet["user_id_str"]]
                yield tweet

                if "quoted_status_id_str" in tweet:
                    quoted = tweets.get(tweet["quoted_status_id_str"])
                    if quoted:
                        quoted = quoted.copy()
                        quoted["author"] = users[quoted["user_id_str"]]
                        quoted["user"] = tweet["user"]
                        quoted["quoted_by_id_str"] = tweet["id_str"]
                        yield quoted

            # update cursor value
            if "replaceEntry" in instr[-1] :
                cursor = (instr[-1]["replaceEntry"]["entry"]
                          ["content"]["operation"]["cursor"]["value"])

            if not cursor or not tweet:
                return
            params["cursor"] = cursor

    def _pagination_tweets(self, endpoint, variables, path=None):
        extr = self.extractor
        variables.update(self.variables)
        original_retweets = (extr.retweets == "original")
        pinned_tweet = extr.pinned

        while True:
            params = {"variables": self._json_dumps(variables)}
            data = self._call(endpoint, params)["data"]

            try:
                if path is None:
                    instructions = (data["user"]["result"]["timeline"]
                                    ["timeline"]["instructions"])
                else:
                    instructions = data
                    for key in path:
                        instructions = instructions[key]
                    instructions = instructions["instructions"]

                for instr in instructions:
                    if instr.get("type") == "TimelineAddEntries":
                        entries = instr["entries"]
                        break
                else:
                    raise KeyError()

            except LookupError:
                extr.log.debug(data)

                if self._user:
                    user = self._user
                    if user is util.SENTINEL:
                        try:
                            user = self.user_by_rest_id(variables["userId"])
                        except KeyError:
                            raise exception.NotFoundError("user")
                    user = user.get("legacy")
                    if not user:
                        pass
                    elif user.get("blocked_by"):
                        if self.headers["x-twitter-auth-type"] and \
                                extr.config("logout"):
                            guest_token = self._guest_token()
                            extr.session.cookies.set(
                                "gt", guest_token, domain=extr.cookiedomain)
                            extr._cookiefile = None
                            del extr.session.cookies["auth_token"]
                            self.headers["x-guest-token"] = guest_token
                            self.headers["x-twitter-auth-type"] = None
                            extr.log.info("Retrying API request as guest")
                            continue
                        raise exception.AuthorizationError(
                            "{} blocked your account".format(
                                user["screen_name"]))
                    elif user.get("protected"):
                        raise exception.AuthorizationError(
                            "{}'s Tweets are protected".format(
                                user["screen_name"]))

                raise exception.StopExtraction(
                    "Unable to retrieve Tweets from this timeline")

            tweets = []
            tweet = cursor = None

            if pinned_tweet:
                pinned_tweet = False
                if instructions[-1]["type"] == "TimelinePinEntry":
                    tweets.append(instructions[-1]["entry"])

            for entry in entries:
                esw = entry["entryId"].startswith

                if esw("tweet-"):
                    tweets.append(entry)
                elif esw("homeConversation-"):
                    tweets.extend(entry["content"]["items"])
                elif esw("conversationthread-"):
                    tweets.extend(entry["content"]["items"])
                elif esw("tombstone-"):
                    self._report_tombstone(
                        entry,
                        entry["content"]["itemContent"]["tombstoneInfo"])
                elif esw("cursor-bottom-"):
                    cursor = entry["content"]
                    if not cursor.get("stopOnEmptyResponse", True):
                        # keep going even if there are no tweets
                        tweet = True
                    cursor = cursor.get("value")

            for entry in tweets:
                try:
                    tweet = ((entry.get("content") or entry["item"])
                             ["itemContent"]["tweet_results"]["result"])
                    if "tombstone" in tweet:
                        self._report_tombstone(entry, tweet["tombstone"])
                        continue
                    if "tweet" in tweet:
                        tweet = tweet["tweet"]
                    legacy = tweet["legacy"]
                except KeyError:
                    extr.log.debug(
                        "Skipping %s (deleted)",
                        (entry.get("entryId") or "").rpartition("-")[2])
                    continue

                if "retweeted_status_result" in legacy:
                    retweet = legacy["retweeted_status_result"]["result"]
                    if original_retweets:
                        try:
                            retweet["legacy"]["retweeted_status_id_str"] = \
                                retweet["rest_id"]
                            retweet["_retweet_id_str"] = tweet["rest_id"]
                            tweet = retweet
                        except KeyError:
                            continue
                    else:
                        try:
                            legacy["retweeted_status_id_str"] = \
                                retweet["rest_id"]
                            legacy["author"] = \
                                retweet["core"]["user_results"]["result"]
                            if "extended_entities" in retweet["legacy"] and \
                                    "extended_entities" not in legacy:
                                legacy["extended_entities"] = \
                                    retweet["legacy"]["extended_entities"]
                        except KeyError:
                            pass

                yield tweet

                if "quoted_status_result" in tweet:
                    try:
                        quoted = tweet["quoted_status_result"]["result"]
                        quoted["legacy"]["author"] = \
                            quoted["core"]["user_results"]["result"]
                        quoted["core"] = tweet["core"]
                        quoted["legacy"]["quoted_by_id_str"] = tweet["rest_id"]
                        yield quoted
                    except KeyError:
                        extr.log.debug(
                            "Skipping quote of %s (deleted)",
                            tweet.get("rest_id"))
                        continue

            if not tweet or not cursor:
                return
            variables["cursor"] = cursor

    def _pagination_users(self, endpoint, variables, path=None):
        variables.update(self.variables)

        while True:
            cursor = entry = stop = None
            params = {"variables": self._json_dumps(variables)}
            data = self._call(endpoint, params)["data"]

            try:
                if path is None:
                    instructions = (data["user"]["result"]["timeline"]
                                    ["timeline"]["instructions"])
                else:
                    for key in path:
                        data = data[key]
                    instructions = data["instructions"]
            except KeyError:
                return

            for instr in instructions:
                if instr["type"] == "TimelineAddEntries":
                    for entry in instr["entries"]:
                        if entry["entryId"].startswith("user-"):
                            user = (entry["content"]["itemContent"]
                                    ["user_results"]["result"])
                            if "rest_id" in user:
                                yield user
                        elif entry["entryId"].startswith("cursor-bottom-"):
                            cursor = entry["content"]["value"]
                elif instr["type"] == "TimelineTerminateTimeline":
                    if instr["direction"] == "Bottom":
                        stop = True

            if stop or not cursor or not entry:
                return
            variables["cursor"] = cursor

    def _report_tombstone(self, entry, tombstone):
        text = (tombstone.get("richText") or tombstone["text"])["text"]
        if text.startswith("Age-restricted") and self._nsfw_warning:
            self.extractor.log.warning(text)
            self._nsfw_warning = False
        self.extractor.log.debug(
            "Skipping %s (%s)", entry["entryId"].rpartition("-")[2], text)

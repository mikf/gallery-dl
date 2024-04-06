# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://twitter.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import itertools
import json
import re

BASE_PATTERN = (r"(?:https?://)?(?:www\.|mobile\.)?"
                r"(?:(?:[fv]x)?twitter|(?:fixup)?x)\.com")


class TwitterExtractor(Extractor):
    """Base class for twitter extractors"""
    category = "twitter"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{retweet_id}_{num}"
    cookies_domain = ".twitter.com"
    cookies_names = ("auth_token",)
    root = "https://twitter.com"
    browser = "firefox"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def _init(self):
        self.textonly = self.config("text-tweets", False)
        self.retweets = self.config("retweets", False)
        self.replies = self.config("replies", True)
        self.twitpic = self.config("twitpic", False)
        self.pinned = self.config("pinned", False)
        self.quoted = self.config("quoted", False)
        self.videos = self.config("videos", True)
        self.cards = self.config("cards", False)
        self.ads = self.config("ads", False)
        self.cards_blacklist = self.config("cards-blacklist")

        if not self.config("transform", True):
            self._transform_user = util.identity
            self._transform_tweet = util.identity
        self._user = None
        self._user_obj = None
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

        if self.config("expand"):
            tweets = self._expand_tweets(self.tweets())
            self.tweets = lambda : tweets

        if self.config("unique", True):
            seen_tweets = set()
        else:
            seen_tweets = None

        if self.twitpic:
            self._find_twitpic = re.compile(
                r"https?(://twitpic\.com/(?!photos/)\w+)").findall

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
                    data["user_id_str"] !=
                    (self._user_obj["rest_id"] if self._user else
                     data["in_reply_to_user_id_str"])
                )
            ):
                self.log.debug("Skipping %s (reply)", data["id_str"])
                continue

            if seen_tweets is not None:
                if data["id_str"] in seen_tweets:
                    self.log.debug(
                        "Skipping %s (previously seen)", data["id_str"])
                    continue
                seen_tweets.add(data["id_str"])

            if "withheld_scope" in data:
                txt = data.get("full_text") or data.get("text") or ""
                self.log.warning("'%s' (%s)", txt, data["id_str"])

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
            tdata["count"] = len(files)
            yield Message.Directory, tdata
            for tdata["num"], file in enumerate(files, 1):
                file.update(tdata)
                url = file.pop("url")
                if "extension" not in file:
                    text.nameext_from_url(url, file)
                yield Message.Url, url, file

    def _extract_media(self, tweet, entities, files):
        for media in entities:
            descr = media.get("ext_alt_text")
            width = media["original_info"].get("width", 0)
            height = media["original_info"].get("height", 0)

            if "video_info" in media:
                if self.videos == "ytdl":
                    files.append({
                        "url": "ytdl:{}/i/web/status/{}".format(
                            self.root, tweet["id_str"]),
                        "width"      : width,
                        "height"     : height,
                        "extension"  : None,
                        "description": descr,
                    })
                elif self.videos:
                    video_info = media["video_info"]
                    variant = max(
                        video_info["variants"],
                        key=lambda v: v.get("bitrate", 0),
                    )
                    files.append({
                        "url"        : variant["url"],
                        "width"      : width,
                        "height"     : height,
                        "bitrate"    : variant.get("bitrate", 0),
                        "duration"   : video_info.get(
                            "duration_millis", 0) / 1000,
                        "description": descr,
                    })
            elif "media_url_https" in media:
                url = media["media_url_https"]
                if url[-4] == ".":
                    base, _, fmt = url.rpartition(".")
                    base += "?format=" + fmt + "&name="
                else:
                    base = url.rpartition("=")[0] + "="
                files.append(text.nameext_from_url(url, {
                    "url"        : base + self._size_image,
                    "width"      : width,
                    "height"     : height,
                    "_fallback"  : self._image_fallback(base),
                    "description": descr,
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

        name = card["name"].rpartition(":")[2]
        bvals = card["binding_values"]
        if isinstance(bvals, list):
            bvals = {bval["key"]: bval["value"]
                     for bval in card["binding_values"]}

        cbl = self.cards_blacklist
        if cbl:
            if name in cbl:
                return
            if "vanity_url" in bvals:
                domain = bvals["vanity_url"]["string_value"]
                if domain in cbl or name + ":" + domain in cbl:
                    return

        if name in ("summary", "summary_large_image"):
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
            data = util.json_loads(bvals["unified_card"]["string_value"])
            self._extract_media(tweet, data["media_entities"].values(), files)
            return

        if self.cards == "ytdl":
            tweet_id = tweet.get("rest_id") or tweet["id_str"]
            url = "ytdl:{}/i/web/status/{}".format(self.root, tweet_id)
            files.append({"url": url})

    def _extract_twitpic(self, tweet, files):
        urls = {}

        # collect URLs from entities
        for url in tweet["entities"].get("urls") or ():
            url = url["expanded_url"]
            if "//twitpic.com/" not in url or "/photos/" in url:
                continue
            if url.startswith("http:"):
                url = "https" + url[4:]
            urls[url] = None

        # collect URLs from text
        for url in self._find_twitpic(
                tweet.get("full_text") or tweet.get("text") or ""):
            urls["https" + url] = None

        # extract actual URLs
        for url in urls:
            response = self.request(url, fatal=False)
            if response.status_code >= 400:
                continue
            url = text.extr(response.text, 'name="twitter:image" value="', '"')
            if url:
                files.append({"url": url})

    def _transform_tweet(self, tweet):
        if "author" in tweet:
            author = tweet["author"]
        elif "core" in tweet:
            author = tweet["core"]["user_results"]["result"]
        else:
            author = tweet["user"]
        author = self._transform_user(author)

        if "legacy" in tweet:
            legacy = tweet["legacy"]
        else:
            legacy = tweet
        tget = legacy.get

        tweet_id = int(legacy["id_str"])
        if tweet_id >= 300000000000000:
            date = text.parse_timestamp(
                ((tweet_id >> 22) + 1288834974657) // 1000)
        else:
            try:
                date = text.parse_datetime(
                    legacy["created_at"], "%a %b %d %H:%M:%S %z %Y")
            except Exception:
                date = util.NONE

        tdata = {
            "tweet_id"      : tweet_id,
            "retweet_id"    : text.parse_int(
                tget("retweeted_status_id_str")),
            "quote_id"      : text.parse_int(
                tget("quoted_by_id_str")),
            "reply_id"      : text.parse_int(
                tget("in_reply_to_status_id_str")),
            "conversation_id": text.parse_int(
                tget("conversation_id_str")),
            "date"          : date,
            "author"        : author,
            "user"          : self._user or author,
            "lang"          : legacy["lang"],
            "source"        : text.extr(tweet["source"], ">", "<"),
            "sensitive"     : tget("possibly_sensitive"),
            "favorite_count": tget("favorite_count"),
            "quote_count"   : tget("quote_count"),
            "reply_count"   : tget("reply_count"),
            "retweet_count" : tget("retweet_count"),
        }

        if "note_tweet" in tweet:
            note = tweet["note_tweet"]["note_tweet_results"]["result"]
            content = note["text"]
            entities = note["entity_set"]
        else:
            content = tget("full_text") or tget("text") or ""
            entities = legacy["entities"]

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

        content = text.unescape(content)
        urls = entities.get("urls")
        if urls:
            for url in urls:
                content = content.replace(url["url"], url["expanded_url"])
        txt, _, tco = content.rpartition(" ")
        tdata["content"] = txt if tco.startswith("https://t.co/") else content

        if "birdwatch_pivot" in tweet:
            try:
                tdata["birdwatch"] = \
                    tweet["birdwatch_pivot"]["subtitle"]["text"]
            except KeyError:
                self.log.debug("Unable to extract 'birdwatch' note from %s",
                               tweet["birdwatch_pivot"])
        if "in_reply_to_screen_name" in legacy:
            tdata["reply_to"] = legacy["in_reply_to_screen_name"]
        if "quoted_by" in legacy:
            tdata["quote_by"] = legacy["quoted_by"]
        if tdata["retweet_id"]:
            tdata["content"] = "RT @{}: {}".format(
                author["name"], tdata["content"])
            tdata["date_original"] = text.parse_timestamp(
                ((tdata["retweet_id"] >> 22) + 1288834974657) // 1000)

        return tdata

    def _transform_user(self, user):
        try:
            uid = user.get("rest_id") or user["id_str"]
        except KeyError:
            # private/invalid user (#4349)
            return {}

        try:
            return self._user_cache[uid]
        except KeyError:
            pass

        if "legacy" in user:
            user = user["legacy"]

        uget = user.get
        if uget("withheld_scope"):
            self.log.warning("'%s'", uget("description"))

        entities = user["entities"]
        self._user_cache[uid] = udata = {
            "id"              : text.parse_int(uid),
            "name"            : user["screen_name"],
            "nick"            : user["name"],
            "location"        : uget("location"),
            "date"            : text.parse_datetime(
                uget("created_at"), "%a %b %d %H:%M:%S %z %Y"),
            "verified"        : uget("verified", False),
            "protected"       : uget("protected", False),
            "profile_banner"  : uget("profile_banner_url", ""),
            "profile_image"   : uget(
                "profile_image_url_https", "").replace("_normal.", "."),
            "favourites_count": uget("favourites_count"),
            "followers_count" : uget("followers_count"),
            "friends_count"   : uget("friends_count"),
            "listed_count"    : uget("listed_count"),
            "media_count"     : uget("media_count"),
            "statuses_count"  : uget("statuses_count"),
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

    def _assign_user(self, user):
        self._user_obj = user
        self._user = self._transform_user(user)

    def _users_result(self, users):
        userfmt = self.config("users")
        if not userfmt or userfmt == "user":
            cls = TwitterUserExtractor
            fmt = (self.root + "/i/user/{rest_id}").format_map
        elif userfmt == "timeline":
            cls = TwitterTimelineExtractor
            fmt = (self.root + "/id:{rest_id}/timeline").format_map
        elif userfmt == "media":
            cls = TwitterMediaExtractor
            fmt = (self.root + "/id:{rest_id}/media").format_map
        elif userfmt == "tweets":
            cls = TwitterTweetsExtractor
            fmt = (self.root + "/id:{rest_id}/tweets").format_map
        else:
            cls = None
            fmt = userfmt.format_map

        for user in users:
            user["_extractor"] = cls
            yield Message.Queue, fmt(user), user

    def _expand_tweets(self, tweets):
        seen = set()
        for tweet in tweets:
            obj = tweet["legacy"] if "legacy" in tweet else tweet
            cid = obj.get("conversation_id_str")
            if not cid:
                tid = obj["id_str"]
                self.log.warning(
                    "Unable to expand %s (no 'conversation_id')", tid)
                continue
            if cid in seen:
                self.log.debug(
                    "Skipping expansion of %s (previously seen)", cid)
                continue
            seen.add(cid)
            try:
                yield from self.api.tweet_detail(cid)
            except Exception:
                yield tweet

    def _make_tweet(self, user, url, id_str):
        return {
            "id_str": id_str,
            "lang": None,
            "user": user,
            "source": "><",
            "entities": {},
            "extended_entities": {
                "media": [
                    {
                        "original_info": {},
                        "media_url": url,
                    },
                ],
            },
        }

    def metadata(self):
        """Return general metadata"""
        return {}

    def tweets(self):
        """Yield all relevant tweet objects"""

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(_login_impl(self, username, password))


class TwitterUserExtractor(TwitterExtractor):
    """Extractor for a Twitter user"""
    subcategory = "user"
    pattern = (BASE_PATTERN + r"/(?!search)(?:([^/?#]+)/?(?:$|[?#])"
               r"|i(?:/user/|ntent/user\?user_id=)(\d+))")
    example = "https://twitter.com/USER"

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        user_id = match.group(2)
        if user_id:
            self.user = "id:" + user_id

    def initialize(self):
        pass

    def items(self):
        base = "{}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (TwitterAvatarExtractor    , base + "photo"),
            (TwitterBackgroundExtractor, base + "header_photo"),
            (TwitterTimelineExtractor  , base + "timeline"),
            (TwitterTweetsExtractor    , base + "tweets"),
            (TwitterMediaExtractor     , base + "media"),
            (TwitterRepliesExtractor   , base + "with_replies"),
            (TwitterLikesExtractor     , base + "likes"),
        ), ("timeline",))


class TwitterTimelineExtractor(TwitterExtractor):
    """Extractor for a Twitter user timeline"""
    subcategory = "timeline"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/timeline(?!\w)"
    example = "https://twitter.com/USER/timeline"

    def tweets(self):
        # yield initial batch of (media) tweets
        tweet = None
        for tweet in self._select_tweet_source()(self.user):
            yield tweet
        if tweet is None:
            return

        # build search query
        query = "from:{} max_id:{}".format(
            self._user["name"], tweet["rest_id"])
        if self.retweets:
            query += " include:retweets include:nativeretweets"

        if not self.textonly:
            # try to search for media-only tweets
            tweet = None
            for tweet in self.api.search_timeline(query + " filter:links"):
                yield tweet
            if tweet is not None:
                return

        # yield unfiltered search results
        yield from self.api.search_timeline(query)

    def _select_tweet_source(self):
        strategy = self.config("strategy")
        if strategy is None or strategy == "auto":
            if self.retweets or self.textonly:
                return self.api.user_tweets
            else:
                return self.api.user_media
        if strategy == "tweets":
            return self.api.user_tweets
        if strategy == "media":
            return self.api.user_media
        if strategy == "with_replies":
            return self.api.user_tweets_and_replies
        raise exception.StopExtraction("Invalid strategy '%s'", strategy)


class TwitterTweetsExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's Tweets timeline"""
    subcategory = "tweets"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/tweets(?!\w)"
    example = "https://twitter.com/USER/tweets"

    def tweets(self):
        return self.api.user_tweets(self.user)


class TwitterRepliesExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's timeline including replies"""
    subcategory = "replies"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/with_replies(?!\w)"
    example = "https://twitter.com/USER/with_replies"

    def tweets(self):
        return self.api.user_tweets_and_replies(self.user)


class TwitterMediaExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's Media timeline"""
    subcategory = "media"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/media(?!\w)"
    example = "https://twitter.com/USER/media"

    def tweets(self):
        return self.api.user_media(self.user)


class TwitterLikesExtractor(TwitterExtractor):
    """Extractor for liked tweets"""
    subcategory = "likes"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/likes(?!\w)"
    example = "https://twitter.com/USER/likes"

    def metadata(self):
        return {"user_likes": self.user}

    def tweets(self):
        return self.api.user_likes(self.user)


class TwitterBookmarkExtractor(TwitterExtractor):
    """Extractor for bookmarked tweets"""
    subcategory = "bookmark"
    pattern = BASE_PATTERN + r"/i/bookmarks()"
    example = "https://twitter.com/i/bookmarks"

    def tweets(self):
        return self.api.user_bookmarks()

    def _transform_tweet(self, tweet):
        tdata = TwitterExtractor._transform_tweet(self, tweet)
        tdata["date_bookmarked"] = text.parse_timestamp(
            (int(tweet["sortIndex"] or 0) >> 20) // 1000)
        return tdata


class TwitterListExtractor(TwitterExtractor):
    """Extractor for Twitter lists"""
    subcategory = "list"
    pattern = BASE_PATTERN + r"/i/lists/(\d+)/?$"
    example = "https://twitter.com/i/lists/12345"

    def tweets(self):
        return self.api.list_latest_tweets_timeline(self.user)


class TwitterListMembersExtractor(TwitterExtractor):
    """Extractor for members of a Twitter list"""
    subcategory = "list-members"
    pattern = BASE_PATTERN + r"/i/lists/(\d+)/members"
    example = "https://twitter.com/i/lists/12345/members"

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).list_members(self.user))


class TwitterFollowingExtractor(TwitterExtractor):
    """Extractor for followed users"""
    subcategory = "following"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/following(?!\w)"
    example = "https://twitter.com/USER/following"

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).user_following(self.user))


class TwitterSearchExtractor(TwitterExtractor):
    """Extractor for Twitter search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?(?:[^&#]+&)*q=([^&#]+)"
    example = "https://twitter.com/search?q=QUERY"

    def metadata(self):
        return {"search": text.unquote(self.user)}

    def tweets(self):
        query = text.unquote(self.user.replace("+", " "))

        user = None
        for item in query.split():
            item = item.strip("()")
            if item.startswith("from:"):
                if user:
                    user = None
                    break
                else:
                    user = item[5:]

        if user is not None:
            try:
                self._assign_user(self.api.user_by_screen_name(user))
            except KeyError:
                pass

        return self.api.search_timeline(query)


class TwitterHashtagExtractor(TwitterExtractor):
    """Extractor for Twitter hashtags"""
    subcategory = "hashtag"
    pattern = BASE_PATTERN + r"/hashtag/([^/?#]+)"
    example = "https://twitter.com/hashtag/NAME"

    def items(self):
        url = "{}/search?q=%23{}".format(self.root, self.user)
        data = {"_extractor": TwitterSearchExtractor}
        yield Message.Queue, url, data


class TwitterCommunityExtractor(TwitterExtractor):
    """Extractor for a Twitter community"""
    subcategory = "community"
    pattern = BASE_PATTERN + r"/i/communities/(\d+)"
    example = "https://twitter.com/i/communities/12345"

    def tweets(self):
        if self.textonly:
            return self.api.community_tweets_timeline(self.user)
        return self.api.community_media_timeline(self.user)


class TwitterCommunitiesExtractor(TwitterExtractor):
    """Extractor for followed Twitter communities"""
    subcategory = "communities"
    pattern = BASE_PATTERN + r"/([^/?#]+)/communities/?$"
    example = "https://twitter.com/i/communities"

    def tweets(self):
        return self.api.communities_main_page_timeline(self.user)


class TwitterEventExtractor(TwitterExtractor):
    """Extractor for Tweets from a Twitter Event"""
    subcategory = "event"
    directory_fmt = ("{category}", "Events",
                     "{event[id]} {event[short_title]}")
    pattern = BASE_PATTERN + r"/i/events/(\d+)"
    example = "https://twitter.com/i/events/12345"

    def metadata(self):
        return {"event": self.api.live_event(self.user)}

    def tweets(self):
        return self.api.live_event_timeline(self.user)


class TwitterTweetExtractor(TwitterExtractor):
    """Extractor for individual tweets"""
    subcategory = "tweet"
    pattern = (BASE_PATTERN + r"/([^/?#]+|i/web)/status/(\d+)"
               r"/?(?:$|\?|#|photo/)")
    example = "https://twitter.com/USER/status/12345"

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        self.tweet_id = match.group(2)

    def tweets(self):
        conversations = self.config("conversations")
        if conversations:
            self._accessible = (conversations == "accessible")
            return self._tweets_conversation(self.tweet_id)

        endpoint = self.config("tweet-endpoint")
        if endpoint == "detail" or endpoint in (None, "auto") and \
                self.api.headers["x-twitter-auth-type"]:
            return self._tweets_detail(self.tweet_id)

        return self._tweets_single(self.tweet_id)

    def _tweets_single(self, tweet_id):
        tweet = self.api.tweet_result_by_rest_id(tweet_id)

        try:
            self._assign_user(tweet["core"]["user_results"]["result"])
        except KeyError:
            raise exception.StopExtraction(
                "'%s'", tweet.get("reason") or "Unavailable")

        yield tweet

        if not self.quoted:
            return

        while True:
            tweet_id = tweet["legacy"].get("quoted_status_id_str")
            if not tweet_id:
                break
            tweet = self.api.tweet_result_by_rest_id(tweet_id)
            tweet["legacy"]["quoted_by_id_str"] = tweet_id
            yield tweet

    def _tweets_detail(self, tweet_id):
        tweets = []

        for tweet in self.api.tweet_detail(tweet_id):
            if tweet["rest_id"] == tweet_id or \
                    tweet.get("_retweet_id_str") == tweet_id:
                if self._user_obj is None:
                    self._assign_user(tweet["core"]["user_results"]["result"])
                tweets.append(tweet)

                tweet_id = tweet["legacy"].get("quoted_status_id_str")
                if not tweet_id:
                    break

        return tweets

    def _tweets_conversation(self, tweet_id):
        tweets = self.api.tweet_detail(tweet_id)
        buffer = []

        for tweet in tweets:
            buffer.append(tweet)
            if tweet["rest_id"] == tweet_id or \
                    tweet.get("_retweet_id_str") == tweet_id:
                self._assign_user(tweet["core"]["user_results"]["result"])
                break
        else:
            # initial Tweet not accessible
            if self._accessible:
                return ()
            return buffer

        return itertools.chain(buffer, tweets)


class TwitterQuotesExtractor(TwitterExtractor):
    """Extractor for quotes of a Tweet"""
    subcategory = "quotes"
    pattern = BASE_PATTERN + r"/(?:[^/?#]+|i/web)/status/(\d+)/quotes"
    example = "https://twitter.com/USER/status/12345/quotes"

    def items(self):
        url = "{}/search?q=quoted_tweet_id:{}".format(self.root, self.user)
        data = {"_extractor": TwitterSearchExtractor}
        yield Message.Queue, url, data


class TwitterAvatarExtractor(TwitterExtractor):
    subcategory = "avatar"
    filename_fmt = "avatar {date}.{extension}"
    archive_fmt = "AV_{user[id]}_{date}"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/photo"
    example = "https://twitter.com/USER/photo"

    def tweets(self):
        self.api._user_id_by_screen_name(self.user)
        user = self._user_obj
        url = user["legacy"]["profile_image_url_https"]

        if url == ("https://abs.twimg.com/sticky"
                   "/default_profile_images/default_profile_normal.png"):
            return ()

        url = url.replace("_normal.", ".")
        id_str = url.rsplit("/", 2)[1]

        return (self._make_tweet(user, url, id_str),)


class TwitterBackgroundExtractor(TwitterExtractor):
    subcategory = "background"
    filename_fmt = "background {date}.{extension}"
    archive_fmt = "BG_{user[id]}_{date}"
    pattern = BASE_PATTERN + r"/(?!search)([^/?#]+)/header_photo"
    example = "https://twitter.com/USER/header_photo"

    def tweets(self):
        self.api._user_id_by_screen_name(self.user)
        user = self._user_obj

        try:
            url = user["legacy"]["profile_banner_url"]
            _, timestamp = url.rsplit("/", 1)
        except (KeyError, ValueError):
            return ()

        id_str = str((int(timestamp) * 1000 - 1288834974657) << 22)
        return (self._make_tweet(user, url, id_str),)


class TwitterImageExtractor(Extractor):
    category = "twitter"
    subcategory = "image"
    pattern = r"https?://pbs\.twimg\.com/media/([\w-]+)(?:\?format=|\.)(\w+)"
    example = "https://pbs.twimg.com/media/ABCDE?format=jpg&name=orig"

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
        self.log = extractor.log

        self.root = "https://twitter.com/i/api"
        self._nsfw_warning = True
        self._json_dumps = json.JSONEncoder(separators=(",", ":")).encode

        cookies = extractor.cookies
        cookies_domain = extractor.cookies_domain

        csrf = extractor.config("csrf")
        if csrf is None or csrf == "cookies":
            csrf_token = cookies.get("ct0", domain=cookies_domain)
        else:
            csrf_token = None
        if not csrf_token:
            csrf_token = util.generate_token()
            cookies.set("ct0", csrf_token, domain=cookies_domain)

        auth_token = cookies.get("auth_token", domain=cookies_domain)

        self.headers = {
            "Accept": "*/*",
            "Referer": "https://twitter.com/",
            "content-type": "application/json",
            "x-guest-token": None,
            "x-twitter-auth-type": "OAuth2Session" if auth_token else None,
            "x-csrf-token": csrf_token,
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejR"
                             "COuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu"
                             "4FA33AGWWjCpTnA",
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
            "include_ext_is_blue_verified": "1",
            "include_ext_verified_type": "1",
            "skip_status": "1",
            "cards_platform": "Web-12",
            "include_cards": "1",
            "include_ext_alt_text": "true",
            "include_ext_limited_action_results": "false",
            "include_quote_count": "true",
            "include_reply_count": "1",
            "tweet_mode": "extended",
            "include_ext_collab_control": "true",
            "include_ext_views": "true",
            "include_entities": "true",
            "include_user_entities": "true",
            "include_ext_media_color": "true",
            "include_ext_media_availability": "true",
            "include_ext_sensitive_media_warning": "true",
            "include_ext_trusted_friends_metadata": "true",
            "send_error_codes": "true",
            "simple_quoted_tweet": "true",
            "q": None,
            "count": "100",
            "query_source": None,
            "cursor": None,
            "pc": None,
            "spelling_corrections": None,
            "include_ext_edit_control": "true",
            "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,"
                   "enrichments,superFollowMetadata,unmentionInfo,editControl,"
                   "collab_control,vibe",
        }
        self.features = {
            "hidden_profile_likes_enabled": True,
            "hidden_profile_subscriptions_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_notes_tab_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_"
            "skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }
        self.features_pagination = {
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_"
            "image_extensions_enabled": False,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_"
            "limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        }

    def tweet_result_by_rest_id(self, tweet_id):
        endpoint = "/graphql/MWY3AO9_I3rcP_L2A4FR4A/TweetResultByRestId"
        variables = {
            "tweetId": tweet_id,
            "withCommunity": False,
            "includePromotedContent": False,
            "withVoice": False,
        }
        params = {
            "variables": self._json_dumps(variables),
            "features" : self._json_dumps(self.features_pagination),
        }
        tweet = self._call(endpoint, params)["data"]["tweetResult"]["result"]
        if "tweet" in tweet:
            tweet = tweet["tweet"]

        if tweet.get("__typename") == "TweetUnavailable":
            reason = tweet.get("reason")
            if reason == "NsfwLoggedOut":
                raise exception.AuthorizationError("NSFW Tweet")
            if reason == "Protected":
                raise exception.AuthorizationError("Protected Tweet")
            raise exception.StopExtraction("Tweet unavailable ('%s')", reason)

        return tweet

    def tweet_detail(self, tweet_id):
        endpoint = "/graphql/B9_KmbkLhXt6jRwGjJrweg/TweetDetail"
        variables = {
            "focalTweetId": tweet_id,
            "referrer": "profile",
            "with_rux_injections": False,
            "includePromotedContent": False,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withBirdwatchNotes": True,
            "withVoice": True,
            "withV2Timeline": True,
        }
        return self._pagination_tweets(
            endpoint, variables, ("threaded_conversation_with_injections_v2",))

    def user_tweets(self, screen_name):
        endpoint = "/graphql/5ICa5d9-AitXZrIA3H-4MQ/UserTweets"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_tweets_and_replies(self, screen_name):
        endpoint = "/graphql/UtLStR_BnYUGD7Q453UXQg/UserTweetsAndReplies"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withCommunity": True,
            "withVoice": True,
            "withV2Timeline": True,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_media(self, screen_name):
        endpoint = "/graphql/tO4LMUYAZbR4T0SqQ85aAw/UserMedia"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
            "withV2Timeline": True,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_likes(self, screen_name):
        endpoint = "/graphql/9s8V6sUI8fZLDiN-REkAxA/Likes"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
            "withV2Timeline": True,
        }
        return self._pagination_tweets(endpoint, variables)

    def user_bookmarks(self):
        endpoint = "/graphql/cQxQgX8MJYjWwC0dxpyfYg/Bookmarks"
        variables = {
            "count": 100,
            "includePromotedContent": False,
        }
        features = self.features_pagination.copy()
        features["graphql_timeline_v2_bookmark_timeline"] = True
        return self._pagination_tweets(
            endpoint, variables, ("bookmark_timeline_v2", "timeline"), False,
            features=features)

    def list_latest_tweets_timeline(self, list_id):
        endpoint = "/graphql/HjsWc-nwwHKYwHenbHm-tw/ListLatestTweetsTimeline"
        variables = {
            "listId": list_id,
            "count": 100,
        }
        return self._pagination_tweets(
            endpoint, variables, ("list", "tweets_timeline", "timeline"))

    def search_timeline(self, query):
        endpoint = "/graphql/fZK7JipRHWtiZsTodhsTfQ/SearchTimeline"
        variables = {
            "rawQuery": query,
            "count": 100,
            "querySource": "",
            "product": "Latest",
        }

        return self._pagination_tweets(
            endpoint, variables,
            ("search_by_raw_query", "search_timeline", "timeline"))

    def community_tweets_timeline(self, community_id):
        endpoint = "/graphql/7B2AdxSuC-Er8qUr3Plm_w/CommunityTweetsTimeline"
        variables = {
            "communityId": community_id,
            "count": 100,
            "displayLocation": "Community",
            "rankingMode": "Recency",
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("communityResults", "result", "ranked_community_timeline",
             "timeline"))

    def community_media_timeline(self, community_id):
        endpoint = "/graphql/qAGUldfcIoMv5KyAyVLYog/CommunityMediaTimeline"
        variables = {
            "communityId": community_id,
            "count": 100,
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("communityResults", "result", "community_media_timeline",
             "timeline"))

    def communities_main_page_timeline(self, screen_name):
        endpoint = ("/graphql/GtOhw2mstITBepTRppL6Uw"
                    "/CommunitiesMainPageTimeline")
        variables = {
            "count": 100,
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("viewer", "communities_timeline", "timeline"))

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

    def list_members(self, list_id):
        endpoint = "/graphql/BQp2IEYkgxuSxqbTAr1e1g/ListMembers"
        variables = {
            "listId": list_id,
            "count": 100,
            "withSafetyModeUserFields": True,
        }
        return self._pagination_users(
            endpoint, variables, ("list", "members_timeline", "timeline"))

    def user_following(self, screen_name):
        endpoint = "/graphql/PAnE9toEjRfE-4tozRcsfw/Following"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
        }
        return self._pagination_users(endpoint, variables)

    @memcache(keyarg=1)
    def user_by_rest_id(self, rest_id):
        endpoint = "/graphql/tD8zKvQzwY3kdx5yz6YmOw/UserByRestId"
        features = self.features
        params = {
            "variables": self._json_dumps({
                "userId": rest_id,
                "withSafetyModeUserFields": True,
            }),
            "features": self._json_dumps(features),
        }
        return self._call(endpoint, params)["data"]["user"]["result"]

    @memcache(keyarg=1)
    def user_by_screen_name(self, screen_name):
        endpoint = "/graphql/k5XapwcSikNsEsILW5FvgA/UserByScreenName"
        features = self.features.copy()
        features["subscriptions_verification_info_"
                 "is_identity_verified_enabled"] = True
        features["subscriptions_verification_info_"
                 "verified_since_enabled"] = True
        params = {
            "variables": self._json_dumps({
                "screen_name": screen_name,
                "withSafetyModeUserFields": True,
            }),
            "features": self._json_dumps(features),
        }
        return self._call(endpoint, params)["data"]["user"]["result"]

    def _user_id_by_screen_name(self, screen_name):
        user = ()
        try:
            if screen_name.startswith("id:"):
                user = self.user_by_rest_id(screen_name[3:])
            else:
                user = self.user_by_screen_name(screen_name)
            self.extractor._assign_user(user)
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
        endpoint = "/1.1/guest/activate.json"
        self.log.info("Requesting guest token")
        return str(self._call(
            endpoint, None, "POST", False, "https://api.twitter.com",
        )["guest_token"])

    def _authenticate_guest(self):
        guest_token = self._guest_token()
        if guest_token != self.headers["x-guest-token"]:
            self.headers["x-guest-token"] = guest_token
            self.extractor.cookies.set(
                "gt", guest_token, domain=self.extractor.cookies_domain)

    def _call(self, endpoint, params, method="GET", auth=True, root=None):
        url = (root or self.root) + endpoint

        while True:
            if not self.headers["x-twitter-auth-type"] and auth:
                self._authenticate_guest()

            response = self.extractor.request(
                url, method=method, params=params,
                headers=self.headers, fatal=None)

            # update 'x-csrf-token' header (#1170)
            csrf_token = response.cookies.get("ct0")
            if csrf_token:
                self.headers["x-csrf-token"] = csrf_token

            if response.status_code < 400:
                data = response.json()

                errors = data.get("errors")
                if not errors:
                    return data

                retry = False
                for error in errors:
                    msg = error.get("message") or "Unspecified"
                    self.log.debug("API error: '%s'", msg)

                    if "this account is temporarily locked" in msg:
                        msg = "Account temporarily locked"
                        if self.extractor.config("locked") != "wait":
                            raise exception.AuthorizationError(msg)
                        self.log.warning("%s. Press ENTER to retry.", msg)
                        try:
                            input()
                        except (EOFError, OSError):
                            pass
                        retry = True

                    elif msg.lower().startswith("timeout"):
                        retry = True

                if not retry:
                    return data
                elif self.headers["x-twitter-auth-type"]:
                    self.log.debug("Retrying API request")
                    continue

                # fall through to "Login Required"
                response.status_code = 404

            if response.status_code == 429:
                # rate limit exceeded
                if self.extractor.config("ratelimit") == "abort":
                    raise exception.StopExtraction("Rate limit exceeded")

                until = response.headers.get("x-rate-limit-reset")
                seconds = None if until else 60
                self.extractor.wait(until=until, seconds=seconds)
                continue

            if response.status_code in (403, 404) and \
                    not self.headers["x-twitter-auth-type"]:
                raise exception.AuthorizationError("Login required")

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
        bottom = ("cursor-bottom-", "sq-cursor-bottom")

        while True:
            data = self._call(endpoint, params)

            instructions = data["timeline"]["instructions"]
            if not instructions:
                return

            tweets = data["globalObjects"]["tweets"]
            users = data["globalObjects"]["users"]
            tweet_id = cursor = None
            tweet_ids = []
            entries = ()

            # process instructions
            for instr in instructions:
                if "addEntries" in instr:
                    entries = instr["addEntries"]["entries"]
                elif "replaceEntry" in instr:
                    entry = instr["replaceEntry"]["entry"]
                    if entry["entryId"].startswith(bottom):
                        cursor = (entry["content"]["operation"]
                                  ["cursor"]["value"])

            # collect tweet IDs and cursor value
            for entry in entries:
                entry_startswith = entry["entryId"].startswith

                if entry_startswith(("tweet-", "sq-I-t-")):
                    tweet_ids.append(
                        entry["content"]["item"]["content"]["tweet"]["id"])

                elif entry_startswith("homeConversation-"):
                    tweet_ids.extend(
                        entry["content"]["timelineModule"]["metadata"]
                        ["conversationMetadata"]["allTweetIds"][::-1])

                elif entry_startswith(bottom):
                    cursor = entry["content"]["operation"]["cursor"]
                    if not cursor.get("stopOnEmptyResponse", True):
                        # keep going even if there are no tweets
                        tweet_id = True
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
                    self.log.debug("Skipping %s (deleted)", tweet_id)
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
                        quoted["quoted_by"] = tweet["user"]["screen_name"]
                        quoted["quoted_by_id_str"] = tweet["id_str"]
                        yield quoted

            # stop on empty response
            if not cursor or (not tweets and not tweet_id):
                return
            params["cursor"] = cursor

    def _pagination_tweets(self, endpoint, variables,
                           path=None, stop_tweets=True, features=None):
        extr = self.extractor
        original_retweets = (extr.retweets == "original")
        pinned_tweet = extr.pinned

        params = {"variables": None}
        if features is None:
            features = self.features_pagination
        if features:
            params["features"] = self._json_dumps(features)

        while True:
            params["variables"] = self._json_dumps(variables)
            data = self._call(endpoint, params)["data"]

            try:
                if path is None:
                    instructions = (data["user"]["result"]["timeline_v2"]
                                    ["timeline"]["instructions"])
                else:
                    instructions = data
                    for key in path:
                        instructions = instructions[key]
                    instructions = instructions["instructions"]

                cursor = None
                entries = None
                for instr in instructions:
                    instr_type = instr.get("type")
                    if instr_type == "TimelineAddEntries":
                        if entries:
                            entries.extend(instr["entries"])
                        else:
                            entries = instr["entries"]
                    elif instr_type == "TimelineAddToModule":
                        entries = instr["moduleItems"]
                    elif instr_type == "TimelineReplaceEntry":
                        entry = instr["entry"]
                        if entry["entryId"].startswith("cursor-bottom-"):
                            cursor = entry["content"]["value"]
                if entries is None:
                    if not cursor:
                        return
                    entries = ()

            except LookupError:
                extr.log.debug(data)

                user = extr._user_obj
                if user:
                    user = user["legacy"]
                    if user.get("blocked_by"):
                        if self.headers["x-twitter-auth-type"] and \
                                extr.config("logout"):
                            extr.cookies_file = None
                            del extr.cookies["auth_token"]
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
            tweet = None

            if pinned_tweet:
                pinned_tweet = False
                if instructions[-1]["type"] == "TimelinePinEntry":
                    tweets.append(instructions[-1]["entry"])

            for entry in entries:
                esw = entry["entryId"].startswith

                if esw("tweet-"):
                    tweets.append(entry)
                elif esw(("profile-grid-",
                          "communities-grid-")):
                    if "content" in entry:
                        tweets.extend(entry["content"]["items"])
                    else:
                        tweets.append(entry)
                elif esw(("homeConversation-",
                          "profile-conversation-",
                          "conversationthread-")):
                    tweets.extend(entry["content"]["items"])
                elif esw("tombstone-"):
                    item = entry["content"]["itemContent"]
                    item["tweet_results"] = \
                        {"result": {"tombstone": item["tombstoneInfo"]}}
                    tweets.append(entry)
                elif esw("cursor-bottom-"):
                    cursor = entry["content"]
                    if "itemContent" in cursor:
                        cursor = cursor["itemContent"]
                    if not cursor.get("stopOnEmptyResponse", True):
                        # keep going even if there are no tweets
                        tweet = True
                    cursor = cursor.get("value")

            for entry in tweets:
                try:
                    item = ((entry.get("content") or entry["item"])
                            ["itemContent"])
                    if "promotedMetadata" in item and not extr.ads:
                        extr.log.debug(
                            "Skipping %s (ad)",
                            (entry.get("entryId") or "").rpartition("-")[2])
                        continue

                    tweet = item["tweet_results"]["result"]
                    if "tombstone" in tweet:
                        tweet = self._process_tombstone(
                            entry, tweet["tombstone"])
                        if not tweet:
                            continue

                    if "tweet" in tweet:
                        tweet = tweet["tweet"]
                    legacy = tweet["legacy"]
                    tweet["sortIndex"] = entry.get("sortIndex")
                except KeyError:
                    extr.log.debug(
                        "Skipping %s (deleted)",
                        (entry.get("entryId") or "").rpartition("-")[2])
                    continue

                if "retweeted_status_result" in legacy:
                    retweet = legacy["retweeted_status_result"]["result"]
                    if "tweet" in retweet:
                        retweet = retweet["tweet"]
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
                            tweet["author"] = \
                                retweet["core"]["user_results"]["result"]

                            rtlegacy = retweet["legacy"]

                            if "note_tweet" in retweet:
                                tweet["note_tweet"] = retweet["note_tweet"]

                            if "extended_entities" in rtlegacy and \
                                    "extended_entities" not in legacy:
                                legacy["extended_entities"] = \
                                    rtlegacy["extended_entities"]

                            if "withheld_scope" in rtlegacy and \
                                    "withheld_scope" not in legacy:
                                legacy["withheld_scope"] = \
                                    rtlegacy["withheld_scope"]

                            legacy["full_text"] = rtlegacy["full_text"]
                        except KeyError:
                            pass

                yield tweet

                if "quoted_status_result" in tweet:
                    try:
                        quoted = tweet["quoted_status_result"]["result"]
                        quoted["legacy"]["quoted_by"] = (
                            tweet["core"]["user_results"]["result"]
                            ["legacy"]["screen_name"])
                        quoted["legacy"]["quoted_by_id_str"] = tweet["rest_id"]
                        quoted["sortIndex"] = entry.get("sortIndex")

                        yield quoted
                    except KeyError:
                        extr.log.debug(
                            "Skipping quote of %s (deleted)",
                            tweet.get("rest_id"))
                        continue

            if stop_tweets and not tweet:
                return
            if not cursor or cursor == variables.get("cursor"):
                return
            variables["cursor"] = cursor

    def _pagination_users(self, endpoint, variables, path=None):
        params = {
            "variables": None,
            "features" : self._json_dumps(self.features_pagination),
        }

        while True:
            cursor = entry = None
            params["variables"] = self._json_dumps(variables)
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
                            try:
                                user = (entry["content"]["itemContent"]
                                        ["user_results"]["result"])
                            except KeyError:
                                pass
                            else:
                                if "rest_id" in user:
                                    yield user
                        elif entry["entryId"].startswith("cursor-bottom-"):
                            cursor = entry["content"]["value"]

            if not cursor or cursor.startswith(("-1|", "0|")) or not entry:
                return
            variables["cursor"] = cursor

    def _process_tombstone(self, entry, tombstone):
        text = (tombstone.get("richText") or tombstone["text"])["text"]
        tweet_id = entry["entryId"].rpartition("-")[2]

        if text.startswith("Age-restricted"):
            if self._nsfw_warning:
                self._nsfw_warning = False
                self.log.warning('"%s"', text)

        self.log.debug("Skipping %s ('%s')", tweet_id, text)


@cache(maxage=365*86400, keyarg=1)
def _login_impl(extr, username, password):

    import re
    import random

    if re.fullmatch(r"[\w.%+-]+@[\w.-]+\.\w{2,}", username):
        extr.log.warning(
            "Login with email is no longer possible. "
            "You need to provide your username or phone number instead.")

    def process(response):
        try:
            data = response.json()
        except ValueError:
            data = {"errors": ({"message": "Invalid response"},)}
        else:
            if response.status_code < 400:
                return data["flow_token"]

        errors = []
        for error in data.get("errors") or ():
            msg = error.get("message")
            errors.append('"{}"'.format(msg) if msg else "Unknown error")
        extr.log.debug(response.text)
        raise exception.AuthenticationError(", ".join(errors))

    extr.cookies.clear()
    api = TwitterAPI(extr)
    api._authenticate_guest()
    headers = api.headers

    extr.log.info("Logging in as %s", username)

    # init
    data = {
        "input_flow_data": {
            "flow_context": {
                "debug_overrides": {},
                "start_location": {"location": "unknown"},
            },
        },
        "subtask_versions": {
            "action_list": 2,
            "alert_dialog": 1,
            "app_download_cta": 1,
            "check_logged_in_account": 1,
            "choice_selection": 3,
            "contacts_live_sync_permission_prompt": 0,
            "cta": 7,
            "email_verification": 2,
            "end_flow": 1,
            "enter_date": 1,
            "enter_email": 2,
            "enter_password": 5,
            "enter_phone": 2,
            "enter_recaptcha": 1,
            "enter_text": 5,
            "enter_username": 2,
            "generic_urt": 3,
            "in_app_notification": 1,
            "interest_picker": 3,
            "js_instrumentation": 1,
            "menu_dialog": 1,
            "notifications_permission_prompt": 2,
            "open_account": 2,
            "open_home_timeline": 1,
            "open_link": 1,
            "phone_verification": 4,
            "privacy_options": 1,
            "security_key": 3,
            "select_avatar": 4,
            "select_banner": 2,
            "settings_list": 7,
            "show_code": 1,
            "sign_up": 2,
            "sign_up_review": 4,
            "tweet_selection_urt": 1,
            "update_users": 1,
            "upload_media": 1,
            "user_recommendations_list": 4,
            "user_recommendations_urt": 1,
            "wait_spinner": 3,
            "web_modal": 1,
        },
    }
    url = "https://api.twitter.com/1.1/onboarding/task.json?flow_name=login"
    response = extr.request(url, method="POST", headers=headers, json=data)

    data = {
        "flow_token": process(response),
        "subtask_inputs": [
            {
                "subtask_id": "LoginJsInstrumentationSubtask",
                "js_instrumentation": {
                    "response": "{}",
                    "link": "next_link",
                },
            },
        ],
    }
    url = "https://api.twitter.com/1.1/onboarding/task.json"
    response = extr.request(
        url, method="POST", headers=headers, json=data, fatal=None)

    # username
    data = {
        "flow_token": process(response),
        "subtask_inputs": [
            {
                "subtask_id": "LoginEnterUserIdentifierSSO",
                "settings_list": {
                    "setting_responses": [
                        {
                            "key": "user_identifier",
                            "response_data": {
                                "text_data": {"result": username},
                            },
                        },
                    ],
                    "link": "next_link",
                },
            },
        ],
    }
    #  url = "https://api.twitter.com/1.1/onboarding/task.json"
    extr.sleep(random.uniform(2.0, 4.0), "login (username)")
    response = extr.request(
        url, method="POST", headers=headers, json=data, fatal=None)

    # password
    data = {
        "flow_token": process(response),
        "subtask_inputs": [
            {
                "subtask_id": "LoginEnterPassword",
                "enter_password": {
                    "password": password,
                    "link": "next_link",
                },
            },
        ],
    }
    #  url = "https://api.twitter.com/1.1/onboarding/task.json"
    extr.sleep(random.uniform(2.0, 4.0), "login (password)")
    response = extr.request(
        url, method="POST", headers=headers, json=data, fatal=None)

    # account duplication check ?
    data = {
        "flow_token": process(response),
        "subtask_inputs": [
            {
                "subtask_id": "AccountDuplicationCheck",
                "check_logged_in_account": {
                    "link": "AccountDuplicationCheck_false",
                },
            },
        ],
    }
    #  url = "https://api.twitter.com/1.1/onboarding/task.json"
    response = extr.request(
        url, method="POST", headers=headers, json=data, fatal=None)
    process(response)

    return {
        cookie.name: cookie.value
        for cookie in extr.cookies
    }

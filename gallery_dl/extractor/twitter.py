# -*- coding: utf-8 -*-

# Copyright 2016-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://x.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache, memcache
import itertools
import random

BASE_PATTERN = (r"(?:https?://)?(?:www\.|mobile\.)?"
                r"(?:(?:[fv]x)?twitter|(?:fix(?:up|v))?x)\.com")
USER_PATTERN = rf"{BASE_PATTERN}/([^/?#]+)"


class TwitterExtractor(Extractor):
    """Base class for twitter extractors"""
    category = "twitter"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{tweet_id}_{num}.{extension}"
    archive_fmt = "{tweet_id}_{retweet_id}_{num}"
    cookies_domain = ".x.com"
    cookies_names = ("auth_token",)
    root = "https://x.com"
    browser = "firefox"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match[1]

    def _init(self):
        self.unavailable = self.config("unavailable", False)
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
            self._transform_community = \
                self._transform_tweet = \
                self._transform_user = util.identity

        self._cursor = None
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
        seen_tweets = set() if self.config("unique", True) else None

        if self.twitpic:
            self._find_twitpic = text.re(
                r"https?(://twitpic\.com/(?!photos/)\w+)").findall

        tweets = self.tweets()
        if self.config("expand"):
            tweets = self._expand_tweets(tweets)
        for tweet in tweets:

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

            files = self._extract_files(data, tweet)
            if not files and not self.textonly:
                continue

            tdata = self._transform_tweet(tweet)
            tdata.update(metadata)
            tdata["count"] = len(files)
            yield Message.Directory, "", tdata

            tdata.pop("source_id", None)
            tdata.pop("source_user", None)
            tdata.pop("sensitive_flags", None)

            for tdata["num"], file in enumerate(files, 1):
                file.update(tdata)
                url = file.pop("url")
                if "extension" not in file:
                    text.nameext_from_url(url, file)
                yield Message.Url, url, file

    def _extract_files(self, data, tweet):
        files = []

        if "extended_entities" in data:
            try:
                self._extract_media(
                    data, data["extended_entities"]["media"], files)
            except Exception as exc:
                self.log.traceback(exc)
                self.log.warning(
                    "%s: Error while extracting media files (%s: %s)",
                    data["id_str"], exc.__class__.__name__, exc)

        if self.cards and "card" in tweet:
            try:
                self._extract_card(tweet, files)
            except Exception as exc:
                self.log.traceback(exc)
                self.log.warning(
                    "%s: Error while extracting Card files (%s: %s)",
                    data["id_str"], exc.__class__.__name__, exc)

        if self.twitpic:
            try:
                self._extract_twitpic(data, files)
            except Exception as exc:
                self.log.traceback(exc)
                self.log.warning(
                    "%s: Error while extracting TwitPic files (%s: %s)",
                    data["id_str"], exc.__class__.__name__, exc)

        return files

    def _extract_media(self, tweet, entities, files):
        flags_tweet = None

        for media in entities:

            if "sensitive_media_warning" in media:
                flags_media = media["sensitive_media_warning"]

                flags = []
                if "adult_content" in flags_media:
                    flags.append("Nudity")
                if "other" in flags_media:
                    flags.append("Sensitive")
                if "graphic_violence" in flags_media:
                    flags.append("Violence")

                if flags_tweet is None:
                    flags_tweet = set(flags)
                else:
                    flags_tweet.update(flags)
                flags_media = flags
            else:
                flags_media = ()

            if "ext_media_availability" in media:
                ext = media["ext_media_availability"]
                if ext.get("status") == "Unavailable":
                    self.log.warning("Media unavailable (%s - '%s')",
                                     tweet["id_str"], ext.get("reason"))
                    if not self.unavailable:
                        continue

            if "video_info" in media:
                if self.videos == "ytdl":
                    url = f"ytdl:{self.root}/i/web/status/{tweet['id_str']}"
                    file = {"url": url, "extension": "mp4"}
                elif self.videos:
                    video_info = media["video_info"]
                    variant = max(
                        video_info["variants"],
                        key=lambda v: v.get("bitrate", 0),
                    )
                    file = {
                        "url"     : variant["url"],
                        "bitrate" : variant.get("bitrate", 0),
                        "duration": video_info.get(
                            "duration_millis", 0) / 1000,
                    }
                else:
                    continue
            elif "media_url_https" in media:
                url = media["media_url_https"]
                if url[-4] == ".":
                    base, _, fmt = url.rpartition(".")
                    base += "?format=" + fmt + "&name="
                else:
                    base = url.rpartition("=")[0] + "="
                file = text.nameext_from_url(url, {
                    "url"      : base + self._size_image,
                    "_fallback": self._image_fallback(base),
                })
            else:
                files.append({"url": media["media_url"]})
                continue

            file["type"] = media.get("type")
            file["width"] = media["original_info"].get("width", 0)
            file["height"] = media["original_info"].get("height", 0)
            file["description"] = media.get("ext_alt_text")
            file["sensitive_flags"] = flags_media
            self._extract_media_source(file, media)
            files.append(file)

        tweet["sensitive_flags"] = \
            () if flags_tweet is None else sorted(flags_tweet)

    def _extract_media_source(self, dest, media):
        dest["source_id"] = 0

        if "source_status_id_str" in media:
            try:
                dest["source_id"] = text.parse_int(
                    media["source_status_id_str"])
                dest["source_user"] = self._transform_user(
                    media["additional_media_info"]["source_user"]
                    ["user_results"]["result"])
            except Exception:
                pass

    def _image_fallback(self, base):
        for fmt in self._size_fallback:
            yield base + fmt

    def _extract_components(self, tweet, data, files):
        for component_id in data["components"]:
            com = data["component_objects"][component_id]
            for conv in com["data"].get("conversation_preview") or ():
                for url in conv.get("mediaUrls") or ():
                    files.append({"url": url})

    def _extract_card(self, tweet, files):
        card = tweet["card"]
        if "legacy" in card:
            card = card["legacy"]

        name = card["name"].rpartition(":")[2]
        bvals = card["binding_values"]
        if isinstance(bvals, list):
            bvals = {bval["key"]: bval["value"]
                     for bval in card["binding_values"]}

        if cbl := self.cards_blacklist:
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
            if "media_entities" in data:
                self._extract_media(
                    tweet, data["media_entities"].values(), files)
            if "component_objects" in data:
                self._extract_components(tweet, data, files)
            return

        if self.cards == "ytdl":
            tweet_id = tweet.get("rest_id") or tweet["id_str"]
            url = f"ytdl:{self.root}/i/web/status/{tweet_id}"
            files.append({"url": url})

    def _extract_twitpic(self, tweet, files):
        urls = {}

        # collect URLs from entities
        for url in tweet["entities"].get("urls") or ():
            url = url.get("expanded_url") or url.get("url") or ""
            if not url or "//twitpic.com/" not in url or "/photos/" in url:
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
            if url := text.extr(
                    response.text, 'name="twitter:image" value="', '"'):
                files.append({"url": url})

    def _transform_tweet(self, tweet):
        if "legacy" in tweet:
            legacy = tweet["legacy"]
        else:
            legacy = tweet
        tweet_id = int(legacy["id_str"])

        if "author" in tweet:
            author = tweet["author"]
        elif "core" in tweet:
            try:
                author = tweet["core"]["user_results"]["result"]
            except KeyError:
                self.log.warning("%s: Missing 'author' data", tweet_id)
                author = util.NONE
        else:
            author = tweet["user"]
        author = self._transform_user(author)

        if tweet_id >= 300000000000000:
            date = self.parse_timestamp(
                ((tweet_id >> 22) + 1288834974657) // 1000)
        else:
            try:
                date = self.parse_datetime(
                    legacy["created_at"], "%a %b %d %H:%M:%S %z %Y")
            except Exception:
                date = util.NONE
        source = tweet.get("source")

        tget = legacy.get
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
            "source_id"     : 0,
            "date"          : date,
            "author"        : author,
            "user"          : self._user or author,
            "lang"          : legacy["lang"],
            "source"        : text.extr(source, ">", "<") if source else "",
            "sensitive"     : tget("possibly_sensitive"),
            "sensitive_flags": tget("sensitive_flags"),
            "favorite_count": tget("favorite_count"),
            "quote_count"   : tget("quote_count"),
            "reply_count"   : tget("reply_count"),
            "retweet_count" : tget("retweet_count"),
            "bookmark_count": tget("bookmark_count"),
        }

        if "views" in tweet:
            try:
                tdata["view_count"] = int(tweet["views"]["count"])
            except Exception:
                tdata["view_count"] = 0
        else:
            tdata["view_count"] = 0

        if "note_tweet" in tweet:
            note = tweet["note_tweet"]["note_tweet_results"]["result"]
            content = note["text"]
            entities = note["entity_set"]
        else:
            content = tget("full_text") or tget("text") or ""
            entities = legacy["entities"]

        if "author_community_relationship" in tweet:
            tdata["community"] = self._transform_community(
                tweet["author_community_relationship"]
                ["community_results"]["result"])

        if hashtags := entities.get("hashtags"):
            tdata["hashtags"] = [t["text"] for t in hashtags]

        if mentions := entities.get("user_mentions"):
            tdata["mentions"] = [{
                "id": text.parse_int(u["id_str"]),
                "name": u["screen_name"],
                "nick": u["name"],
            } for u in mentions]

        content = text.unescape(content)
        if urls := entities.get("urls"):
            for url in urls:
                try:
                    content = content.replace(url["url"], url["expanded_url"])
                except KeyError:
                    pass
        txt, _, tco = content.rpartition(" ")
        tdata["content"] = txt if tco.startswith("https://t.co/") else content

        if "pinned" in tweet:
            tdata["pinned"] = True
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
        if "extended_entities" in legacy:
            self._extract_media_source(
                tdata, legacy["extended_entities"]["media"][0])
        if tdata["retweet_id"]:
            tdata["content"] = f"RT @{author['name']}: {tdata['content']}"
            tdata["date_original"] = self.parse_timestamp(
                ((tdata["retweet_id"] >> 22) + 1288834974657) // 1000)

        return tdata

    def _transform_community(self, com):
        try:
            cid = com.get("id_str") or com["rest_id"]
        except KeyError:
            return {}

        try:
            return self._user_cache[f"C#{cid}"]
        except KeyError:
            pass

        admin = creator = banner = None
        try:
            if results := com.get("admin_results"):
                admin = results["result"]["core"]["screen_name"]
        except Exception:
            pass
        try:
            if results := com.get("creator_results"):
                creator = results["result"]["core"]["screen_name"]
        except Exception:
            pass
        try:
            if results := com.get("custom_banner_media"):
                banner = results["media_info"]["original_img_url"]
        except Exception:
            pass

        self._user_cache[f"C#{cid}"] = cdata = {
            "id": text.parse_int(cid),
            "name": com.get("name"),
            "description": com.get("description"),
            "date": self.parse_timestamp(com.get("created_at", 0) // 1000),
            "nsfw": com.get("is_nsfw"),
            "role": com.get("role"),
            "member_count": com.get("member_count"),
            "rules": [rule["name"] for rule in com.get("rules", ())],
            "admin"  : admin,
            "creator": creator,
            "banner" : banner,
        }

        return cdata

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

        core = user.get("core") or user
        legacy = user.get("legacy") or user
        lget = legacy.get

        if lget("withheld_scope"):
            self.log.warning("'%s'", lget("description"))

        entities = legacy["entities"]
        self._user_cache[uid] = udata = {
            "id"              : text.parse_int(uid),
            "name"            : core.get("screen_name"),
            "nick"            : core.get("name"),
            "location"        : user["location"].get("location"),
            "date"            : self.parse_datetime(
                core["created_at"], "%a %b %d %H:%M:%S %z %Y"),
            "verified"        : user["verification"]["verified"],
            "protected"       : user["privacy"]["protected"],
            "profile_banner"  : lget("profile_banner_url", ""),
            "profile_image"   : user["avatar"].get("image_url", "").replace(
                "_normal.", "."),
            "favourites_count": lget("favourites_count"),
            "followers_count" : lget("followers_count"),
            "friends_count"   : lget("friends_count"),
            "listed_count"    : lget("listed_count"),
            "media_count"     : lget("media_count"),
            "statuses_count"  : lget("statuses_count"),
        }

        descr = legacy["description"]
        if urls := entities["description"].get("urls"):
            for url in urls:
                try:
                    descr = descr.replace(url["url"], url["expanded_url"])
                except KeyError:
                    pass
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
                if cid is False:
                    yield tweet
                else:
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
            "conversation_id_str": False,
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

    def _init_cursor(self):
        cursor = self.config("cursor", True)
        if not cursor:
            self._update_cursor = util.identity
        elif isinstance(cursor, str):
            return cursor

    def _update_cursor(self, cursor):
        self.log.debug("Cursor: %s", cursor)
        self._cursor = cursor
        return cursor

    def metadata(self):
        """Return general metadata"""
        return {}

    def tweets(self):
        """Yield all relevant tweet objects"""

    def finalize(self):
        if self._cursor:
            self.log.info("Use '-o cursor=%s' to continue downloading "
                          "from the current position", self._cursor)

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(_login_impl(self, username, password))


class TwitterHomeExtractor(TwitterExtractor):
    """Extractor for Twitter home timelines"""
    subcategory = "home"
    pattern = (rf"{BASE_PATTERN}/"
               rf"(?:home(?:/fo(?:llowing|r[-_ ]?you()))?|i/timeline)/?$")
    example = "https://x.com/home"

    def tweets(self):
        if self.groups[0] is None:
            return self.api.home_latest_timeline()
        return self.api.home_timeline()


class TwitterSearchExtractor(TwitterExtractor):
    """Extractor for Twitter search results"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search/?\?(?:[^&#]+&)*q=([^&#]+)"
    example = "https://x.com/search?q=QUERY"

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
    pattern = rf"{BASE_PATTERN}/hashtag/([^/?#]+)"
    example = "https://x.com/hashtag/NAME"

    def items(self):
        url = f"{self.root}/search?q=%23{self.user}"
        data = {"_extractor": TwitterSearchExtractor}
        yield Message.Queue, url, data


class TwitterUserExtractor(Dispatch, TwitterExtractor):
    """Extractor for a Twitter user"""
    pattern = (rf"{BASE_PATTERN}/(?:"
               r"([^/?#]+)/?(?:$|\?|#)"
               r"|i(?:/user/|ntent/user\?user_id=)(\d+))")
    example = "https://x.com/USER"

    def items(self):
        user, user_id = self.groups
        if user_id is not None:
            user = f"id:{user_id}"

        base = f"{self.root}/{user}/"
        return self._dispatch_extractors((
            (TwitterInfoExtractor      , f"{base}info"),
            (TwitterAvatarExtractor    , f"{base}photo"),
            (TwitterBackgroundExtractor, f"{base}header_photo"),
            (TwitterTimelineExtractor  , f"{base}timeline"),
            (TwitterTweetsExtractor    , f"{base}tweets"),
            (TwitterMediaExtractor     , f"{base}media"),
            (TwitterRepliesExtractor   , f"{base}with_replies"),
            (TwitterHighlightsExtractor, f"{base}highlights"),
            (TwitterLikesExtractor     , f"{base}likes"),
        ), ("timeline",))


class TwitterTimelineExtractor(TwitterExtractor):
    """Extractor for a Twitter user timeline"""
    subcategory = "timeline"
    pattern = rf"{USER_PATTERN}/timeline(?!\w)"
    example = "https://x.com/USER/timeline"

    def _init_cursor(self):
        if self._cursor:
            return self._cursor.partition("/")[2] or None
        return None

    def _update_cursor(self, cursor):
        if cursor:
            self._cursor = self._cursor_prefix + cursor
            self.log.debug("Cursor: %s", self._cursor)
        else:
            self._cursor = None
        return cursor

    def tweets(self):
        reset = False

        cursor = self.config("cursor", True)
        if not cursor:
            self._update_cursor = util.identity
        elif isinstance(cursor, str):
            self._cursor = cursor
        else:
            cursor = None

        if cursor:
            state = cursor.partition("/")[0]
            state, _, tweet_id = state.partition("_")
            state = text.parse_int(state, 1)
        else:
            state = 1

        if state <= 1:
            self._cursor_prefix = "1/"

            # yield initial batch of (media) tweets
            tweet = None
            for tweet in self._select_tweet_source()(self.user):
                yield tweet
            if tweet is None and not cursor:
                return
            tweet_id = tweet["rest_id"]

            state = reset = 2
        else:
            self.api._user_id_by_screen_name(self.user)

        # build search query
        query = f"from:{self._user['name']} max_id:{tweet_id}"
        if self.retweets:
            query += " include:retweets include:nativeretweets"

        if state <= 2:
            self._cursor_prefix = f"2_{tweet_id}/"
            if reset:
                self._cursor = self._cursor_prefix

            if not self.textonly:
                # try to search for media-only tweets
                tweet = None
                for tweet in self.api.search_timeline(query + " filter:links"):
                    yield tweet
                if tweet is not None:
                    return self._update_cursor(None)

            state = reset = 3

        if state <= 3:
            # yield unfiltered search results
            self._cursor_prefix = f"3_{tweet_id}/"
            if reset:
                self._cursor = self._cursor_prefix

            yield from self.api.search_timeline(query)
            return self._update_cursor(None)

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
        raise exception.AbortExtraction(f"Invalid strategy '{strategy}'")


class TwitterTweetsExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's Tweets timeline"""
    subcategory = "tweets"
    pattern = rf"{USER_PATTERN}/tweets(?!\w)"
    example = "https://x.com/USER/tweets"

    def tweets(self):
        return self.api.user_tweets(self.user)


class TwitterRepliesExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's timeline including replies"""
    subcategory = "replies"
    pattern = rf"{USER_PATTERN}/with_replies(?!\w)"
    example = "https://x.com/USER/with_replies"

    def tweets(self):
        return self.api.user_tweets_and_replies(self.user)


class TwitterHighlightsExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's highlights timeline"""
    subcategory = "highlights"
    pattern = rf"{USER_PATTERN}/highlights(?!\w)"
    example = "https://x.com/USER/highlights"

    def tweets(self):
        return self.api.user_highlights(self.user)


class TwitterMediaExtractor(TwitterExtractor):
    """Extractor for Tweets from a user's Media timeline"""
    subcategory = "media"
    pattern = rf"{USER_PATTERN}/media(?!\w)"
    example = "https://x.com/USER/media"

    def tweets(self):
        return self.api.user_media(self.user)


class TwitterLikesExtractor(TwitterExtractor):
    """Extractor for liked tweets"""
    subcategory = "likes"
    pattern = rf"{USER_PATTERN}/likes(?!\w)"
    example = "https://x.com/USER/likes"

    def metadata(self):
        return {"user_likes": self.user}

    def tweets(self):
        return self.api.user_likes(self.user)


class TwitterBookmarkExtractor(TwitterExtractor):
    """Extractor for bookmarked tweets"""
    subcategory = "bookmark"
    pattern = rf"{BASE_PATTERN}/i/bookmarks()"
    example = "https://x.com/i/bookmarks"

    def tweets(self):
        return self.api.user_bookmarks()

    def _transform_tweet(self, tweet):
        tdata = TwitterExtractor._transform_tweet(self, tweet)
        tdata["date_bookmarked"] = self.parse_timestamp(
            (int(tweet["sortIndex"] or 0) >> 20) // 1000)
        return tdata


class TwitterListExtractor(TwitterExtractor):
    """Extractor for Twitter lists"""
    subcategory = "list"
    pattern = rf"{BASE_PATTERN}/i/lists/(\d+)/?$"
    example = "https://x.com/i/lists/12345"

    def tweets(self):
        return self.api.list_latest_tweets_timeline(self.user)


class TwitterListMembersExtractor(TwitterExtractor):
    """Extractor for members of a Twitter list"""
    subcategory = "list-members"
    pattern = rf"{BASE_PATTERN}/i/lists/(\d+)/members"
    example = "https://x.com/i/lists/12345/members"

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).list_members(self.user))


class TwitterFollowingExtractor(TwitterExtractor):
    """Extractor for followed users"""
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/following(?!\w)"
    example = "https://x.com/USER/following"

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).user_following(self.user))


class TwitterFollowersExtractor(TwitterExtractor):
    """Extractor for a user's followers"""
    subcategory = "followers"
    pattern = rf"{USER_PATTERN}/followers(?!\w)"
    example = "https://x.com/USER/followers"

    def items(self):
        self.login()
        return self._users_result(TwitterAPI(self).user_followers(self.user))


class TwitterCommunityExtractor(TwitterExtractor):
    """Extractor for a Twitter community"""
    subcategory = "community"
    directory_fmt = ("{category}", "Communities",
                     "{community[name]} ({community[id]})")
    archive_fmt = "C_{community[id]}_{tweet_id}_{num}"
    pattern = rf"{BASE_PATTERN}/i/communities/(\d+)"
    example = "https://x.com/i/communities/12345"

    def tweets(self):
        if self.textonly:
            return self.api.community_tweets_timeline(self.user)
        return self.api.community_media_timeline(self.user)


class TwitterCommunitiesExtractor(TwitterExtractor):
    """Extractor for followed Twitter communities"""
    subcategory = "communities"
    directory_fmt = TwitterCommunityExtractor.directory_fmt
    archive_fmt = TwitterCommunityExtractor.archive_fmt
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/communities/?$"
    example = "https://x.com/i/communities"

    def tweets(self):
        return self.api.communities_main_page_timeline(self.user)


class TwitterEventExtractor(TwitterExtractor):
    """Extractor for Tweets from a Twitter Event"""
    subcategory = "event"
    directory_fmt = ("{category}", "Events",
                     "{event[id]} {event[short_title]}")
    pattern = rf"{BASE_PATTERN}/i/events/(\d+)"
    example = "https://x.com/i/events/12345"

    def metadata(self):
        return {"event": self.api.live_event(self.user)}

    def tweets(self):
        return self.api.live_event_timeline(self.user)


class TwitterTweetExtractor(TwitterExtractor):
    """Extractor for individual tweets"""
    subcategory = "tweet"
    pattern = (rf"{BASE_PATTERN}/([^/?#]+|i/web)/status/(\d+)"
               r"/?(?:$|\?|#|photo/|video/)")
    example = "https://x.com/USER/status/12345"

    def __init__(self, match):
        TwitterExtractor.__init__(self, match)
        self.tweet_id = match[2]

    def tweets(self):
        if conversations := self.config("conversations"):
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
            raise exception.AbortExtraction(
                f"'{tweet.get('reason') or 'Unavailable'}'")

        yield tweet

        if not self.quoted:
            return

        while True:
            parent_id = tweet["rest_id"]
            tweet_id = tweet["legacy"].get("quoted_status_id_str")
            if not tweet_id:
                break
            tweet = self.api.tweet_result_by_rest_id(tweet_id)
            tweet["legacy"]["quoted_by_id_str"] = parent_id
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
    pattern = rf"{BASE_PATTERN}/(?:[^/?#]+|i/web)/status/(\d+)/quotes"
    example = "https://x.com/USER/status/12345/quotes"

    def items(self):
        url = f"{self.root}/search?q=quoted_tweet_id:{self.user}"
        data = {"_extractor": TwitterSearchExtractor}
        yield Message.Queue, url, data


class TwitterInfoExtractor(TwitterExtractor):
    """Extractor for a user's profile data"""
    subcategory = "info"
    pattern = rf"{USER_PATTERN}/info"
    example = "https://x.com/USER/info"

    def items(self):
        api = TwitterAPI(self)

        screen_name = self.user
        if screen_name.startswith("id:"):
            user = api.user_by_rest_id(screen_name[3:])
        else:
            user = api.user_by_screen_name(screen_name)

        return iter(((Message.Directory, "", self._transform_user(user)),))


class TwitterAvatarExtractor(TwitterExtractor):
    subcategory = "avatar"
    filename_fmt = "avatar {date}.{extension}"
    archive_fmt = "AV_{user[id]}_{date}"
    pattern = rf"{USER_PATTERN}/photo"
    example = "https://x.com/USER/photo"

    def tweets(self):
        self.api._user_id_by_screen_name(self.user)
        user = self._user_obj
        url = user["avatar"]["image_url"]

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
    pattern = rf"{USER_PATTERN}/header_photo"
    example = "https://x.com/USER/header_photo"

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
        base = f"https://pbs.twimg.com/media/{self.id}?format={self.fmt}&name="

        data = {
            "filename": self.id,
            "extension": self.fmt,
            "_fallback": TwitterExtractor._image_fallback(self, base),
        }

        yield Message.Directory, "", data
        yield Message.Url, base + self._size_image, data


class TwitterAPI():
    client_transaction = None

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log

        self.root = "https://x.com/i/api"
        self._nsfw_warning = True
        self._json_dumps = util.json_dumps

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
            "Referer": extractor.root + "/",
            "content-type": "application/json",
            "x-guest-token": None,
            "x-twitter-auth-type": "OAuth2Session" if auth_token else None,
            "x-csrf-token": csrf_token,
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "x-client-transaction-id": None,
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
            "hidden_profile_subscriptions_enabled": True,
            "payments_enabled": False,
            "rweb_xchat_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": False,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_notes_tab_enabled": True,
            "subscriptions_feature_can_gift_premium": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_"
            "skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }
        self.features_pagination = {
            "rweb_video_screen_enabled": False,
            "payments_enabled": False,
            "rweb_xchat_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql"
            "_timeline_navigation_enabled": True,
            "responsive_web_graphql"
            "_skip_user_profile_image_extensions_enabled": False,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "responsive_web_jetfuel_frame": True,
            "responsive_web_grok_share_attachment_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_grok_show_grok_translated_post": False,
            "responsive_web_grok_analysis_button_from_backend": True,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results"
            "_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_imagine_annotation_enabled": True,
            "responsive_web_grok"
            "_community_note_auto_translation_is_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
        }

    def tweet_result_by_rest_id(self, tweet_id):
        endpoint = "/graphql/qxWQxcMLiTPcavz9Qy5hwQ/TweetResultByRestId"
        variables = {
            "tweetId": tweet_id,
            "withCommunity": False,
            "includePromotedContent": False,
            "withVoice": False,
        }
        features = self.features_pagination.copy()
        del features["rweb_video_screen_enabled"]
        field_toggles = {
            "withArticleRichContentState": True,
            "withArticlePlainText": False,
            "withGrokAnalyze": False,
            "withDisallowedReplyControls": False,
        }
        params = {
            "variables"   : self._json_dumps(variables),
            "features"    : self._json_dumps(features),
            "fieldToggles": self._json_dumps(field_toggles),
        }
        tweet = self._call(endpoint, params)["data"]["tweetResult"]["result"]
        if "tweet" in tweet:
            tweet = tweet["tweet"]

        if tweet.get("__typename") == "TweetUnavailable":
            reason = tweet.get("reason")
            if reason in ("NsfwViewerHasNoStatedAge", "NsfwLoggedOut"):
                raise exception.AuthRequired(message="NSFW Tweet")
            if reason == "Protected":
                raise exception.AuthRequired(message="Protected Tweet")
            raise exception.AbortExtraction(f"Tweet unavailable ('{reason}')")

        return tweet

    def tweet_detail(self, tweet_id):
        endpoint = "/graphql/iFEr5AcP121Og4wx9Yqo3w/TweetDetail"
        variables = {
            "focalTweetId": tweet_id,
            "referrer": "profile",
            "with_rux_injections": False,
            #  "rankingMode": "Relevance",
            "includePromotedContent": False,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": False,
            "withBirdwatchNotes": True,
            "withVoice": True,
        }
        field_toggles = {
            "withArticleRichContentState": True,
            "withArticlePlainText": False,
            "withGrokAnalyze": False,
            "withDisallowedReplyControls": False,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("threaded_conversation_with_injections_v2",),
            field_toggles=field_toggles)

    def user_tweets(self, screen_name):
        endpoint = "/graphql/E8Wq-_jFSaU7hxVcuOPR9g/UserTweets"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_tweets_and_replies(self, screen_name):
        endpoint = "/graphql/-O3QOHrVn1aOm_cF5wyTCQ/UserTweetsAndReplies"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "withCommunity": True,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_highlights(self, screen_name):
        endpoint = "/graphql/gmHw9geMTncZ7jeLLUUNOw/UserHighlightsTweets"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_media(self, screen_name):
        endpoint = "/graphql/jCRhbOzdgOHp6u9H4g2tEg/UserMedia"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_likes(self, screen_name):
        endpoint = "/graphql/TGEKkJG_meudeaFcqaxM-Q/Likes"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_bookmarks(self):
        endpoint = "/graphql/pLtjrO4ubNh996M_Cubwsg/Bookmarks"
        variables = {
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
        }
        return self._pagination_tweets(
            endpoint, variables, ("bookmark_timeline_v2", "timeline"),
            stop_tweets=128)

    def search_timeline(self, query, product=None):
        cfg = self.extractor.config

        if product is None:
            if product := cfg("search-results"):
                product = {
                    "top"  : "Top",
                    "live" : "Latest",
                    "user" : "People",
                    "media": "Media",
                    "list" : "Lists",
                }.get(product.lower(), product).capitalize()
            else:
                product = "Latest"

        endpoint = "/graphql/4fpceYZ6-YQCx_JSl_Cn_A/SearchTimeline"
        variables = {
            "rawQuery": query,
            "count": cfg("search-limit", 20),
            "querySource": "typed_query",
            "product": product,
            "withGrokTranslatedBio": False,
        }

        if cfg("search-pagination") in ("max_id", "maxid", "id"):
            update_variables = self._update_variables_search
        else:
            update_variables = None

        stop_tweets = cfg("search-stop")
        if stop_tweets is None or stop_tweets == "auto":
            stop_tweets = 3

        return self._pagination_tweets(
            endpoint, variables,
            ("search_by_raw_query", "search_timeline", "timeline"),
            stop_tweets=stop_tweets, update_variables=update_variables)

    def community_query(self, community_id):
        endpoint = "/graphql/2W09l7nD7ZbxGQHXvfB22w/CommunityQuery"
        params = {
            "variables": self._json_dumps({
                "communityId": community_id,
            }),
            "features": self._json_dumps({
                "c9s_list_members_action_api_enabled": False,
                "c9s_superc9s_indication_enabled": False,
            }),
        }
        return (self._call(endpoint, params)
                ["data"]["communityResults"]["result"])

    def community_tweets_timeline(self, community_id):
        endpoint = "/graphql/Nyt-88UX4-pPCImZNUl9RQ/CommunityTweetsTimeline"
        variables = {
            "communityId": community_id,
            "count": self.extractor.config("limit", 50),
            "displayLocation": "Community",
            "rankingMode": "Recency",
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("communityResults", "result", "ranked_community_timeline",
             "timeline"))

    def community_media_timeline(self, community_id):
        endpoint = "/graphql/ZniZ7AAK_VVu1xtSx1V-gQ/CommunityMediaTimeline"
        variables = {
            "communityId": community_id,
            "count": self.extractor.config("limit", 50),
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("communityResults", "result", "community_media_timeline",
             "timeline"))

    def communities_main_page_timeline(self, screen_name):
        endpoint = ("/graphql/p048a9n3hTPppQyK7FQTFw"
                    "/CommunitiesMainPageTimeline")
        variables = {
            "count": self.extractor.config("limit", 50),
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("viewer", "communities_timeline", "timeline"))

    def home_timeline(self):
        endpoint = "/graphql/DXmgQYmIft1oLP6vMkJixw/HomeTimeline"
        variables = {
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "latestControlAvailable": True,
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables, ("home", "home_timeline_urt"))

    def home_latest_timeline(self):
        endpoint = "/graphql/SFxmNKWfN9ySJcXG_tjX8g/HomeLatestTimeline"
        variables = {
            "count": self.extractor.config("limit", 50),
            "includePromotedContent": False,
            "latestControlAvailable": True,
        }
        return self._pagination_tweets(
            endpoint, variables, ("home", "home_timeline_urt"))

    def live_event_timeline(self, event_id):
        endpoint = f"/2/live_event/timeline/{event_id}.json"
        params = self.params.copy()
        params["timeline_id"] = "recap"
        params["urt"] = "true"
        params["get_annotations"] = "true"
        return self._pagination_legacy(endpoint, params)

    def live_event(self, event_id):
        endpoint = f"/1.1/live_event/1/{event_id}/timeline.json"
        params = self.params.copy()
        params["count"] = "0"
        params["urt"] = "true"
        return (self._call(endpoint, params)
                ["twitter_objects"]["live_events"][event_id])

    def list_latest_tweets_timeline(self, list_id):
        endpoint = "/graphql/06JtmwM8k_1cthpFZITVVA/ListLatestTweetsTimeline"
        variables = {
            "listId": list_id,
            "count": self.extractor.config("limit", 50),
        }
        return self._pagination_tweets(
            endpoint, variables, ("list", "tweets_timeline", "timeline"))

    def list_members(self, list_id):
        endpoint = "/graphql/naea_MSad4pOb-D6_oVv_g/ListMembers"
        variables = {
            "listId": list_id,
            "count": 100,
        }
        return self._pagination_users(
            endpoint, variables, ("list", "members_timeline", "timeline"))

    def user_followers(self, screen_name):
        endpoint = "/graphql/i6PPdIMm1MO7CpAqjau7sw/Followers"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withGrokTranslatedBio": False,
        }
        return self._pagination_users(endpoint, variables)

    def user_followers_verified(self, screen_name):
        endpoint = "/graphql/fxEl9kp1Tgolqkq8_Lo3sg/BlueVerifiedFollowers"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withGrokTranslatedBio": False,
        }
        return self._pagination_users(endpoint, variables)

    def user_following(self, screen_name):
        endpoint = "/graphql/SaWqzw0TFAWMx1nXWjXoaQ/Following"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withGrokTranslatedBio": False,
        }
        return self._pagination_users(endpoint, variables)

    @memcache(keyarg=1)
    def user_by_rest_id(self, rest_id):
        endpoint = "/graphql/8r5oa_2vD0WkhIAOkY4TTA/UserByRestId"
        features = self.features
        params = {
            "variables": self._json_dumps({
                "userId": rest_id,
            }),
            "features": self._json_dumps(features),
        }
        return self._call(endpoint, params)["data"]["user"]["result"]

    @memcache(keyarg=1)
    def user_by_screen_name(self, screen_name):
        endpoint = "/graphql/ck5KkZ8t5cOmoLssopN99Q/UserByScreenName"
        features = self.features.copy()
        features["subscriptions_verification_info_"
                 "is_identity_verified_enabled"] = True
        features["subscriptions_verification_info_"
                 "verified_since_enabled"] = True
        params = {
            "variables": self._json_dumps({
                "screen_name": screen_name,
                "withGrokTranslatedBio": False,
            }),
            "features": self._json_dumps(features),
            "fieldToggles": self._json_dumps({
                "withAuxiliaryUserLabels": True,
            }),
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
            if user and user.get("__typename") == "UserUnavailable":
                raise exception.NotFoundError(user["message"], False)
            else:
                raise exception.NotFoundError("user")

    @cache(maxage=3600)
    def _guest_token(self):
        endpoint = "/1.1/guest/activate.json"
        self.log.info("Requesting guest token")
        return str(self._call(
            endpoint, None, "POST", False, "https://api.x.com",
        )["guest_token"])

    def _authenticate_guest(self):
        guest_token = self._guest_token()
        if guest_token != self.headers["x-guest-token"]:
            self.headers["x-guest-token"] = guest_token
            self.extractor.cookies.set(
                "gt", guest_token, domain=self.extractor.cookies_domain)

    @cache(maxage=10800)
    def _client_transaction(self):
        self.log.info("Initializing client transaction keys")

        from .. import transaction_id
        ct = transaction_id.ClientTransaction()
        ct.initialize(self.extractor)

        # update 'x-csrf-token' header (#7467)
        csrf_token = self.extractor.cookies.get(
            "ct0", domain=self.extractor.cookies_domain)
        if csrf_token:
            self.headers["x-csrf-token"] = csrf_token

        return ct

    def _transaction_id(self, url, method="GET"):
        if self.client_transaction is None:
            TwitterAPI.client_transaction = self._client_transaction()
        path = url[url.find("/", 8):]
        self.headers["x-client-transaction-id"] = \
            self.client_transaction.generate_transaction_id(method, path)

    def _call(self, endpoint, params, method="GET", auth=True, root=None):
        url = (self.root if root is None else root) + endpoint

        while True:
            if auth:
                if self.headers["x-twitter-auth-type"]:
                    self._transaction_id(url, method)
                else:
                    self._authenticate_guest()

            response = self.extractor.request(
                url, method=method, params=params,
                headers=self.headers, fatal=None)

            # update 'x-csrf-token' header (#1170)
            if csrf_token := response.cookies.get("ct0"):
                self.headers["x-csrf-token"] = csrf_token

            remaining = int(response.headers.get("x-rate-limit-remaining", 6))
            if remaining < 6 and remaining <= random.randrange(1, 6):
                self._handle_ratelimit(response)
                continue

            try:
                data = response.json()
            except ValueError:
                data = {"errors": ({"message": response.text},)}

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
                    self.log.warning(msg)
                    self.extractor.input("Press ENTER to retry.")
                    retry = True

                elif "Could not authenticate you" in msg:
                    raise exception.AbortExtraction(f"'{msg}'")

                elif msg.lower().startswith("timeout"):
                    retry = True

            if retry:
                if self.headers["x-twitter-auth-type"]:
                    self.log.debug("Retrying API request")
                    continue
                else:
                    # fall through to "Login Required"
                    response.status_code = 404

            if response.status_code < 400:
                return data
            elif response.status_code in (403, 404) and \
                    not self.headers["x-twitter-auth-type"]:
                raise exception.AuthRequired(
                    "authenticated cookies", "timeline")
            elif response.status_code == 429:
                self._handle_ratelimit(response)
                continue

            # error
            try:
                errors = ", ".join(e["message"] for e in errors)
            except Exception:
                pass

            raise exception.AbortExtraction(
                f"{response.status_code} {response.reason} ({errors})")

    def _pagination_legacy(self, endpoint, params):
        extr = self.extractor
        if cursor := extr._init_cursor():
            params["cursor"] = cursor
        original_retweets = (extr.retweets == "original")
        bottom = ("cursor-bottom-", "sq-cursor-bottom")

        while True:
            data = self._call(endpoint, params)

            instructions = data["timeline"]["instructions"]
            if not instructions:
                return extr._update_cursor(None)

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
                    if quoted := tweets.get(tweet["quoted_status_id_str"]):
                        quoted = quoted.copy()
                        quoted["author"] = users[quoted["user_id_str"]]
                        quoted["quoted_by"] = tweet["user"]["screen_name"]
                        quoted["quoted_by_id_str"] = tweet["id_str"]
                        yield quoted

            # stop on empty response
            if not cursor or (not tweets and not tweet_id):
                return extr._update_cursor(None)
            params["cursor"] = extr._update_cursor(cursor)

    def _pagination_tweets(self, endpoint, variables,
                           path=None, stop_tweets=0, update_variables=None,
                           features=None, field_toggles=None):
        extr = self.extractor
        original_retweets = (extr.retweets == "original")
        pinned_tweet = True if extr.pinned else None
        stop_tweets_max = stop_tweets
        api_retries = None

        if isinstance(count := variables.get("count"), list):
            count = count.copy()
            count.reverse()
            self.log.debug("Using 'count: %s'", count[-1])
            variables["count"] = count.pop()
        else:
            count = False

        params = {"variables": None}
        if cursor := extr._init_cursor():
            variables["cursor"] = cursor
        if features is None:
            features = self.features_pagination
        if features:
            params["features"] = self._json_dumps(features)
        if field_toggles:
            params["fieldToggles"] = self._json_dumps(field_toggles)

        while True:
            params["variables"] = self._json_dumps(variables)
            data = self._call(endpoint, params)

            try:
                if path is None:
                    instructions = (data["data"]["user"]["result"]["timeline"]
                                    ["timeline"]["instructions"])
                else:
                    instructions = data["data"]
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
                    elif instr_type == "TimelinePinEntry":
                        if pinned_tweet is not None:
                            pinned_tweet = instr["entry"]
                    elif instr_type == "TimelineReplaceEntry":
                        entry = instr["entry"]
                        if entry["entryId"].startswith("cursor-bottom-"):
                            cursor = entry["content"]["value"]
                if entries is None:
                    if not cursor:
                        return extr._update_cursor(None)
                    entries = ()

            except LookupError:
                extr.log.debug(data)

                if errors := data.get("errors"):
                    if api_retries is None:
                        api_tries = 1
                        api_retries = extr.config("retries-api", 9)
                        if api_retries < 0:
                            api_retries = float("inf")

                    err = []
                    srv = False
                    for e in errors:
                        err.append(f"- '{e.get('message') or e.get('name')}'")
                        if e.get("source") == "Server":
                            srv = True

                    self.log.warning("API errors (%s/%s):\n%s",
                                     api_tries, api_retries+1, "\n".join(err))
                    if srv and api_tries <= api_retries:
                        api_tries += 1
                        continue

                if user := extr._user_obj:
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
                            f"{user['screen_name']} blocked your account")
                    elif user.get("protected"):
                        raise exception.AuthorizationError(
                            f"{user['screen_name']}'s Tweets are protected")

                raise exception.AbortExtraction(
                    "Unable to retrieve Tweets from this timeline")

            tweets = []
            tweet = last_tweet = retry = None
            api_tries = 1

            if pinned_tweet is not None and isinstance(pinned_tweet, dict):
                pinned_tweet["pinned"] = True
                tweets.append(pinned_tweet)
                pinned_tweet = None

            for entry in entries:
                esw = entry["entryId"].startswith

                if esw("tweet-"):
                    tweets.append(entry)
                elif esw(("profile-grid-",
                          "search-grid-",
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

            if pinned_tweet is not None:
                if extr._user_obj is None:
                    pinned = None
                elif pinned := extr._user_obj["legacy"].get(
                        "pinned_tweet_ids_str"):
                    pinned = f"-tweet-{pinned[0]}"
                    for idx, entry in enumerate(tweets):
                        if entry["entryId"].endswith(pinned):
                            # mark as pinned / set 'pinned = True'
                            pinned_tweet = (
                                (entry.get("content") or entry["item"])
                                ["itemContent"]["tweet_results"]["result"])
                            if "tweet" in pinned_tweet:
                                pinned_tweet = pinned_tweet["tweet"]
                            pinned_tweet["pinned"] = True
                            # move to front of 'tweets'
                            del tweets[idx]
                            tweets.insert(0, entry)
                            break
                del pinned
                pinned_tweet = None

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

                if retry is None:
                    try:
                        tweet["core"]["user_results"]["result"]
                        retry = False
                    except KeyError:
                        self.log.warning("Received Tweet results without "
                                         "'core' data ... Retrying")
                        retry = True
                        break

                if "retweeted_status_result" in legacy:
                    try:
                        retweet = legacy["retweeted_status_result"]["result"]
                        if "tweet" in retweet:
                            retweet = retweet["tweet"]
                        if original_retweets:
                            retweet["legacy"]["retweeted_status_id_str"] = \
                                retweet["rest_id"]
                            retweet["_retweet_id_str"] = tweet["rest_id"]
                            tweet = retweet
                        else:
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
                    except Exception as exc:
                        extr.log.debug(
                            "%s:  %s: %s",
                            tweet.get("rest_id"), exc.__class__.__name__, exc)
                        continue

                yield tweet

                if "quoted_status_result" in tweet:
                    try:
                        quoted = tweet["quoted_status_result"]["result"]
                        quoted["legacy"]["quoted_by"] = (
                            tweet["core"]["user_results"]["result"]
                            ["core"]["screen_name"])
                        quoted["legacy"]["quoted_by_id_str"] = tweet["rest_id"]
                        quoted["sortIndex"] = entry.get("sortIndex")

                        yield quoted
                    except KeyError:
                        extr.log.debug(
                            "Skipping quote of %s (deleted)",
                            tweet.get("rest_id"))
                        continue

            if retry:
                continue
            elif tweet:
                stop_tweets = stop_tweets_max
                last_tweet = tweet
            elif stop_tweets <= 0:
                if not count:
                    return extr._update_cursor(None)
                self.log.debug("Switching to 'count: %s'", count[-1])
                variables["count"] = count.pop()
                continue
            else:
                self.log.debug(
                    "No Tweet results (%s/%s)",
                    stop_tweets_max - stop_tweets + 1, stop_tweets_max)
                stop_tweets -= 1

            if not cursor or cursor == variables.get("cursor"):
                self.log.debug("No continuation cursor")
                return extr._update_cursor(None)

            if update_variables is None:
                variables["cursor"] = extr._update_cursor(cursor)
            else:
                variables = update_variables(variables, cursor, last_tweet)

    def _pagination_users(self, endpoint, variables, path=None):
        extr = self.extractor
        if cursor := extr._init_cursor():
            variables["cursor"] = cursor
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
                return extr._update_cursor(None)

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
                return extr._update_cursor(None)
            variables["cursor"] = extr._update_cursor(cursor)

    def _handle_ratelimit(self, response):
        rl = self.extractor.config("ratelimit")
        if rl == "abort":
            raise exception.AbortExtraction("Rate limit exceeded")
        elif rl and isinstance(rl, str) and rl.startswith("wait:"):
            until = None
            seconds = text.parse_float(rl.partition(":")[2]) or 60.0
        else:
            until = response.headers.get("x-rate-limit-reset")
            seconds = None if until else 60.0
        self.extractor.wait(until=until, seconds=seconds)

    def _process_tombstone(self, entry, tombstone):
        text = (tombstone.get("richText") or tombstone["text"])["text"]
        tweet_id = entry["entryId"].rpartition("-")[2]

        if text.startswith("Age-restricted"):
            if self._nsfw_warning:
                self._nsfw_warning = False
                self.log.warning('"%s"', text)

        self.log.debug("Skipping %s ('%s')", tweet_id, text)

    def _update_variables_search(self, variables, cursor, tweet):
        try:
            tweet_id = tweet.get("id_str") or tweet["legacy"]["id_str"]
            max_id = f"max_id:{int(tweet_id)-1}"

            query, n = text.re(r"\bmax_id:\d+").subn(
                max_id, variables["rawQuery"])
            if n:
                variables["rawQuery"] = query
            else:
                variables["rawQuery"] = f"{query} {max_id}"

            if prefix := getattr(self.extractor, "_cursor_prefix", None):
                self.extractor._cursor_prefix = \
                    f"{prefix.partition('_')[0]}_{tweet_id}/"
            variables["cursor"] = None
        except Exception as exc:
            self.extractor.log.debug(
                "Failed to update 'max_id' search query (%s: %s). Falling "
                "back to 'cursor' pagination", exc.__class__.__name__, exc)
            variables["cursor"] = self.extractor._update_cursor(cursor)

        return variables


@cache(maxage=365*86400, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.error("Login with username & password is no longer supported. "
                   "Use browser cookies instead.")
    return {}

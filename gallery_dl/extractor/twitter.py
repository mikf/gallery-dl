# -*- coding: utf-8 -*-

# Copyright 2016-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://x.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
import itertools

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
        self.api = self.utils().TwitterAPI(self)
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
            yield Message.Directory, tdata

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
            date = self.parse_timestamp(
                ((tweet_id >> 22) + 1288834974657) // 1000)
        else:
            try:
                date = self.parse_datetime(
                    legacy["created_at"], "%a %b %d %H:%M:%S %z %Y")
            except Exception:
                date = util.NONE
        source = tweet.get("source")

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
            return self.cookies_update(
                self.utils()._login_impl(self, username, password))


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
        api = self.utils().TwitterAPI(self)
        return self._users_result(api.list_members(self.user))


class TwitterFollowingExtractor(TwitterExtractor):
    """Extractor for followed users"""
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/following(?!\w)"
    example = "https://x.com/USER/following"

    def items(self):
        self.login()
        api = self.utils().TwitterAPI(self)
        return self._users_result(api.user_following(self.user))


class TwitterFollowersExtractor(TwitterExtractor):
    """Extractor for a user's followers"""
    subcategory = "followers"
    pattern = rf"{USER_PATTERN}/followers(?!\w)"
    example = "https://x.com/USER/followers"

    def items(self):
        self.login()
        api = self.utils().TwitterAPI(self)
        return self._users_result(api.user_followers(self.user))


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
        api = self.utils().TwitterAPI(self)

        screen_name = self.user
        if screen_name.startswith("id:"):
            user = api.user_by_rest_id(screen_name[3:])
        else:
            user = api.user_by_screen_name(screen_name)

        return iter(((Message.Directory, self._transform_user(user)),))


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
            "filename" : self.id,
            "extension": self.fmt,
            "_fallback": TwitterExtractor._image_fallback(self, base),
        }

        yield Message.Directory, data
        yield Message.Url, f"{base}{self._size_image}", data

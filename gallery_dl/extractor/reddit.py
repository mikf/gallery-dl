# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.reddit.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache


class RedditExtractor(Extractor):
    """Base class for reddit extractors"""
    category = "reddit"
    directory_fmt = ("{category}", "{subreddit}")
    filename_fmt = "{id}{num:? //>02} {title[:220]}.{extension}"
    archive_fmt = "{filename}"
    cookies_domain = ".reddit.com"
    request_interval = 0.6

    def items(self):
        self.api = RedditAPI(self)
        match_submission = RedditSubmissionExtractor.pattern.match
        match_subreddit = RedditSubredditExtractor.pattern.match
        match_user = RedditUserExtractor.pattern.match

        parentdir = self.config("parent-directory")
        max_depth = self.config("recursion", 0)
        previews = self.config("previews", True)

        videos = self.config("videos", True)
        if videos:
            if videos == "ytdl":
                self._extract_video = self._extract_video_ytdl
            elif videos == "dash":
                self._extract_video = self._extract_video_dash
            videos = True

        submissions = self.submissions()
        visited = set()
        depth = 0

        while True:
            extra = []

            for submission, comments in submissions:
                urls = []

                if submission:
                    submission["date"] = text.parse_timestamp(
                        submission["created_utc"])
                    yield Message.Directory, submission
                    visited.add(submission["id"])
                    submission["num"] = 0

                    if "crosspost_parent_list" in submission:
                        try:
                            media = submission["crosspost_parent_list"][-1]
                        except Exception:
                            media = submission
                    else:
                        media = submission

                    url = media["url"]
                    if url and url.startswith((
                        "https://i.redd.it/",
                        "https://preview.redd.it/",
                    )):
                        text.nameext_from_url(url, submission)
                        yield Message.Url, url, submission

                    elif "gallery_data" in media:
                        for url in self._extract_gallery(media):
                            submission["num"] += 1
                            text.nameext_from_url(url, submission)
                            yield Message.Url, url, submission

                    elif media["is_video"]:
                        if videos:
                            text.nameext_from_url(url, submission)
                            url = "ytdl:" + self._extract_video(media)
                            yield Message.Url, url, submission

                    elif not submission["is_self"]:
                        urls.append((url, submission))

                elif parentdir:
                    yield Message.Directory, comments[0]

                if self.api.comments:
                    if submission:
                        for url in text.extract_iter(
                                submission["selftext_html"] or "",
                                ' href="', '"'):
                            urls.append((url, submission))
                    for comment in comments:
                        html = comment["body_html"] or ""
                        href = (' href="' in html)
                        media = ("media_metadata" in comment)

                        if media or href:
                            comment["date"] = text.parse_timestamp(
                                comment["created_utc"])
                            if submission:
                                data = submission.copy()
                                data["comment"] = comment
                            else:
                                data = comment

                        if media:
                            for embed in self._extract_embed(comment):
                                submission["num"] += 1
                                text.nameext_from_url(embed, submission)
                                yield Message.Url, embed, submission

                        if href:
                            for url in text.extract_iter(html, ' href="', '"'):
                                urls.append((url, data))

                for url, data in urls:
                    if not url or url[0] == "#":
                        continue
                    if url[0] == "/":
                        url = "https://www.reddit.com" + url
                    if url.startswith((
                        "https://www.reddit.com/message/compose",
                        "https://reddit.com/message/compose",
                        "https://preview.redd.it/",
                    )):
                        continue

                    match = match_submission(url)
                    if match:
                        extra.append(match.group(1))
                    elif not match_user(url) and not match_subreddit(url):
                        if previews and "comment" not in data and \
                                "preview" in data:
                            data["_fallback"] = self._previews(data)
                        yield Message.Queue, text.unescape(url), data
                        if "_fallback" in data:
                            del data["_fallback"]

            if not extra or depth == max_depth:
                return
            depth += 1
            submissions = (
                self.api.submission(sid) for sid in extra
                if sid not in visited
            )

    def submissions(self):
        """Return an iterable containing all (submission, comments) tuples"""

    def _extract_gallery(self, submission):
        gallery = submission["gallery_data"]
        if gallery is None:
            self.log.warning("gallery %s: deleted", submission["id"])
            return

        meta = submission.get("media_metadata")
        if meta is None:
            self.log.warning("gallery %s: missing 'media_metadata'",
                             submission["id"])
            return

        for item in gallery["items"]:
            data = meta[item["media_id"]]
            if data["status"] != "valid" or "s" not in data:
                self.log.warning(
                    "gallery %s: skipping item %s (status: %s)",
                    submission["id"], item["media_id"], data.get("status"))
                continue
            src = data["s"]
            url = src.get("u") or src.get("gif") or src.get("mp4")
            if url:
                yield url.partition("?")[0].replace("/preview.", "/i.", 1)
            else:
                self.log.error(
                    "gallery %s: unable to fetch download URL for item %s",
                    submission["id"], item["media_id"])
                self.log.debug(src)

    def _extract_embed(self, submission):
        meta = submission["media_metadata"]
        if not meta:
            return

        for mid, data in meta.items():
            if data["status"] != "valid" or "s" not in data:
                self.log.warning(
                    "embed %s: skipping item %s (status: %s)",
                    submission["id"], mid, data.get("status"))
                continue
            src = data["s"]
            url = src.get("u") or src.get("gif") or src.get("mp4")
            if url:
                yield url.partition("?")[0].replace("/preview.", "/i.", 1)
            else:
                self.log.error(
                    "embed %s: unable to fetch download URL for item %s",
                    submission["id"], mid)
                self.log.debug(src)

    def _extract_video_ytdl(self, submission):
        return "https://www.reddit.com" + submission["permalink"]

    def _extract_video_dash(self, submission):
        submission["_ytdl_extra"] = {"title": submission["title"]}
        try:
            return (submission["secure_media"]["reddit_video"]["dash_url"] +
                    "#__youtubedl_smuggle=%7B%22to_generic%22%3A+1%7D")
        except Exception:
            return submission["url"]

    def _extract_video(self, submission):
        submission["_ytdl_extra"] = {"title": submission["title"]}
        return submission["url"]

    def _previews(self, post):
        try:
            if "reddit_video_preview" in post["preview"]:
                video = post["preview"]["reddit_video_preview"]
                if "fallback_url" in video:
                    yield video["fallback_url"]
                if "dash_url" in video:
                    yield "ytdl:" + video["dash_url"]
                if "hls_url" in video:
                    yield "ytdl:" + video["hls_url"]
        except Exception as exc:
            self.log.debug("%s: %s", exc.__class__.__name__, exc)

        try:
            for image in post["preview"]["images"]:
                variants = image.get("variants")
                if variants:
                    if "gif" in variants:
                        yield variants["gif"]["source"]["url"]
                    if "mp4" in variants:
                        yield variants["mp4"]["source"]["url"]
                yield image["source"]["url"]
        except Exception as exc:
            self.log.debug("%s: %s", exc.__class__.__name__, exc)


class RedditSubredditExtractor(RedditExtractor):
    """Extractor for URLs from subreddits on reddit.com"""
    subcategory = "subreddit"
    pattern = (r"(?:https?://)?(?:\w+\.)?reddit\.com"
               r"(/r/[^/?#]+(?:/([a-z]+))?)/?(?:\?([^#]*))?(?:$|#)")
    example = "https://www.reddit.com/r/SUBREDDIT/"

    def __init__(self, match):
        self.subreddit, sub, params = match.groups()
        self.params = text.parse_query(params)
        if sub:
            self.subcategory += "-" + sub
        RedditExtractor.__init__(self, match)

    def submissions(self):
        return self.api.submissions_subreddit(self.subreddit, self.params)


class RedditHomeExtractor(RedditSubredditExtractor):
    """Extractor for submissions from your home feed on reddit.com"""
    subcategory = "home"
    pattern = (r"(?:https?://)?(?:\w+\.)?reddit\.com"
               r"((?:/([a-z]+))?)/?(?:\?([^#]*))?(?:$|#)")
    example = "https://www.reddit.com/"


class RedditUserExtractor(RedditExtractor):
    """Extractor for URLs from posts by a reddit user"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:\w+\.)?reddit\.com/u(?:ser)?/"
               r"([^/?#]+(?:/([a-z]+))?)/?(?:\?([^#]*))?$")
    example = "https://www.reddit.com/user/USER/"

    def __init__(self, match):
        self.user, sub, params = match.groups()
        self.params = text.parse_query(params)
        if sub:
            self.subcategory += "-" + sub
        RedditExtractor.__init__(self, match)

    def submissions(self):
        return self.api.submissions_user(self.user, self.params)


class RedditSubmissionExtractor(RedditExtractor):
    """Extractor for URLs from a submission on reddit.com"""
    subcategory = "submission"
    pattern = (r"(?:https?://)?(?:"
               r"(?:\w+\.)?reddit\.com/(?:(?:r|u|user)/[^/?#]+"
               r"/comments|gallery)|redd\.it)/([a-z0-9]+)")
    example = "https://www.reddit.com/r/SUBREDDIT/comments/id/"

    def __init__(self, match):
        RedditExtractor.__init__(self, match)
        self.submission_id = match.group(1)

    def submissions(self):
        return (self.api.submission(self.submission_id),)


class RedditImageExtractor(Extractor):
    """Extractor for reddit-hosted images"""
    category = "reddit"
    subcategory = "image"
    archive_fmt = "{filename}"
    pattern = (r"(?:https?://)?((?:i|preview)\.redd\.it|i\.reddituploads\.com)"
               r"/([^/?#]+)(\?[^#]*)?")
    example = "https://i.redd.it/NAME.EXT"

    def __init__(self, match):
        Extractor.__init__(self, match)
        domain = match.group(1)
        self.path = match.group(2)
        if domain == "preview.redd.it":
            self.domain = "i.redd.it"
            self.query = ""
        else:
            self.domain = domain
            self.query = match.group(3) or ""

    def items(self):
        url = "https://{}/{}{}".format(self.domain, self.path, self.query)
        data = text.nameext_from_url(url)
        yield Message.Directory, data
        yield Message.Url, url, data


class RedditRedirectExtractor(Extractor):
    """Extractor for personalized share URLs produced by the mobile app"""
    category = "reddit"
    subcategory = "redirect"
    pattern = (r"(?:https?://)?(?:"
               r"(?:\w+\.)?reddit\.com/(?:(?:r)/([^/?#]+)))"
               r"/s/([a-zA-Z0-9]{10})")
    example = "https://www.reddit.com/r/SUBREDDIT/s/abc456GHIJ"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.subreddit = match.group(1)
        self.share_url = match.group(2)

    def items(self):
        url = "https://www.reddit.com/r/" + self.subreddit + "/s/" + \
              self.share_url
        data = {"_extractor": RedditSubmissionExtractor}
        response = self.request(url, method="HEAD", allow_redirects=False,
                                notfound="submission")
        yield Message.Queue, response.headers["Location"], data


class RedditAPI():
    """Interface for the Reddit API

    Ref: https://www.reddit.com/dev/api/
    """
    CLIENT_ID = "6N9uN0krSDE-ig"
    USER_AGENT = "Python:gallery-dl:0.8.4 (by /u/mikf1)"

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log

        config = extractor.config
        self.comments = text.parse_int(config("comments", 0))
        self.morecomments = config("morecomments", False)

        client_id = config("client-id")
        if client_id is None:
            self.client_id = self.CLIENT_ID
            self.headers = {"User-Agent": self.USER_AGENT}
        else:
            self.client_id = client_id
            self.headers = {"User-Agent": config("user-agent")}

        if self.client_id == self.CLIENT_ID:
            client_id = self.client_id
            self._warn_429 = True
            kind = "default"
        else:
            client_id = client_id[:5] + "*" * (len(client_id)-5)
            self._warn_429 = False
            kind = "custom"

        self.log.debug(
            "Using %s API credentials (client-id %s)", kind, client_id)

        token = config("refresh-token")
        if token is None or token == "cache":
            key = "#" + self.client_id
            self.refresh_token = _refresh_token_cache(key)
        else:
            self.refresh_token = token

        if not self.refresh_token:
            # allow downloading from quarantined subreddits (#2180)
            extractor.cookies.set(
                "_options", '%7B%22pref_quarantine_optin%22%3A%20true%7D',
                domain=extractor.cookies_domain)

    def submission(self, submission_id):
        """Fetch the (submission, comments)=-tuple for a submission id"""
        endpoint = "/comments/" + submission_id + "/.json"
        link_id = "t3_" + submission_id if self.morecomments else None
        submission, comments = self._call(endpoint, {"limit": self.comments})
        return (submission["data"]["children"][0]["data"],
                self._flatten(comments, link_id) if self.comments else ())

    def submissions_subreddit(self, subreddit, params):
        """Collect all (submission, comments)-tuples of a subreddit"""
        endpoint = subreddit + "/.json"
        params["limit"] = 100
        return self._pagination(endpoint, params)

    def submissions_user(self, user, params):
        """Collect all (submission, comments)-tuples posted by a user"""
        endpoint = "/user/" + user + "/.json"
        params["limit"] = 100
        return self._pagination(endpoint, params)

    def morechildren(self, link_id, children):
        """Load additional comments from a submission"""
        endpoint = "/api/morechildren"
        params = {"link_id": link_id, "api_type": "json"}
        index, done = 0, False
        while not done:
            if len(children) - index < 100:
                done = True
            params["children"] = ",".join(children[index:index + 100])
            index += 100

            data = self._call(endpoint, params)["json"]
            for thing in data["data"]["things"]:
                if thing["kind"] == "more":
                    children.extend(thing["data"]["children"])
                else:
                    yield thing["data"]

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        self.headers["Authorization"] = \
            self._authenticate_impl(self.refresh_token)

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, refresh_token=None):
        """Actual authenticate implementation"""
        url = "https://www.reddit.com/api/v1/access_token"
        self.headers["Authorization"] = None

        if refresh_token:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": refresh_token}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": ("https://oauth.reddit.com/"
                                   "grants/installed_client"),
                    "device_id": "DO_NOT_TRACK_THIS_DEVICE"}

        auth = util.HTTPBasicAuth(self.client_id, "")
        response = self.extractor.request(
            url, method="POST", headers=self.headers,
            data=data, auth=auth, fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError('"{}: {}"'.format(
                data.get("error"), data.get("message")))
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, params):
        url = "https://oauth.reddit.com" + endpoint
        params["raw_json"] = "1"

        while True:
            self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            remaining = response.headers.get("x-ratelimit-remaining")
            if remaining and float(remaining) < 2:
                self.log.warning("API rate limit exceeded")
                if self._warn_429 and self.client_id == self.CLIENT_ID:
                    self.log.info(
                        "Register your own OAuth application and use its "
                        "credentials to prevent this error: "
                        "https://gdl-org.github.io/docs/configuration.html"
                        "#extractor-reddit-client-id-user-agent")
                self._warn_429 = False
                self.extractor.wait(
                    seconds=response.headers["x-ratelimit-reset"])
                continue

            try:
                data = response.json()
            except ValueError:
                raise exception.StopExtraction(text.remove_html(response.text))

            if "error" in data:
                if data["error"] == 403:
                    raise exception.AuthorizationError()
                if data["error"] == 404:
                    raise exception.NotFoundError()
                self.log.debug(data)
                raise exception.StopExtraction(data.get("message"))
            return data

    def _pagination(self, endpoint, params):
        id_min = self._parse_id("id-min", 0)
        id_max = self._parse_id("id-max", float("inf"))
        if id_max == 2147483647:
            self.log.debug("Ignoring 'id-max' setting \"zik0zj\"")
            id_max = float("inf")
        date_min, date_max = self.extractor._get_date_min_max(0, 253402210800)

        while True:
            data = self._call(endpoint, params)["data"]

            for child in data["children"]:
                kind = child["kind"]
                post = child["data"]

                if (date_min <= post["created_utc"] <= date_max and
                        id_min <= self._decode(post["id"]) <= id_max):

                    if kind == "t3":
                        if post["num_comments"] and self.comments:
                            try:
                                yield self.submission(post["id"])
                            except exception.AuthorizationError:
                                pass
                        else:
                            yield post, ()

                    elif kind == "t1" and self.comments:
                        yield None, (post,)

            if not data["after"]:
                return
            params["after"] = data["after"]

    def _flatten(self, comments, link_id=None):
        extra = []
        queue = comments["data"]["children"]
        while queue:
            comment = queue.pop(0)
            if comment["kind"] == "more":
                if link_id:
                    extra.extend(comment["data"]["children"])
                continue
            comment = comment["data"]
            yield comment
            if comment["replies"]:
                queue += comment["replies"]["data"]["children"]
        if link_id and extra:
            yield from self.morechildren(link_id, extra)

    def _parse_id(self, key, default):
        sid = self.extractor.config(key)
        return self._decode(sid.rpartition("_")[2].lower()) if sid else default

    @staticmethod
    def _decode(sid):
        return util.bdecode(sid, "0123456789abcdefghijklmnopqrstuvwxyz")


@cache(maxage=36500*86400, keyarg=0)
def _refresh_token_cache(token):
    if token and token[0] == "#":
        return None
    return token

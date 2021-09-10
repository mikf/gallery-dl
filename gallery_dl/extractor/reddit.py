# -*- coding: utf-8 -*-

# Copyright 2017-2021 Mike Fährmann
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
    cookiedomain = None

    def items(self):
        self.api = RedditAPI(self)
        match_submission = RedditSubmissionExtractor.pattern.match
        match_subreddit = RedditSubredditExtractor.pattern.match
        match_user = RedditUserExtractor.pattern.match

        parentdir = self.config("parent-directory")
        max_depth = self.config("recursion", 0)
        videos = self.config("videos", True)

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
                    url = submission["url"]
                    submission["num"] = 0

                    if url.startswith("https://i.redd.it/"):
                        text.nameext_from_url(url, submission)
                        yield Message.Url, url, submission

                    elif "gallery_data" in submission:
                        for submission["num"], url in enumerate(
                                self._extract_gallery(submission), 1):
                            text.nameext_from_url(url, submission)
                            yield Message.Url, url, submission

                    elif submission["is_video"]:
                        if videos:
                            text.nameext_from_url(url, submission)
                            if videos == "ytdl":
                                url = "https://www.reddit.com" + \
                                    submission["permalink"]
                            else:
                                submission["_ytdl_extra"] = {
                                    "title": submission["title"],
                                }
                            yield Message.Url, "ytdl:" + url, submission

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
                        for url in text.extract_iter(
                                comment["body_html"] or "", ' href="', '"'):
                            urls.append((url, comment))

                for url, data in urls:
                    if not url or url[0] == "#":
                        continue
                    if url[0] == "/":
                        url = "https://www.reddit.com" + url

                    match = match_submission(url)
                    if match:
                        extra.append(match.group(1))
                    elif not match_user(url) and not match_subreddit(url):
                        yield Message.Queue, text.unescape(url), data

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
        if submission["gallery_data"] is None:
            self.log.warning("gallery %s: deleted", submission["id"])
            return

        meta = submission["media_metadata"]
        for item in submission["gallery_data"]["items"]:
            data = meta[item["media_id"]]
            if data["status"] != "valid" or "s" not in data:
                self.log.warning(
                    "gallery %s: skipping item %s ('status: %s')",
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


class RedditSubredditExtractor(RedditExtractor):
    """Extractor for URLs from subreddits on reddit.com"""
    subcategory = "subreddit"
    pattern = (r"(?:https?://)?(?:\w+\.)?reddit\.com/r/"
               r"([^/?#]+(?:/([a-z]+))?)/?(?:\?([^#]*))?(?:$|#)")
    test = (
        ("https://www.reddit.com/r/lavaporn/", {
            "range": "1-20",
            "count": ">= 20",
        }),
        ("https://www.reddit.com/r/lavaporn/top/?sort=top&t=month"),
        ("https://old.reddit.com/r/lavaporn/"),
        ("https://np.reddit.com/r/lavaporn/"),
        ("https://m.reddit.com/r/lavaporn/"),
    )

    def __init__(self, match):
        self.subreddit, sub, params = match.groups()
        self.params = text.parse_query(params)
        if sub:
            self.subcategory += "-" + sub
        RedditExtractor.__init__(self, match)

    def submissions(self):
        return self.api.submissions_subreddit(self.subreddit, self.params)


class RedditUserExtractor(RedditExtractor):
    """Extractor for URLs from posts by a reddit user"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:\w+\.)?reddit\.com/u(?:ser)?/"
               r"([^/?#]+(?:/([a-z]+))?)/?(?:\?([^#]*))?")
    test = (
        ("https://www.reddit.com/user/username/", {
            "count": ">= 2",
        }),
        ("https://www.reddit.com/user/username/gilded/?sort=top&t=month"),
        ("https://old.reddit.com/user/username/"),
        ("https://www.reddit.com/u/username/"),
    )

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
               r"(?:\w+\.)?reddit\.com/(?:r/[^/?#]+/comments|gallery)"
               r"|redd\.it)/([a-z0-9]+)")
    test = (
        ("https://www.reddit.com/r/lavaporn/comments/8cqhub/", {
            "pattern": r"https://c2.staticflickr.com/8/7272/\w+_k.jpg",
            "count": 1,
        }),
        ("https://www.reddit.com/r/lavaporn/comments/8cqhub/", {
            "options": (("comments", 500),),
            "pattern": r"https://",
            "count": 3,
        }),
        ("https://www.reddit.com/gallery/hrrh23", {
            "url": "25b91ede15459470274dd17291424b037ed8b0ae",
            "content": "1e7dde4ee7d5f4c4b45749abfd15b2dbfa27df3f",
            "count": 3,
        }),
        # deleted gallery (#953)
        ("https://www.reddit.com/gallery/icfgzv", {
            "count": 0,
        }),
        # animated gallery items (#955)
        ("https://www.reddit.com/r/araragi/comments/ib32hm", {
            "pattern": r"https://i\.redd\.it/\w+\.gif",
            "count": 2,
        }),
        # "failed" gallery item (#1127)
        ("https://www.reddit.com/r/cosplay/comments/jvwaqr", {
            "count": 1,
        }),
        ("https://old.reddit.com/r/lavaporn/comments/2a00np/"),
        ("https://np.reddit.com/r/lavaporn/comments/2a00np/"),
        ("https://m.reddit.com/r/lavaporn/comments/2a00np/"),
        ("https://redd.it/2a00np/"),
    )

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
    pattern = (r"(?:https?://)?i\.redd(?:\.it|ituploads\.com)"
               r"/[^/?#]+(?:\?[^#]*)?")
    test = (
        ("https://i.redd.it/upjtjcx2npzz.jpg", {
            "url": "0de614900feef103e580b632190458c0b62b641a",
            "content": "cc9a68cf286708d5ce23c68e79cd9cf7826db6a3",
        }),
        (("https://i.reddituploads.com/0f44f1b1fca2461f957c713d9592617d"
          "?fit=max&h=1536&w=1536&s=e96ce7846b3c8e1f921d2ce2671fb5e2"), {
            "url": "f24f25efcedaddeec802e46c60d77ef975dc52a5",
            "content": "541dbcc3ad77aa01ee21ca49843c5e382371fae7",
        }),
    )

    def items(self):
        data = text.nameext_from_url(self.url)
        yield Message.Directory, data
        yield Message.Url, self.url, data


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

        token = config("refresh-token")
        if token is None or token == "cache":
            key = "#" + self.client_id
            self.refresh_token = _refresh_token_cache(key)
        else:
            self.refresh_token = token

    def submission(self, submission_id):
        """Fetch the (submission, comments)=-tuple for a submission id"""
        endpoint = "/comments/" + submission_id + "/.json"
        link_id = "t3_" + submission_id if self.morecomments else None
        submission, comments = self._call(endpoint, {"limit": self.comments})
        return (submission["data"]["children"][0]["data"],
                self._flatten(comments, link_id) if self.comments else ())

    def submissions_subreddit(self, subreddit, params):
        """Collect all (submission, comments)-tuples of a subreddit"""
        endpoint = "/r/" + subreddit + "/.json"
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

        response = self.extractor.request(
            url, method="POST", headers=self.headers,
            data=data, auth=(self.client_id, ""), fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError('"{}: {}"'.format(
                data.get("error"), data.get("message")))
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, params):
        url = "https://oauth.reddit.com" + endpoint
        params["raw_json"] = "1"
        self.authenticate()
        response = self.extractor.request(
            url, params=params, headers=self.headers, fatal=None)

        remaining = response.headers.get("x-ratelimit-remaining")
        if remaining and float(remaining) < 2:
            self.extractor.wait(seconds=response.headers["x-ratelimit-reset"])
            return self._call(endpoint, params)

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
        id_max = self._parse_id("id-max", 2147483647)
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


@cache(maxage=100*365*24*3600, keyarg=0)
def _refresh_token_cache(token):
    if token and token[0] == "#":
        return None
    return token

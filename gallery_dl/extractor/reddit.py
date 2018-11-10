# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images subreddits at https://reddit.com/"""

from .common import Extractor, Message
from .. import text, util, extractor, exception
from ..cache import cache
import datetime
import time
import re


class RedditExtractor(Extractor):
    """Base class for reddit extractors"""
    category = "reddit"

    def __init__(self):
        Extractor.__init__(self)
        self.api = RedditAPI(self)
        self.max_depth = int(self.config("recursion", 0))
        self._visited = set()

    def items(self):
        subre = re.compile(RedditSubmissionExtractor.pattern[0])
        submissions = self.submissions()
        depth = 0

        yield Message.Version, 1
        with extractor.blacklist(
                util.SPECIAL_EXTRACTORS, [RedditSubredditExtractor]):
            while True:
                extra = []
                for url in self._urls(submissions):
                    if url[0] == "#":
                        continue
                    if url[0] == "/":
                        url = "https://www.reddit.com" + url

                    match = subre.match(url)
                    if match:
                        extra.append(match.group(1))
                    else:
                        yield Message.Queue, text.unescape(url), {}

                if not extra or depth == self.max_depth:
                    return
                depth += 1
                submissions = (
                    self.api.submission(sid) for sid in extra
                    if sid not in self._visited
                )

    def submissions(self):
        """Return an iterable containing all (submission, comments) tuples"""

    def _urls(self, submissions):
        for submission, comments in submissions:
            self._visited.add(submission["id"])
            if not submission["is_self"]:
                yield submission["url"]
            strings = [submission["selftext_html"] or ""]
            strings += [c["body_html"] or "" for c in comments]
            yield from text.extract_iter("".join(strings), ' href="', '"')


class RedditSubredditExtractor(RedditExtractor):
    """Extractor for images from subreddits on reddit.com"""
    subcategory = "subreddit"
    pattern = [r"(?:https?://)?(?:\w+\.)?reddit\.com/r/([^/?&#]+)"
               r"(/[a-z]+)?/?"
               r"(?:\?.*?(?:\bt=([a-z]+))?)?$"]
    test = [
        ("https://www.reddit.com/r/lavaporn/", None),
        ("https://www.reddit.com/r/lavaporn/top/?sort=top&t=month", None),
        ("https://old.reddit.com/r/lavaporn/", None),
        ("https://np.reddit.com/r/lavaporn/", None),
        ("https://m.reddit.com/r/lavaporn/", None),
    ]

    def __init__(self, match):
        RedditExtractor.__init__(self)
        self.subreddit, self.order, self.timeframe = match.groups()

    def submissions(self):
        subreddit = self.subreddit + (self.order or "")
        params = {"t": self.timeframe} if self.timeframe else {}
        return self.api.submissions_subreddit(subreddit, params)


class RedditSubmissionExtractor(RedditExtractor):
    """Extractor for images from a submission on reddit.com"""
    subcategory = "submission"
    pattern = [(r"(?:https?://)?(?:"
                r"(?:\w+\.)?reddit\.com/r/[^/?&#]+/comments|"
                r"redd\.it"
                r")/([a-z0-9]+)")]
    test = [
        ("https://www.reddit.com/r/lavaporn/comments/2a00np/", {
            "pattern": r"https?://i\.imgur\.com/AaAUCgy\.jpg",
            "count": 1,
        }),
        ("https://old.reddit.com/r/lavaporn/comments/2a00np/", None),
        ("https://np.reddit.com/r/lavaporn/comments/2a00np/", None),
        ("https://m.reddit.com/r/lavaporn/comments/2a00np/", None),
        ("https://redd.it/2a00np/", None),
    ]

    def __init__(self, match):
        RedditExtractor.__init__(self)
        self.submission_id = match.group(1)

    def submissions(self):
        return (self.api.submission(self.submission_id),)


class RedditImageExtractor(Extractor):
    """Extractor for reddit-hosted images"""
    category = "reddit"
    subcategory = "image"
    archive_fmt = "{name}"
    pattern = [r"(?:https?://)?i\.redd(?:\.it|ituploads\.com)"
               r"/[^/?&#]+(?:\?[^#]*)?"]
    test = [
        ("https://i.redd.it/upjtjcx2npzz.jpg", {
            "url": "0de614900feef103e580b632190458c0b62b641a",
            "content": "cc9a68cf286708d5ce23c68e79cd9cf7826db6a3",
        }),
        (("https://i.reddituploads.com/0f44f1b1fca2461f957c713d9592617d"
          "?fit=max&h=1536&w=1536&s=e96ce7846b3c8e1f921d2ce2671fb5e2"), {
            "url": "f24f25efcedaddeec802e46c60d77ef975dc52a5",
            "content": "541dbcc3ad77aa01ee21ca49843c5e382371fae7",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)

    def items(self):
        data = text.nameext_from_url(self.url)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, self.url, data


class RedditAPI():
    """Minimal interface for the reddit API"""
    CLIENT_ID = "6N9uN0krSDE-ig"
    USER_AGENT = "Python:gallery-dl:0.8.4 (by /u/mikf1)"

    def __init__(self, extractor):
        self.extractor = extractor
        self.comments = extractor.config("comments", 500)
        self.morecomments = extractor.config("morecomments", False)
        self.refresh_token = extractor.config("refresh-token")
        self.log = extractor.log
        self.session = extractor.session

        client_id = extractor.config("client-id", self.CLIENT_ID)
        user_agent = extractor.config("user-agent", self.USER_AGENT)

        if (client_id == self.CLIENT_ID) ^ (user_agent == self.USER_AGENT):
            self.client_id = None
            self.log.warning(
                "Conflicting values for 'client-id' and 'user-agent': "
                "override either both or none of them.")
        else:
            self.client_id = client_id
            self.session.headers["User-Agent"] = user_agent

    def submission(self, submission_id):
        """Fetch the (submission, comments)=-tuple for a submission id"""
        endpoint = "/comments/" + submission_id + "/.json"
        link_id = "t3_" + submission_id if self.morecomments else None
        submission, comments = self._call(endpoint, {"limit": self.comments})
        return (submission["data"]["children"][0]["data"],
                self._flatten(comments, link_id))

    def submissions_subreddit(self, subreddit, params):
        """Collect all (submission, comments)-tuples of a subreddit"""
        endpoint = "/r/" + subreddit + "/.json"
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
        access_token = self._authenticate_impl(self.refresh_token)
        self.session.headers["Authorization"] = access_token

    @cache(maxage=3590, keyarg=1)
    def _authenticate_impl(self, refresh_token=None):
        """Actual authenticate implementation"""
        url = "https://www.reddit.com/api/v1/access_token"
        if refresh_token:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": refresh_token}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": ("https://oauth.reddit.com/"
                                   "grants/installed_client"),
                    "device_id": "DO_NOT_TRACK_THIS_DEVICE"}
        response = self.session.post(url, data=data, auth=(self.client_id, ""))
        if response.status_code != 200:
            raise exception.AuthenticationError('"{} ({})"'.format(
                response.json().get("message"), response.status_code))
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint, params):
        url = "https://oauth.reddit.com" + endpoint
        params["raw_json"] = 1
        self.authenticate()
        response = self.session.get(url, params=params)
        remaining = response.headers.get("x-ratelimit-remaining")
        if remaining and float(remaining) < 2:
            wait = int(response.headers["x-ratelimit-reset"])
            self.log.info("Waiting %d seconds for ratelimit reset", wait)
            time.sleep(wait)
        data = response.json()
        if "error" in data:
            if data["error"] == 403:
                raise exception.AuthorizationError()
            if data["error"] == 404:
                raise exception.NotFoundError()
            raise Exception(data["message"])
        return data

    def _pagination(self, endpoint, params, _empty=()):
        date_fmt = self.extractor.config("date-format", "%Y-%m-%dT%H:%M:%S")
        date_min = self._parse_datetime("date-min", 0, date_fmt)
        date_max = self._parse_datetime("date-max", 253402210800, date_fmt)

        id_min = self._parse_id("id-min", 0)
        id_max = self._parse_id("id-max", 2147483647)

        while True:
            data = self._call(endpoint, params)["data"]

            for submission in data["children"]:
                submission = submission["data"]
                if (date_min <= submission["created_utc"] <= date_max and
                        id_min <= self._decode(submission["id"]) <= id_max):
                    if submission["num_comments"] and self.comments:
                        try:
                            yield self.submission(submission["id"])
                        except exception.AuthorizationError:
                            pass
                    else:
                        yield submission, _empty

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

    def _parse_datetime(self, key, default, fmt):
        ts = self.extractor.config(key, default)
        if isinstance(ts, str):
            try:
                ts = int(datetime.datetime.strptime(ts, fmt).timestamp())
            except ValueError as exc:
                self.log.warning("Unable to parse '%s': %s", key, exc)
                ts = default
        return ts

    def _parse_id(self, key, default):
        sid = self.extractor.config(key)
        return self._decode(sid.rpartition("_")[2].lower()) if sid else default

    @staticmethod
    def _decode(sid):
        return util.bdecode(sid, "0123456789abcdefghijklmnopqrstuvwxyz")

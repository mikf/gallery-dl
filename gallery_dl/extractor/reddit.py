# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images subreddits at https://reddit.com/"""

from .common import Extractor, Message
from .. import text, extractor, exception
from ..cache import cache
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
        with extractor.blacklist("reddit"):
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
                        yield Message.Queue, url

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
    pattern = [r"(?:https?://)?(?:m\.|www\.)?reddit\.com/r/([^/?&#]+)"
               r"(/[a-z]+)?/?"
               r"(?:\?.*?(?:\bt=([a-z]+))?)?$"]

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
                r"(?:m\.|www\.)?reddit\.com/r/[^/]+/comments|"
                r"redd\.it"
                r")/([a-z0-9]+)")]

    def __init__(self, match):
        RedditExtractor.__init__(self)
        self.submission_id = match.group(1)

    def submissions(self):
        return (self.api.submission(self.submission_id),)


class RedditAPI():
    """Minimal interface for the reddit API"""
    def __init__(self, extractor, client_id="6N9uN0krSDE-ig"):
        self.session = extractor.session
        self.date_min = int(extractor.config("date-min", 0))
        # 253402210800 == datetime.max.timestamp()
        self.date_max = int(extractor.config("date-max", 253402210800))
        self.client_id = client_id
        self.session.headers["User-Agent"] = ("Python:gallery-dl:0.8.4"
                                              " (by /u/mikf1)")

    def submission(self, submission_id):
        """Fetch the (submission, comments)=-tuple for a submission id"""
        endpoint = "/comments/" + submission_id + "/.json"
        submission, comments = self._call(endpoint, {"limit": 500})
        return (submission["data"]["children"][0]["data"],
                self._unfold(comments))

    def submissions_subreddit(self, subreddit, params):
        """Collect all (submission, comments)-tuples of a subreddit"""
        endpoint = "/r/" + subreddit + "/.json"
        params["limit"] = 100
        return self._pagination(endpoint, params)

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        access_token = self._authenticate_impl(self.client_id)
        self.session.headers["Authorization"] = access_token

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, client_id):
        """Actual authenticate implementation"""
        url = "https://www.reddit.com/api/v1/access_token"
        data = {
            "grant_type": "https://oauth.reddit.com/grants/installed_client",
            "device_id": "DO_NOT_TRACK_THIS_DEVICE",
        }
        response = self.session.post(url, data=data, auth=(client_id, ""))
        if response.status_code != 200:
            raise exception.AuthenticationError()
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint, params):
        url = "https://oauth.reddit.com" + endpoint
        params["raw_json"] = 1
        self.authenticate()
        data = self.session.get(url, params=params).json()
        if "error" in data:
            if data["error"] == 403:
                raise exception.AuthorizationError()
            if data["error"] == 404:
                raise exception.NotFoundError()
            raise Exception(data["message"])
        return data

    def _pagination(self, endpoint, params, _empty=()):
        while True:
            data = self._call(endpoint, params)["data"]

            for submission in data["children"]:
                submission = submission["data"]
                if self.date_min <= submission["created_utc"] <= self.date_max:
                    if submission["num_comments"]:
                        yield self.submission(submission["id"])
                    else:
                        yield submission, _empty

            if not data["after"]:
                return
            params["after"] = data["after"]

    @staticmethod
    def _unfold(comments):
        # TODO: order?
        queue = comments["data"]["children"]
        while queue:
            comment = queue.pop()
            if comment["kind"] == "more":
                continue
            comment = comment["data"]
            yield comment
            if comment["replies"]:
                queue += comment["replies"]["data"]["children"]

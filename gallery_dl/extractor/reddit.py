# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images subreddits at https://reddit.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import re


class RedditExtractor(Extractor):
    """Base class for reddit extractors"""
    category = "reddit"

    def __init__(self):
        Extractor.__init__(self)
        self.api = RedditAPI(self.session, self.log)

    def items(self):
        regex = re.compile(r"https?://(?:[^.]+\.)?reddit.com/")
        yield Message.Version, 1
        for submission, comments in self.submissions():
            urls = [submission["url"]]
            urls.extend(
                text.extract_iter(
                    " ".join(self._collect(submission, comments)),
                    ' href="', '"'
                )
            )
            for url in urls:
                if url[0] == "#":
                    continue
                elif url[0] == "/":
                    url = "nofollow:https://www.reddit.com" + url
                elif regex.match(url):
                    url = "nofollow:" + url
                yield Message.Queue, url

    def _collect(self, submission, comments):
        yield submission["selftext_html"] or ""
        for comment in comments:
            yield comment["body_html"] or ""


class RedditSubredditExtractor(RedditExtractor):
    """Extractor for images from subreddits on reddit.com"""
    subcategory = "submission"
    pattern = [r"(?:https?://)?(?:m\.|www\.)?reddit\.com/r/([^/]+)/?$"]

    def __init__(self, match):
        RedditExtractor.__init__(self)
        self.subreddit = match.group(1)

    def submissions(self):
        return self.api.submissions_subreddit(self.subreddit)


class RedditSubmissionExtractor(RedditExtractor):
    """Extractor for images from a submission on reddit.com"""
    subcategory = "subreddit"
    pattern = [(r"(?:https?://)?(?:m\.|www\.)?reddit\.com/r/[^/]+"
                r"/comments/([a-z0-9]+)"),
               (r"(?:https?://)?redd\.it/([a-z0-9]+)")]

    def __init__(self, match):
        RedditExtractor.__init__(self)
        self.submission_id = match.group(1)

    def submissions(self):
        return (self.api.submission(self.submission_id),)


class RedditAPI():
    """Minimal interface for the reddit API"""
    def __init__(self, session, log, client_id="6N9uN0krSDE-ig"):
        self.session = session
        self.log = log
        self.client_id = client_id
        session.headers["User-Agent"] = "Python:gallery-dl:0.8.4 (by /u/mikf1)"

    def submission(self, submission_id):
        """Fetch the (submission, comments)=-tuple for a submission id"""
        endpoint = "/comments/" + submission_id + "/.json"
        params = {"raw_json": 1, "limit": 100}
        submission, comments = self._call(endpoint, params)
        return (submission["data"]["children"][0]["data"],
                self._unfold(comments))

    def submissions_subreddit(self, subreddit):
        """Collect all (submission, comments)-tuples of a subreddit"""
        endpoint = "/r/" + subreddit + "/.json"
        params = {"raw_json": 1, "limit": 100}
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
        self.log.info("Requesting access token")
        response = self.session.post(url, data=data, auth=(client_id, ""))
        if response.status_code != 200:
            raise exception.AuthenticationError()
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint, params):
        url = "https://oauth.reddit.com" + endpoint
        # TODO: handle errors / rate limits
        self.authenticate()
        response = self.session.get(url, params=params)
        return response.json()

    def _pagination(self, endpoint, params, _empty=()):
        while True:
            data = self._call(endpoint, params)["data"]

            for submission in data["children"]:
                submission = submission["data"]
                if submission["num_comments"]:
                    yield self.submission(submission["id"])
                else:
                    yield submission, _empty

            if not data["after"]:
                return
            params["after"] = data["after"]

    def _unfold(self, comments):
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

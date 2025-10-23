# -*- coding: utf-8 -*-

# Copyright 2017-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.reddit.com/"""

from .common import Extractor, Message
from .. import text


class RedditExtractor(Extractor):
    """Base class for reddit extractors"""
    category = "reddit"
    directory_fmt = ("{category}", "{subreddit}")
    filename_fmt = "{id}{num:? //>02} {title|link_title:[:220]}.{extension}"
    archive_fmt = "{filename}"
    cookies_domain = ".reddit.com"
    request_interval = 0.6

    def items(self):
        self.api = self.utils().RedditAPI(self)
        match_submission = RedditSubmissionExtractor.pattern.match
        match_subreddit = RedditSubredditExtractor.pattern.match
        match_user = RedditUserExtractor.pattern.match

        parentdir = self.config("parent-directory")
        max_depth = self.config("recursion", 0)
        previews = self.config("previews", True)
        embeds = self.config("embeds", True)

        if videos := self.config("videos", True):
            if videos == "ytdl":
                self._extract_video = self._extract_video_ytdl
            elif videos == "dash":
                self._extract_video = self._extract_video_dash
            videos = True

        selftext = self.config("selftext")
        if selftext is None:
            selftext = self.api.comments
        selftext = True if selftext else False

        submissions = self.submissions()
        visited = set()
        depth = 0

        while True:
            extra = []

            for submission, comments in submissions:
                urls = []

                if submission:
                    submission["comment"] = None
                    submission["date"] = self.parse_timestamp(
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

                    elif embeds and "media_metadata" in media:
                        for embed in self._extract_embed(submission):
                            submission["num"] += 1
                            text.nameext_from_url(embed, submission)
                            yield Message.Url, embed, submission

                    elif media["is_video"]:
                        if videos:
                            text.nameext_from_url(url, submission)
                            url = "ytdl:" + self._extract_video(media)
                            yield Message.Url, url, submission

                    elif not submission["is_self"]:
                        urls.append((url, submission))

                    if selftext and (txt := submission["selftext_html"]):
                        for url in text.extract_iter(txt, ' href="', '"'):
                            urls.append((url, submission))

                elif parentdir:
                    yield Message.Directory, comments[0]

                if self.api.comments:
                    if comments and not submission:
                        submission = comments[0]
                        submission.setdefault("num", 0)
                        if not parentdir:
                            yield Message.Directory, submission

                    for comment in comments:
                        media = (embeds and "media_metadata" in comment)
                        html = comment["body_html"] or ""
                        href = (' href="' in html)

                        if not media and not href:
                            continue

                        data = submission.copy()
                        data["comment"] = comment
                        comment["date"] = self.parse_timestamp(
                            comment["created_utc"])

                        if media:
                            for url in self._extract_embed(comment):
                                data["num"] += 1
                                text.nameext_from_url(url, data)
                                yield Message.Url, url, data
                            submission["num"] = data["num"]

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

                    if match := match_submission(url):
                        extra.append(match[1])
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
            if url := src.get("u") or src.get("gif") or src.get("mp4"):
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
            if data["status"] != "valid":
                self.log.warning(
                    "embed %s: skipping item %s (status: %s)",
                    submission["id"], mid, data.get("status"))
                continue

            if src := data.get("s"):
                if url := src.get("u") or src.get("gif") or src.get("mp4"):
                    yield url.partition("?")[0].replace("/preview.", "/i.", 1)
                else:
                    self.log.error(
                        "embed %s: unable to fetch download URL for item %s",
                        submission["id"], mid)
                    self.log.debug(src)
            elif url := data.get("dashUrl"):
                submission["_ytdl_manifest"] = "dash"
                yield f"ytdl:{url}"
            elif url := data.get("hlsUrl"):
                submission["_ytdl_manifest"] = "hls"
                yield f"ytdl:{url}"

    def _extract_video_ytdl(self, submission):
        return "https://www.reddit.com" + submission["permalink"]

    def _extract_video_dash(self, submission):
        submission["_ytdl_extra"] = {"title": submission["title"]}
        try:
            url = submission["secure_media"]["reddit_video"]["dash_url"]
            submission["_ytdl_manifest"] = "dash"
            return url
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
                if variants := image.get("variants"):
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
            if sub == "search" and "restrict_sr" not in self.params:
                self.params["restrict_sr"] = "1"
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
               r"(?:\w+\.)?reddit\.com/(?:(?:(?:r|u|user)/[^/?#]+/)?"
               r"comments|gallery)|redd\.it)/([a-z0-9]+)")
    example = "https://www.reddit.com/r/SUBREDDIT/comments/id/"

    def __init__(self, match):
        RedditExtractor.__init__(self, match)
        self.submission_id = match[1]

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
        domain = match[1]
        self.path = match[2]
        if domain == "preview.redd.it":
            self.domain = "i.redd.it"
            self.query = ""
        else:
            self.domain = domain
            self.query = match[3] or ""

    def items(self):
        url = f"https://{self.domain}/{self.path}{self.query}"
        data = text.nameext_from_url(url)
        yield Message.Directory, data
        yield Message.Url, url, data


class RedditRedirectExtractor(Extractor):
    """Extractor for personalized share URLs produced by the mobile app"""
    category = "reddit"
    subcategory = "redirect"
    pattern = (r"(?:https?://)?(?:"
               r"(?:\w+\.)?reddit\.com/(?:(r|u|user)/([^/?#]+)))"
               r"/s/([a-zA-Z0-9]{10})")
    example = "https://www.reddit.com/r/SUBREDDIT/s/abc456GHIJ"

    def items(self):
        sub_type, subreddit, share_url = self.groups
        if sub_type == "u":
            sub_type = "user"
        url = f"https://www.reddit.com/{sub_type}/{subreddit}/s/{share_url}"
        location = self.request_location(url, notfound="submission")
        data = {"_extractor": RedditSubmissionExtractor}
        yield Message.Queue, location, data

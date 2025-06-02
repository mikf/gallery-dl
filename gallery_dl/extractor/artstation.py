# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.artstation.com/"""

from .common import Extractor, Message
from .. import text, util, exception
import itertools


class ArtstationExtractor(Extractor):
    """Base class for artstation extractors"""
    category = "artstation"
    filename_fmt = "{category}_{id}_{asset[id]}_{title}.{extension}"
    directory_fmt = ("{category}", "{userinfo[username]}")
    archive_fmt = "{asset[id]}"
    browser = "firefox"
    tls12 = False
    root = "https://www.artstation.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1) or match.group(2)

    def _init(self):
        self.session.headers["Cache-Control"] = "max-age=0"

    def items(self):
        videos = self.config("videos", True)
        previews = self.config("previews", False)
        external = self.config("external", False)
        max_posts = self.config("max-posts")

        data = self.metadata()
        projects = self.projects()
        if max_posts:
            projects = itertools.islice(projects, max_posts)

        for project in projects:
            for num, asset in enumerate(
                    self.get_project_assets(project["hash_id"]), 1):
                asset.update(data)
                adict = asset["asset"]
                asset["num"] = num
                yield Message.Directory, asset

                if adict["has_embedded_player"]:
                    player = adict["player_embedded"]
                    url = (text.extr(player, 'src="', '"') or
                           text.extr(player, "src='", "'"))
                    if url.startswith(self.root):
                        # video clip hosted on artstation
                        if videos:
                            page = self.request(url).text
                            url = text.extr(page, ' src="', '"')
                            text.nameext_from_url(url, asset)
                            yield Message.Url, url, asset
                    elif url:
                        # external URL
                        if external:
                            asset["extension"] = "mp4"
                            yield Message.Url, "ytdl:" + url, asset
                    else:
                        self.log.debug(player)
                        self.log.warning(
                            "Failed to extract embedded player URL (%s)",
                            adict.get("id"))

                    if not previews:
                        continue

                if adict["has_image"]:
                    url = adict["image_url"]
                    text.nameext_from_url(url, asset)

                    url = self._no_cache(url)
                    if "/video_clips/" not in url:
                        lhs, _, rhs = url.partition("/large/")
                        if rhs:
                            url = lhs + "/4k/" + rhs
                            asset["_fallback"] = self._image_fallback(lhs, rhs)

                    yield Message.Url, url, asset

    @staticmethod
    def _image_fallback(lhs, rhs):
        yield lhs + "/large/" + rhs
        yield lhs + "/medium/" + rhs
        yield lhs + "/small/" + rhs

    def metadata(self):
        """Return general metadata"""
        return {"userinfo": self.get_user_info(self.user)}

    def projects(self):
        """Return an iterable containing all relevant project IDs"""

    def get_project_assets(self, project_id):
        """Return all assets associated with 'project_id'"""
        url = "{}/projects/{}.json".format(self.root, project_id)

        try:
            data = self.request(url).json()
        except exception.HttpError as exc:
            self.log.warning(exc)
            return

        data["title"] = text.unescape(data["title"])
        data["description"] = text.unescape(text.remove_html(
            data["description"]))
        data["date"] = text.parse_datetime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

        assets = data["assets"]
        del data["assets"]

        data["count"] = len(assets)
        if len(assets) == 1:
            data["asset"] = assets[0]
            yield data
        else:
            for asset in assets:
                data["asset"] = asset
                yield data.copy()

    def get_user_info(self, username):
        """Return metadata for a specific user"""
        url = "{}/users/{}/quick.json".format(self.root, username.lower())
        response = self.request(url, notfound="user")
        return response.json()

    def _pagination(self, url, params=None, json=None):
        headers = {
            "Accept" : "application/json, text/plain, */*",
            "Origin" : self.root,
        }

        if json:
            params = json
            headers["PUBLIC-CSRF-TOKEN"] = self._init_csrf_token()
            kwargs = {"method": "POST", "headers": headers, "json": json}
        else:
            if not params:
                params = {}
            kwargs = {"params": params, "headers": headers}

        total = 0
        params["page"] = 1

        while True:
            data = self.request(url, **kwargs).json()
            yield from data["data"]

            total += len(data["data"])
            if total >= data["total_count"]:
                return

            params["page"] += 1

    def _init_csrf_token(self):
        url = self.root + "/api/v2/csrf_protection/token.json"
        headers = {
            "Accept" : "*/*",
            "Origin" : self.root,
        }
        return self.request(
            url, method="POST", headers=headers, json={},
        ).json()["public_csrf_token"]

    @staticmethod
    def _no_cache(url):
        """Cause a cache miss to prevent Cloudflare 'optimizations'

        Cloudflare's 'Polish' optimization strips image metadata and may even
        recompress an image as lossy JPEG. This can be prevented by causing
        a cache miss when requesting an image by adding a random dummy query
        parameter.

        Ref:
        https://github.com/r888888888/danbooru/issues/3528
        https://danbooru.donmai.us/forum_topics/14952
        """
        sep = "&" if "?" in url else "?"
        token = util.generate_token(8)
        return url + sep + token[:4] + "=" + token[4:]


class ArtstationUserExtractor(ArtstationExtractor):
    """Extractor for all projects of an artstation user"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:(?:www\.)?artstation\.com"
               r"/(?!artwork|projects|search)([^/?#]+)(?:/albums/all)?"
               r"|((?!www)[\w-]+)\.artstation\.com(?:/projects)?)/?$")
    example = "https://www.artstation.com/USER"

    def projects(self):
        url = "{}/users/{}/projects.json".format(self.root, self.user)
        params = {"album_id": "all"}
        return self._pagination(url, params)


class ArtstationAlbumExtractor(ArtstationExtractor):
    """Extractor for all projects in an artstation album"""
    subcategory = "album"
    directory_fmt = ("{category}", "{userinfo[username]}", "Albums",
                     "{album[id]} - {album[title]}")
    archive_fmt = "a_{album[id]}_{asset[id]}"
    pattern = (r"(?:https?://)?(?:(?:www\.)?artstation\.com"
               r"/(?!artwork|projects|search)([^/?#]+)"
               r"|((?!www)[\w-]+)\.artstation\.com)/albums/(\d+)")
    example = "https://www.artstation.com/USER/albums/12345"

    def __init__(self, match):
        ArtstationExtractor.__init__(self, match)
        self.album_id = text.parse_int(match.group(3))

    def metadata(self):
        userinfo = self.get_user_info(self.user)
        album = None

        for album in userinfo["albums_with_community_projects"]:
            if album["id"] == self.album_id:
                break
        else:
            raise exception.NotFoundError("album")

        return {
            "userinfo": userinfo,
            "album": album
        }

    def projects(self):
        url = "{}/users/{}/projects.json".format(self.root, self.user)
        params = {"album_id": self.album_id}
        return self._pagination(url, params)


class ArtstationLikesExtractor(ArtstationExtractor):
    """Extractor for liked projects of an artstation user"""
    subcategory = "likes"
    directory_fmt = ("{category}", "{userinfo[username]}", "Likes")
    archive_fmt = "f_{userinfo[id]}_{asset[id]}"
    pattern = (r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/(?!artwork|projects|search)([^/?#]+)/likes")
    example = "https://www.artstation.com/USER/likes"

    def projects(self):
        url = "{}/users/{}/likes.json".format(self.root, self.user)
        return self._pagination(url)


class ArtstationCollectionExtractor(ArtstationExtractor):
    """Extractor for an artstation collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{user}",
                     "{collection[id]} {collection[name]}")
    archive_fmt = "c_{collection[id]}_{asset[id]}"
    pattern = (r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/(?!artwork|projects|search)([^/?#]+)/collections/(\d+)")
    example = "https://www.artstation.com/USER/collections/12345"

    def __init__(self, match):
        ArtstationExtractor.__init__(self, match)
        self.collection_id = match.group(2)

    def metadata(self):
        url = "{}/collections/{}.json".format(
            self.root, self.collection_id)
        params = {"username": self.user}
        collection = self.request(
            url, params=params, notfound="collection").json()
        return {"collection": collection, "user": self.user}

    def projects(self):
        url = "{}/collections/{}/projects.json".format(
            self.root, self.collection_id)
        params = {"collection_id": self.collection_id}
        return self._pagination(url, params)


class ArtstationCollectionsExtractor(ArtstationExtractor):
    """Extractor for an artstation user's collections"""
    subcategory = "collections"
    pattern = (r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/(?!artwork|projects|search)([^/?#]+)/collections/?$")
    example = "https://www.artstation.com/USER/collections"

    def items(self):
        url = self.root + "/collections.json"
        params = {"username": self.user}

        for collection in self.request(
                url, params=params, notfound="collections").json():
            url = "{}/{}/collections/{}".format(
                self.root, self.user, collection["id"])
            collection["_extractor"] = ArtstationCollectionExtractor
            yield Message.Queue, url, collection


class ArtstationChallengeExtractor(ArtstationExtractor):
    """Extractor for submissions of artstation challenges"""
    subcategory = "challenge"
    filename_fmt = "{submission_id}_{asset_id}_{filename}.{extension}"
    directory_fmt = ("{category}", "Challenges",
                     "{challenge[id]} - {challenge[title]}")
    archive_fmt = "c_{challenge[id]}_{asset_id}"
    pattern = (r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/contests/[^/?#]+/challenges/(\d+)"
               r"/?(?:\?sorting=([a-z]+))?")
    example = "https://www.artstation.com/contests/NAME/challenges/12345"

    def __init__(self, match):
        ArtstationExtractor.__init__(self, match)
        self.challenge_id = match.group(1)
        self.sorting = match.group(2) or "popular"

    def items(self):
        challenge_url = "{}/contests/_/challenges/{}.json".format(
            self.root, self.challenge_id)
        submission_url = "{}/contests/_/challenges/{}/submissions.json".format(
            self.root, self.challenge_id)
        update_url = "{}/contests/submission_updates.json".format(
            self.root)

        challenge = self.request(challenge_url).json()
        yield Message.Directory, {"challenge": challenge}

        params = {"sorting": self.sorting}
        for submission in self._pagination(submission_url, params):

            params = {"submission_id": submission["id"]}
            for update in self._pagination(update_url, params=params):

                del update["replies"]
                update["challenge"] = challenge
                for url in text.extract_iter(
                        update["body_presentation_html"], ' href="', '"'):
                    update["asset_id"] = self._id_from_url(url)
                    text.nameext_from_url(url, update)
                    yield Message.Url, self._no_cache(url), update

    @staticmethod
    def _id_from_url(url):
        """Get an image's submission ID from its URL"""
        parts = url.split("/")
        return text.parse_int("".join(parts[7:10]))


class ArtstationSearchExtractor(ArtstationExtractor):
    """Extractor for artstation search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Searches", "{search[query]}")
    archive_fmt = "s_{search[query]}_{asset[id]}"
    pattern = (r"(?:https?://)?(?:\w+\.)?artstation\.com"
               r"/search/?\?([^#]+)")
    example = "https://www.artstation.com/search?query=QUERY"

    def __init__(self, match):
        ArtstationExtractor.__init__(self, match)
        self.params = query = text.parse_query(match.group(1))
        self.query = text.unquote(query.get("query") or query.get("q", ""))
        self.sorting = query.get("sort_by", "relevance").lower()
        self.tags = query.get("tags", "").split(",")

    def metadata(self):
        return {"search": {
            "query"  : self.query,
            "sorting": self.sorting,
            "tags"   : self.tags,
        }}

    def projects(self):
        filters = []
        for key, value in self.params.items():
            if key.endswith("_ids") or key == "tags":
                filters.append({
                    "field" : key,
                    "method": "include",
                    "value" : value.split(","),
                })

        url = "{}/api/v2/search/projects.json".format(self.root)
        data = {
            "query"            : self.query,
            "page"             : None,
            "per_page"         : 50,
            "sorting"          : self.sorting,
            "pro_first"        : ("1" if self.config("pro-first", True) else
                                  "0"),
            "filters"          : filters,
            "additional_fields": (),
        }
        return self._pagination(url, json=data)


class ArtstationArtworkExtractor(ArtstationExtractor):
    """Extractor for projects on artstation's artwork page"""
    subcategory = "artwork"
    directory_fmt = ("{category}", "Artworks", "{artwork[sorting]!c}")
    archive_fmt = "A_{asset[id]}"
    pattern = (r"(?:https?://)?(?:\w+\.)?artstation\.com"
               r"/artwork/?\?([^#]+)")
    example = "https://www.artstation.com/artwork?sorting=SORT"

    def __init__(self, match):
        ArtstationExtractor.__init__(self, match)
        self.query = text.parse_query(match.group(1))

    def metadata(self):
        return {"artwork": self.query}

    def projects(self):
        url = "{}/projects.json".format(self.root)
        return self._pagination(url, self.query.copy())


class ArtstationImageExtractor(ArtstationExtractor):
    """Extractor for images from a single artstation project"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:[\w-]+\.)?artstation\.com/(?:artwork|projects|search)"
               r"|artstn\.co/p)/(\w+)")
    example = "https://www.artstation.com/artwork/abcde"

    def __init__(self, match):
        ArtstationExtractor.__init__(self, match)
        self.project_id = match.group(1)
        self.assets = None

    def metadata(self):
        self.assets = list(ArtstationExtractor.get_project_assets(
            self, self.project_id))
        try:
            self.user = self.assets[0]["user"]["username"]
        except IndexError:
            self.user = ""
        return ArtstationExtractor.metadata(self)

    def projects(self):
        return ({"hash_id": self.project_id},)

    def get_project_assets(self, project_id):
        return self.assets


class ArtstationFollowingExtractor(ArtstationExtractor):
    """Extractor for a user's followed users"""
    subcategory = "following"
    pattern = (r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/(?!artwork|projects|search)([^/?#]+)/following")
    example = "https://www.artstation.com/USER/following"

    def items(self):
        url = "{}/users/{}/following.json".format(self.root, self.user)
        for user in self._pagination(url):
            url = "{}/{}".format(self.root, user["username"])
            user["_extractor"] = ArtstationUserExtractor
            yield Message.Queue, url, user

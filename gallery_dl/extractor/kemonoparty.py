# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kemono.su/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import itertools
import json
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.|beta\.)?(kemono|coomer)\.(su|party)"
USER_PATTERN = BASE_PATTERN + r"/([^/?#]+)/user/([^/?#]+)"
HASH_PATTERN = r"/[0-9a-f]{2}/[0-9a-f]{2}/([0-9a-f]{64})"


class KemonopartyExtractor(Extractor):
    """Base class for kemonoparty extractors"""
    category = "kemonoparty"
    root = "https://kemono.su"
    directory_fmt = ("{category}", "{service}", "{user}")
    filename_fmt = "{id}_{title[:180]}_{num:>02}_{filename[:180]}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"
    cookies_domain = ".kemono.su"

    def __init__(self, match):
        domain = match.group(1)
        tld = match.group(2)
        self.category = domain + "party"
        self.root = text.root_from_url(match.group(0))
        self.cookies_domain = ".{}.{}".format(domain, tld)
        Extractor.__init__(self, match)

    def _init(self):
        self.api = KemonoAPI(self)
        self.revisions = self.config("revisions")
        if self.revisions:
            self.revisions_unique = (self.revisions == "unique")
        order = self.config("order-revisions")
        self.revisions_reverse = order[0] in ("r", "a") if order else False

        self._prepare_ddosguard_cookies()
        self._find_inline = re.compile(
            r'src="(?:https?://(?:kemono|coomer)\.(?:su|party))?(/inline/[^"]+'
            r'|/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{64}\.[^"]+)').findall
        self._json_dumps = json.JSONEncoder(
            ensure_ascii=False, check_circular=False,
            sort_keys=True, separators=(",", ":")).encode

    def items(self):
        find_hash = re.compile(HASH_PATTERN).match
        generators = self._build_file_generators(self.config("files"))
        announcements = True if self.config("announcements") else None
        archives = True if self.config("archives") else False
        comments = True if self.config("comments") else False
        duplicates = True if self.config("duplicates") else False
        dms = True if self.config("dms") else None
        max_posts = self.config("max-posts")
        creator_info = {} if self.config("metadata", True) else None
        exts_archive = {"zip", "rar", "7z"}

        # prevent files from being sent with gzip compression
        headers = {"Accept-Encoding": "identity"}

        posts = self.posts()
        if max_posts:
            posts = itertools.islice(posts, max_posts)
        if self.revisions:
            posts = self._revisions(posts)

        for post in posts:
            headers["Referer"] = "{}/{}/user/{}/post/{}".format(
                self.root, post["service"], post["user"], post["id"])
            post["_http_headers"] = headers
            post["date"] = self._parse_datetime(
                post.get("published") or post.get("added") or "")
            service = post["service"]
            creator_id = post["user"]

            if creator_info is not None:
                key = "{}_{}".format(service, creator_id)
                if key not in creator_info:
                    creator = creator_info[key] = self.api.creator_profile(
                        service, creator_id)
                else:
                    creator = creator_info[key]

                post["user_profile"] = creator
                post["username"] = creator["name"]

            if comments:
                try:
                    post["comments"] = self.api.creator_post_comments(
                        service, creator_id, post["id"])
                except exception.HttpError:
                    post["comments"] = ()
            if dms is not None:
                if dms is True:
                    dms = self.api.creator_dms(
                        post["service"], post["user"])
                    try:
                        dms = dms["props"]["dms"]
                    except Exception:
                        dms = ()
                post["dms"] = dms
            if announcements is not None:
                if announcements is True:
                    announcements = self.api.creator_announcements(
                        post["service"], post["user"])
                post["announcements"] = announcements

            files = []
            hashes = set()
            post_archives = post["archives"] = []

            for file in itertools.chain.from_iterable(
                    g(post) for g in generators):
                url = file["path"]

                if "\\" in url:
                    file["path"] = url = url.replace("\\", "/")

                match = find_hash(url)
                if match:
                    file["hash"] = hash = match.group(1)
                    if not duplicates:
                        if hash in hashes:
                            self.log.debug("Skipping %s (duplicate)", url)
                            continue
                        hashes.add(hash)
                else:
                    file["hash"] = hash = ""

                if url[0] == "/":
                    url = self.root + "/data" + url
                elif url.startswith(self.root):
                    url = self.root + "/data" + url[20:]
                file["url"] = url

                text.nameext_from_url(file.get("name", url), file)
                ext = text.ext_from_url(url)
                if not file["extension"]:
                    file["extension"] = ext
                elif ext == "txt" and file["extension"] != "txt":
                    file["_http_validate"] = _validate
                elif ext in exts_archive:
                    file["type"] = "archive"
                    if archives:
                        try:
                            data = self.api.posts_archives(file["hash"])
                            data.update(file)
                            post_archives.append(data)
                        except Exception as exc:
                            self.log.warning(
                                "%s: Failed to retrieve archive metadata of "
                                "'%s' (%s: %s)", post["id"], file.get("name"),
                                exc.__class__.__name__, exc)
                            post_archives.append(file.copy())
                    else:
                        post_archives.append(file.copy())

                files.append(file)

            post["count"] = len(files)
            yield Message.Directory, post
            for post["num"], file in enumerate(files, 1):
                if "id" in file:
                    del file["id"]
                post.update(file)
                yield Message.Url, file["url"], post

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(
                (username, self.cookies_domain), password))

    @cache(maxage=3650*86400, keyarg=1)
    def _login_impl(self, username, password):
        username = username[0]
        self.log.info("Logging in as %s", username)

        url = self.root + "/api/v1/authentication/login"
        data = {"username": username, "password": password}

        response = self.request(url, method="POST", json=data, fatal=False)
        if response.status_code >= 400:
            try:
                msg = '"' + response.json()["error"] + '"'
            except Exception:
                msg = '"Username or password is incorrect"'
            raise exception.AuthenticationError(msg)

        return {c.name: c.value for c in response.cookies}

    def _file(self, post):
        file = post["file"]
        if not file or "path" not in file:
            return ()
        file["type"] = "file"
        return (file,)

    def _attachments(self, post):
        for attachment in post["attachments"]:
            attachment["type"] = "attachment"
        return post["attachments"]

    def _inline(self, post):
        for path in self._find_inline(post.get("content") or ""):
            yield {"path": path, "name": path, "type": "inline"}

    def _build_file_generators(self, filetypes):
        if filetypes is None:
            return (self._attachments, self._file, self._inline)
        genmap = {
            "file"       : self._file,
            "attachments": self._attachments,
            "inline"     : self._inline,
        }
        if isinstance(filetypes, str):
            filetypes = filetypes.split(",")
        return [genmap[ft] for ft in filetypes]

    def _parse_datetime(self, date_string):
        if len(date_string) > 19:
            date_string = date_string[:19]
        return text.parse_datetime(date_string, "%Y-%m-%dT%H:%M:%S")

    def _revisions(self, posts):
        return itertools.chain.from_iterable(
            self._revisions_post(post) for post in posts)

    def _revisions_post(self, post):
        post["revision_id"] = 0

        try:
            revs = self.api.creator_post_revisions(
                post["service"], post["user"], post["id"])
        except exception.HttpError:
            post["revision_hash"] = self._revision_hash(post)
            post["revision_index"] = 1
            post["revision_count"] = 1
            return (post,)
        revs.insert(0, post)

        for rev in revs:
            rev["revision_hash"] = self._revision_hash(rev)

        if self.revisions_unique:
            uniq = []
            last = None
            for rev in revs:
                if last != rev["revision_hash"]:
                    last = rev["revision_hash"]
                    uniq.append(rev)
            revs = uniq

        cnt = idx = len(revs)
        for rev in revs:
            rev["revision_index"] = idx
            rev["revision_count"] = cnt
            idx -= 1

        if self.revisions_reverse:
            revs.reverse()

        return revs

    def _revisions_all(self, service, creator_id, post_id):
        revs = self.api.creator_post_revisions(service, creator_id, post_id)

        cnt = idx = len(revs)
        for rev in revs:
            rev["revision_hash"] = self._revision_hash(rev)
            rev["revision_index"] = idx
            rev["revision_count"] = cnt
            idx -= 1

        if self.revisions_reverse:
            revs.reverse()

        return revs

    def _revision_hash(self, revision):
        rev = revision.copy()
        rev.pop("revision_id", None)
        rev.pop("added", None)
        rev.pop("next", None)
        rev.pop("prev", None)
        rev["file"] = rev["file"].copy()
        rev["file"].pop("name", None)
        rev["attachments"] = [a.copy() for a in rev["attachments"]]
        for a in rev["attachments"]:
            a.pop("name", None)
        return util.sha1(self._json_dumps(rev))


def _validate(response):
    return (response.headers["content-length"] != "9" or
            response.content != b"not found")


class KemonopartyUserExtractor(KemonopartyExtractor):
    """Extractor for all posts from a kemono.su user listing"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:\?([^#]+))?(?:$|\?|#)"
    example = "https://kemono.su/SERVICE/user/12345"

    def __init__(self, match):
        self.subcategory = match.group(3)
        KemonopartyExtractor.__init__(self, match)

    def posts(self):
        _, _, service, creator_id, query = self.groups
        params = text.parse_query(query)
        if params.get("tag"):
            return self.api.creator_tagged_posts(
                service, creator_id, params.get("tag"), params.get("o"))
        else:
            return self.api.creator_posts(
                service, creator_id, params.get("o"), params.get("q"))


class KemonopartyPostsExtractor(KemonopartyExtractor):
    """Extractor for kemono.su post listings"""
    subcategory = "posts"
    pattern = BASE_PATTERN + r"/posts()()(?:/?\?([^#]+))?"
    example = "https://kemono.su/posts"

    def posts(self):
        params = text.parse_query(self.groups[4])
        return self.api.posts(
            params.get("o"), params.get("q"), params.get("tag"))


class KemonopartyPostExtractor(KemonopartyExtractor):
    """Extractor for a single kemono.su post"""
    subcategory = "post"
    pattern = USER_PATTERN + r"/post/([^/?#]+)(/revisions?(?:/(\d*))?)?"
    example = "https://kemono.su/SERVICE/user/12345/post/12345"

    def __init__(self, match):
        self.subcategory = match.group(3)
        KemonopartyExtractor.__init__(self, match)

    def posts(self):
        _, _, service, creator_id, post_id, revision, revision_id = self.groups
        post = self.api.creator_post(service, creator_id, post_id)
        if not revision:
            return (post["post"],)

        self.revisions = False

        revs = self._revisions_all(service, creator_id, post_id)
        if not revision_id:
            return revs

        for rev in revs:
            if str(rev["revision_id"]) == revision_id:
                return (rev,)

        raise exception.NotFoundError("revision")


class KemonopartyDiscordExtractor(KemonopartyExtractor):
    """Extractor for kemono.su discord servers"""
    subcategory = "discord"
    directory_fmt = ("{category}", "discord", "{server}",
                     "{channel_name|channel}")
    filename_fmt = "{id}_{num:>02}_{filename}.{extension}"
    archive_fmt = "discord_{server}_{id}_{num}"
    pattern = (BASE_PATTERN + r"/discord/server/(\d+)"
               r"(?:/(?:channel/)?(\d+)(?:#(.+))?|#(.+))")
    example = "https://kemono.su/discord/server/12345/12345"

    def items(self):
        self._prepare_ddosguard_cookies()
        _, _, server_id, channel_id, channel_name, channel = self.groups

        if channel_id is None:
            if channel.isdecimal() and len(channel) >= 16:
                key = "id"
            else:
                key = "name"
        else:
            key = "id"
            channel = channel_id

        if not channel_name or not channel_id:
            for ch in self.api.discord_server(server_id):
                if ch[key] == channel:
                    break
            else:
                raise exception.NotFoundError("channel")
            channel_id = ch["id"]
            channel_name = ch["name"]

        find_inline = re.compile(
            r"https?://(?:cdn\.discordapp.com|media\.discordapp\.net)"
            r"(/[A-Za-z0-9-._~:/?#\[\]@!$&'()*+,;%=]+)").findall
        find_hash = re.compile(HASH_PATTERN).match

        posts = self.api.discord_channel(channel_id)
        max_posts = self.config("max-posts")
        if max_posts:
            posts = itertools.islice(posts, max_posts)

        for post in posts:
            files = []
            append = files.append
            for attachment in post["attachments"]:
                match = find_hash(attachment["path"])
                attachment["hash"] = match.group(1) if match else ""
                attachment["type"] = "attachment"
                append(attachment)
            for path in find_inline(post["content"] or ""):
                append({"path": "https://cdn.discordapp.com" + path,
                        "name": path, "type": "inline", "hash": ""})

            post["channel_name"] = channel_name
            post["date"] = self._parse_datetime(post["published"])
            post["count"] = len(files)
            yield Message.Directory, post

            for post["num"], file in enumerate(files, 1):
                post["hash"] = file["hash"]
                post["type"] = file["type"]
                url = file["path"]

                text.nameext_from_url(file.get("name", url), post)
                if not post["extension"]:
                    post["extension"] = text.ext_from_url(url)

                if url[0] == "/":
                    url = self.root + "/data" + url
                elif url.startswith(self.root):
                    url = self.root + "/data" + url[20:]
                yield Message.Url, url, post


class KemonopartyDiscordServerExtractor(KemonopartyExtractor):
    subcategory = "discord-server"
    pattern = BASE_PATTERN + r"/discord/server/(\d+)$"
    example = "https://kemono.su/discord/server/12345"

    def items(self):
        server_id = self.groups[2]
        for channel in self.api.discord_server(server_id):
            url = "{}/discord/server/{}/{}#{}".format(
                self.root, server_id, channel["id"], channel["name"])
            channel["_extractor"] = KemonopartyDiscordExtractor
            yield Message.Queue, url, channel


class KemonopartyFavoriteExtractor(KemonopartyExtractor):
    """Extractor for kemono.su favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/(?:account/)?favorites()()(?:/?\?([^#]+))?"
    example = "https://kemono.su/account/favorites/artists"

    def items(self):
        self._prepare_ddosguard_cookies()
        self.login()

        params = text.parse_query(self.groups[4])
        type = params.get("type") or self.config("favorites") or "artist"

        sort = params.get("sort")
        order = params.get("order") or "desc"

        if type == "artist":
            users = self.api.account_favorites("artist")

            if not sort:
                sort = "updated"
            users.sort(key=lambda x: x[sort] or util.NONE,
                       reverse=(order == "desc"))

            for user in users:
                service = user["service"]
                if service == "discord":
                    user["_extractor"] = KemonopartyDiscordServerExtractor
                    url = "{}/discord/server/{}".format(
                        self.root, user["id"])
                else:
                    user["_extractor"] = KemonopartyUserExtractor
                    url = "{}/{}/user/{}".format(
                        self.root, service, user["id"])
                yield Message.Queue, url, user

        elif type == "post":
            posts = self.api.account_favorites("post")

            if not sort:
                sort = "faved_seq"
            posts.sort(key=lambda x: x[sort] or util.NONE,
                       reverse=(order == "desc"))

            for post in posts:
                post["_extractor"] = KemonopartyPostExtractor
                url = "{}/{}/user/{}/post/{}".format(
                    self.root, post["service"], post["user"], post["id"])
                yield Message.Queue, url, post


class KemonoAPI():
    """Interface for the Kemono API v1.1.0

    https://kemono.su/documentation/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api/v1"

    def posts(self, offset=0, query=None, tags=None):
        endpoint = "/posts"
        params = {"q": query, "o": offset, "tag": tags}
        return self._pagination(endpoint, params, 50, "posts")

    def posts_archives(self, file_hash):
        endpoint = "/posts/archives/" + file_hash
        return self._call(endpoint)["archive"]

    def creator_posts(self, service, creator_id, offset=0, query=None):
        endpoint = "/{}/user/{}".format(service, creator_id)
        params = {"q": query, "o": offset}
        return self._pagination(endpoint, params, 50)

    def creator_tagged_posts(self, service, creator_id, tags, offset=0):
        endpoint = "/{}/user/{}/posts-legacy".format(service, creator_id)
        params = {"o": offset, "tag": tags}
        return self._pagination(endpoint, params, 50, "results")

    def creator_announcements(self, service, creator_id):
        endpoint = "/{}/user/{}/announcements".format(service, creator_id)
        return self._call(endpoint)

    def creator_dms(self, service, creator_id):
        endpoint = "/{}/user/{}/dms".format(service, creator_id)
        return self._call(endpoint)

    def creator_fancards(self, service, creator_id):
        endpoint = "/{}/user/{}/fancards".format(service, creator_id)
        return self._call(endpoint)

    def creator_post(self, service, creator_id, post_id):
        endpoint = "/{}/user/{}/post/{}".format(service, creator_id, post_id)
        return self._call(endpoint)

    def creator_post_comments(self, service, creator_id, post_id):
        endpoint = "/{}/user/{}/post/{}/comments".format(
            service, creator_id, post_id)
        return self._call(endpoint)

    def creator_post_revisions(self, service, creator_id, post_id):
        endpoint = "/{}/user/{}/post/{}/revisions".format(
            service, creator_id, post_id)
        return self._call(endpoint)

    def creator_profile(self, service, creator_id):
        endpoint = "/{}/user/{}/profile".format(service, creator_id)
        return self._call(endpoint)

    def creator_links(self, service, creator_id):
        endpoint = "/{}/user/{}/links".format(service, creator_id)
        return self._call(endpoint)

    def creator_tags(self, service, creator_id):
        endpoint = "/{}/user/{}/tags".format(service, creator_id)
        return self._call(endpoint)

    def discord_channel(self, channel_id):
        endpoint = "/discord/channel/{}".format(channel_id)
        return self._pagination(endpoint, {}, 150)

    def discord_server(self, server_id):
        endpoint = "/discord/channel/lookup/{}".format(server_id)
        return self._call(endpoint)

    def account_favorites(self, type):
        endpoint = "/account/favorites"
        params = {"type": type}
        return self._call(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.root + endpoint
        response = self.extractor.request(url, params=params)
        return response.json()

    def _pagination(self, endpoint, params, batch=50, key=False):
        offset = text.parse_int(params.get("o"))
        params["o"] = offset - offset % batch

        while True:
            data = self._call(endpoint, params)

            if key:
                data = data.get(key)
            if not data:
                return
            yield from data

            if len(data) < batch:
                return
            params["o"] += batch

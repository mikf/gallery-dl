# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kemono.cr/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import itertools
import json

BASE_PATTERN = (r"(?:https?://)?(?:www\.|beta\.)?"
                r"(kemono|coomer)\.(cr|s[tu]|party)")
USER_PATTERN = rf"{BASE_PATTERN}/([^/?#]+)/user/([^/?#]+)"
HASH_PATTERN = r"/[0-9a-f]{2}/[0-9a-f]{2}/([0-9a-f]{64})"


class KemonoExtractor(Extractor):
    """Base class for kemono extractors"""
    category = "kemono"
    root = "https://kemono.cr"
    directory_fmt = ("{category}", "{service}", "{user}")
    filename_fmt = "{id}_{title[:180]}_{num:>02}_{filename[:180]}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"
    cookies_domain = ".kemono.cr"

    def __init__(self, match):
        if match[1] == "coomer":
            self.category = "coomer"
            self.root = "https://coomer.st"
            self.cookies_domain = ".coomer.st"
        Extractor.__init__(self, match)

    def _init(self):
        self.api = KemonoAPI(self)
        self.revisions = self.config("revisions")
        if self.revisions:
            self.revisions_unique = (self.revisions == "unique")
        order = self.config("order-revisions")
        self.revisions_reverse = order[0] in ("r", "a") if order else False

        self._find_inline = text.re(
            r'src="(?:https?://(?:kemono\.cr|coomer\.st))?(/inline/[^"]+'
            r'|/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{64}\.[^"]+)').findall
        self._json_dumps = json.JSONEncoder(
            ensure_ascii=False, check_circular=False,
            sort_keys=True, separators=(",", ":")).encode

    def items(self):
        find_hash = text.re(HASH_PATTERN).match
        generators = self._build_file_generators(self.config("files"))
        announcements = True if self.config("announcements") else None
        archives = True if self.config("archives") else False
        comments = True if self.config("comments") else False
        dms = True if self.config("dms") else None
        max_posts = self.config("max-posts")
        creator_info = {} if self.config("metadata", True) else None
        exts_archive = util.EXTS_ARCHIVE

        if duplicates := self.config("duplicates"):
            if isinstance(duplicates, str):
                duplicates = set(duplicates.split(","))
            elif isinstance(duplicates, (list, tuple)):
                duplicates = set(duplicates)
            else:
                duplicates = {"file", "attachment", "inline"}
        else:
            duplicates = ()

        # prevent files from being sent with gzip compression
        headers = {"Accept-Encoding": "identity"}

        posts = self.posts()
        if max_posts:
            posts = itertools.islice(posts, max_posts)
        if self.revisions:
            posts = self._revisions(posts)

        for post in posts:
            headers["Referer"] = (f"{self.root}/{post['service']}/user/"
                                  f"{post['user']}/post/{post['id']}")
            post["_http_headers"] = headers
            post["date"] = self._parse_datetime(
                post.get("published") or post.get("added") or "")
            service = post["service"]
            creator_id = post["user"]

            if creator_info is not None:
                key = f"{service}_{creator_id}"
                if key not in creator_info:
                    try:
                        creator = creator_info[key] = self.api.creator_profile(
                            service, creator_id)
                    except exception.HttpError:
                        self.log.warning("%s/%s/%s: 'Creator not found'",
                                         service, creator_id, post["id"])
                        creator = creator_info[key] = util.NONE
                else:
                    creator = creator_info[key]

                post["user_profile"] = creator
                post["username"] = creator["name"]

            if comments:
                post["comments"] = cmts = self.api.creator_post_comments(
                    service, creator_id, post["id"])
                if not isinstance(cmts, list):
                    self.log.debug("%s/%s: %s", creator_id, post["id"], cmts)
                    post["comments"] = ()
            if dms is not None:
                if dms is True:
                    dms = self.api.creator_dms(
                        post["service"], post["user"])
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

                if match := find_hash(url):
                    file["hash"] = hash = match[1]
                    if file["type"] not in duplicates and hash in hashes:
                        self.log.debug("Skipping %s %s (duplicate)",
                                       file["type"], url)
                        continue
                    hashes.add(hash)
                else:
                    file["hash"] = hash = ""

                if url[0] == "/":
                    url = f"{self.root}/data{url}"
                elif url.startswith(self.root):
                    url = f"{self.root}/data{url[20:]}"
                file["url"] = url

                if name := file.get("name"):
                    text.nameext_from_name(name, file)
                    ext = text.ext_from_url(url)

                    if not file["extension"]:
                        file["extension"] = ext
                    elif ext == "txt" and file["extension"] != "txt":
                        file["_http_validate"] = _validate
                else:
                    text.nameext_from_url(url, file)
                    ext = file["extension"]

                if ext in exts_archive or \
                        ext == "bin" and file["extension"] in exts_archive:
                    file["type"] = "archive"
                    if archives:
                        try:
                            data = self.api.file(hash)
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
            yield Message.Directory, "", post
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

        url = f"{self.root}/api/v1/authentication/login"
        data = {"username": username, "password": password}

        response = self.request(url, method="POST", json=data, fatal=False)
        if response.status_code >= 400:
            try:
                msg = f'"{response.json()["error"]}"'
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
        return self.parse_datetime_iso(date_string)

    def _revisions(self, posts):
        return itertools.chain.from_iterable(
            self._revisions_post(post) for post in posts)

    def _revisions_post(self, post):
        post["revision_id"] = 0

        revs = self.api.creator_post_revisions(
            post["service"], post["user"], post["id"])
        if not revs:
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


class KemonoUserExtractor(KemonoExtractor):
    """Extractor for all posts from a kemono.cr user listing"""
    subcategory = "user"
    pattern = rf"{USER_PATTERN}/?(?:\?([^#]+))?(?:$|\?|#)"
    example = "https://kemono.cr/SERVICE/user/12345"

    def __init__(self, match):
        self.subcategory = match[3]
        KemonoExtractor.__init__(self, match)

    def posts(self):
        _, _, service, creator_id, query = self.groups
        params = text.parse_query(query)

        if self.config("endpoint") in ("posts+", "legacy+"):
            endpoint = self.api.creator_posts_expand
        else:
            endpoint = self.api.creator_posts

        return endpoint(service, creator_id,
                        params.get("o"), params.get("q"), params.get("tag"))


class KemonoPostsExtractor(KemonoExtractor):
    """Extractor for kemono.cr post listings"""
    subcategory = "posts"
    pattern = rf"{BASE_PATTERN}/posts()()(?:/?\?([^#]+))?"
    example = "https://kemono.cr/posts"

    def posts(self):
        params = text.parse_query(self.groups[4])
        return self.api.posts(
            params.get("o"), params.get("q"), params.get("tag"))


class KemonoPostExtractor(KemonoExtractor):
    """Extractor for a single kemono.cr post"""
    subcategory = "post"
    pattern = rf"{USER_PATTERN}/post/([^/?#]+)(/revisions?(?:/(\d*))?)?"
    example = "https://kemono.cr/SERVICE/user/12345/post/12345"

    def __init__(self, match):
        self.subcategory = match[3]
        KemonoExtractor.__init__(self, match)

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


class KemonoDiscordExtractor(KemonoExtractor):
    """Extractor for kemono.cr discord servers"""
    subcategory = "discord"
    directory_fmt = ("{category}", "discord",
                     "{server_id} {server}", "{channel_id} {channel}")
    filename_fmt = "{id}_{num:>02}_{filename}.{extension}"
    archive_fmt = "discord_{server_id}_{id}_{num}"
    pattern = rf"{BASE_PATTERN}/discord/server/(\d+)[/#](?:channel/)?(\d+)"
    example = "https://kemono.cr/discord/server/12345/12345"

    def items(self):
        _, _, server_id, channel_id = self.groups

        try:
            server, channels = discord_server_info(self, server_id)
            channel = channels[channel_id]
        except Exception:
            raise exception.NotFoundError("channel")

        data = {
            "server"       : server["name"],
            "server_id"    : server["id"],
            "channel"      : channel["name"],
            "channel_id"   : channel["id"],
            "channel_nsfw" : channel["is_nsfw"],
            "channel_type" : channel["type"],
            "channel_topic": channel["topic"],
            "parent_id"    : channel["parent_channel_id"],
        }

        find_inline = text.re(
            r"https?://(?:cdn\.discordapp.com|media\.discordapp\.net)"
            r"(/[A-Za-z0-9-._~:/?#\[\]@!$&'()*+,;%=]+)").findall
        find_hash = text.re(HASH_PATTERN).match

        if (order := self.config("order-posts")) and order[0] in ("r", "d"):
            posts = self.api.discord_channel(channel_id, channel["post_count"])
        else:
            posts = self.api.discord_channel(channel_id)

        if max_posts := self.config("max-posts"):
            posts = itertools.islice(posts, max_posts)

        for post in posts:
            files = []
            for attachment in post["attachments"]:
                match = find_hash(attachment["path"])
                attachment["hash"] = match[1] if match else ""
                attachment["type"] = "attachment"
                files.append(attachment)
            for path in find_inline(post["content"] or ""):
                files.append({"path": f"https://cdn.discordapp.com{path}",
                              "name": path, "type": "inline", "hash": ""})

            post.update(data)
            post["date"] = self._parse_datetime(post["published"])
            post["count"] = len(files)
            yield Message.Directory, "", post

            for post["num"], file in enumerate(files, 1):
                post["hash"] = file["hash"]
                post["type"] = file["type"]
                url = file["path"]

                text.nameext_from_url(file.get("name", url), post)
                if not post["extension"]:
                    post["extension"] = text.ext_from_url(url)

                if url[0] == "/":
                    url = f"{self.root}/data{url}"
                elif url.startswith(self.root):
                    url = f"{self.root}/data{url[20:]}"
                yield Message.Url, url, post


class KemonoDiscordServerExtractor(KemonoExtractor):
    subcategory = "discord-server"
    pattern = rf"{BASE_PATTERN}/discord/server/(\d+)$"
    example = "https://kemono.cr/discord/server/12345"

    def items(self):
        server_id = self.groups[2]
        server, channels = discord_server_info(self, server_id)
        for channel in channels.values():
            url = (f"{self.root}/discord/server/{server_id}/"
                   f"{channel['id']}#{channel['name']}")
            yield Message.Queue, url, {
                "server"    : server,
                "channel"   : channel,
                "_extractor": KemonoDiscordExtractor,
            }


@memcache(keyarg=1)
def discord_server_info(extr, server_id):
    server = extr.api.discord_server(server_id)
    return server, {
        channel["id"]: channel
        for channel in server.pop("channels")
    }


class KemonoFavoriteExtractor(KemonoExtractor):
    """Extractor for kemono.cr favorites"""
    subcategory = "favorite"
    pattern = rf"{BASE_PATTERN}/(?:account/)?favorites()()(?:/?\?([^#]+))?"
    example = "https://kemono.cr/account/favorites/artists"

    def items(self):
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
                    user["_extractor"] = KemonoDiscordServerExtractor
                    url = f"{self.root}/discord/server/{user['id']}"
                else:
                    user["_extractor"] = KemonoUserExtractor
                    url = f"{self.root}/{service}/user/{user['id']}"
                yield Message.Queue, url, user

        elif type == "post":
            posts = self.api.account_favorites("post")

            if not sort:
                sort = "faved_seq"
            posts.sort(key=lambda x: x[sort] or util.NONE,
                       reverse=(order == "desc"))

            for post in posts:
                post["_extractor"] = KemonoPostExtractor
                url = (f"{self.root}/{post['service']}/user/"
                       f"{post['user']}/post/{post['id']}")
                yield Message.Queue, url, post


class KemonoArtistsExtractor(KemonoExtractor):
    """Extractor for kemono artists"""
    subcategory = "artists"
    pattern = rf"{BASE_PATTERN}/artists(?:\?([^#]+))?"
    example = "https://kemono.cr/artists"

    def items(self):
        params = text.parse_query(self.groups[2])
        users = self.api.creators()

        if params.get("service"):
            service = params["service"].lower()
            users = [user for user in users
                     if user["service"] == service]

        if params.get("q"):
            q = params["q"].lower()
            users = [user for user in users
                     if q in user["name"].lower()]

        sort = params.get("sort_by") or "favorited"
        order = params.get("order") or "desc"
        users.sort(key=lambda user: user[sort] or util.NONE,
                   reverse=(order != "asc"))

        for user in users:
            service = user["service"]
            if service == "discord":
                user["_extractor"] = KemonoDiscordServerExtractor
                url = f"{self.root}/discord/server/{user['id']}"
            else:
                user["_extractor"] = KemonoUserExtractor
                url = f"{self.root}/{service}/user/{user['id']}"
            yield Message.Queue, url, user


class KemonoAPI():
    """Interface for the Kemono API v1.3.0

    https://kemono.cr/documentation/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = f"{extractor.root}/api"
        self.headers = {"Accept": "text/css"}

    def posts(self, offset=0, query=None, tags=None):
        endpoint = "/v1/posts"
        params = {"q": query, "o": offset, "tag": tags}
        return self._pagination(endpoint, params, 50, "posts")

    def file(self, file_hash):
        endpoint = f"/v1/file/{file_hash}"
        return self._call(endpoint)

    def creators(self):
        endpoint = "/v1/creators"
        return self._call(endpoint)

    def creator_posts(self, service, creator_id,
                      offset=0, query=None, tags=None):
        endpoint = f"/v1/{service}/user/{creator_id}/posts"
        params = {"o": offset, "tag": tags, "q": query}
        return self._pagination(endpoint, params, 50)

    def creator_posts_expand(self, service, creator_id,
                             offset=0, query=None, tags=None):
        for post in self.creator_posts(
                service, creator_id, offset, query, tags):
            yield self.creator_post(
                service, creator_id, post["id"])["post"]

    def creator_announcements(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/announcements"
        return self._call(endpoint)

    def creator_dms(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/dms"
        return self._call(endpoint)

    def creator_fancards(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/fancards"
        return self._call(endpoint)

    def creator_post(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}"
        return self._call(endpoint)

    def creator_post_comments(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}/comments"
        return self._call(endpoint, fatal=False)

    def creator_post_revisions(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}/revisions"
        return self._call(endpoint, fatal=False)

    def creator_profile(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/profile"
        return self._call(endpoint)

    def creator_links(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/links"
        return self._call(endpoint)

    def creator_tags(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/tags"
        return self._call(endpoint)

    def discord_channel(self, channel_id, post_count=None):
        endpoint = f"/v1/discord/channel/{channel_id}"
        if post_count is None:
            return self._pagination(endpoint, {}, 150)
        else:
            return self._pagination_reverse(endpoint, {}, 150, post_count)

    def discord_channel_lookup(self, server_id):
        endpoint = f"/v1/discord/channel/lookup/{server_id}"
        return self._call(endpoint)

    def discord_server(self, server_id):
        endpoint = f"/v1/discord/server/{server_id}"
        return self._call(endpoint)

    def account_favorites(self, type):
        endpoint = "/v1/account/favorites"
        params = {"type": type}
        return self._call(endpoint, params)

    def _call(self, endpoint, params=None, headers=None, fatal=True):
        if headers is None:
            headers = self.headers
        else:
            headers = {**self.headers, **headers}

        return self.extractor.request_json(
            f"{self.root}{endpoint}", params=params, headers=headers,
            encoding="utf-8", fatal=fatal)

    def _pagination(self, endpoint, params, batch=50, key=None):
        offset = text.parse_int(params.get("o"))
        params["o"] = offset - offset % batch

        while True:
            data = self._call(endpoint, params)

            if key is not None:
                data = data.get(key)
            if not data:
                return
            yield from data

            if len(data) < batch:
                return
            params["o"] += batch

    def _pagination_reverse(self, endpoint, params, batch, count):
        params["o"] = count // batch * batch

        while True:
            data = self._call(endpoint, params)

            if not data:
                return
            data.reverse()
            yield from data

            if not params["o"]:
                return
            params["o"] -= batch

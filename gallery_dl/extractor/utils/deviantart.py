# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import cache, memcache
import collections


@cache(maxage=36500*86400, keyarg=0, utils=True)
def _refresh_token_cache(token):
    if token and token[0] == "#":
        return None
    return token


@cache(maxage=28*86400, keyarg=1, utils=True)
def _login_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    url = "https://www.deviantart.com/users/login"
    page = extr.request(url).text

    data = {}
    for item in text.extract_iter(page, '<input type="hidden" name="', '"/>'):
        name, _, value = item.partition('" value="')
        data[name] = value

    challenge = data.get("challenge")
    if challenge and challenge != "0":
        extr.log.warning("Login requires solving a CAPTCHA")
        extr.log.debug(challenge)

    data["username"] = username
    data["password"] = password
    data["remember"] = "on"

    extr.sleep(2.0, "login")
    url = "https://www.deviantart.com/_sisu/do/signin"
    response = extr.request(url, method="POST", data=data)

    if not response.history:
        raise exception.AuthenticationError()

    return {
        cookie.name: cookie.value
        for cookie in extr.cookies
    }


###############################################################################
# API Interfaces ##############################################################

class DeviantartOAuthAPI():
    """Interface for the DeviantArt OAuth API

    https://www.deviantart.com/developers/http/v1/20160316
    """
    CLIENT_ID = "5388"
    CLIENT_SECRET = "76b08c69cfb27f26d6161f9ab6d061a1"

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.headers = {"dA-minor-version": "20210526"}
        self._warn_429 = True

        self.delay = extractor.config("wait-min", 0)
        self.delay_min = max(2, self.delay)

        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"

        self.strategy = extractor.config("pagination")
        self.folders = extractor.config("folders", False)
        self.public = extractor.config("public", True)

        if client_id := extractor.config("client-id"):
            self.client_id = str(client_id)
            self.client_secret = extractor.config("client-secret")
        else:
            self.client_id = self.CLIENT_ID
            self.client_secret = self.CLIENT_SECRET

        token = extractor.config("refresh-token")
        if token is None or token == "cache":
            token = "#" + self.client_id
            if not _refresh_token_cache(token):
                token = None
        self.refresh_token_key = token

        metadata = extractor.config("metadata", False)
        if not metadata:
            metadata = True if extractor.extra else False
        if metadata:
            self.metadata = True

            if isinstance(metadata, str):
                if metadata == "all":
                    metadata = ("submission", "camera", "stats",
                                "collection", "gallery")
                else:
                    metadata = metadata.replace(" ", "").split(",")
            elif not isinstance(metadata, (list, tuple)):
                metadata = ()

            self._metadata_params = {"mature_content": self.mature}
            self._metadata_public = None
            if metadata:
                # extended metadata
                self.limit = 10
                for param in metadata:
                    self._metadata_params["ext_" + param] = "1"
                if "ext_collection" in self._metadata_params or \
                        "ext_gallery" in self._metadata_params:
                    if token:
                        self._metadata_public = False
                    else:
                        self.log.error("'collection' and 'gallery' metadata "
                                       "require a refresh token")
            else:
                # base metadata
                self.limit = 50
        else:
            self.metadata = False
            self.limit = None

        self.log.debug(
            "Using %s API credentials (client-id %s)",
            "default" if self.client_id == self.CLIENT_ID else "custom",
            self.client_id,
        )

    def browse_deviantsyouwatch(self, offset=0):
        """Yield deviations from users you watch"""
        endpoint = "/browse/deviantsyouwatch"
        params = {"limit": 50, "offset": offset,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params, public=False)

    def browse_posts_deviantsyouwatch(self, offset=0):
        """Yield posts from users you watch"""
        endpoint = "/browse/posts/deviantsyouwatch"
        params = {"limit": 50, "offset": offset,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params, public=False, unpack=True)

    def browse_tags(self, tag, offset=0):
        """ Browse a tag """
        endpoint = "/browse/tags"
        params = {
            "tag"           : tag,
            "offset"        : offset,
            "limit"         : 50,
            "mature_content": self.mature,
        }
        return self._pagination(endpoint, params)

    def browse_user_journals(self, username, offset=0):
        journals = filter(
            lambda post: "/journal/" in post["url"],
            self.user_profile_posts(username))
        if offset:
            journals = util.advance(journals, offset)
        return journals

    def collections(self, username, folder_id, offset=0):
        """Yield all Deviation-objects contained in a collection folder"""
        endpoint = "/collections/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def collections_all(self, username, offset=0):
        """Yield all deviations in a user's collection"""
        endpoint = "/collections/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def collections_folders(self, username, offset=0):
        """Yield all collection folders of a specific user"""
        endpoint = "/collections/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    def comments(self, target_id, target_type="deviation",
                 comment_id=None, offset=0):
        """Fetch comments posted on a target"""
        endpoint = f"/comments/{target_type}/{target_id}"
        params = {
            "commentid"     : comment_id,
            "maxdepth"      : "5",
            "offset"        : offset,
            "limit"         : 50,
            "mature_content": self.mature,
        }
        return self._pagination_list(endpoint, params=params, key="thread")

    def deviation(self, deviation_id, public=None):
        """Query and return info about a single Deviation"""
        endpoint = "/deviation/" + deviation_id

        deviation = self._call(endpoint, public=public)
        if deviation.get("is_mature") and public is None and \
                self.refresh_token_key:
            deviation = self._call(endpoint, public=False)

        if self.metadata:
            self._metadata((deviation,))
        if self.folders:
            self._folders((deviation,))
        return deviation

    def deviation_content(self, deviation_id, public=None):
        """Get extended content of a single Deviation"""
        endpoint = "/deviation/content"
        params = {"deviationid": deviation_id}
        content = self._call(endpoint, params=params, public=public)
        if public and content["html"].startswith(
                '        <span class=\"username-with-symbol'):
            if self.refresh_token_key:
                content = self._call(endpoint, params=params, public=False)
            else:
                self.log.warning("Private Journal")
        return content

    def deviation_download(self, deviation_id, public=None):
        """Get the original file download (if allowed)"""
        endpoint = "/deviation/download/" + deviation_id
        params = {"mature_content": self.mature}

        try:
            return self._call(
                endpoint, params=params, public=public, log=False)
        except Exception:
            if not self.refresh_token_key:
                raise
            return self._call(endpoint, params=params, public=False)

    def deviation_metadata(self, deviations):
        """ Fetch deviation metadata for a set of deviations"""
        endpoint = "/deviation/metadata?" + "&".join(
            f"deviationids[{num}]={deviation['deviationid']}"
            for num, deviation in enumerate(deviations)
        )
        return self._call(
            endpoint,
            params=self._metadata_params,
            public=self._metadata_public,
        )["metadata"]

    def gallery(self, username, folder_id, offset=0, extend=True, public=None):
        """Yield all Deviation-objects contained in a gallery folder"""
        endpoint = "/gallery/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature, "mode": "newest"}
        return self._pagination(endpoint, params, extend, public)

    def gallery_all(self, username, offset=0):
        """Yield all Deviation-objects of a specific user"""
        endpoint = "/gallery/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def gallery_folders(self, username, offset=0):
        """Yield all gallery folders of a specific user"""
        endpoint = "/gallery/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    def user_friends(self, username, offset=0):
        """Get the users list of friends"""
        endpoint = "/user/friends/" + username
        params = {"limit": 50, "offset": offset, "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def user_friends_watch(self, username):
        """Watch a user"""
        endpoint = "/user/friends/watch/" + username
        data = {
            "watch[friend]"       : "0",
            "watch[deviations]"   : "0",
            "watch[journals]"     : "0",
            "watch[forum_threads]": "0",
            "watch[critiques]"    : "0",
            "watch[scraps]"       : "0",
            "watch[activity]"     : "0",
            "watch[collections]"  : "0",
            "mature_content"      : self.mature,
        }
        return self._call(
            endpoint, method="POST", data=data, public=False, fatal=False,
        ).get("success")

    def user_friends_unwatch(self, username):
        """Unwatch a user"""
        endpoint = "/user/friends/unwatch/" + username
        return self._call(
            endpoint, method="POST", public=False, fatal=False,
        ).get("success")

    @memcache(keyarg=1)
    def user_profile(self, username):
        """Get user profile information"""
        endpoint = "/user/profile/" + username
        return self._call(endpoint, fatal=False)

    def user_profile_posts(self, username):
        endpoint = "/user/profile/posts"
        params = {"username": username, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def user_statuses(self, username, offset=0):
        """Yield status updates of a specific user"""
        statuses = filter(
            lambda post: "/status-update/" in post["url"],
            self.user_profile_posts(username))
        if offset:
            statuses = util.advance(statuses, offset)
        return statuses

    def authenticate(self, refresh_token_key):
        """Authenticate the application by requesting an access token"""
        self.headers["Authorization"] = \
            self._authenticate_impl(refresh_token_key)

    @cache(maxage=3600, keyarg=1, utils=True)
    def _authenticate_impl(self, refresh_token_key):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        if refresh_token_key:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": _refresh_token_cache(refresh_token_key)}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": "client_credentials"}

        auth = util.HTTPBasicAuth(self.client_id, self.client_secret)
        response = self.extractor.request(
            url, method="POST", data=data, auth=auth, fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError(
                f"\"{data.get('error_description')}\" ({data.get('error')})")
        if refresh_token_key:
            _refresh_token_cache.update(
                refresh_token_key, data["refresh_token"])
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, fatal=True, log=True, public=None, **kwargs):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2" + endpoint
        kwargs["fatal"] = None

        if public is None:
            public = self.public

        while True:
            if self.delay:
                self.extractor.sleep(self.delay, "api")

            self.authenticate(None if public else self.refresh_token_key)
            kwargs["headers"] = self.headers
            response = self.extractor.request(url, **kwargs)

            try:
                data = response.json()
            except ValueError:
                self.log.error("Unable to parse API response")
                data = {}

            status = response.status_code
            if 200 <= status < 400:
                if self.delay > self.delay_min:
                    self.delay -= 1
                return data
            if not fatal and status != 429:
                return None

            error = data.get("error_description")
            if error == "User not found.":
                raise exception.NotFoundError("user or group")
            if error == "Deviation not downloadable.":
                raise exception.AuthorizationError()

            self.log.debug(response.text)
            msg = f"API responded with {status} {response.reason}"
            if status == 429:
                if self.delay < 30:
                    self.delay += 1
                self.log.warning("%s. Using %ds delay.", msg, self.delay)

                if self._warn_429 and self.delay >= 3:
                    self._warn_429 = False
                    if self.client_id == self.CLIENT_ID:
                        self.log.info(
                            "Register your own OAuth application and use its "
                            "credentials to prevent this error: "
                            "https://gdl-org.github.io/docs/configuration.html"
                            "#extractor-deviantart-client-id-client-secret")
            else:
                if log:
                    self.log.error(msg)
                return data

    def _should_switch_tokens(self, results, params):
        if len(results) < params["limit"]:
            return True

        if not self.extractor.jwt:
            for item in results:
                if item.get("is_mature"):
                    return True

        return False

    def _pagination(self, endpoint, params,
                    extend=True, public=None, unpack=False, key="results"):
        warn = True
        if public is None:
            public = self.public

        if self.limit and params["limit"] > self.limit:
            params["limit"] = (params["limit"] // self.limit) * self.limit

        while True:
            data = self._call(endpoint, params=params, public=public)
            try:
                results = data[key]
            except KeyError:
                self.log.error("Unexpected API response: %s", data)
                return

            if unpack:
                results = [item["journal"] for item in results
                           if "journal" in item]
            if extend:
                if public and self._should_switch_tokens(results, params):
                    if self.refresh_token_key:
                        self.log.debug("Switching to private access token")
                        public = False
                        continue
                    elif data["has_more"] and warn:
                        warn = False
                        self.log.warning(
                            "Private or mature deviations detected! "
                            "Run 'gallery-dl oauth:deviantart' and follow the "
                            "instructions to be able to access them.")

                # "statusid" cannot be used instead
                if results and "deviationid" in results[0]:
                    if self.metadata:
                        self._metadata(results)
                    if self.folders:
                        self._folders(results)
                else:  # attempt to fix "deleted" deviations
                    for dev in self._shared_content(results):
                        if not dev["is_deleted"]:
                            continue
                        patch = self._call(
                            "/deviation/" + dev["deviationid"], fatal=False)
                        if patch:
                            dev.update(patch)

            yield from results

            if not data["has_more"] and (
                    self.strategy != "manual" or not results or not extend):
                return

            if "next_cursor" in data:
                if not data["next_cursor"]:
                    return
                params["offset"] = None
                params["cursor"] = data["next_cursor"]
            elif data["next_offset"] is not None:
                params["offset"] = data["next_offset"]
                params["cursor"] = None
            else:
                if params.get("offset") is None:
                    return
                params["offset"] = int(params["offset"]) + len(results)

    def _pagination_list(self, endpoint, params, key="results"):
        return list(self._pagination(endpoint, params, False, key=key))

    def _shared_content(self, results):
        """Return an iterable of shared deviations in 'results'"""
        for result in results:
            for item in result.get("items") or ():
                if "deviation" in item:
                    yield item["deviation"]

    def _metadata(self, deviations):
        """Add extended metadata to each deviation object"""
        if len(deviations) <= self.limit:
            self._metadata_batch(deviations)
        else:
            n = self.limit
            for index in range(0, len(deviations), n):
                self._metadata_batch(deviations[index:index+n])

    def _metadata_batch(self, deviations):
        """Fetch extended metadata for a single batch of deviations"""
        for deviation, metadata in zip(
                deviations, self.deviation_metadata(deviations)):
            deviation.update(metadata)
            deviation["tags"] = [t["tag_name"] for t in deviation["tags"]]

    def _folders(self, deviations):
        """Add a list of all containing folders to each deviation object"""
        for deviation in deviations:
            deviation["folders"] = self._folders_map(
                deviation["author"]["username"])[deviation["deviationid"]]

    @memcache(keyarg=1)
    def _folders_map(self, username):
        """Generate a deviation_id -> folders mapping for 'username'"""
        self.log.info("Collecting folder information for '%s'", username)
        folders = self.gallery_folders(username)

        # create 'folderid'-to-'folder' mapping
        fmap = {
            folder["folderid"]: folder
            for folder in folders
        }

        # add parent names to folders, but ignore "Featured" as parent
        featured = folders[0]["folderid"]
        done = False

        while not done:
            done = True
            for folder in folders:
                parent = folder["parent"]
                if not parent:
                    pass
                elif parent == featured:
                    folder["parent"] = None
                else:
                    parent = fmap[parent]
                    if parent["parent"]:
                        done = False
                    else:
                        folder["name"] = parent["name"] + "/" + folder["name"]
                        folder["parent"] = None

        # map deviationids to folder names
        dmap = collections.defaultdict(list)
        for folder in folders:
            for deviation in self.gallery(
                    username, folder["folderid"], 0, False):
                dmap[deviation["deviationid"]].append(folder["name"])
        return dmap


class DeviantartEclipseAPI():
    """Interface to the DeviantArt Eclipse API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.request = self.extractor._limited_request
        self.csrf_token = None

    def deviation_extended_fetch(self, deviation_id, user, kind=None):
        endpoint = "/_puppy/dadeviation/init"
        params = {
            "deviationid"     : deviation_id,
            "username"        : user,
            "type"            : kind,
            "include_session" : "false",
            "expand"          : "deviation.related",
            "da_minor_version": "20230710",
        }
        return self._call(endpoint, params)

    def gallery_scraps(self, user, offset=0):
        endpoint = "/_puppy/dashared/gallection/contents"
        params = {
            "username"     : user,
            "type"         : "gallery",
            "offset"       : offset,
            "limit"        : 24,
            "scraps_folder": "true",
        }
        return self._pagination(endpoint, params)

    def galleries_search(self, user, query, offset=0, order="most-recent"):
        endpoint = "/_puppy/dashared/gallection/search"
        params = {
            "username": user,
            "type"    : "gallery",
            "order"   : order,
            "q"       : query,
            "offset"  : offset,
            "limit"   : 24,
        }
        return self._pagination(endpoint, params)

    def search_deviations(self, params):
        endpoint = "/_puppy/dabrowse/search/deviations"
        return self._pagination(endpoint, params, key="deviations")

    def user_info(self, user, expand=False):
        endpoint = "/_puppy/dauserprofile/init/about"
        params = {"username": user}
        return self._call(endpoint, params)

    def user_watching(self, user, offset=0):
        gruserid, moduleid = self._ids_watching(user)

        endpoint = "/_puppy/gruser/module/watching"
        params = {
            "gruserid"     : gruserid,
            "gruser_typeid": "4",
            "username"     : user,
            "moduleid"     : moduleid,
            "offset"       : offset,
            "limit"        : 24,
        }
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params):
        url = "https://www.deviantart.com" + endpoint
        params["csrf_token"] = self.csrf_token or self._fetch_csrf_token()

        response = self.request(url, params=params, fatal=None)

        try:
            return response.json()
        except Exception:
            return {"error": response.text}

    def _pagination(self, endpoint, params, key="results"):
        limit = params.get("limit", 24)
        warn = True

        while True:
            data = self._call(endpoint, params)

            results = data.get(key)
            if results is None:
                return
            if len(results) < limit and warn and data.get("hasMore"):
                warn = False
                self.log.warning(
                    "Private deviations detected! "
                    "Provide login credentials or session cookies "
                    "to be able to access them.")
            yield from results

            if not data.get("hasMore"):
                return

            if "nextCursor" in data:
                params["offset"] = None
                params["cursor"] = data["nextCursor"]
            elif "nextOffset" in data:
                params["offset"] = data["nextOffset"]
                params["cursor"] = None
            elif params.get("offset") is None:
                return
            else:
                params["offset"] = int(params["offset"]) + len(results)

    def _ids_watching(self, user):
        url = f"{self.extractor.root}/{user}/about"
        page = self.request(url).text

        gruser_id = text.extr(page, ' data-userid="', '"')

        pos = page.find('\\"name\\":\\"watching\\"')
        if pos < 0:
            raise exception.NotFoundError("'watching' module ID")
        module_id = text.rextr(page, '\\"id\\":', ',', pos).strip('" ')

        self._fetch_csrf_token(page)
        return gruser_id, module_id

    def _fetch_csrf_token(self, page=None):
        if page is None:
            page = self.request(self.extractor.root + "/").text
        self.csrf_token = token = text.extr(
            page, "window.__CSRF_TOKEN__ = '", "'")
        return token


###############################################################################
# Journal Formats #############################################################

SHADOW_TEMPLATE = """
<span class="shadow">
    <img src="{src}" class="smshadow" width="{width}" height="{height}">
</span>
<br><br>
"""

HEADER_TEMPLATE = """<div usr class="gr">
<div class="metadata">
    <h2><a href="{url}">{title}</a></h2>
    <ul>
        <li class="author">
            by <span class="name"><span class="username-with-symbol u">
            <a class="u regular username" href="{userurl}">{username}</a>\
<span class="user-symbol regular"></span></span></span>,
            <span>{date}</span>
        </li>
    </ul>
</div>
"""

HEADER_CUSTOM_TEMPLATE = """<div class='boxtop journaltop'>
<h2>
    <img src="https://st.deviantart.net/minish/gruzecontrol/icons/journal.gif\
?2" style="vertical-align:middle" alt=""/>
    <a href="{url}">{title}</a>
</h2>
Journal Entry: <span>{date}</span>
"""

JOURNAL_TEMPLATE_HTML = """text:<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/deviantart-network_lc.css?3843780832"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/group_secrets_lc.css?3250492874"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/v6core_lc.css?4246581581"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/sidebar_lc.css?1490570941"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/writer_lc.css?3090682151"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/v6loggedin_lc.css?3001430805"/>
    <style>{css}</style>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/core.css?1488405371919"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/peeky.css?1487067424177"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/desktop.css?1491362542749"/>
    <link rel="stylesheet" href="https://static.parastorage.com/services\
/da-deviation/2bfd1ff7a9d6bf10d27b98dd8504c0399c3f9974a015785114b7dc6b\
/app.min.css"/>
</head>
<body id="deviantART-v7" class="bubble no-apps loggedout w960 deviantart">
    <div id="output">
    <div class="dev-page-container bubbleview">
    <div class="dev-page-view view-mode-normal">
    <div class="dev-view-main-content">
    <div class="dev-view-deviation">
    {shadow}
    <div class="journal-wrapper tt-a">
    <div class="journal-wrapper2">
    <div class="journal {cls} journalcontrol">
    {html}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
</body>
</html>
"""

JOURNAL_TEMPLATE_HTML_EXTRA = """\
<div id="devskin0"><div class="negate-box-margin" style="">\
<div usr class="gr-box gr-genericbox"
        ><i usr class="gr1"><i></i></i
        ><i usr class="gr2"><i></i></i
        ><i usr class="gr3"><i></i></i
        ><div usr class="gr-top">
            <i usr class="tri"></i>
            {}
            </div>
    </div><div usr class="gr-body"><div usr class="gr">
            <div class="grf-indent">
            <div class="text">
                {}            </div>
        </div>
                </div></div>
        <i usr class="gr3 gb"></i>
        <i usr class="gr2 gb"></i>
        <i usr class="gr1 gb gb1"></i>    </div>
    </div></div>"""

JOURNAL_TEMPLATE_TEXT = """text:{title}
by {username}, {date}

{content}
"""

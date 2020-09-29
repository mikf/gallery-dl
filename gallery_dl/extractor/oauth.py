# -*- coding: utf-8 -*-

# Copyright 2017-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility classes to setup OAuth and link accounts to gallery-dl"""

from .common import Extractor, Message
from . import deviantart, flickr, reddit, smugmug, tumblr
from .. import text, oauth, util, config, exception
from ..cache import cache
import urllib.parse

REDIRECT_URI_LOCALHOST = "http://localhost:6414/"
REDIRECT_URI_HTTPS = "https://mikf.github.io/gallery-dl/oauth-redirect.html"


class OAuthBase(Extractor):
    """Base class for OAuth Helpers"""
    category = "oauth"
    redirect_uri = REDIRECT_URI_LOCALHOST

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.client = None
        self.cache = config.get(("extractor", self.category), "cache", True)

    def oauth_config(self, key, default=None):
        return config.interpolate(
            ("extractor", self.subcategory), key, default)

    def recv(self):
        """Open local HTTP server and recv callback parameters"""
        import socket
        print("Waiting for response. (Cancel with Ctrl+c)")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", self.config("port", 6414)))
        server.listen(1)

        # workaround for ctrl+c not working during server.accept on Windows
        if util.WINDOWS:
            server.settimeout(1.0)
        while True:
            try:
                self.client = server.accept()[0]
                break
            except socket.timeout:
                pass
        server.close()

        data = self.client.recv(1024).decode()
        path = data.split(" ", 2)[1]
        return text.parse_query(path.partition("?")[2])

    def send(self, msg):
        """Send 'msg' to the socket opened in 'recv()'"""
        print(msg)
        self.client.send(b"HTTP/1.1 200 OK\r\n\r\n" + msg.encode())
        self.client.close()

    def open(self, url, params):
        """Open 'url' in browser amd return response parameters"""
        import webbrowser
        url += "?" + urllib.parse.urlencode(params)
        if not self.config("browser", True) or not webbrowser.open(url):
            print("Please open this URL in your browser:")
            print(url, end="\n\n", flush=True)
        return self.recv()

    def _oauth1_authorization_flow(
            self, request_token_url, authorize_url, access_token_url):
        """Perform the OAuth 1.0a authorization flow"""
        # get a request token
        params = {"oauth_callback": self.redirect_uri}
        data = self.session.get(request_token_url, params=params).text

        data = text.parse_query(data)
        self.session.auth.token_secret = data["oauth_token_secret"]

        # get the user's authorization
        params = {"oauth_token": data["oauth_token"], "perms": "read"}
        data = self.open(authorize_url, params)

        # exchange the request token for an access token
        data = self.session.get(access_token_url, params=data).text
        data = text.parse_query(data)
        token = data["oauth_token"]
        token_secret = data["oauth_token_secret"]

        # write to cache
        if self.cache:
            key = (self.subcategory, self.session.auth.consumer_key)
            oauth._token_cache.update(key, (token, token_secret))
            self.log.info("Writing tokens to cache")

        # display tokens
        self.send(self._generate_message(
            ("access-token", "access-token-secret"),
            (token, token_secret),
        ))

    def _oauth2_authorization_code_grant(
            self, client_id, client_secret, auth_url, token_url,
            scope="read", key="refresh_token", auth=True,
            message_template=None, cache=None):
        """Perform an OAuth2 authorization code grant"""

        state = "gallery-dl_{}_{}".format(
            self.subcategory,
            oauth.nonce(8),
        )

        auth_params = {
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": scope,
        }

        # receive an authorization code
        params = self.open(auth_url, auth_params)

        # check authorization response
        if state != params.get("state"):
            self.send("'state' mismatch: expected {}, got {}.".format(
                state, params.get("state")
            ))
            return
        if "error" in params:
            self.send(params["error"])
            return

        # exchange the authorization code for a token
        data = {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": self.redirect_uri,
        }

        if auth:
            auth = (client_id, client_secret)
        else:
            auth = None
            data["client_id"] = client_id
            data["client_secret"] = client_secret

        data = self.session.post(token_url, data=data, auth=auth).json()

        # check token response
        if "error" in data:
            self.send(data["error"])
            return

        # write to cache
        if self.cache and cache:
            cache.update("#" + str(client_id), data[key])
            self.log.info("Writing 'refresh-token' to cache")

        # display token
        if message_template:
            msg = message_template.format(
                category=self.subcategory,
                key=key.partition("_")[0],
                token=data[key],
                instance=getattr(self, "instance", ""),
                client_id=client_id,
                client_secret=client_secret,
            )
        else:
            msg = self._generate_message(
                ("refresh-token",),
                (data[key],),
            )
        self.send(msg)

    def _generate_message(self, names, values):
        _vh, _va, _is, _it = (
            ("This value has", "this value", "is", "it")
            if len(names) == 1 else
            ("These values have", "these values", "are", "them")
        )

        msg = "\nYour {} {}\n\n{}\n\n".format(
            " and ".join("'" + n + "'" for n in names),
            _is,
            "\n".join(values),
        )

        opt = self.oauth_config(names[0])
        if self.cache and (opt is None or opt == "cache"):
            msg += _vh + " been cached and will automatically be used."
        else:
            msg += "Put " + _va + " into your configuration file as \n"
            msg += " and\n".join(
                "'extractor." + self.subcategory + "." + n + "'"
                for n in names
            )
            if self.cache:
                msg += (
                    "\nor set\n'extractor.{}.{}' to \"cache\""
                    .format(self.subcategory, names[0])
                )
            msg += "\nto use {}.".format(_it)

        return msg


class OAuthDeviantart(OAuthBase):
    subcategory = "deviantart"
    pattern = "oauth:deviantart$"
    redirect_uri = REDIRECT_URI_HTTPS

    def items(self):
        yield Message.Version, 1

        self._oauth2_authorization_code_grant(
            self.oauth_config(
                "client-id", deviantart.DeviantartOAuthAPI.CLIENT_ID),
            self.oauth_config(
                "client-secret", deviantart.DeviantartOAuthAPI.CLIENT_SECRET),
            "https://www.deviantart.com/oauth2/authorize",
            "https://www.deviantart.com/oauth2/token",
            scope="browse",
            cache=deviantart._refresh_token_cache,
        )


class OAuthFlickr(OAuthBase):
    subcategory = "flickr"
    pattern = "oauth:flickr$"
    redirect_uri = REDIRECT_URI_HTTPS

    def __init__(self, match):
        OAuthBase.__init__(self, match)
        self.session = oauth.OAuth1Session(
            self.oauth_config("api-key", flickr.FlickrAPI.API_KEY),
            self.oauth_config("api-secret", flickr.FlickrAPI.API_SECRET),
        )

    def items(self):
        yield Message.Version, 1

        self._oauth1_authorization_flow(
            "https://www.flickr.com/services/oauth/request_token",
            "https://www.flickr.com/services/oauth/authorize",
            "https://www.flickr.com/services/oauth/access_token",
        )


class OAuthReddit(OAuthBase):
    subcategory = "reddit"
    pattern = "oauth:reddit$"

    def items(self):
        yield Message.Version, 1

        self.session.headers["User-Agent"] = reddit.RedditAPI.USER_AGENT
        self._oauth2_authorization_code_grant(
            self.oauth_config("client-id", reddit.RedditAPI.CLIENT_ID),
            "",
            "https://www.reddit.com/api/v1/authorize",
            "https://www.reddit.com/api/v1/access_token",
            scope="read history",
            cache=reddit._refresh_token_cache,
        )


class OAuthSmugmug(OAuthBase):
    subcategory = "smugmug"
    pattern = "oauth:smugmug$"

    def __init__(self, match):
        OAuthBase.__init__(self, match)
        self.session = oauth.OAuth1Session(
            self.oauth_config("api-key", smugmug.SmugmugAPI.API_KEY),
            self.oauth_config("api-secret", smugmug.SmugmugAPI.API_SECRET),
        )

    def items(self):
        yield Message.Version, 1

        self._oauth1_authorization_flow(
            "https://api.smugmug.com/services/oauth/1.0a/getRequestToken",
            "https://api.smugmug.com/services/oauth/1.0a/authorize",
            "https://api.smugmug.com/services/oauth/1.0a/getAccessToken",
        )


class OAuthTumblr(OAuthBase):
    subcategory = "tumblr"
    pattern = "oauth:tumblr$"

    def __init__(self, match):
        OAuthBase.__init__(self, match)
        self.session = oauth.OAuth1Session(
            self.oauth_config("api-key", tumblr.TumblrAPI.API_KEY),
            self.oauth_config("api-secret", tumblr.TumblrAPI.API_SECRET),
        )

    def items(self):
        yield Message.Version, 1

        self._oauth1_authorization_flow(
            "https://www.tumblr.com/oauth/request_token",
            "https://www.tumblr.com/oauth/authorize",
            "https://www.tumblr.com/oauth/access_token",
        )


class OAuthMastodon(OAuthBase):
    subcategory = "mastodon"
    pattern = "oauth:mastodon:(?:https?://)?([^/?&#]+)"

    def __init__(self, match):
        OAuthBase.__init__(self, match)
        self.instance = match.group(1)

    def items(self):
        yield Message.Version, 1

        application = self.oauth_config(self.instance)
        if not application:
            application = self._register(self.instance)

        self._oauth2_authorization_code_grant(
            application["client-id"],
            application["client-secret"],
            "https://{}/oauth/authorize".format(self.instance),
            "https://{}/oauth/token".format(self.instance),
            key="access_token",
            message_template=MASTODON_MSG_TEMPLATE,
        )

    @cache(maxage=10*365*24*3600, keyarg=1)
    def _register(self, instance):
        self.log.info("Registering application for '%s'", instance)

        url = "https://{}/api/v1/apps".format(instance)
        data = {
            "client_name": "gdl:" + oauth.nonce(8),
            "redirect_uris": self.redirect_uri,
            "scopes": "read",
        }
        data = self.session.post(url, data=data).json()

        if "client_id" not in data or "client_secret" not in data:
            raise exception.StopExtraction(
                "Failed to register new application: '%s'", data)

        data["client-id"] = data.pop("client_id")
        data["client-secret"] = data.pop("client_secret")

        self.log.info("client-id:\n%s", data["client-id"])
        self.log.info("client-secret:\n%s", data["client-secret"])

        return data


MASTODON_MSG_TEMPLATE = """
Your 'access-token' is

{token}

Put this value into your configuration file as
'extractor.mastodon.{instance}.{key}-token'.

You can also add your 'client-id' and 'client-secret' values
if you want to register another account in the future.

Example:
{{
    "extractor": {{
        "mastodon": {{
            "{instance}": {{
                "{key}-token": "{token}",
                "client-id": "{client_id}",
                "client-secret": "{client_secret}"
            }}
        }}
    }}
}}
"""

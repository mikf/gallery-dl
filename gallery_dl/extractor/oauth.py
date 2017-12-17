# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility classes to setup OAuth and link a users account to gallery-dl"""

from .common import Extractor, Message
from . import deviantart, flickr, reddit
from .. import util
import os
import urllib.parse


class OAuthBase(Extractor):
    """Base class for OAuth Helpers"""
    category = "oauth"
    redirect_uri = "http://localhost:6414/"

    def __init__(self, match):
        Extractor.__init__(self)
        self.client = None

    def recv(self):
        """Open local HTTP server and recv callback parameters"""
        import socket
        print("Waiting for response. (Cancel with Ctrl+c)")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 6414))
        server.listen(1)

        # workaround for ctrl+c not working during server.accept on Windows
        if os.name == "nt":
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
        query = path.partition("?")[2]
        return {
            key: urllib.parse.unquote(value)
            for key, _, value in [
                part.partition("=")
                for part in query.split("&")
            ]
        }

    def send(self, msg):
        """Send 'msg' to the socket opened in 'recv()'"""
        print(msg)
        self.client.send(b"HTTP/1.1 200 OK\r\n\r\n" + msg.encode())
        self.client.close()

    def open(self, url, params):
        """Open 'url' in browser amd return response parameters"""
        import webbrowser
        url += "?" + urllib.parse.urlencode(params)
        browser = self.config("browser", True)
        if not browser or (browser and not webbrowser.open(url)):
            print("Please open this URL in your browser:")
            print(url, end="\n\n", flush=True)
        return self.recv()

    def _oauth2_authorization_code_grant(
            self, client_id, client_secret, auth_url, token_url, scope):
        """Perform an OAuth2 authorization code grant"""

        state = "gallery-dl:{}:{}".format(
            self.subcategory, util.OAuthSession.nonce(8))

        auth_params = {
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": scope,
        }

        # receive 'code'
        params = self.open(auth_url, auth_params)

        # check auth response
        if state != params.get("state"):
            self.send("'state' mismatch: expected {}, got {}.".format(
                state, params.get("state")))
            return
        if "error" in params:
            self.send(params["error"])
            return

        # exchange 'code' for 'refresh_token'
        data = {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": self.redirect_uri,
        }
        auth = (client_id, client_secret)
        data = self.session.post(token_url, data=data, auth=auth).json()

        # check token response
        if "error" in data:
            self.send(data["error"])
            return

        # display refresh token
        self.send(OAUTH2_MSG_TEMPLATE.format(
            category=self.subcategory,
            token=data["refresh_token"]
        ))


class OAuthReddit(OAuthBase):
    subcategory = "reddit"
    pattern = ["oauth:reddit$"]

    def items(self):
        yield Message.Version, 1

        self.session.headers["User-Agent"] = reddit.RedditAPI.USER_AGENT
        self._oauth2_authorization_code_grant(
            reddit.RedditAPI.CLIENT_ID,
            "",
            "https://www.reddit.com/api/v1/authorize",
            "https://www.reddit.com/api/v1/access_token",
            "read",
        )


class OAuthDeviantart(OAuthBase):
    subcategory = "deviantart"
    pattern = ["oauth:deviantart$"]
    redirect_uri = "https://mikf.github.io/gallery-dl/oauth-redirect.html"

    def items(self):
        yield Message.Version, 1

        self._oauth2_authorization_code_grant(
            deviantart.DeviantartAPI.CLIENT_ID,
            deviantart.DeviantartAPI.CLIENT_SECRET,
            "https://www.deviantart.com/oauth2/authorize",
            "https://www.deviantart.com/oauth2/token",
            "browse",
        )


class OAuthFlickr(OAuthBase):
    subcategory = "flickr"
    pattern = ["oauth:flickr$"]

    def __init__(self, match):
        OAuthBase.__init__(self, match)
        self.session = util.OAuthSession(
            self.session,
            flickr.FlickrAPI.API_KEY, flickr.FlickrAPI.API_SECRET
        )
        del self.session.params["oauth_token"]

    def items(self):
        yield Message.Version, 1

        # Get a Request Token
        url = "https://www.flickr.com/services/oauth/request_token"
        params = {"oauth_callback": self.redirect_uri}
        data = self.session.get(url, params=params).text

        data = urllib.parse.parse_qs(data)
        self.session.params["oauth_token"] = token = data["oauth_token"][0]
        self.session.token_secret = data["oauth_token_secret"][0]

        # Get the User's Authorization
        url = "https://www.flickr.com/services/oauth/authorize"
        params = {"oauth_token": token, "perms": "read"}
        data = self.open(url, params)

        # Exchange the Request Token for an Access Token
        url = "https://www.flickr.com/services/oauth/access_token"
        data = self.session.get(url, params=data).text

        data = urllib.parse.parse_qs(data)
        self.send(FLICKR_MSG_TEMPLATE.format(
            token=data["oauth_token"][0],
            token_secret=data["oauth_token_secret"][0]))


OAUTH2_MSG_TEMPLATE = """
Your Refresh Token is

{token}

Put this value into your configuration file as
'extractor.{category}.refesh-token'.

Example:
{{
    "extractor": {{
        "{category}": {{
            "refresh-token": "{token}"
        }}
    }}
}}
"""

FLICKR_MSG_TEMPLATE = """
Your Access Token and Access Token Secret are

{token}
{token_secret}

Put these values into your configuration file as
'extractor.flickr.access-token' and 'extractor.flickr.access-token-secret'.

Example:
{{
    "extractor": {{
        "flickr": {{
            "access-token": "{token}",
            "access-token-secret": "{token_secret}"
        }}
    }}
}}
"""

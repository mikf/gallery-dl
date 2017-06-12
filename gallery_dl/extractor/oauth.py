# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility classes to setup OAuth"""

from .common import Extractor, Message
from . import reddit, flickr
import time
import hmac
import base64
import random
import string
import hashlib
import urllib.parse


class OAuthSession():
    """Minimal wrapper for requests.session objects to support OAuth 1.0"""
    def __init__(self, session, consumer_key, consumer_secret,
                 token=None, token_secret=None):
        self.session = session
        self.consumer_secret = consumer_secret
        self.token_secret = token_secret or ""
        self.params = session.params
        self.params["oauth_consumer_key"] = consumer_key
        self.params["oauth_token"] = token
        self.params["oauth_signature_method"] = "HMAC-SHA1"
        self.params["oauth_version"] = "1.0"

    def get(self, url, params):
        params.update(self.params)
        params["oauth_nonce"] = self.nonce(16)
        params["oauth_timestamp"] = int(time.time())
        params["oauth_signature"] = self.signature(url, params)
        return self.session.get(url, params=params)

    def signature(self, url, params):
        """Generate 'oauth_signature' value"""
        query = urllib.parse.urlencode(sorted(params.items()))
        message = self.concat("GET", url, query).encode()
        key = self.concat(self.consumer_secret, self.token_secret).encode()
        signature = hmac.new(key, message, hashlib.sha1).digest()
        return base64.b64encode(signature)

    @staticmethod
    def concat(*args):
        return "&".join(urllib.parse.quote(item, "") for item in args)

    @staticmethod
    def nonce(N, alphabet=string.ascii_letters):
        return "".join(random.choice(alphabet) for _ in range(N))


class OAuthBase(Extractor):
    """Base class for OAuth Helpers"""
    category = "oauth"
    redirect_uri = "http://localhost:6414/"

    def __init__(self):
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
        self.client = server.accept()[0]
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
        if not webbrowser.open(url):
            print("Please open this URL in your browser:")
            print(url, end="\n\n", flush=True)
        return self.recv()


class OAuthReddit(OAuthBase):
    subcategory = "reddit"
    pattern = ["oauth:reddit$"]

    def __init__(self, match):
        OAuthBase.__init__(self)
        self.session.headers["User-Agent"] = reddit.RedditAPI.USER_AGENT
        self.client_id = reddit.RedditAPI.CLIENT_ID
        self.state = "gallery-dl:{}:{}".format(
            self.subcategory, OAuthSession.nonce(8))

    def items(self):
        yield Message.Version, 1

        url = "https://www.reddit.com/api/v1/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": self.state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": "read",
        }

        # receive 'code'
        params = self.open(url, params)

        if self.state != params.get("state"):
            self.send("'state' mismatch: expected {}, got {}.".format(
                      self.state, params.get("state")))
            return
        if "error" in params:
            self.send(params["error"])
            return

        # exchange 'code' for 'refresh_token'
        url = "https://www.reddit.com/api/v1/access_token"
        auth = (self.client_id, "")
        data = {
            "grant_type": "authorization_code",
            "code": params["code"],
            "redirect_uri": self.redirect_uri,
        }
        data = self.session.post(url, auth=auth, data=data).json()

        if "error" in data:
            self.send(data["error"])
        else:
            self.send(REDDIT_MSG_TEMPLATE.format(token=data["refresh_token"]))


class OAuthFlickr(OAuthBase):
    subcategory = "flickr"
    pattern = ["oauth:flickr$"]

    def __init__(self, match):
        OAuthBase.__init__(self)
        self.session = OAuthSession(self.session,
                                    flickr.FlickrAPI.API_KEY,
                                    flickr.FlickrAPI.API_SECRET)
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


REDDIT_MSG_TEMPLATE = """
Your Refresh Token is

{token}

Put this value into your configuration file as 'extractor.reddit.refesh-token'.

Example:
{{
    "extractor": {{
        "reddit": {{
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

# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bsky.social/"""

from .common import Extractor, Message
from .. import text, util

import json
import dataclasses
import netrc
import posixpath

import chitose

@dataclasses.dataclass(unsafe_hash=True)
class PostReference():
    user_id: str = dataclasses.field(hash=True)
    post_id: str = dataclasses.field(hash=True)

class BlueskyAPI():
    def __init__(self, extractor, instance="bsky.social"):
        self.root = extractor.root
        self.extractor = extractor

        self.agent = chitose.BskyAgent(service=f'https://{instance}')

        # BSKY_USER = extractor.config("username"),
        # BSKY_PASSWD = extractor.config("password")

        rc = netrc.netrc()
        (BSKY_USER, _, BSKY_PASSWD) = rc.authenticators(instance)

        self.agent.login(BSKY_USER, BSKY_PASSWD)

    def bskyGetDid(self, user_id: str) -> str:
        return json.loads(self.agent.get_profile(actor=user_id))['did']

    def bskyTupleToUri(self, post_reference: PostReference) -> str:
        return f"at://{self.bskyGetDid(post_reference.user_id)}/app.bsky.feed.post/{post_reference.post_id}"

    def bskyGetThread(self, post_reference) -> dict:
        thread_response = self.agent.get_post_thread(
            uri=self.bskyTupleToUri(post_reference)
        )
        thread_response = json.loads(thread_response)

        return thread_response

    def getSkeetJson(self, post_reference):
        thread_response = self.bskyGetThread(post_reference)
        thread_response['thread']['post']['id'] = post_reference.post_id

        json_obj = thread_response['thread']['post']

        return json_obj

class _BlueskyPostExtractor(Extractor):
    """Extractor for bluesky posts"""
    category = "bluesky"
    subcategory = "post"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{post_id} {filename}.{extension}"
    root = "https://bsky.social"
    referer = False
    pattern = r"(?:https?://)?bsky.app/profile/(?P<user_id>[^/]+)/post/(?P<post_id>[^ )]+)"
    example = "https://bsky.app/profile/im.giovanh.com/post/3kaxkwevkn626"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id, self.post_id = match.groups()
        self.api = BlueskyAPI(self)
        self.json_obj = self.api.getSkeetJson(PostReference(self.user_id, self.post_id))

        self.metadata = self.json_obj
        self.metadata.update(match.groupdict())

    def items(self):

        yield Message.Directory, self.metadata

        for image_def in self.json_obj.get('embed', {}).get('images', []):
            src_url = image_def['fullsize']
            name = posixpath.split(src_url)[-1].replace('@', '.')
            img_meta = text.nameext_from_url(name, None)
            img_meta.update(self.metadata)
            yield Message.Url, src_url, img_meta

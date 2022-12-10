# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://soundgasm.net/"""

from .common import Extractor, Message
from .. import text


class SoundgasmSoundExtractor(Extractor):
    """Extractor for individual sounds on soundgasm.net"""
    category = "soundgasm"
    subcategory = "sound"
    filename_fmt = "{title}.{extension}"
    directory_fmt = ("{category}", "{user}")
    archive_fmt = "{user}_{slug}"
    pattern = (r"(?:https?://)?(?:www\.)?soundgasm\.net"
               r"/u(?:ser)?/([^/?#]+)/([^/?#]+)")
    test = (
        (("https://soundgasm.net/user/fierce-aphrodite"
         "/Soap-by-Melanie-Martinez-Cover"), {
            "pattern": (r"https://media\.soundgasm\.net/sounds"
                        r"/04614d5a142ee4d56967ed2b764de3453d048c5b\.m4a"),
            "keyword": {
                "user" : "fierce-aphrodite",
                "slug" : "Soap-by-Melanie-Martinez-Cover",
                "title": "Soap by Melanie Martinez (Cover)",
                "description": str,
            },
        }),
        ("https://soundgasm.net/u/anner1234/Your-girlfriend-is-sick", {
            "pattern": (r"https://media\.soundgasm\.net/sounds"
                        r"/db4d34bb9e11f71385fce1fb6bd17674faaae483\.m4a"),
            "keyword": {
                "user" : "anner1234",
                "slug" : "Your-girlfriend-is-sick",
                "title": "Your girlfriend is sick",
                "description": str,
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user, self.slug = match.groups()

    def items(self):
        page = self.request("https://soundgasm.net/user/{}/{}".format(
            self.user, self.slug)).text
        data = {
            "user" : self.user,
            "slug" : self.slug,
            "title": text.unescape(text.extr(
                page, 'aria-label="title">', "</div>")),
            "description": text.unescape(text.remove_html(text.extr(
                page, 'class="jp-description">', "</div>"))),
        }
        url = text.extract(page, ': "', '"', page.index('("setMedia",'))[0]
        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)


class SoundgasmUserExtractor(Extractor):
    """Extractor for all sounds from a soundgasm user"""
    category = "soundgasm"
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.)?soundgasm\.net"
               r"/u(?:ser)?/([^/?#]+)/?$")
    test = ("https://soundgasm.net/u/fierce-aphrodite", {
        "pattern": SoundgasmSoundExtractor.pattern,
        "count"  : ">= 15",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        page = self.request("https://soundgasm.net/user/" + self.user).text
        data = {"_extractor": SoundgasmSoundExtractor}
        for sound in text.extract_iter(
                page, 'class="sound-details">', "</a>"):
            yield Message.Queue, text.extr(sound, '<a href="', '"'), data

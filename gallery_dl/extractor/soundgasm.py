# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://soundgasm.net/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?soundgasm\.net/u(?:ser)?"


class SoundgasmExtractor(Extractor):
    """Base class for soundgasm extractors"""
    category = "soundgasm"
    root = "https://soundgasm.net"
    request_interval = (0.5, 1.5)
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{title}.{extension}"
    archive_fmt = "{user}_{slug}"

    def items(self):
        for sound in map(self._extract_sound, self.sounds()):
            url = sound["url"]
            yield Message.Directory, sound
            yield Message.Url, url, text.nameext_from_url(url, sound)

    def _extract_sound(self, url):
        extr = text.extract_from(self.request(url).text)

        _, user, slug = url.rstrip("/").rsplit("/", 2)
        data = {
            "user" : user,
            "slug" : slug,
            "title": text.unescape(extr('aria-label="title">', "<")),
            "description": text.unescape(text.remove_html(extr(
                'class="jp-description">', '</div>'))),
        }

        formats = extr('"setMedia", {', '}')
        data["url"] = text.extr(formats, ': "', '"')

        return data


class SoundgasmAudioExtractor(SoundgasmExtractor):
    """Extractor for audio clips from soundgasm.net"""
    subcategory = "audio"
    pattern = BASE_PATTERN + r"/([^/?#]+)/([^/?#]+)"
    test = (
        (("https://soundgasm.net/u/ClassWarAndPuppies2"
          "/687-Otto-von-Toontown-12822"), {
            "pattern": r"https://media\.soundgasm\.net/sounds"
                       r"/26cb2b23b2f2c6094b40ee3a9167271e274b570a\.m4a",
            "keyword": {
                "description": "We celebrate today’s important prisoner swap, "
                               "and finally bring the 2022 mid-terms to a clos"
                               "e with Raphael Warnock’s defeat of Herschel Wa"
                               "lker in Georgia. Then, we take a look at the Q"
                               "anon-addled attempt to overthrow the German go"
                               "vernment and install Heinrich XIII Prince of R"
                               "euss as kaiser.",
                "extension": "m4a",
                "filename": "26cb2b23b2f2c6094b40ee3a9167271e274b570a",
                "slug": "687-Otto-von-Toontown-12822",
                "title": "687 - Otto von Toontown (12/8/22)",
                "user": "ClassWarAndPuppies2",
            },
        }),
        ("https://www.soundgasm.net/user/ClassWarAndPuppies2"
         "/687-Otto-von-Toontown-12822"),
    )

    def __init__(self, match):
        SoundgasmExtractor.__init__(self, match)
        self.user, self.slug = match.groups()

    def sounds(self):
        return ("{}/u/{}/{}".format(self.root, self.user, self.slug),)


class SoundgasmUserExtractor(SoundgasmExtractor):
    """Extractor for all sounds from a soundgasm user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/([^/?#]+)/?$"
    test = ("https://soundgasm.net/u/fierce-aphrodite", {
        "pattern": r"https://media\.soundgasm\.net/sounds/[0-9a-f]{40}\.m4a",
        "count"  : ">= 15",
        "keyword": {
            "description": str,
            "extension": "m4a",
            "filename": "re:^[0-9a-f]{40}$",
            "slug": str,
            "title": str,
            "url": str,
            "user": "fierce-aphrodite"
        },
    })

    def __init__(self, match):
        SoundgasmExtractor.__init__(self, match)
        self.user = match.group(1)

    def sounds(self):
        page = self.request(self.root + "/user/" + self.user).text
        return [
            text.extr(sound, '<a href="', '"')
            for sound in text.extract_iter(
                page, 'class="sound-details">', "</a>")
        ]

# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://soundgasm.net/"""

from .common import Extractor, Message
from .. import text


class SoundgasmAudioExtractor(Extractor):
    """Extractor for audio clips from soundgasm.net"""
    category = "soundgasm"
    subcategory = "audio"
    root = "https://soundgasm.net"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{title}.{extension}"
    archive_fmt = "{user}_{slug}"
    pattern = (r"(?:https?://)?(?:www\.)?soundgasm\.net"
               r"/u(?:ser)?/([^/?#]+)/([^/?#]+)")
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
        Extractor.__init__(self, match)
        self.user, self.slug = match.groups()

    def items(self):
        url = "{}/u/{}/{}".format(self.root, self.user, self.slug)
        extr = text.extract_from(self.request(url).text)

        data = {
            "user" : self.user,
            "slug" : self.slug,
            "title": text.unescape(extr('aria-label="title">', "<")),
            "description": text.unescape(text.remove_html(extr(
                'class="jp-description">', '</div>'))),
        }

        formats = extr('"setMedia", {', '}')
        url = text.extr(formats, ': "', '"')

        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)


class SoundgasmUserExtractor(Extractor):
    """Extractor for all sounds from a soundgasm user"""
    category = "soundgasm"
    subcategory = "user"
    root = "https://soundgasm.net"
    pattern = (r"(?:https?://)?(?:www\.)?soundgasm\.net"
               r"/u(?:ser)?/([^/?#]+)/?$")
    test = ("https://soundgasm.net/u/fierce-aphrodite", {
        "pattern": SoundgasmAudioExtractor.pattern,
        "count"  : ">= 15",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        page = self.request(self.root + "/user/" + self.user).text
        data = {"_extractor": SoundgasmAudioExtractor}
        for sound in text.extract_iter(
                page, 'class="sound-details">', "</a>"):
            yield Message.Queue, text.extr(sound, '<a href="', '"'), data

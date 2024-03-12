# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "mastodon:https://donotsta.re/@elly/AcoUaA7EH1igiYKmFU",
    "#category": ("mastodon", "donotsta.re", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#urls"    : "https://asdf.donotsta.re/media/917e7722dd30d510686ce9f3717a1f722dac96fd974b5af5ec2ccbc8cbd740c6.png",

    "instance": "donotsta.re",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://wanderingwires.net/@quarc/9qppkxzyd1ee3i9p",
    "#comment" : "null moved account",
    "#category": ("mastodon", "wanderingwires.net", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#urls"    : "https://s3.wanderingwires.net/null/4377e826-72ab-4659-885c-fa12945eb207.png",

    "instance": "wanderingwires.net",
    "instance_remote": None,
},

)

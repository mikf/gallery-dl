# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "mastodon:https://donotsta.re/@elly/AcoUaA7EH1igiYKmFU",
    "#comment" : "Akkoma - /:user/:status_id",
    "#category": ("mastodon", "donotsta.re", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://asdf.donotsta.re/media/917e7722dd30d510686ce9f3717a1f722dac96fd974b5af5ec2ccbc8cbd740c6.png",

    "instance": "donotsta.re",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://wanderingwires.net/@quarc/9qppkxzyd1ee3i9p",
    "#comment" : "null moved account",
    "#category": ("mastodon", "wanderingwires.net", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://s3.wanderingwires.net/null/4377e826-72ab-4659-885c-fa12945eb207.png",

    "instance": "wanderingwires.net",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://woem.space/notice/Aswds12sVGsm55NS2S",
    "#comment" : "Akkoma - /notice/:status_id",
    "#category": ("mastodon", "woem.space", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://nbg1.your-objectstorage.com/woem-space/261f4f482e1cb641db732dab91f0177b1f5ea0bcf008f4831c593ff718dff4fe.jpg",

    "instance" : "woem.space",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://labyrinth.zone/notice/Ai9Y2EijwN3gAil1nM",
    "#comment" : "Akkoma - /notice/:status_id",
    "#category": ("mastodon", "labyrinth.zone", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://media.labyrinth.zone/media/96e10a9e3b0f24f63713d8a03e939eec7f9e636cdef57a14c389163f58e60947.png",

    "instance" : "labyrinth.zone",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://udongein.xyz/notice/Asl9hUpShUamlVAZiC",
    "#comment" : "Pleroma - /notice/:status_id",
    "#category": ("mastodon", "udongein.xyz", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://statics.udongein.xyz/udongein/cc3c7a8b749cd88298fda6553e10f81f9c4de280f03ad107ed25a439e6be23eb.jpg?name=Husky_1743801357069_6QIL5OZLXK.jpg",

    "instance" : "udongein.xyz",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://freeradical.zone/@bitartbot/114477182939377350",
    "#comment" : "Mastodon - /:user/:status_id",
    "#category": ("mastodon", "freeradical.zone", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://nfts.freeradical.zone/media_attachments/files/114/477/182/897/690/030/original/96700c8ae9a79651.png",

    "instance" : "freeradical.zone",
    "instance_remote": None,
},

{
    "#url"     : "mastodon:https://labyrinth.zone/objects/ac523779-93d3-4315-ab8e-25b1665740cf",
    "#comment" : "/objects/:uuid (#7497)",
    "#category": ("mastodon", "labyrinth.zone", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://media.labyrinth.zone/media/96e10a9e3b0f24f63713d8a03e939eec7f9e636cdef57a14c389163f58e60947.png",

    "instance" : "labyrinth.zone",
    "instance_remote": None,
},

)

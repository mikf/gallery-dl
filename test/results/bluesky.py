# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bluesky


__tests__ = (
{
    "#url"     : "https://bsky.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#urls"        : "https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:z72i7hdynmk6r22z27h6tvur&cid=bafkreidypzoaybmfj5h7pnpiyct6ng5yae6ydp4czrm72ocg7ev6vbirri",
    "#sha1_content": "ffcf25e7c511173a12de5276b85903309fcd8d14",

    "author": {
        "avatar"     : "https://cdn.bsky.app/img/avatar/plain/did:plc:z72i7hdynmk6r22z27h6tvur/bafkreihagr2cmvl2jt4mgx3sppwe2it3fwolkrbtjrhcnwjk4jdijhsoze@jpeg",
        "did"        : "did:plc:z72i7hdynmk6r22z27h6tvur",
        "displayName": "Bluesky",
        "handle"     : "bsky.app",
        "labels"     : [],
    },
    "cid"        : "bafyreihh7m6bfrwlcjfklwturmja7qfse5gte7lskpmgw76flivimbnoqm",
    "count"      : 1,
    "createdAt"  : "2023-12-22T18:58:32.715Z",
    "date"       : "dt:2023-12-22 18:58:32",
    "description": "The bluesky logo with the blue butterfly",
    "extension"  : "jpeg",
    "filename"   : "bafkreidypzoaybmfj5h7pnpiyct6ng5yae6ydp4czrm72ocg7ev6vbirri",
    "height"     : 630,
    "indexedAt"  : "2023-12-22T18:58:32.715Z",
    "labels"     : [],
    "likeCount"  : int,
    "num"        : 1,
    "post_id"    : "3kh5rarr3gn2n",
    "replyCount" : int,
    "repostCount": int,
    "uri"        : "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3kh5rarr3gn2n",
    "width"      : 1200,
},

)

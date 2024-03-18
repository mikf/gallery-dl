# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bluesky


__tests__ = (
{
    "#url"     : "https://bsky.app/profile/bsky.app",
    "#category": ("", "bluesky", "user"),
    "#class"   : bluesky.BlueskyUserExtractor,
    "#urls"    : (
        "https://bsky.app/profile/bsky.app/media",
    ),
},

{
    "#url"     : "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur",
    "#category": ("", "bluesky", "user"),
    "#class"   : bluesky.BlueskyUserExtractor,
    "#options" : {"include": "all"},
    "#urls"    : (
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/avatar",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/banner",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/posts",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/replies",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/media",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/likes",
    ),
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/avatar",
    "#category": ("", "bluesky", "avatar"),
    "#class"   : bluesky.BlueskyAvatarExtractor,
    "#urls"    : "https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:z72i7hdynmk6r22z27h6tvur&cid=bafkreihagr2cmvl2jt4mgx3sppwe2it3fwolkrbtjrhcnwjk4jdijhsoze",
},

{
    "#url"     : "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/banner",
    "#category": ("", "bluesky", "background"),
    "#class"   : bluesky.BlueskyBackgroundExtractor,
    "#urls"    : "https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:z72i7hdynmk6r22z27h6tvur&cid=bafkreichzyovokfzmymz36p5jibbjrhsur6n7hjnzxrpbt5jaydp2szvna",
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/posts",
    "#category": ("", "bluesky", "posts"),
    "#class"   : bluesky.BlueskyPostsExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/replies",
    "#category": ("", "bluesky", "replies"),
    "#class"   : bluesky.BlueskyRepliesExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/media",
    "#category": ("", "bluesky", "media"),
    "#class"   : bluesky.BlueskyMediaExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://bsky.app/profile/did:plc:jfhpnnst6flqway4eaeqzj2a/feed/for-science",
    "#category": ("", "bluesky", "feed"),
    "#class"   : bluesky.BlueskyFeedExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/follows",
    "#category": ("", "bluesky", "following"),
    "#class"   : bluesky.BlueskyFollowingExtractor,
    "#urls"    : (
        "https://bsky.app/profile/did:plc:eon2iu7v3x2ukgxkqaf7e5np",
        "https://bsky.app/profile/did:plc:ewvi7nxzyoun6zhxrhs64oiz",
    ),
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/likes",
    "#category": ("", "bluesky", "likes"),
    "#class"   : bluesky.BlueskyLikesExtractor,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/lists/abcdefghijklm",
    "#category": ("", "bluesky", "list"),
    "#class"   : bluesky.BlueskyListExtractor,
},

{
    "#url"     : "https://bsky.app/search?q=nature",
    "#category": ("", "bluesky", "search"),
    "#class"   : bluesky.BlueskySearchExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
    "#archive" : False,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options"     : {"metadata": True},
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
    "instance"   : "bsky.app",
    "labels"     : [],
    "likeCount"  : int,
    "num"        : 1,
    "post_id"    : "3kh5rarr3gn2n",
    "replyCount" : int,
    "repostCount": int,
    "uri"        : "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3kh5rarr3gn2n",
    "width"      : 1200,
    "hashtags"   : [],
    "mentions"   : [],
    "uris"       : ["https://blueskyweb.xyz/blog/12-21-2023-butterfly"],
    "user"       : {
        "avatar"        : str,
        "banner"        : str,
        "description"   : "Official Bluesky account (check domain👆)\n\nFollow for updates and announcements",
        "did"           : "did:plc:z72i7hdynmk6r22z27h6tvur",
        "displayName"   : "Bluesky",
        "followersCount": int,
        "followsCount"  : int,
        "handle"        : "bsky.app",
        "indexedAt"     : "2024-01-20T05:04:41.904Z",
        "labels"        : [],
        "postsCount"    : int,
    },
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/post/3kkzc3xaf5m2w",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options"     : {"metadata": "facets"},
    "#urls"        : "https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreib7ydpe3xxo4cq7nn32w7eqhcanfaanz6caepd2z4kzplxtx2ctgi",
    "#sha1_content": "9cf5748f6d00aae83fbb3cc2c6eb3caa832b90f4",

    "author": {
        "did"        : "did:plc:cslxjqkeexku6elp5xowxkq7",
        "displayName": "mikf",
        "handle"     : "mikf.bsky.social",
        "labels"     : [],
    },
    "cid"        : "bafyreihtck7clocti2qshaiounadof74pxqhz7gnvbstxujqzhlodigqru",
    "count"      : 1,
    "createdAt"  : "2024-02-09T21:57:31.917Z",
    "date"       : "dt:2024-02-09 21:57:31",
    "description": "reading lewd books",
    "extension"  : "jpeg",
    "filename"   : "bafkreib7ydpe3xxo4cq7nn32w7eqhcanfaanz6caepd2z4kzplxtx2ctgi",
    "hashtags"   : [
        "patchouli",
        "patchy",
    ],
    "mentions"   : [
        "did:plc:cslxjqkeexku6elp5xowxkq7",
    ],
    "uris"       : [
        "https://seiga.nicovideo.jp/seiga/im5977527",
    ],
    "width"      : 1024,
    "height"     : 768,
    "langs"      : ["en"],
    "likeCount"  : int,
    "num"        : 1,
    "post_id"    : "3kkzc3xaf5m2w",
    "replyCount" : int,
    "repostCount": int,
    "text"       : "testing \"facets\"\n\nsource: seiga.nicovideo.jp/seiga/im5977...\n#patchouli #patchy\n@mikf.bsky.social",
    "uri"        : "at://did:plc:cslxjqkeexku6elp5xowxkq7/app.bsky.feed.post/3kkzc3xaf5m2w",
},

{
    "#url"     : "https://bsky.app/profile/go-guiltism.bsky.social/post/3klgth6lilt2l",
    "#comment" : "different embed CID path",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#urls"    : "https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:owc2r2dsewj3hk73rtd746zh&cid=bafkreieuhplc7fpbvi3suvacaf2dqxzvuu4hgl5o6eifqb76tf3uopldmi",
},

)

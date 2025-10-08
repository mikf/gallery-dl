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
    "#results" : (
        "https://bsky.app/profile/bsky.app/media",
    ),
},

{
    "#url"     : "https://www.bsky.app/profile/bsky.app",
    "#class"   : bluesky.BlueskyUserExtractor,
},

{
    "#url"     : "https://main.bsky.dev/profile/bsky.app",
    "#class"   : bluesky.BlueskyUserExtractor,
},

{
    "#url"     : "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur",
    "#category": ("", "bluesky", "user"),
    "#class"   : bluesky.BlueskyUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/info",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/avatar",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/banner",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/posts",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/replies",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/media",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/video",
        "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/likes",
    ),
},

{
    "#url"     : "https://bsky.app/profile/bsky.app",
    "#class"   : bluesky.BlueskyUserExtractor,
    "#options" : {"quoted": True},
    "#results" : "https://bsky.app/profile/bsky.app/posts",
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/info",
    "#class"   : bluesky.BlueskyInfoExtractor,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/avatar",
    "#category": ("", "bluesky", "avatar"),
    "#class"   : bluesky.BlueskyAvatarExtractor,
    "#results" : "https://puffball.us-east.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:z72i7hdynmk6r22z27h6tvur&cid=bafkreihagr2cmvl2jt4mgx3sppwe2it3fwolkrbtjrhcnwjk4jdijhsoze",
},

{
    "#url"     : "https://bsky.app/profile/did:plc:z72i7hdynmk6r22z27h6tvur/banner",
    "#category": ("", "bluesky", "background"),
    "#class"   : bluesky.BlueskyBackgroundExtractor,
    "#results" : "https://puffball.us-east.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:z72i7hdynmk6r22z27h6tvur&cid=bafkreichzyovokfzmymz36p5jibbjrhsur6n7hjnzxrpbt5jaydp2szvna",
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
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/video",
    "#category": ("", "bluesky", "video"),
    "#class"   : bluesky.BlueskyVideoExtractor,
    "#results" : (
        "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreibmoobktxndnzauku65onoxu2tvvqswetezv76tqcwipktjs3cw3m",
        "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreihq2nsfocrnlpx4nykb4szouqszxwmy3ucnk4k46nx5t6hjnxlti4",
    ),
},

{
    "#url"     : "https://bsky.app/profile/did:plc:jfhpnnst6flqway4eaeqzj2a/feed/for-science",
    "#category": ("", "bluesky", "feed"),
    "#class"   : bluesky.BlueskyFeedExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
    "#archive" : False,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/follows",
    "#category": ("", "bluesky", "following"),
    "#class"   : bluesky.BlueskyFollowingExtractor,
    "#results" : (
        "https://bsky.app/profile/did:plc:eon2iu7v3x2ukgxkqaf7e5np",
        "https://bsky.app/profile/did:plc:ewvi7nxzyoun6zhxrhs64oiz",
    ),
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/likes",
    "#category": ("", "bluesky", "likes"),
    "#class"   : bluesky.BlueskyLikesExtractor,
    "#auth"    : False,
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/likes",
    "#class"   : bluesky.BlueskyLikesExtractor,
    "#auth"    : False,
    "#results" : "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreih2dn2xeyoayabgvpyutv5ldubcdxzfqipijasfzxyeez7fff5ymi",
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/likes",
    "#class"   : bluesky.BlueskyLikesExtractor,
    "#options" : {"endpoint": "getActorLikes"},
    "#auth"    : True,
    "#results" : "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreih2dn2xeyoayabgvpyutv5ldubcdxzfqipijasfzxyeez7fff5ymi",
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/likes",
    "#class"   : bluesky.BlueskyLikesExtractor,
    "#options" : {"endpoint": "getActorLikes"},
    "#auth"    : False,
    "#count"   : 0,
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
    "#url"     : "https://bsky.app/hashtag/nature",
    "#class"   : bluesky.BlueskyHashtagExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
    "#archive" : False,
},
{
    "#url"     : "https://bsky.app/hashtag/top",
    "#class"   : bluesky.BlueskyHashtagExtractor,
},
{
    "#url"     : "https://bsky.app/hashtag/nature/latest",
    "#class"   : bluesky.BlueskyHashtagExtractor,
},

{
    "#url"     : "https://bsky.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options"     : {"metadata": True},
    "#results"     : "https://puffball.us-east.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:z72i7hdynmk6r22z27h6tvur&cid=bafkreidypzoaybmfj5h7pnpiyct6ng5yae6ydp4czrm72ocg7ev6vbirri",
    "#sha1_content": "ffcf25e7c511173a12de5276b85903309fcd8d14",

    "author": {
        "avatar"     : "https://cdn.bsky.app/img/avatar/plain/did:plc:z72i7hdynmk6r22z27h6tvur/bafkreihagr2cmvl2jt4mgx3sppwe2it3fwolkrbtjrhcnwjk4jdijhsoze@jpeg",
        "did"        : "did:plc:z72i7hdynmk6r22z27h6tvur",
        "displayName": "Bluesky",
        "handle"     : "bsky.app",
        "instance"   : "bsky.app",
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
        "description"   : str,
        "did"           : "did:plc:z72i7hdynmk6r22z27h6tvur",
        "displayName"   : "Bluesky",
        "followersCount": int,
        "followsCount"  : int,
        "handle"        : "bsky.app",
        "instance"      : "bsky.app",
        "indexedAt"     : str,
        "labels"        : [],
        "postsCount"    : int,
    },
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/post/3kkzc3xaf5m2w",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options"     : {"metadata": "facets"},
    "#results"     : "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreib7ydpe3xxo4cq7nn32w7eqhcanfaanz6caepd2z4kzplxtx2ctgi",
    "#sha1_content": "9cf5748f6d00aae83fbb3cc2c6eb3caa832b90f4",

    "author": {
        "did"        : "did:plc:cslxjqkeexku6elp5xowxkq7",
        "displayName": "mikf",
        "handle"     : "mikf.bsky.social",
        "instance"   : "bsky.social",
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
    "#results" : "https://amanita.us-east.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:owc2r2dsewj3hk73rtd746zh&cid=bafkreieuhplc7fpbvi3suvacaf2dqxzvuu4hgl5o6eifqb76tf3uopldmi",
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/post/3l46q5glfex27",
    "#comment" : "video (#6183)",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
    "#results" : "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreihq2nsfocrnlpx4nykb4szouqszxwmy3ucnk4k46nx5t6hjnxlti4",

    "description": "kirby and reimu dance",
    "text"       : "video",
    "width"      : 1280,
    "height"     : 720,
    "filename"   : "bafkreihq2nsfocrnlpx4nykb4szouqszxwmy3ucnk4k46nx5t6hjnxlti4",
    "extension"  : "mp4",
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/post/3kmfodjotln2f",
    "#comment" : "quote (#6183)",
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options" : {"quoted": True},
    "#results" : "https://lionsmane.us-east.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:eyhmjdxsnthqhvvszdejaocz&cid=bafkreib6eb7tfozksquveaj3z5msyx3hkniubrulxdys3eftthvmuzrtme",

    "author": {
        "associated" : dict,
        "avatar"     : "https://cdn.bsky.app/img/avatar/plain/did:plc:eyhmjdxsnthqhvvszdejaocz/bafkreigjrftlw7tabtpie32saydttpnoi7276v252vnycr6zt6euef7vdi@jpeg",
        "createdAt"  : "2024-01-11T00:27:37.404Z",
        "did"        : "did:plc:eyhmjdxsnthqhvvszdejaocz",
        "displayName": "フナ",
        "handle"     : "ykfuna.bsky.social",
        "labels"     : list,
    },
    "quote_by": {
        "avatar"     : "https://cdn.bsky.app/img/avatar/plain/did:plc:cslxjqkeexku6elp5xowxkq7/bafkreic5jqkn5ohqhgsm6zzi7vnapuz54trojv3io4tfkrcyaprl4b2ztm@jpeg",
        "createdAt"  : "2024-02-05T00:03:54.087Z",
        "did"        : "did:plc:cslxjqkeexku6elp5xowxkq7",
        "displayName": "mikf",
        "handle"     : "mikf.bsky.social",
        "labels"     : list,
    },
    "quote_id": "3kmfodjotln2f",
    "post_id" : "3km4qy5y3jc2z",
},

{
    "#url"     : "https://bsky.app/profile/mikf.bsky.social/post/3kmfp2qktil25",
    "#comment" : "quote with media (#6183)",
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options" : {"quoted": True},
    "#results" : (
        "https://conocybe.us-west.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:cslxjqkeexku6elp5xowxkq7&cid=bafkreiegcyremdrecmnpisci3a3nduc7lm3zdcl76z5o5rd4nstyolrxki",
        "https://lionsmane.us-east.host.bsky.network/xrpc/com.atproto.sync.getBlob?did=did:plc:eyhmjdxsnthqhvvszdejaocz&cid=bafkreicojrnwiw5eqo3ko2q6duduyjaoyiqvdc25kuikcedlijtbgvlt5e",

    ),

    "text"     : {"quote with media", ""},
},

{
    "#url"     : "https://bsky.app/profile/nytimes.com/post/3l7xvcjgdxg2g",
    "#comment" : "instance metadata",
    "#class"   : bluesky.BlueskyPostExtractor,
    "#options" : {"metadata": "user"},

    "instance": "bsky.app",
    "author": {
        "createdAt"  : "2023-06-05T18:50:31.498Z",
        "did"        : "did:plc:eclio37ymobqex2ncko63h4r",
        "displayName": "The New York Times",
        "handle"     : "nytimes.com",
        "instance"   : "nytimes.com",
    },
    "user": {
        "avatar"        : "https://cdn.bsky.app/img/avatar/plain/did:plc:eclio37ymobqex2ncko63h4r/bafkreidvvqj5jymmpaeklwkpq6gi532el447mjy2yultuukypzqm5ohfju@jpeg",
        "banner"        : "https://cdn.bsky.app/img/banner/plain/did:plc:eclio37ymobqex2ncko63h4r/bafkreidlzzmt7sy2n6imz5mg7siygb3cy4e526nvbjucczeu5cutqro5ni@jpeg",
        "createdAt"     : "2023-06-05T18:50:31.498Z",
        "description"   : "In-depth, independent reporting to better understand the world, now on Bluesky. News tips? Share them here: http://nyti.ms/2FVHq9v",
        "did"           : "did:plc:eclio37ymobqex2ncko63h4r",
        "displayName"   : "The New York Times",
        "followersCount": int,
        "followsCount"  : int,
        "handle"        : "nytimes.com",
        "instance"      : "nytimes.com",
        "indexedAt"     : "iso:datetime",
        "labels"        : [],
        "postsCount"    : int,
    },
},

{
    "#url"     : "https://bsky.app/profile/stupidsaru.woke.cat/post/3l66wwwqw6u2w",
    "#comment" : "instance metadata",
    "#class"   : bluesky.BlueskyPostExtractor,

    "author": {
        "createdAt": "2023-08-31T23:28:42.305Z",
        "did"      : "did:plc:b7s3pdcjk6qvxmu3n674hlgj",
        "handle"   : "stupidsaru.woke.cat",
        "instance" : "woke.cat",
    },
},

{
    "#url"     : "https://bsky.app/profile/alt.bun.how/post/3l7rdfxhyds2f",
    "#comment" : "non-bsky PDS (#6406)",
    "#class"   : bluesky.BlueskyPostExtractor,
    "#results"     : "https://pds.bun.how/xrpc/com.atproto.sync.getBlob?did=did:plc:7x6rtuenkuvxq3zsvffp2ide&cid=bafkreielhgekjheckgjusx7x5hxkbrqryfdmzdwwp2zoxchovgnpzkxzae",
    "#sha1_content": "1777956de0dc8cf0815c5c7eb574a24ce54a1d42",

    "author": {
        "createdAt": "2024-10-17T13:55:48.833Z",
        "did"      : "did:plc:7x6rtuenkuvxq3zsvffp2ide",
        "handle"   : "cinny.bun.how",
        "instance" : "bun.how",
    },
},

{
    "#url"     : "https://cbsky.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
},

{
    "#url"     : "https://bskye.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
},

{
    "#url"     : "https://bskyx.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
},

{
    "#url"     : "https://bsyy.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
},

{
    "#url"     : "https://fxbsky.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
},

{
    "#url"     : "https://vxbsky.app/profile/bsky.app/post/3kh5rarr3gn2n",
    "#category": ("", "bluesky", "post"),
    "#class"   : bluesky.BlueskyPostExtractor,
},

{
    "#url"     : "https://bsky.app/profile/jacksonlab.bsky.social/post/3m2ms33o6p52k",
    "#comment" : "'external' embed - 'images': [], 'video': null",
    "#class"   : bluesky.BlueskyPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://bsky.app/saved",
    "#class"   : bluesky.BlueskyBookmarkExtractor,
},

)

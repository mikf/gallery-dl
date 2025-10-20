# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imgur
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://imgur.com/21yMxCS",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
    "#sha1_url"    : "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",
    "#results"     : "https://i.imgur.com/21yMxCS.png",

    "account_id"    : 0,
    "comment_count" : int,
    "cover_id"      : "21yMxCS",
    "date"          : "dt:2016-11-10 14:24:35",
    "description"   : "",
    "downvote_count": int,
    "duration"      : 0,
    "ext"           : "png",
    "favorite"      : False,
    "favorite_count": 0,
    "has_sound"     : False,
    "height"        : 32,
    "id"            : "21yMxCS",
    "image_count"   : 1,
    "in_most_viral" : False,
    "is_ad"         : False,
    "is_album"      : False,
    "is_animated"   : False,
    "is_looping"    : False,
    "is_mature"     : False,
    "is_pending"    : False,
    "mime_type"     : "image/png",
    "name"          : "test-テスト",
    "point_count"   : int,
    "privacy"       : "",
    "score"         : int,
    "size"          : 182,
    "title"         : "Test",
    "upvote_count"  : int,
    "url"           : "https://i.imgur.com/21yMxCS.png",
    "view_count"    : int,
    "width"         : 64,
},

{
    "#url"     : "http://imgur.com/0gybAXR",
    "#comment" : "gifv/mp4 video",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
    "#sha1_url"    : "a2220eb265a55b0c95e0d3d721ec7665460e3fd7",
    "#sha1_content": "a3c080e43f58f55243ab830569ba02309d59abfc",
},

{
    "#url"     : "https://imgur.com/XFfsmuC",
    "#comment" : "missing title in API response (#467)",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,

    "title": "Tears are a natural response to irritants",
},

{
    "#url"     : "https://imgur.com/1Nily2P",
    "#comment" : "animated png",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
    "#pattern" : "https://i.imgur.com/1Nily2P.png",
},

{
    "#url"     : "https://imgur.com/zzzzzzz",
    "#comment" : "not found",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://imgur.com/test-21yMxCS",
    "#comment" : "slug",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://m.imgur.com/r/Celebs/iHJ7tsM",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://www.imgur.com/21yMxCS",
    "#comment" : "www",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://m.imgur.com/21yMxCS",
    "#comment" : "mobile",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://imgur.com/zxaY6",
    "#comment" : "5 character key",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://imgur.io/zxaY6",
    "#comment" : ".io",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://i.imgur.com/21yMxCS.png",
    "#comment" : "direct link",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://i.imgur.io/21yMxCS.png",
    "#comment" : "direct link .io",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://i.imgur.com/21yMxCSh.png",
    "#comment" : "direct link thumbnail",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://i.imgur.com/zxaY6.gif",
    "#comment" : "direct link (short)",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://i.imgur.com/zxaY6s.gif",
    "#comment" : "direct link (short; thumb)",
    "#category": ("", "imgur", "image"),
    "#class"   : imgur.ImgurImageExtractor,
},

{
    "#url"     : "https://imgur.com/a/TcBmP",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
    "#sha1_url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
    "#results" : (
        "https://i.imgur.com/693j2Kr.jpg",
        "https://i.imgur.com/ZNalkAC.jpg",
        "https://i.imgur.com/lMox9Ek.jpg",
        "https://i.imgur.com/6PryGOv.jpg",
        "https://i.imgur.com/ecasnH2.jpg",
        "https://i.imgur.com/NlJDmFG.jpg",
        "https://i.imgur.com/aCwKs8S.jpg",
        "https://i.imgur.com/Oz4rpxo.jpg",
        "https://i.imgur.com/hE93Xsn.jpg",
        "https://i.imgur.com/A5uBLSx.jpg",
        "https://i.imgur.com/zZghWiD.jpg",
        "https://i.imgur.com/ALV4fYV.jpg",
        "https://i.imgur.com/FDd90t9.jpg",
        "https://i.imgur.com/Txw37NO.jpg",
        "https://i.imgur.com/DcLw7Cl.jpg",
        "https://i.imgur.com/a4VChy8.jpg",
        "https://i.imgur.com/auCwCig.jpg",
        "https://i.imgur.com/Z8VihIb.jpg",
        "https://i.imgur.com/6WDRFne.jpg",
    ),

    "album"      : {
        "account_id"    : 0,
        "comment_count" : int,
        "cover_id"      : "693j2Kr",
        "date"          : "dt:2015-10-09 10:37:50",
        "description"   : "",
        "downvote_count": 0,
        "favorite"      : False,
        "favorite_count": 0,
        "id"            : "TcBmP",
        "image_count"   : 19,
        "in_most_viral" : False,
        "is_ad"         : False,
        "is_album"      : True,
        "is_mature"     : False,
        "is_pending"    : False,
        "privacy"       : "private",
        "score"         : int,
        "title"         : "138",
        "upvote_count"  : int,
        "url"           : "https://imgur.com/a/TcBmP",
        "view_count"    : int,
        "virality"      : int,
    },
    "account_id" : 0,
    "count"      : 19,
    "date"       : "type:datetime",
    "description": "",
    "ext"        : "jpg",
    "has_sound"  : False,
    "height"     : int,
    "id"         : str,
    "is_animated": False,
    "is_looping" : False,
    "mime_type"  : "image/jpeg",
    "name"       : str,
    "num"        : int,
    "size"       : int,
    "title"      : str,
    "type"       : "image",
    "updated_at" : None,
    "url"        : str,
    "width"      : int,
},

{
    "#url"     : "https://imgur.com/a/eD9CT",
    "#comment" : "large album",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://imgur.com/a/RhJXhVT/all",
    "#comment" : "7 character album hash",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
    "#sha1_url": "695ef0c950023362a0163ee5041796300db76674",
},

{
    "#url"     : "https://imgur.com/a/TcBmQ",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://imgur.com/a/pjOnJA0",
    "#comment" : "empty, no 'media' (#2557)",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://imgur.com/a/138-TcBmP",
    "#comment" : "slug",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
},

{
    "#url"     : "https://www.imgur.com/a/TcBmP",
    "#comment" : "www",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
},

{
    "#url"     : "https://imgur.io/a/TcBmP",
    "#comment" : ".io",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
},

{
    "#url"     : "https://m.imgur.com/a/TcBmP",
    "#comment" : "mobile",
    "#category": ("", "imgur", "album"),
    "#class"   : imgur.ImgurAlbumExtractor,
},

{
    "#url"     : "https://imgur.com/gallery/zf2fIms",
    "#comment" : "non-album gallery (#380)",
    "#category": ("", "imgur", "gallery"),
    "#class"   : imgur.ImgurGalleryExtractor,
    "#pattern" : "https://imgur.com/zf2fIms",
},

{
    "#url"     : "https://imgur.com/gallery/eD9CT",
    "#category": ("", "imgur", "gallery"),
    "#class"   : imgur.ImgurGalleryExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://imgur.com/gallery/guy-gets-out-of-car-during-long-traffic-jam-to-pet-dog-zf2fIms",
    "#comment" : "slug",
    "#category": ("", "imgur", "gallery"),
    "#class"   : imgur.ImgurGalleryExtractor,
},

{
    "#url"     : "https://imgur.com/t/unmuted/26sEhNr",
    "#category": ("", "imgur", "gallery"),
    "#class"   : imgur.ImgurGalleryExtractor,
},

{
    "#url"     : "https://imgur.com/t/cat/qSB8NbN",
    "#category": ("", "imgur", "gallery"),
    "#class"   : imgur.ImgurGalleryExtractor,
},

{
    "#url"     : "https://imgur.io/t/cat/qSB8NbN",
    "#comment" : ".io",
    "#category": ("", "imgur", "gallery"),
    "#class"   : imgur.ImgurGalleryExtractor,
},

{
    "#url"     : "https://imgur.com/user/Miguenzo",
    "#category": ("", "imgur", "user"),
    "#class"   : imgur.ImgurUserExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://imgur.com/user/Miguenzo/posts",
    "#category": ("", "imgur", "user"),
    "#class"   : imgur.ImgurUserExtractor,
},

{
    "#url"     : "https://imgur.com/user/Miguenzo/submitted",
    "#category": ("", "imgur", "user"),
    "#class"   : imgur.ImgurUserExtractor,
},

{
    "#url"     : "https://imgur.com/user/Miguenzo/favorites",
    "#category": ("", "imgur", "favorite"),
    "#class"   : imgur.ImgurFavoriteExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://imgur.com/user/mikf1/favorites/folder/11896757/public",
    "#category": ("", "imgur", "favorite-folder"),
    "#class"   : imgur.ImgurFavoriteFolderExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#count"   : 3,
},

{
    "#url"     : "https://imgur.com/user/mikf1/favorites/folder/11896741/private",
    "#category": ("", "imgur", "favorite-folder"),
    "#class"   : imgur.ImgurFavoriteFolderExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#count"   : 5,
},

{
    "#url"     : "https://imgur.com/user/me",
    "#class"   : imgur.ImgurMeExtractor,
    "#auth"    : True,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#count"   : 3,
},

{
    "#url"     : "https://imgur.com/user/me/hidden",
    "#class"   : imgur.ImgurMeExtractor,
    "#auth"    : True,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#count"   : 2,
},

{
    "#url"     : "https://imgur.com/user/me/posts",
    "#class"   : imgur.ImgurMeExtractor,
},

{
    "#url"     : "https://imgur.com/user/me/posts/hidden",
    "#class"   : imgur.ImgurMeExtractor,
},

{
    "#url"     : "https://imgur.com/r/pics",
    "#category": ("", "imgur", "subreddit"),
    "#class"   : imgur.ImgurSubredditExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://imgur.com/t/animals",
    "#category": ("", "imgur", "tag"),
    "#class"   : imgur.ImgurTagExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://imgur.com/search?q=cute+cat",
    "#category": ("", "imgur", "search"),
    "#class"   : imgur.ImgurSearchExtractor,
    "#pattern" : r"https://imgur\.com(/a)?/\w+$",
    "#range"   : "1-100",
    "#count"   : 100,
},

)

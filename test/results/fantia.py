# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fantia


__tests__ = (
{
    "#url"     : "https://fantia.jp/fanclubs/6939",
    "#category": ("", "fantia", "creator"),
    "#class"   : fantia.FantiaCreatorExtractor,
    "#range"   : "1-25",
    "#count"   : ">= 25",

    "fanclub_user_id": 52152,
    "tags"           : list,
    "post_title"     : str,
},

{
    "#url"     : "https://fantia.jp/posts/1166373",
    "#category": ("", "fantia", "post"),
    "#class"   : fantia.FantiaPostExtractor,
    "#pattern" : r"https://(c\.fantia\.jp/uploads/post/file/1166373/|cc\.fantia\.jp/uploads/post_content_photo/file/732549[01]|fantia\.jp/posts/1166373/album_image\?)",

    "blogpost_text"   : r"re:^$|This is a test.\n\n(This is a test.)?\n\n|Link to video:\nhttps://www.youtube.com/watch\?v=5SSdvNcAagI\n\nhtml img from another site:\n\n\n\n\n\n",
    "comment"         : "\n\n",
    "content_category": r"re:thumb|blog|photo_gallery",
    "content_comment" : str,
    "content_count"   : 5,
    "content_filename": r"re:|",
    "content_num"     : range(1, 5),
    "content_title"   : r"re:Test (Blog Content \d+|Image Gallery)|thumb",
    "date"            : "dt:2022-03-09 16:46:12",
    "fanclub_id"      : 356320,
    "fanclub_name"    : "Test Fantia",
    "fanclub_url"     : "https://fantia.jp/fanclubs/356320",
    "fanclub_user_id" : 7487131,
    "fanclub_user_name": "2022/03/08 15:13:52の名無し",
    "file_url"        : str,
    "filename"        : str,
    "num"             : int,
    "plan"            : dict,
    "post_id"         : 1166373,
    "post_title"      : "Test Fantia Post",
    "post_url"        : "https://fantia.jp/posts/1166373",
    "posted_at"       : "Thu, 10 Mar 2022 01:46:12 +0900",
    "rating"          : "general",
    "tags"            : [],
},

{
    "#url"     : "https://fantia.jp/posts/508363",
    "#category": ("", "fantia", "post"),
    "#class"   : fantia.FantiaPostExtractor,
    "#count"   : 6,

    "post_title": "zunda逆バニーでおしりｺｯｼｮﾘ",
    "tags"      : list,
    "rating"    : "adult",
    "post_id"   : 508363,
},

)

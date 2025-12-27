# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import linkedin
from gallery_dl import exception

__tests__ = (
{
    "#url"     : "https://www.linkedin.com/feed/update/urn:li:activity:7381400030911500288/",
    "#comment" : "feed URL with video content - Found 1 media item",
    "#class"   : linkedin.LinkedinFeedExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://www.linkedin.com/posts/groveben_in-a-time-of-agentic-creation-taste-and-ugcPost-7403592769451335681-Jt4n",
    "#comment" : "posts URL with video content - Found 1 media item",
    "#class"   : linkedin.LinkedinPostExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://www.linkedin.com/posts/the-brand-identity-group-ltd_since-2003-nuits-sonores-has-transformed-activity-7404006895822372867-2rvj?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAkyN_sBOslkonzC5zCQEyrDt7AVDULHCNA",
    "#comment" : "posts URL with multiple photos and querystring - Found 4 media items",
    "#class"   : linkedin.LinkedinPostExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.linkedin.com/posts/invalid-url-format",
    "#comment" : "invalid URL format - should trigger StopExtraction when post ID extraction fails",
    "#class"   : linkedin.LinkedinPostExtractor,
    "#exception": exception.StopExtraction,
},

)

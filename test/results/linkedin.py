# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import linkedin
from gallery_dl import exception

__tests__ = (
    {
        "#url": "https://www.linkedin.com/posts/invalid-url-format",
        "#class": linkedin.LinkedinPostExtractor,
        "#exception": exception.StopExtraction,
        "#comment": "invalid URL format - should trigger StopExtraction when post ID extraction fails",
    },
    {
        "#url": "https://www.linkedin.com/feed/update/urn:li:activity:7381400030911500288/",
        "#category": ("", "linkedin", "feed"),
        "#class": linkedin.LinkedinFeedExtractor,
        "#count": 1,
        "#comment": "feed URL with video content - Found 1 media item",
    },
    {
        "#url": "https://www.linkedin.com/posts/groveben_in-a-time-of-agentic-creation-taste-and-ugcPost-7403592769451335681-Jt4n",
        "#category": ("", "linkedin", "post"),
        "#class": linkedin.LinkedinPostExtractor,
        "#count": 1,
        "#comment": "posts URL with video content - Found 1 media item",
    },
    {
        "#url": "https://www.linkedin.com/posts/the-brand-identity-group-ltd_since-2003-nuits-sonores-has-transformed-activity-7404006895822372867-2rvj?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAkyN_sBOslkonzC5zCQEyrDt7AVDULHCNA",
        "#category": ("", "linkedin", "post"),
        "#class": linkedin.LinkedinPostExtractor,
        "#count": 4,
        "#comment": "posts URL with multiple photos and querystring - Found 4 media items",
    },
    {
        "#url": "https://www.linkedin.com/posts/groveben_in-a-time-of-agentic-creation-taste-and-ugcPost-7403592769451335681-Jt4n?utm_source=test&utm_medium=test",
        "#category": ("", "linkedin", "post"),
        "#class": linkedin.LinkedinPostExtractor,
        "#count": 1,
        "#comment": "querystring removal verification - should work same as without querystring",
    },
)

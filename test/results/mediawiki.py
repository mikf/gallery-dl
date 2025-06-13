# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.mediawiki.org/wiki/Help:Navigation",
    "#category": ("wikimedia", "mediawiki", "help"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#results" : (
        "https://upload.wikimedia.org/wikipedia/commons/e/ec/OOjs_UI_icon_information-progressive.svg",
        "https://upload.wikimedia.org/wikipedia/commons/6/62/PD-icon.svg",
        "https://upload.wikimedia.org/wikipedia/commons/0/0e/Vector_Sidebar.png",
        "https://upload.wikimedia.org/wikipedia/commons/7/77/Vector_page_tabs.png",
        "https://upload.wikimedia.org/wikipedia/commons/6/6e/Vector_user_links.png",
    ),
},

)

# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


SHADOW = """
<span class="shadow">
    <img src="{src}" class="smshadow" width="{width}" height="{height}">
</span>
<br><br>
"""

HEADER = """<div usr class="gr">
<div class="metadata">
    <h2><a href="{url}">{title}</a></h2>
    <ul>
        <li class="author">
            by <span class="name"><span class="username-with-symbol u">
            <a class="u regular username" href="{userurl}">{username}</a>\
<span class="user-symbol regular"></span></span></span>,
            <span>{date}</span>
        </li>
    </ul>
</div>
"""

HEADER_CUSTOM = """<div class='boxtop journaltop'>
<h2>
    <img src="https://st.deviantart.net/minish/gruzecontrol/icons/journal.gif\
?2" style="vertical-align:middle" alt=""/>
    <a href="{url}">{title}</a>
</h2>
Journal Entry: <span>{date}</span>
"""

HTML = """text:<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/deviantart-network_lc.css?3843780832"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/group_secrets_lc.css?3250492874"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/v6core_lc.css?4246581581"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/sidebar_lc.css?1490570941"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/writer_lc.css?3090682151"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/css/v6loggedin_lc.css?3001430805"/>
    <style>{css}</style>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/core.css?1488405371919"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/peeky.css?1487067424177"/>
    <link rel="stylesheet" href="https://st.deviantart.net\
/roses/cssmin/desktop.css?1491362542749"/>
    <link rel="stylesheet" href="https://static.parastorage.com/services\
/da-deviation/2bfd1ff7a9d6bf10d27b98dd8504c0399c3f9974a015785114b7dc6b\
/app.min.css"/>
</head>
<body id="deviantART-v7" class="bubble no-apps loggedout w960 deviantart">
    <div id="output">
    <div class="dev-page-container bubbleview">
    <div class="dev-page-view view-mode-normal">
    <div class="dev-view-main-content">
    <div class="dev-view-deviation">
    {shadow}
    <div class="journal-wrapper tt-a">
    <div class="journal-wrapper2">
    <div class="journal {cls} journalcontrol">
    {html}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
</body>
</html>
"""

HTML_EXTRA = """\
<div id="devskin0"><div class="negate-box-margin" style="">\
<div usr class="gr-box gr-genericbox"
        ><i usr class="gr1"><i></i></i
        ><i usr class="gr2"><i></i></i
        ><i usr class="gr3"><i></i></i
        ><div usr class="gr-top">
            <i usr class="tri"></i>
            {}
            </div>
    </div><div usr class="gr-body"><div usr class="gr">
            <div class="grf-indent">
            <div class="text">
                {}            </div>
        </div>
                </div></div>
        <i usr class="gr3 gb"></i>
        <i usr class="gr2 gb"></i>
        <i usr class="gr1 gb gb1"></i>    </div>
    </div></div>"""

TEXT = """text:{title}
by {username}, {date}

{content}
"""

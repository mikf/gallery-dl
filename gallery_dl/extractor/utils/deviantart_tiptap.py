# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util
from .. deviantart import eclipse_media


def to_html(markup):
    html = []

    html.append('<div data-editor-viewer="1" '
                'class="_83r8m _2CKTq _3NjDa mDnFl">')
    data = util.json_loads(markup)
    for block in data["document"]["content"]:
        process_content(html, block)
    html.append("</div>")

    return "".join(html)


def process_content(html, content):
    type = content["type"]

    if type == "paragraph":
        if children := content.get("content"):
            html.append('<p style="')

            if attrs := content.get("attrs"):
                if align := attrs.get("textAlign"):
                    html.append("text-align:")
                    html.append(align)
                    html.append(";")
                process_indentation(html, attrs)
                html.append('">')
            else:
                html.append('margin-inline-start:0px">')

            for block in children:
                process_content(html, block)
            html.append("</p>")
        else:
            html.append('<p class="empty-p"><br/></p>')

    elif type == "text":
        process_text(html, content)

    elif type == "heading":
        attrs = content["attrs"]
        level = str(attrs.get("level") or "3")

        html.append("<h")
        html.append(level)
        html.append(' style="text-align:')
        html.append(attrs.get("textAlign") or "left")
        html.append('">')
        html.append('<span style="')
        process_indentation(html, attrs)
        html.append('">')
        process_children(html, content)
        html.append("</span></h")
        html.append(level)
        html.append(">")

    elif type in ("listItem", "bulletList", "orderedList", "blockquote"):
        c = type[1]
        tag = (
            "li" if c == "i" else
            "ul" if c == "u" else
            "ol" if c == "r" else
            "blockquote"
        )
        html.append("<" + tag + ">")
        process_children(html, content)
        html.append("</" + tag + ">")

    elif type == "anchor":
        attrs = content["attrs"]
        html.append('<a id="')
        html.append(attrs.get("id") or "")
        html.append('" data-testid="anchor"></a>')

    elif type == "hardBreak":
        html.append("<br/><br/>")

    elif type == "horizontalRule":
        html.append("<hr/>")

    elif type == "da-deviation":
        process_deviation(html, content)

    elif type == "da-mention":
        user = content["attrs"]["user"]["username"]
        html.append('<a href="https://www.deviantart.com/')
        html.append(user.lower())
        html.append('" data-da-type="da-mention" data-user="">@<!-- -->')
        html.append(user)
        html.append('</a>')

    elif type == "da-gif":
        attrs = content["attrs"]
        width = str(attrs.get("width") or "")
        height = str(attrs.get("height") or "")
        url = text.escape(attrs.get("url") or "")

        html.append('<div data-da-type="da-gif" data-width="')
        html.append(width)
        html.append('" data-height="')
        html.append(height)
        html.append('" data-alignment="')
        html.append(attrs.get("alignment") or "")
        html.append('" data-url="')
        html.append(url)
        html.append('" class="t61qu"><video role="img" autoPlay="" '
                    'muted="" loop="" style="pointer-events:none" '
                    'controlsList="nofullscreen" playsInline="" '
                    'aria-label="gif" data-da-type="da-gif" width="')
        html.append(width)
        html.append('" height="')
        html.append(height)
        html.append('" src="')
        html.append(url)
        html.append('" class="_1Fkk6"></video></div>')

    elif type == "da-video":
        src = text.escape(content["attrs"].get("src") or "")
        html.append('<div data-testid="video" data-da-type="da-video" '
                    'data-src="')
        html.append(src)
        html.append('" class="_1Uxvs"><div data-canfs="yes" data-testid="v'
                    'ideo-inner" class="main-video" style="width:780px;hei'
                    'ght:438px"><div style="width:780px;height:438px">'
                    '<video src="')
        html.append(src)
        html.append('" style="width:100%;height:100%;" preload="auto" cont'
                    'rols=""></video></div></div></div>')

    else:
        import logging
        logging.getLogger("tiptap").warning(
            "Unsupported content type '%s'", type)


def process_text(html, content):
    if marks := content.get("marks"):
        close = []
        for mark in marks:
            type = mark["type"]
            if type == "link":
                attrs = mark.get("attrs") or {}
                html.append('<a href="')
                html.append(text.escape(attrs.get("href") or ""))
                if "target" in attrs:
                    html.append('" target="')
                    html.append(attrs["target"])
                html.append('" rel="')
                html.append(attrs.get("rel") or
                            "noopener noreferrer nofollow ugc")
                html.append('">')
                close.append("</a>")
            elif type == "bold":
                html.append("<strong>")
                close.append("</strong>")
            elif type == "italic":
                html.append("<em>")
                close.append("</em>")
            elif type == "underline":
                html.append("<u>")
                close.append("</u>")
            elif type == "strike":
                html.append("<s>")
                close.append("</s>")
            elif type == "textStyle" and len(mark) <= 1:
                pass
            else:
                import logging
                logging.getLogger("tiptap").warning(
                    "Unsupported text marker '%s'", type)
        close.reverse()
        html.append(text.escape(content["text"]))
        html.extend(close)
    else:
        html.append(text.escape(content["text"]))


def process_children(html, content):
    if children := content.get("content"):
        for block in children:
            process_content(html, block)


def process_indentation(html, attrs):
    itype = ("text-indent" if attrs.get("indentType") == "line" else
             "margin-inline-start")
    isize = str((attrs.get("indentation") or 0) * 24)
    html.append(itype + ":" + isize + "px")


def process_deviation(html, content):
    dev = content["attrs"]["deviation"]
    media = dev.get("media") or ()

    html.append('<div class="jjNX2">')
    html.append('<figure class="Qf-HY" data-da-type="da-deviation" '
                'data-deviation="" '
                'data-width="" data-link="" data-alignment="center">')

    if "baseUri" in media:
        url, formats = eclipse_media(media)
        full = formats["fullview"]

        html.append('<a href="')
        html.append(text.escape(dev["url"]))
        html.append('" class="_3ouD5" style="margin:0 auto;display:flex;'
                    'align-items:center;justify-content:center;'
                    'overflow:hidden;width:780px;height:')
        html.append(str(780 * full["h"] / full["w"]))
        html.append('px">')

        html.append('<img src="')
        html.append(text.escape(url))
        html.append('" alt="')
        html.append(text.escape(dev["title"]))
        html.append('" style="width:100%;max-width:100%;display:block"/>')
        html.append("</a>")

    elif "textContent" in dev:
        html.append('<div class="_32Hs4" style="width:350px">')

        html.append('<a href="')
        html.append(text.escape(dev["url"]))
        html.append('" class="_3ouD5">')

        html.append('''\
<section class="Q91qI aG7Yi" style="width:350px;height:313px">\
<div class="_16ECM _1xMkk" aria-hidden="true">\
<svg height="100%" viewBox="0 0 15 12" preserveAspectRatio="xMidYMin slice" \
fill-rule="evenodd">\
<linearGradient x1="87.8481761%" y1="16.3690766%" \
x2="45.4107524%" y2="71.4898596%" id="app-root-3">\
<stop stop-color="#00FF62" offset="0%"></stop>\
<stop stop-color="#3197EF" stop-opacity="0" offset="100%"></stop>\
</linearGradient>\
<text class="_2uqbc" fill="url(#app-root-3)" text-anchor="end" x="15" y="11">J\
</text></svg></div><div class="_1xz9u">Literature</div><h3 class="_2WvKD">\
''')
        html.append(text.escape(dev["title"]))
        html.append('</h3><div class="_2CPLm">')
        html.append(text.escape(dev["textContent"]["excerpt"]))
        html.append('</div></section></a></div>')

    html.append('</figure></div>')

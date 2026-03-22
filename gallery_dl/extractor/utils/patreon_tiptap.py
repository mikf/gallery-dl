# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util


def to_html(markup):
    html = []

    data = util.json_loads(markup)
    for block in data["content"]:
        process_content(html, block)

    return "".join(html)


def process_content(html, content):
    type = content["type"]

    if type == "paragraph":
        if children := content.get("content"):
            html.append('<p>')
            for block in children:
                process_content(html, block)
            html.append("</p>")
        else:
            html.append("<p></p>")

    elif type == "text":
        process_text(html, content)

    elif type == "heading":
        if attrs := content.get("attrs"):
            level = str(attrs.get("level") or "3")
        else:
            level = "3"
        html.append(f"<h{level}>")
        process_children(html, content)
        html.append(f"</h{level}>")

    elif type in {"listItem", "bulletList", "orderedList", "blockquote"}:
        c = type[1]
        tag = (
            "li" if c == "i" else
            "ul" if c == "u" else
            "ol" if c == "r" else
            "blockquote"
        )
        html.append(f"<{tag}>")
        process_children(html, content)
        html.append(f"</{tag}>")

    elif type == "image":
        if (attrs := content.get("attrs")) and (src := attrs.get("src")):
            html.append('<div data-image-container="true"')
            if align := attrs.get("alignment"):
                html.append(f' data-alignment="{text.escape(align)}"')
            html.append(f'><figure><img src="{text.escape(src)}"')
            if mid := attrs.get("media_id"):
                html.append(f' data-media-id="{text.escape(mid)}"')
            html.append('/></figure></div>')

    elif type == "link":
        if (attrs := content.get("attrs")) and (href := attrs.get("href")):
            html.append(f'<a href="{text.escape(href)}">')
            process_children(html, content)
            html.append("</a>")

    elif type == "hardBreak":
        html.append("<br/>")

    elif type == "horizontalRule":
        html.append("<hr/>")

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
                html.append('"')
                if "target" in attrs:
                    html.append(f' target="{attrs["target"]}"')
                if "rel" in attrs:
                    html.append(f' rel="{attrs["rel"]}"')
                html.append(">")
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
    html.append(f"{itype}:{isize}px")

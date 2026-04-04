# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Twitter article utilities"""

from ... import text


def to_document(article, content=None):
    title = text.escape(article["title"])
    cover = article["cover_media"]["media_info"]

    html = [f"""\
<!DOCTYPE html>
<html dir="ltr" lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{STYLESHEET}    </style>
    <title>{title}</title>
  </head>
  <body>
  <img src="{text.escape(media_url(cover["original_img_url"]))}" \
class="cover" alt="{title}">
  <h1>{title}</h1>

"""]
    html.extend(content or to_html(article))
    html.append("""\
  </body>
</html>
""")

    return html


def to_html(article):
    content = article["content_state"]
    entities = {
        entity["key"]: entity["value"]
        for entity in content["entityMap"]
    }
    media = {
        entity["media_id"]: entity["media_info"]
        for entity in article["media_entities"]
    }

    html = []
    index = 0
    blocks = content["blocks"]
    blocks_len = len(blocks)
    while index < blocks_len:
        index = process_block(html, blocks, index, entities, media)
    return html


def process_block(html, blocks, i, entities, media):
    block = blocks[i]
    type = block["type"]

    html.append(f'<section class="{type}" id="{block["key"]}">\n')
    if type == "unstyled":
        if ranges := block.get("entityRanges"):
            for range in ranges:
                process_entity(html, block, entities[str(range["key"])], media)
        process_text(html, block)
        html.append("\n")

    elif type == "atomic":
        if ranges := block.get("entityRanges"):
            for range in ranges:
                process_entity(html, block, entities[str(range["key"])], media)

    elif type.endswith("ordered-list-item"):
        html.append(f"<{type[0]}l>\n")
        while True:
            html.append("  <li>")
            process_text(html, block)
            html.append("</li>\n")

            try:
                block = blocks[i+1]
                if type != block["type"]:
                    break

            except Exception:
                break

            i += 1
        html.append(f"</{type[0]}l>\n")

    else:
        import logging
        logging.getLogger("twitter.article").warning(
            "Unsupported block type %r", type)

    html.append("</section>\n\n")
    return i + 1


def process_entity(html, block, entity, media):
    if entity is None:
        return
    type = entity["type"]

    if type == "MEDIA":
        data = entity["data"]
        medias = [media[m["mediaId"]] for m in data["mediaItems"]]
        for img in medias:
            src = text.escape(media_url(img["original_img_url"]))
            html.append(f'<img src="{src}">\n')
        if caption := data.get("caption"):
            html.append(
                f'<span class="caption">{text.escape(caption)}</span>\n')

    elif type == "DIVIDER":
        html.append("<hr>\n")

    elif type == "TWEMOJI":
        return

        txt = block["text"]
        r = block["entityRanges"][0]
        li = r["length"]
        ri = li + r["offset"]
        block["text"] = \
            f'{txt[:li]}<span class="emoji">{txt[li:ri]}</span>{txt[ri:]}'

    elif type == "LATEX":
        html.append(f"""\
<math xmlns="http://www.w3.org/1998/Math/MathML">
<semantics>
<annotation encoding="application/x-tex">\
{text.escape(block["text"])}</annotation>
</semantics>
</math>
""")

    else:
        import logging
        logging.getLogger("twitter.article").warning(
            "Unsupported entity type %r", type)


def process_text(html, block):
    txt = block["text"]
    if data := block.get("data"):
        if mentions := data.get("mentions"):
            for r in mentions:
                u = text.unescape(r["text"])
                txt = (f'{txt[:r["fromIndex"]]}'
                       f'<a href="https://x.com/@{u}">@{u}</a>'
                       f'{txt[r["toIndex"]:]}')
        if urls := data.get("urls"):
            for r in urls:
                u = text.unescape(r["text"])
                txt = (f'{txt[:r["fromIndex"]]}'
                       f'<a href="{u}">{u}</a>'
                       f'{txt[r["toIndex"]:]}')
    if ranges := block.get("inlineStyleRanges"):
        for r in ranges:
            el = r["style"][0].lower()
            li = r["length"]
            ri = li + r["offset"]
            txt = f'{txt[:li]}<{el}>{txt[li:ri]}</{el}>{txt[ri:]}'
    html.append(txt)


def media_url(url, name="orig"):
    if url[-4] == ".":
        base, _, fmt = url.rpartition(".")
        return f"{base}?format={fmt}&name={name}"
    return f"{url.rpartition('=')[0]}={name}"


LIST = None
STYLESHEET = """
body{
    width: 598px;
    border: 1px solid rgb(47, 51, 54);
    margin: 0 auto;
    padding: 1em;
    font-family:"TwitterChirpExtendedHeavy","Verdana",-apple-system,\
BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
body > section{
    text-align: center;
    font-size: 17px;
    line-height: 28px;
    margin-bottom: 28px;
}
body > section.unstyled{
    text-align: left;
}
ul, ol {
    list-style-position: outside;
    margin-bottom: 28px;
    margin-top: 0;
    padding: 0;
    overflow-wrap: break-word;
    text-align: left;
}
li {
    margin-bottom: 12px;
    margin-left: 30px;
}
.caption{
    display: block;
    font-size: 13px;
    text-align: left;
    color: rgb(145, 150, 154);
}
.emoji{padding: 0.15em;}
.cover{width: 100%;}
img{max-width: 100%;}
h1{font-size: 34px;}
a{color: rgb(231, 233, 234);}
a:hover{color: revert;}
math{display="block";}
"""

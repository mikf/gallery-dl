#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generate a Markdown document listing all supported sites"""

import os
import sys
import collections

import util
from gallery_dl import extractor

try:
    from test import results
except ImportError:
    results = None


CATEGORY_MAP = {
    "2chan"          : "Futaba Channel",
    "35photo"        : "35PHOTO",
    "adultempire"    : "Adult Empire",
    "agnph"          : "AGNPH",
    "allgirlbooru"   : "All girl",
    "ao3"            : "Archive of Our Own",
    "archivedmoe"    : "Archived.Moe",
    "archiveofsins"  : "Archive of Sins",
    "artstation"     : "ArtStation",
    "aryion"         : "Eka's Portal",
    "atfbooru"       : "ATFBooru",
    "azurlanewiki"   : "Azur Lane Wiki",
    "b4k"            : "arch.b4k.co",
    "baraag"         : "baraag",
    "batoto"         : "BATO.TO",
    "bbc"            : "BBC",
    "cien"           : "Ci-en",
    "cohost"         : "cohost!",
    "comicvine"      : "Comic Vine",
    "coomerparty"    : "Coomer",
    "deltaporno"     : "DeltaPorno",
    "deviantart"     : "DeviantArt",
    "drawfriends"    : "Draw Friends",
    "dynastyscans"   : "Dynasty Reader",
    "e621"           : "e621",
    "e926"           : "e926",
    "e6ai"           : "e6AI",
    "erome"          : "EroMe",
    "everia"         : "EVERIA.CLUB",
    "e-hentai"       : "E-Hentai",
    "exhentai"       : "ExHentai",
    "fallenangels"   : "Fallen Angels Scans",
    "fanbox"         : "pixivFANBOX",
    "fashionnova"    : "Fashion Nova",
    "furaffinity"    : "Fur Affinity",
    "hatenablog"     : "HatenaBlog",
    "hbrowse"        : "HBrowse",
    "hentai2read"    : "Hentai2Read",
    "hentaicosplay"  : "Hentai Cosplay",
    "hentaifoundry"  : "Hentai Foundry",
    "hentaifox"      : "HentaiFox",
    "hentaihand"     : "HentaiHand",
    "hentaihere"     : "HentaiHere",
    "hentaiimg"      : "Hentai Image",
    "hentainexus"    : "HentaiNexus",
    "hiperdex"       : "Hipertoon",
    "hitomi"         : "Hitomi.la",
    "horne"          : "horne",
    "idolcomplex"    : "Idol Complex",
    "illusioncardsbooru": "Illusion Game Cards",
    "imagebam"       : "ImageBam",
    "imagefap"       : "ImageFap",
    "imgbb"          : "ImgBB",
    "imgbox"         : "imgbox",
    "imagechest"     : "ImageChest",
    "imgkiwi"        : "IMG.Kiwi",
    "imgth"          : "imgth",
    "imgur"          : "imgur",
    "joyreactor"     : "JoyReactor",
    "itchio"         : "itch.io",
    "jpgfish"        : "JPG Fish",
    "kabeuchi"       : "かべうち",
    "kemonoparty"    : "Kemono",
    "koharu"         : "SchaleNetwork",
    "livedoor"       : "livedoor Blog",
    "lofter"         : "LOFTER",
    "ohpolly"        : "Oh Polly",
    "omgmiamiswimwear": "Omg Miami Swimwear",
    "mangadex"       : "MangaDex",
    "mangafox"       : "Manga Fox",
    "mangahere"      : "Manga Here",
    "mangakakalot"   : "MangaKakalot",
    "mangalife"      : "MangaLife",
    "manganelo"      : "Manganato",
    "mangapark"      : "MangaPark",
    "mangaread"      : "MangaRead",
    "mangasee"       : "MangaSee",
    "mariowiki"      : "Super Mario Wiki",
    "mastodon.social": "mastodon.social",
    "mediawiki"      : "MediaWiki",
    "micmicidol"     : "MIC MIC IDOL",
    "myhentaigallery": "My Hentai Gallery",
    "myportfolio"    : "Adobe Portfolio",
    "naverwebtoon"   : "NaverWebtoon",
    "nhentai"        : "nhentai",
    "nijie"          : "nijie",
    "nozomi"         : "Nozomi.la",
    "nsfwalbum"      : "NSFWalbum.com",
    "paheal"         : "rule #34",
    "photovogue"     : "PhotoVogue",
    "pidgiwiki"      : "PidgiWiki",
    "pixeldrain"     : "pixeldrain",
    "pornimage"      : "Porn Image",
    "pornpics"       : "PornPics.com",
    "pornreactor"    : "PornReactor",
    "readcomiconline": "Read Comic Online",
    "rbt"            : "RebeccaBlackTech",
    "redgifs"        : "RedGIFs",
    "rozenarcana"    : "Rozen Arcana",
    "rule34"         : "Rule 34",
    "rule34hentai"   : "Rule34Hentai",
    "rule34us"       : "Rule 34",
    "rule34vault"    : "R34 Vault",
    "rule34xyz"      : "Rule 34 XYZ",
    "sankaku"        : "Sankaku Channel",
    "sankakucomplex" : "Sankaku Complex",
    "seiga"          : "Niconico Seiga",
    "senmanga"       : "Sen Manga",
    "sensescans"     : "Sense-Scans",
    "sexcom"         : "Sex.com",
    "simplyhentai"   : "Simply Hentai",
    "slickpic"       : "SlickPic",
    "slideshare"     : "SlideShare",
    "smugmug"        : "SmugMug",
    "speakerdeck"    : "Speaker Deck",
    "steamgriddb"    : "SteamGridDB",
    "subscribestar"  : "SubscribeStar",
    "tbib"           : "The Big ImageBoard",
    "tcbscans"       : "TCB Scans",
    "tco"            : "Twitter t.co",
    "tmohentai"      : "TMOHentai",
    "thatpervert"    : "ThatPervert",
    "thebarchive"    : "The /b/ Archive",
    "thecollection"  : "The /co/llection",
    "tumblrgallery"  : "TumblrGallery",
    "vanillarock"    : "もえぴりあ",
    "vidyart2"       : "/v/idyart2",
    "vidyapics"      : "Vidya Booru",
    "vk"             : "VK",
    "vsco"           : "VSCO",
    "wallpapercave"  : "Wallpaper Cave",
    "webmshare"      : "webmshare",
    "webtoons"       : "Webtoon",
    "wikiart"        : "WikiArt.org",
    "wikigg"         : "wiki.gg",
    "wikimediacommons": "Wikimedia Commons",
    "xbunkr"         : "xBunkr",
    "xhamster"       : "xHamster",
    "xvideos"        : "XVideos",
    "yandere"        : "yande.re",
    "yiffverse"      : "Yiff verse",
}

SUBCATEGORY_MAP = {
    ""       : "",
    "art"    : "Art",
    "audio"  : "Audio",
    "doujin" : "Doujin",
    "home"   : "Home Feed",
    "image"  : "individual Images",
    "index"  : "Site Index",
    "info"   : "User Profile Information",
    "issue"  : "Comic Issues",
    "manga"  : "Manga",
    "media"  : "Media Files",
    "note"   : "Images from Notes",
    "popular": "Popular Images",
    "recent" : "Recent Images",
    "search" : "Search Results",
    "status" : "Images from Statuses",
    "tag"    : "Tag Searches",
    "tweets" : "",
    "user"   : "User Profiles",
    "watch"  : "Watches",
    "following"    : "Followed Users",
    "related-pin"  : "related Pins",
    "related-board": "",

    "ao3": {
        "user-works"   : "",
        "user-series"  : "",
        "user-bookmark": "Bookmarks",
    },
    "artstation": {
        "artwork": "Artwork Listings",
        "collections": "",
    },
    "bilibili": {
        "user-articles": "User Articles",
    },
    "bluesky": {
        "posts": "",
    },
    "boosty": {
        "feed": "Subscriptions Feed",
    },
    "civitai": {
        "models": "Model Listings",
        "images": "Image Listings",
        "user-models": "User Models",
        "user-images": "User Images",
        "user-posts" : "User Posts",
    },
    "coomerparty": {
        "discord"       : "",
        "discord-server": "",
        "posts"         : "",
    },
    "Danbooru": {
        "artist-search": "Artist Searches",
    },
    "desktopography": {
        "site": "",
    },
    "deviantart": {
        "gallery-search": "Gallery Searches",
        "stash" : "Sta.sh",
        "status": "Status Updates",
        "watch-posts": "",
    },
    "fanbox": {
        "supporting": "Supported User Feed",
        "redirect"  : "Pixiv Redirects",
    },
    "fapello": {
        "path": ["Videos", "Trending Posts", "Popular Videos", "Top Models"],
    },
    "furaffinity": {
        "submissions": "New Submissions",
    },
    "hatenablog": {
        "archive": "Archive",
        "entry"  : "Individual Posts",
    },
    "hentaifoundry": {
        "story": "",
    },
    "imgur": {
        "favorite-folder": "Favorites Folders",
    },
    "inkbunny": {
        "unread": "Unread Submissions",
    },
    "instagram": {
        "posts": "",
        "saved": "Saved Posts",
        "tagged": "Tagged Posts",
    },
    "kemonoparty": {
        "discord"       : "Discord Servers",
        "discord-server": "",
        "posts"         : "",
    },
    "lensdump": {
        "albums": "",
    },
    "lofter": {
        "blog-posts": "Blog Posts",
    },
    "mangadex": {
        "feed" : "Followed Feed",
    },
    "nijie": {
        "followed": "Followed Users",
        "nuita" : "Nuita History",
    },
    "pinterest": {
        "board": "",
        "pinit": "pin.it Links",
        "created": "Created Pins",
        "allpins": "All Pins",
    },
    "pixiv": {
        "me"  : "pixiv.me Links",
        "novel-bookmark": "Novel Bookmarks",
        "novel-series": "Novel Series",
        "novel-user": "",
        "pixivision": "pixivision",
        "sketch": "Sketch",
        "unlisted": "Unlisted Works",
        "work": "individual Images",
    },
    "poringa": {
        "post": "Posts Images",
    },
    "pornhub": {
        "gifs": "",
    },
    "raddle": {
        "usersubmissions": "User Profiles",
        "post"           : "Individual Posts",
        "shorturl"       : "",
    },
    "redgifs": {
        "collections": "",
    },
    "sankaku": {
        "books": "Book Searches",
    },
    "scrolller": {
        "following": "Followed Subreddits",
    },
    "sexcom": {
        "pins": "User Pins",
    },
    "skeb": {
        "following"      : "Followed Creators",
        "following-users": "Followed Users",
    },
    "smugmug": {
        "path": "Images from Users and Folders",
    },
    "steamgriddb": {
        "asset": "Individual Assets",
    },
    "tumblr": {
        "day": "Days",
    },
    "twitter": {
        "media": "Media Timelines",
        "tweets": "",
        "replies": "",
        "community": "",
        "list-members": "List Members",
    },
    "vk": {
        "tagged": "Tagged Photos",
    },
    "vsco": {
        "spaces": "",
    },
    "wallhaven": {
        "collections": "",
        "uploads"    : "",
    },
    "wallpapercave": {
        "image": ["individual Images", "Search Results"],
    },
    "weasyl": {
        "journals"   : "",
        "submissions": "",
    },
    "weibo": {
        "home": "",
        "newvideo": "",
    },
    "wikiart": {
        "artists": "Artist Listings",
    },
    "wikimedia": {
        "article": ["Articles", "Categories", "Files"],
    },
}

BASE_MAP = {
    "E621"        : "e621 Instances",
    "foolfuuka"   : "FoolFuuka 4chan Archives",
    "foolslide"   : "FoOlSlide Instances",
    "gelbooru_v01": "Gelbooru Beta 0.1.11",
    "gelbooru_v02": "Gelbooru Beta 0.2",
    "hentaicosplays": "Hentai Cosplay Instances",
    "jschan"      : "jschan Imageboards",
    "lolisafe"    : "lolisafe and chibisafe",
    "lynxchan"    : "LynxChan Imageboards",
    "moebooru"    : "Moebooru and MyImouto",
    "szurubooru"  : "szurubooru Instances",
    "urlshortener": "URL Shorteners",
    "vichan"      : "vichan Imageboards",
}

URL_MAP = {
    "blogspot" : "https://www.blogger.com/",
    "wikimedia": "https://www.wikimedia.org/",
}

_OAUTH = '<a href="https://github.com/mikf/gallery-dl#oauth">OAuth</a>'
_COOKIES = '<a href="https://github.com/mikf/gallery-dl#cookies">Cookies</a>'
_APIKEY_DB = ('<a href="https://gdl-org.github.io/docs/configuration.html'
              '#extractor-derpibooru-api-key">API Key</a>')
_APIKEY_WH = ('<a href="https://gdl-org.github.io/docs/configuration.html'
              '#extractor-wallhaven-api-key">API Key</a>')
_APIKEY_WY = ('<a href="https://gdl-org.github.io/docs/configuration.html'
              '#extractor-weasyl-api-key">API Key</a>')

AUTH_MAP = {
    "aibooru"        : "Supported",
    "ao3"            : "Supported",
    "aryion"         : "Supported",
    "atfbooru"       : "Supported",
    "baraag"         : _OAUTH,
    "bluesky"        : "Supported",
    "booruvar"       : "Supported",
    "boosty"         : _COOKIES,
    "coomerparty"    : "Supported",
    "danbooru"       : "Supported",
    "derpibooru"     : _APIKEY_DB,
    "deviantart"     : _OAUTH,
    "e621"           : "Supported",
    "e6ai"           : "Supported",
    "e926"           : "Supported",
    "e-hentai"       : "Supported",
    "exhentai"       : "Supported",
    "facebook"       : _COOKIES,
    "fanbox"         : _COOKIES,
    "fantia"         : _COOKIES,
    "flickr"         : _OAUTH,
    "furaffinity"    : _COOKIES,
    "furbooru"       : "API Key",
    "horne"          : "Required",
    "idolcomplex"    : "Supported",
    "imgbb"          : "Supported",
    "inkbunny"       : "Supported",
    "instagram"      : _COOKIES,
    "kemonoparty"    : "Supported",
    "mangadex"       : "Supported",
    "mangoxo"        : "Supported",
    "mastodon.social": _OAUTH,
    "newgrounds"     : "Supported",
    "nijie"          : "Required",
    "patreon"        : _COOKIES,
    "pawoo"          : _OAUTH,
    "pillowfort"     : "Supported",
    "pinterest"      : _COOKIES,
    "pixiv"          : _OAUTH,
    "ponybooru"      : "API Key",
    "reddit"         : _OAUTH,
    "sankaku"        : "Supported",
    "scrolller"      : "Supported",
    "seiga"          : "Supported",
    "smugmug"        : _OAUTH,
    "subscribestar"  : "Supported",
    "tapas"          : "Supported",
    "tsumino"        : "Supported",
    "tumblr"         : _OAUTH,
    "twitter"        : "Supported",
    "vipergirls"     : "Supported",
    "wallhaven"      : _APIKEY_WH,
    "weasyl"         : _APIKEY_WY,
    "zerochan"       : "Supported",
}

IGNORE_LIST = (
    "directlink",
    "oauth",
    "recursive",
    "test",
    "ytdl",
    "generic",
    "noop",
)


def domain(cls):
    """Return the domain name associated with an extractor class"""
    try:
        url = sys.modules[cls.__module__].__doc__.split()[-1]
        if url.startswith("http"):
            return url
    except Exception:
        pass

    if hasattr(cls, "root") and cls.root:
        return cls.root + "/"

    url = cls.example
    return url[:url.find("/", 8)+1]


def category_text(c):
    """Return a human-readable representation of a category"""
    return CATEGORY_MAP.get(c) or c.capitalize()


def subcategory_text(bc, c, sc):
    """Return a human-readable representation of a subcategory"""
    if c in SUBCATEGORY_MAP:
        scm = SUBCATEGORY_MAP[c]
        if sc in scm:
            txt = scm[sc]
            if not isinstance(txt, str):
                txt = ", ".join(txt)
            return txt

    if bc and bc in SUBCATEGORY_MAP:
        scm = SUBCATEGORY_MAP[bc]
        if sc in scm:
            txt = scm[sc]
            if not isinstance(txt, str):
                txt = ", ".join(txt)
            return txt

    if sc in SUBCATEGORY_MAP:
        return SUBCATEGORY_MAP[sc]

    sc = sc.capitalize()
    if sc.endswith("y"):
        sc = sc[:-1] + "ies"
    elif not sc.endswith("s"):
        sc += "s"
    return sc


def category_key(c):
    """Generate sorting keys by category"""
    return category_text(c[0]).lower()


def subcategory_key(sc):
    """Generate sorting keys by subcategory"""
    return "A" if sc == "issue" else sc


def build_extractor_list():
    """Generate a sorted list of lists of extractor classes"""
    categories = collections.defaultdict(lambda: collections.defaultdict(list))
    default = categories[""]
    domains = {"": ""}

    for extr in extractor._list_classes():
        category = extr.category
        if category in IGNORE_LIST:
            continue
        if category:
            default[category].append(extr.subcategory)
            if category not in domains:
                domains[category] = domain(extr)
        else:
            base = categories[extr.basecategory]
            if not extr.instances:
                base[""].append(extr.subcategory)
                continue
            for category, root, info in extr.instances:
                base[category].append(extr.subcategory)
                if category not in domains:
                    if not root:
                        if category in URL_MAP:
                            root = URL_MAP[category].rstrip("/")
                        elif results:
                            # use domain from first matching test
                            test = results.category(category)[0]
                            root = test["#class"].from_url(test["#url"]).root
                    domains[category] = root + "/"

    # sort subcategory lists
    for base in categories.values():
        for subcategories in base.values():
            subcategories.sort(key=subcategory_key)

    # add e-hentai.org
    default["e-hentai"] = default["exhentai"]
    domains["e-hentai"] = domains["exhentai"].replace("x", "-")

    # add coomer.party
    default["coomerparty"] = default["kemonoparty"]
    domains["coomerparty"] = domains["kemonoparty"].replace("kemono", "coomer")

    # add manga4life.com
    default["mangalife"] = default["mangasee"]
    domains["mangalife"] = "https://manga4life.com/"

    # add wikifeetx.com
    default["wikifeetx"] = default["wikifeet"]
    domains["wikifeetx"] = "https://www.wikifeetx.com/"

    return categories, domains


# define table columns
COLUMNS = (
    ("Site", 20,
     lambda bc, c, scs, d: category_text(c)),
    ("URL" , 35,
     lambda bc, c, scs, d: d),
    ("Capabilities", 50,
     lambda bc, c, scs, d: ", ".join(subcategory_text(bc, c, sc) for sc in scs
                                     if subcategory_text(bc, c, sc))),
    ("Authentication", 16,
     lambda bc, c, scs, d: AUTH_MAP.get(c, "")),
)


def generate_output(columns, categories, domains):

    thead = []
    append = thead.append
    append("<tr>")
    for column in columns:
        append("    <th>" + column[0] + "</th>")
    append("</tr>")

    tbody = []
    append = tbody.append

    for bcat, base in categories.items():

        if bcat and base:
            name = BASE_MAP.get(bcat) or (bcat.capitalize() + " Instances")
            append('\n<tr>\n    <td colspan="4"><strong>' +
                   name + '</strong></td>\n</tr>')
            clist = base.items()
        else:
            clist = sorted(base.items(), key=category_key)

        for category, subcategories in clist:
            append("<tr>")
            for column in columns:
                domain = domains[category]
                content = column[2](bcat, category, subcategories, domain)
                append("    <td>" + content + "</td>")
            append("</tr>")

    TEMPLATE = """# Supported Sites

<!-- auto-generated by {} -->
Consider all listed sites to potentially be NSFW.

<table>
<thead valign="bottom">
{}
</thead>
<tbody valign="top">
{}
</tbody>
</table>
"""
    return TEMPLATE.format(
        "/".join(os.path.normpath(__file__).split(os.sep)[-2:]),
        "\n".join(thead),
        "\n".join(tbody),
    )


categories, domains = build_extractor_list()
PATH = (sys.argv[1] if len(sys.argv) > 1 else
        util.path("docs", "supportedsites.md"))
with util.lazy(PATH) as fp:
    fp.write(generate_output(COLUMNS, categories, domains))

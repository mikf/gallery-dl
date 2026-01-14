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
    "ahottie"        : "AHottie",
    "aibooru"        : "AIBooru",
    "allgirlbooru"   : "All girl",
    "ao3"            : "Archive of Our Own",
    "archivedmoe"    : "Archived.Moe",
    "archiveofsins"  : "Archive of Sins",
    "arena"          : "Are.na",
    "artstation"     : "ArtStation",
    "aryion"         : "Eka's Portal",
    "atfbooru"       : "ATFBooru",
    "atfforum"       : "All The Fallen",
    "azurlanewiki"   : "Azur Lane Wiki",
    "b4k"            : "arch.b4k.dev",
    "baraag"         : "baraag",
    "batoto"         : "BATO.TO",
    "bbc"            : "BBC",
    "booth"          : "BOOTH",
    "cfake"          : "Celebrity Fakes",
    "cien"           : "Ci-en",
    "cohost"         : "cohost!",
    "comedywildlifephoto": "Comedy Wildlife Photography Awards",
    "comicvine"      : "Comic Vine",
    "cyberfile"      : "CyberFile",
    "dankefuerslesen": "Danke fürs Lesen",
    "deviantart"     : "DeviantArt",
    "drawfriends"    : "Draw Friends",
    "dynastyscans"   : "Dynasty Reader",
    "e621"           : "e621",
    "e926"           : "e926",
    "e6ai"           : "e6AI",
    "erome"          : "EroMe",
    "eporner"        : "EPORNER",
    "everia"         : "EVERIA.CLUB",
    "e-hentai"       : "E-Hentai",
    "exhentai"       : "ExHentai",
    "fallenangels"   : "Fallen Angels Scans",
    "fanbox"         : "pixivFANBOX",
    "fappic"         : "Fappic.com",
    "fashionnova"    : "Fashion Nova",
    "fikfap"         : "FikFap",
    "fitnakedgirls"  : "FitNakedGirls",
    "furaffinity"    : "Fur Affinity",
    "furry34"        : "Furry 34 com",
    "girlswithmuscle": "Girls with Muscle",
    "hatenablog"     : "HatenaBlog",
    "hbrowse"        : "HBrowse",
    "hdoujin"        : "HDoujin Galleries",
    "hentai2read"    : "Hentai2Read",
    "hentaicosplay"  : "Hentai Cosplay",
    "hentaienvy"     : "HentaiEnvy",
    "hentaiera"      : "HentaiEra",
    "hentaifoundry"  : "Hentai Foundry",
    "hentaifox"      : "HentaiFox",
    "hentaihand"     : "HentaiHand",
    "hentaihere"     : "HentaiHere",
    "hentaiimg"      : "Hentai Image",
    "hentainexus"    : "HentaiNexus",
    "hentairox"      : "HentaiRox",
    "hentaizap"      : "HentaiZap",
    "hiperdex"       : "HiperDEX",
    "hitomi"         : "Hitomi.la",
    "horne"          : "horne",
    "idolcomplex"    : "Idol Complex",
    "illusioncardsbooru": "Illusion Game Cards",
    "imagebam"       : "ImageBam",
    "imagefap"       : "ImageFap",
    "imagepond"      : "ImagePond",
    "imagetwist"     : "ImageTwist",
    "imgadult"       : "ImgAdult",
    "imgbb"          : "ImgBB",
    "imgbox"         : "imgbox",
    "imagechest"     : "ImageChest",
    "imgdrive"       : "ImgDrive.net",
    "imgkiwi"        : "IMG.Kiwi",
    "imglike"        : "Nude Celeb",
    "imgpile"        : "imgpile",
    "imgpv"          : "IMGPV",
    "imgtaxi"        : "ImgTaxi.com",
    "imgth"          : "imgth",
    "imgur"          : "imgur",
    "imgwallet"      : "ImgWallet.com",
    "imhentai"       : "IMHentai",
    "imxto"          : "IMX.to",
    "joyreactor"     : "JoyReactor",
    "itchio"         : "itch.io",
    "jpgfish"        : "JPG Fish",
    "kabeuchi"       : "かべうち",
    "mangafire"      : "MangaFire",
    "mangareader"    : "MangaReader",
    "mangataro"      : "MangaTaro",
    "s3ndpics"       : "S3ND",
    "schalenetwork"  : "Schale Network",
    "leakgallery"    : "Leak Gallery",
    "livedoor"       : "livedoor Blog",
    "lofter"         : "LOFTER",
    "ohpolly"        : "Oh Polly",
    "omgmiamiswimwear": "Omg Miami Swimwear",
    "mangadex"       : "MangaDex",
    "mangafox"       : "Manga Fox",
    "mangahere"      : "Manga Here",
    "mangakakalot"   : "MangaKakalot",
    "manganato"      : "MangaNato",
    "mangapark"      : "MangaPark",
    "mangaread"      : "MangaRead",
    "mariowiki"      : "Super Mario Wiki",
    "mastodon.social": "mastodon.social",
    "mediawiki"      : "MediaWiki",
    "micmicidol"     : "MIC MIC IDOL",
    "myhentaigallery": "My Hentai Gallery",
    "myportfolio"    : "Adobe Portfolio",
    "natomanga"      : "MangaNato",
    "naver-blog"     : "Naver Blog",
    "naver-chzzk"    : "CHZZK",
    "naver-webtoon"  : "Naver Webtoon",
    "nelomanga"      : "MangaNelo",
    "nhentai"        : "nhentai",
    "nijie"          : "nijie",
    "nozomi"         : "Nozomi.la",
    "nozrip"         : "GaryC Booru",
    "nsfwalbum"      : "NSFWalbum.com",
    "nudostar"       : "NudoStar.TV",
    "nudostarforum"  : "NudoStar Forums",
    "okporn"         : "OK.PORN",
    "paheal"         : "Rule 34",
    "photovogue"     : "PhotoVogue",
    "picstate"       : "PicState",
    "pidgiwiki"      : "PidgiWiki",
    "pixeldrain"     : "pixeldrain",
    "pixhost"        : "PiXhost",
    "pixiv"          : "[pixiv]",
    "pixiv-novel"    : "[pixiv] Novels",
    "pornimage"      : "Porn Image",
    "pornpics"       : "PornPics.com",
    "pornreactor"    : "PornReactor",
    "pornstarstube"  : "PORNSTARS.TUBE",
    "postimg"        : "Postimages",
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
    "silverpic"      : "SilverPic.com",
    "simpcity"       : "SimpCity Forums",
    "simplyhentai"   : "Simply Hentai",
    "sizebooru"      : "Size Booru",
    "slickpic"       : "SlickPic",
    "slideshare"     : "SlideShare",
    "smugmug"        : "SmugMug",
    "speakerdeck"    : "Speaker Deck",
    "steamgriddb"    : "SteamGridDB",
    "subscribestar"  : "SubscribeStar",
    "tbib"           : "The Big ImageBoard",
    "tcbscans"       : "TCB Scans",
    "tco"            : "Twitter t.co",
    "thatpervert"    : "ThatPervert",
    "thebarchive"    : "The /b/ Archive",
    "thecollection"  : "The /co/llection",
    "thecollectionS" : "The /co/llection",
    "thefap"         : "TheFap",
    "thehentaiworld" : "The Hentai World",
    "tiktok"         : "TikTok",
    "tmohentai"      : "TMOHentai",
    "tumblrgallery"  : "TumblrGallery",
    "turboimagehost" : "TurboImageHost.com",
    "turbovid"       : "turbovid.cr",
    "vanillarock"    : "もえぴりあ",
    "vidyart2"       : "/v/idyart2",
    "vidyapics"      : "Vidya Booru",
    "vipr"           : "Vipr.im",
    "visuabusters"   : "VISUABUSTERS",
    "vk"             : "VK",
    "vsco"           : "VSCO",
    "wallpapercave"  : "Wallpaper Cave",
    "webmshare"      : "webmshare",
    "webtoons"       : "WEBTOON",
    "weebcentral"    : "Weeb Central",
    "weebdex"        : "WeebDex",
    "wikiart"        : "WikiArt.org",
    "wikigg"         : "wiki.gg",
    "wikimediacommons": "Wikimedia Commons",
    "xbunkr"         : "xBunkr",
    "xhamster"       : "xHamster",
    "xvideos"        : "XVideos",
    "yandere"        : "yande.re",
    "yiffverse"      : "Yiff verse",
    "yourlesbians"   : "YourLesbians",
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
    "popular": "Popular Images",
    "recent" : "Recent Images",
    "saved"  : "Saved Posts",
    "search" : "Search Results",
    "status" : "Images from Statuses",
    "tag"    : "Tag Searches",
    "tweets" : "",
    "user"   : "User Profiles",
    "watch"  : "Watches",
    "direct-messages": "DMs",
    "following"      : "Followed Users",
    "related-pin"    : "related Pins",
    "related-board"  : "",

    "arcalive": {
        "user": "User Posts",
    },
    "artstation": {
        "artwork": "Artwork Listings",
        "collections": "",
    },
    "audiochan": {
        "audio": "Audios",
    },
    "bilibili": {
        "user-articles-favorite": "User Article Favorites",
    },
    "bluesky": {
        "posts": "",
    },
    "boosty": {
        "feed": "Subscriptions Feed",
    },
    "booth": {
        "category": "Item Categories",
    },
    "cfake": {
        "created": "Created",
    },
    "civitai": {
        "models": "Model Listings",
        "images": "Image Listings",
        "videos": "Video Listings",
        "posts" : "Post Listings",
        "search-models": "Model Searches",
        "search-images": "Image Searches",
        "user-images": ("User Images", "Image Reactions"),
        "user-videos": ("User Videos", "Video Reactions"),
        "generated": "Generated Files",
    },
    "coomer": {
        "discord"       : "",
        "discord-server": "",
        "posts"         : "",
    },
    "cyberfile": {
        "shared": "Shares",
    },
    "Danbooru": {
        "favgroup": "Favorite Groups",
        "random"  : "Random Posts",
    },
    "desktopography": {
        "site": "",
    },
    "deviantart": {
        "stash" : "Sta.sh",
        "status": "Status Updates",
        "watch-posts": "",
    },
    "discord": {
        "direct-message" : "",
    },
    "facebook": {
        "photos" : "Profile Photos",
    },
    "fanbox": {
        "supporting": "Supported User Feed",
        "redirect"  : "Pixiv Redirects",
    },
    "fansly": {
        "lists": "Account Lists",
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
        "me": "Personal Posts",
    },
    "inkbunny": {
        "unread": "Unread Submissions",
    },
    "instagram": {
        "posts": "",
        "tagged": "Tagged Posts",
        "stories-tray": "Stories Home Tray",
    },
    "itaku": {
        "posts": "",
    },
    "kemono": {
        "discord"       : "Discord Servers",
        "discord-server": "",
        "posts"         : "",
    },
    "koofr": {
        "shared": "Shared Links",
    },
    "leakgallery": {
        "trending" : "Trending Medias",
        "mostliked": "Most Liked Posts",
    },
    "lensdump": {
        "albums": "",
    },
    "mangadex": {
        "feed": "Updates Feed",
        "following" : "Library",
        "list": "MDLists",
    },
    "misskey": {
        "notes": "User Notes",
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
    "pixeldrain": {
        "folder": "Filesystems",
    },
    "pixiv": {
        "me"  : "pixiv.me Links",
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
        "feed": "Feed",
    },
    "sizebooru": {
        "user": "User Uploads",
    },
    "skeb": {
        "following"      : "Followed Creators",
        "following-users": "Followed Users",
        "sentrequests"   : "Sent Requests",
    },
    "smugmug": {
        "path": "Images from Users and Folders",
    },
    "steamgriddb": {
        "asset": "Individual Assets",
    },
    "tiktok": {
        "posts": "User Posts",
        "vmpost": "VM Posts",
        "following": "Followed Users (Stories Only)",
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
        "wall-post": "individual Wall Posts",
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
    "xenforo": {
        "media-user": "User Media",
        "media-item": "Media Files",
        "media-category": "Media Categories",
    },
}

BASE_MAP = {
    "E621"        : "e621 Instances",
    "foolfuuka"   : "FoolFuuka 4chan Archives",
    "foolslide"   : "FoOlSlide Instances",
    "gelbooru_v01": "Gelbooru Beta 0.1.11",
    "gelbooru_v02": "Gelbooru Beta 0.2",
    "hentaicosplays": "Hentai Cosplay Instances",
    "imagehost"   : "Image Hosting Sites",
    "IMHentai"    : "IMHentai and Mirror Sites",
    "jschan"      : "jschan Imageboards",
    "lolisafe"    : "lolisafe and chibisafe",
    "lynxchan"    : "LynxChan Imageboards",
    "manganelo"   : "MangaNelo and Mirror Sites",
    "moebooru"    : "Moebooru and MyImouto",
    "szurubooru"  : "szurubooru Instances",
    "urlshortener": "URL Shorteners",
    "vichan"      : "vichan Imageboards",
    "xenforo"     : "XenForo Forums",
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
    "coomer"         : "Supported",
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
    "girlswithmuscle": "Supported",
    "horne"          : "Required",
    "idolcomplex"    : "Supported",
    "imgbb"          : "Supported",
    "inkbunny"       : "Supported",
    "instagram"      : _COOKIES,
    "iwara"          : "Supported",
    "kemono"         : "Supported",
    "madokami"       : "Required",
    "mangadex"       : "Supported",
    "mangoxo"        : "Supported",
    "mastodon.social": _OAUTH,
    "newgrounds"     : "Supported",
    "nijie"          : "Required",
    "nudostarforum"  : "Supported",
    "patreon"        : _COOKIES,
    "pawoo"          : _OAUTH,
    "pillowfort"     : "Supported",
    "pinterest"      : _COOKIES,
    "pixiv"          : _OAUTH,
    "pixiv-novel"    : _OAUTH,
    "poipiku"        : _COOKIES,
    "ponybooru"      : "API Key",
    "reddit"         : _OAUTH,
    "rule34xyz"      : "Supported",
    "sankaku"        : "Supported",
    "scrolller"      : "Supported",
    "seiga"          : "Supported",
    "simpcity"       : "Supported",
    "smugmug"        : _OAUTH,
    "subscribestar"  : "Supported",
    "tapas"          : "Supported",
    "tiktok"         : _COOKIES,
    "tsumino"        : "Supported",
    "tumblr"         : _OAUTH,
    "twitter"        : _COOKIES,
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

    if "-" in sc:
        sc = " ".join(s.capitalize() for s in sc.split("-"))
    else:
        sc = sc.capitalize()

    if sc.endswith("y"):
        sc = f"{sc[:-1]}ies"
    elif sc.endswith("h"):
        sc = f"{sc}es"
    elif not sc.endswith("s") and not sc.endswith("edia"):
        sc = f"{sc}s"
    return sc


def category_key(c):
    """Generate sorting keys by category"""
    return category_text(c[0]).lower().lstrip("[")


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
            if extr.basecategory == "imagehost":
                base = categories[extr.basecategory]
            else:
                base = default
            base[category].append(extr.subcategory)
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

    domains["pixiv-novel"] += "novel"

    # add e-hentai.org
    default["e-hentai"] = default["exhentai"]
    domains["e-hentai"] = domains["exhentai"].replace("x", "-")

    # add coomer.st
    default["coomer"] = default["kemono"]
    domains["coomer"] = "https://coomer.st/"

    # add wikifeetx.com
    default["wikifeetx"] = default["wikifeet"]
    domains["wikifeetx"] = "https://www.wikifeetx.com/"

    # turbovid
    default["turbovid"] = default["saint"]
    domains["turbovid"] = "https://turbovid.cr/"
    domains["saint"] = "https://saint2.su/"

    # imgdrive / imgtaxi / imgwallet
    base = categories["imagehost"]
    base["imgtaxi"] = base["imgdrive"]
    base["imgwallet"] = base["imgdrive"]
    categories["imagehost"] = {k: base[k] for k in sorted(base)}
    domains["postimg"] = "https://postimages.org/"
    domains["imgtaxi"] = "https://imgtaxi.com/"
    domains["imgwallet"] = "https://imgwallet.com/"

    # add extra e621 extractors
    categories["E621"]["e621"].extend(default.pop("e621", ()))

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
    thead.append("<tr>")
    for column in columns:
        thead.append(f"    <th>{column[0]}</th>")
    thead.append("</tr>")

    tbody = []
    for bcat, base in categories.items():
        if bcat and base:
            name = BASE_MAP.get(bcat) or (bcat.capitalize() + " Instances")
            tbody.append(f"""
<tr id="{bcat}" title="{bcat}">
    <td colspan="4"><strong>{name}</strong></td>
</tr>\
""")
            clist = base.items()
        else:
            clist = sorted(base.items(), key=category_key)

        for category, subcategories in clist:
            tbody.append(f"""<tr id="{category}" title="{category}">""")
            for column in columns:
                domain = domains[category]
                content = column[2](bcat, category, subcategories, domain)
                tbody.append(f"    <td>{content}</td>")
            tbody.append("</tr>")

    NL = "\n"
    GENERATOR = "/".join(os.path.normpath(__file__).split(os.sep)[-2:])
    return f"""\
# Supported Sites

<!-- auto-generated by {GENERATOR} -->
Consider all listed sites to potentially be NSFW.

<table>
<thead valign="bottom">
{NL.join(thead)}
</thead>
<tbody valign="top">
{NL.join(tbody)}
</tbody>
</table>
"""


def main(path=None):
    categories, domains = build_extractor_list()

    if path is None:
        path = util.path("docs", "supportedsites.md")
    with util.lazy(path) as fp:
        fp.write(generate_output(COLUMNS, categories, domains))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

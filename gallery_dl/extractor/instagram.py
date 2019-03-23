# -*- coding: utf-8 -*-

# Copyright 2018-2019 Leonardo Taccari, Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.instagram.com/"""

import hashlib
import json
from .common import Extractor, Message
from .. import text


class InstagramExtractor(Extractor):
    """Base class for instagram extractors"""
    category = "instagram"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{media_id}.{extension}"
    archive_fmt = "{media_id}"
    root = "https://www.instagram.com"

    def items(self):
        yield Message.Version, 1

        for data in self.instagrams():
            yield Message.Directory, data

            if data['typename'] == 'GraphImage':
                yield Message.Url, data['display_url'], \
                    text.nameext_from_url(data['display_url'], data)
            elif data['typename'] == 'GraphVideo':
                yield Message.Url, \
                    'ytdl:{}/p/{}/'.format(self.root, data['shortcode']), data

    def _extract_shared_data(self, page):
        return json.loads(text.extract(page,
                          'window._sharedData = ', ';</script>')[0])

    def _extract_postpage(self, url):
        page = self.request(url).text
        shared_data = self._extract_shared_data(page)
        media = shared_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']

        common = {
            'comments': text.parse_int(media['edge_media_to_comment']['count']),
            'likes': text.parse_int(media['edge_media_preview_like']['count']),
            'owner_id': media['owner']['id'],
            'username': media['owner']['username'],
            'fullname': media['owner']['full_name'],
        }

        medias = []
        if media['__typename'] == 'GraphSidecar':
            for n in media['edge_sidecar_to_children']['edges']:
                children = n['node']
                medias.append({
                    'media_id': children['id'],
                    'shortcode': children['shortcode'],
                    'typename': children['__typename'],
                    'display_url': children['display_url'],
                    'height': text.parse_int(children['dimensions']['height']),
                    'width': text.parse_int(children['dimensions']['width']),
                    'sidecar_media_id': media['id'],
                    'sidecar_shortcode': media['shortcode'],
                    **common,
                })
        else:
            medias.append({
                'media_id': media['id'],
                'shortcode': media['shortcode'],
                'typename': media['__typename'],
                'display_url': media['display_url'],
                'height': text.parse_int(media['dimensions']['height']),
                'width': text.parse_int(media['dimensions']['width']),
                **common,
            })

        return medias

    def _extract_profilepage(self, url):
        page = self.request(url).text
        shared_data = self._extract_shared_data(page)

        while True:
            # Deal with different structure of profile pages: the first page
            # has interesting data in `entry_data', next pages in `data'.
            if 'entry_data' in shared_data:
                base_shared_data = shared_data['entry_data']['ProfilePage'][0]['graphql']

                # `rhx_gis' and `user_id' are available only in the first page
                rhx_gis = shared_data['rhx_gis']
                user_id = base_shared_data['user']['id']
            else:
                base_shared_data = shared_data['data']

            timeline = base_shared_data['user']['edge_owner_to_timeline_media']
            has_next_page = timeline['page_info']['has_next_page']
            shortcodes = [n['node']['shortcode'] for n in timeline['edges']]

            for s in shortcodes:
                url = '{}/p/{}/'.format(self.root, s)
                for p in self._extract_postpage(url):
                    yield p

            if not has_next_page:
                break

            end_cursor = timeline['page_info']['end_cursor']
            variables = '{{"id":"{}","first":12,"after":"{}"}}'.format(
                user_id,
                end_cursor,
            )
            xigis = '{}:{}'.format(rhx_gis, variables)
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "X-Instagram-GIS": hashlib.md5(xigis.encode()).hexdigest(),
            }
            url = '{}/graphql/query/?query_hash={}&variables={}'.format(
                self.root,
                '66eb9403e44cc12e5b5ecda48b667d41',
                variables,
            )
            shared_data = self.request(url, headers=headers).json()


class InstagramImageExtractor(InstagramExtractor):
    """Extractor for PostPage"""
    subcategory = "image"
    pattern = r"(?:https?://)?(?:www\.)?instagram\.com/p/([^/?&#]+)"
    test = (
        # GraphImage
        ("https://www.instagram.com/p/BqvsDleB3lV/", {
            "pattern": r"https://[^/]+\.(cdninstagram\.com|fbcdn\.net)"
                       r"/vp/[0-9a-f]+/[0-9A-F]+/t51.2885-15/e35"
                       r"/44877605_725955034447492_3123079845831750529_n.jpg",
            "keyword": {
                "comments": int,
                "height": int,
                "likes": int,
                "media_id": "1922949326347663701",
                "shortcode": "BqvsDleB3lV",
                "typename": "GraphImage",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphSidecar
        ("https://www.instagram.com/p/BoHk1haB5tM/", {
            "count": 5,
            "keyword": {
                "sidecar_media_id": "1875629777499953996",
                "sidecar_shortcode": "BoHk1haB5tM",
                "comments": int,
                "likes": int,
                "username": "instagram",
            }
        }),

        # GraphVideo
        ("https://www.instagram.com/p/Bqxp0VSBgJg/", {
            "url": "8f38c1cf460c9804842f7306c487410f33f82e7e",
            "keyword": {
                "comments": int,
                "height": int,
                "likes": int,
                "media_id": "1923502432034620000",
                "shortcode": "Bqxp0VSBgJg",
                "typename": "GraphVideo",
                "username": "instagram",
                "width": int,
            }
        }),
    )

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.shortcode = match.group(1)

    def instagrams(self):
        url = '{}/p/{}/'.format(self.root, self.shortcode)
        return self._extract_postpage(url)


class InstagramUserExtractor(InstagramExtractor):
    """Extractor for ProfilePage"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?!p/|explore/|directory/|accounts/)([^/?&#]+)")
    test = ("https://www.instagram.com/instagram/", {
        "range": "1-12",
        "count": ">= 12",
    })

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.username = match.group(1)

    def instagrams(self):
        url = '{}/{}/'.format(self.root, self.username)
        return self._extract_profilepage(url)

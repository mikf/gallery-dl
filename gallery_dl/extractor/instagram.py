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
    filename_fmt = "{sidecar_media_id:?/_/}{media_id}.{extension}"
    archive_fmt = "{media_id}"
    root = "https://www.instagram.com"

    def get_metadata(self):
        return {}

    def items(self):
        yield Message.Version, 1

        metadata = self.get_metadata()
        for data in self.instagrams():
            data.update(metadata)
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
            'date': text.parse_timestamp(media['taken_at_timestamp']),
            'likes': text.parse_int(media['edge_media_preview_like']['count']),
            'owner_id': media['owner']['id'],
            'username': media['owner']['username'],
            'fullname': media['owner']['full_name'],
        }

        medias = []
        if media['__typename'] == 'GraphSidecar':
            yi = 0
            for n in media['edge_sidecar_to_children']['edges']:
                children = n['node']
                media_data = {
                    'media_id': children['id'],
                    'shortcode': children['shortcode'],
                    'typename': children['__typename'],
                    'display_url': children['display_url'],
                    'height': text.parse_int(children['dimensions']['height']),
                    'width': text.parse_int(children['dimensions']['width']),
                    'sidecar_media_id': media['id'],
                    'sidecar_shortcode': media['shortcode'],
                }
                if children['__typename'] == 'GraphVideo':
                    media_data["_ytdl_index"] = yi
                    yi += 1
                media_data.update(common)
                medias.append(media_data)

        else:
            media_data = {
                'media_id': media['id'],
                'shortcode': media['shortcode'],
                'typename': media['__typename'],
                'display_url': media['display_url'],
                'height': text.parse_int(media['dimensions']['height']),
                'width': text.parse_int(media['dimensions']['width']),
            }
            media_data.update(common)
            medias.append(media_data)

        return medias

    def _extract_page(self, url, page_type):
        shared_data_fields = {
            'ProfilePage': {
                'node': 'user',
                'node_id': 'id',
                'edge_to_medias': 'edge_owner_to_timeline_media',
                'variables_id': 'id',
                'query_hash': '66eb9403e44cc12e5b5ecda48b667d41',
            },
            'TagPage': {
                'node': 'hashtag',
                'node_id': 'name',
                'edge_to_medias': 'edge_hashtag_to_media',
                'variables_id': 'tag_name',
                'query_hash': 'f92f56d47dc7a55b606908374b43a314',
            },
        }

        page = self.request(url).text
        shared_data = self._extract_shared_data(page)
        psdf = shared_data_fields[page_type]

        while True:
            # Deal with different structure of pages: the first page
            # has interesting data in `entry_data', next pages in `data'.
            if 'entry_data' in shared_data:
                base_shared_data = shared_data['entry_data'][page_type][0]['graphql']

                # variables_id is available only in the first page
                variables_id = base_shared_data[psdf['node']][psdf['node_id']]
            else:
                base_shared_data = shared_data['data']

            medias = base_shared_data[psdf['node']][psdf['edge_to_medias']]
            has_next_page = medias['page_info']['has_next_page']
            shortcodes = [n['node']['shortcode'] for n in medias['edges']]

            for s in shortcodes:
                url = '{}/p/{}/'.format(self.root, s)
                yield from self._extract_postpage(url)

            if not has_next_page:
                break

            end_cursor = medias['page_info']['end_cursor']
            variables = '{{"{}":"{}","first":12,"after":"{}"}}'.format(
                psdf['variables_id'],
                variables_id,
                end_cursor,
            )
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "X-Instagram-GIS": hashlib.md5(variables.encode()).hexdigest(),
            }
            url = '{}/graphql/query/?query_hash={}&variables={}'.format(
                self.root,
                psdf['query_hash'],
                variables,
            )
            shared_data = self.request(url, headers=headers).json()

    def _extract_profilepage(self, url):
        yield from self._extract_page(url, 'ProfilePage')

    def _extract_tagpage(self, url):
        yield from self._extract_page(url, 'TagPage')


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
                "date": "type:datetime",
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
                "likes": int,
                "username": "instagram",
            }
        }),

        # GraphVideo
        ("https://www.instagram.com/p/Bqxp0VSBgJg/", {
            "url": "8f38c1cf460c9804842f7306c487410f33f82e7e",
            "keyword": {
                "date": "type:datetime",
                "height": int,
                "likes": int,
                "media_id": "1923502432034620000",
                "shortcode": "Bqxp0VSBgJg",
                "typename": "GraphVideo",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphSidecar with 2 embedded GraphVideo objects
        ("https://www.instagram.com/p/BtOvDOfhvRr/", {
            "count": 2,
            "url": "e290d4180a58ae50c910d51d3b04d5f5c4622cd7",
            "keyword": {
                "sidecar_media_id": "1967717017113261163",
                "sidecar_shortcode": "BtOvDOfhvRr",
                "_ytdl_index": int,
            }
        })
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


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for TagPage"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{subcategory}", "{tag}")
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/explore/tags/([^/?&#]+)")
    test = ("https://www.instagram.com/explore/tags/instagram/", {
        "range": "1-12",
        "count": ">= 12",
    })

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.tag = match.group(1)

    def get_metadata(self):
        return {"tag": self.tag}

    def instagrams(self):
        url = '{}/explore/tags/{}/'.format(self.root, self.tag)
        return self._extract_tagpage(url)

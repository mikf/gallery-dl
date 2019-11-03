# -*- coding: utf-8 -*-

# Copyright 2018-2019 Leonardo Taccari, Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.instagram.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import json


class InstagramExtractor(Extractor):
    """Base class for instagram extractors"""
    category = "instagram"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{sidecar_media_id:?/_/}{media_id}.{extension}"
    archive_fmt = "{media_id}"
    root = "https://www.instagram.com"
    cookiedomain = ".instagram.com"
    cookienames = ("sessionid",)

    def get_metadata(self):
        return {}

    def items(self):
        self.login()
        yield Message.Version, 1

        metadata = self.get_metadata()
        for data in self.instagrams():
            data.update(metadata)
            yield Message.Directory, data

            if data['typename'] == 'GraphHighlightReel':
                url = '{}/stories/highlights/{}/'.format(self.root, data['id'])
                data['_extractor'] = InstagramStoriesExtractor
                yield Message.Queue, url, data
            else:
                url = data['video_url'] or data['display_url']
                yield Message.Url, url, text.nameext_from_url(url, data)

    def login(self):
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            self.session.cookies.set("ig_cb", "1", domain="www.instagram.com")
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        page = self.request(self.root + "/accounts/login/").text
        headers = {
            "Referer"         : self.root + "/accounts/login/",
            "X-IG-App-ID"     : "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = self.request(self.root + "/web/__mid/", headers=headers)
        headers["X-CSRFToken"] = response.cookies["csrftoken"]
        headers["X-Instagram-AJAX"] = text.extract(
            page, '"rollout_hash":"', '"')[0]

        url = self.root + "/accounts/login/ajax/"
        data = {
            "username"     : username,
            "password"     : password,
            "queryParams"  : "{}",
            "optIntoOneTap": "true",
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.json().get("authenticated"):
            raise exception.AuthenticationError()
        return {
            key: self.session.cookies.get(key)
            for key in ("sessionid", "mid", "csrftoken")
        }

    def _request_graphql(self, variables, query_hash, csrf=None):
        headers = {
            'X-CSRFToken': csrf,
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
        }
        url = '{}/graphql/query/?query_hash={}&variables={}'.format(
            self.root, query_hash, variables,
        )
        return self.request(url, headers=headers).json()

    def _extract_shared_data(self, url):
        page = self.request(url).text
        shared_data, pos = text.extract(
            page, 'window._sharedData =', ';</script>')
        additional_data, pos = text.extract(
            page, 'window.__additionalDataLoaded(', ');</script>', pos)

        data = json.loads(shared_data)
        if additional_data:
            next(iter(data['entry_data'].values()))[0] = \
                json.loads(additional_data.partition(',')[2])
        return data

    def _extract_postpage(self, url):
        data = self.request(url + "?__a=1").json()
        media = data['graphql']['shortcode_media']

        common = {
            'date': text.parse_timestamp(media['taken_at_timestamp']),
            'likes': text.parse_int(media['edge_media_preview_like']['count']),
            'owner_id': media['owner']['id'],
            'username': media['owner']['username'],
            'fullname': media['owner']['full_name'],
            'description': text.parse_unicode_escapes('\n'.join(
                edge['node']['text']
                for edge in media['edge_media_to_caption']['edges']
            )),
        }

        medias = []
        if media['__typename'] == 'GraphSidecar':
            for n in media['edge_sidecar_to_children']['edges']:
                children = n['node']
                media_data = {
                    'media_id': children['id'],
                    'shortcode': children['shortcode'],
                    'typename': children['__typename'],
                    'display_url': children['display_url'],
                    'video_url': children.get('video_url'),
                    'height': text.parse_int(children['dimensions']['height']),
                    'width': text.parse_int(children['dimensions']['width']),
                    'sidecar_media_id': media['id'],
                    'sidecar_shortcode': media['shortcode'],
                }
                media_data.update(common)
                medias.append(media_data)

        else:
            media_data = {
                'media_id': media['id'],
                'shortcode': media['shortcode'],
                'typename': media['__typename'],
                'display_url': media['display_url'],
                'video_url': media.get('video_url'),
                'height': text.parse_int(media['dimensions']['height']),
                'width': text.parse_int(media['dimensions']['width']),
            }
            media_data.update(common)
            medias.append(media_data)

        return medias

    def _extract_stories(self, url):
        if self.highlight_id:
            user_id = ''
            highlight_id = '"{}"'.format(self.highlight_id)
            query_hash = '30a89afdd826d78a5376008a7b81c205'
        else:
            shared_data = self._extract_shared_data(url)

            # If no stories are present the URL redirects to `ProfilePage'
            if 'StoriesPage' not in shared_data['entry_data']:
                return []

            user_id = '"{}"'.format(
                shared_data['entry_data']['StoriesPage'][0]['user']['id'])
            highlight_id = ''
            query_hash = 'cda12de4f7fd3719c0569ce03589f4c4'

        variables = (
            '{{'
            '"reel_ids":[{}],"tag_names":[],"location_ids":[],'
            '"highlight_reel_ids":[{}],"precomposed_overlay":true,'
            '"show_story_viewer_list":true,'
            '"story_viewer_fetch_count":50,"story_viewer_cursor":"",'
            '"stories_video_dash_manifest":false'
            '}}'
        ).format(user_id, highlight_id)
        shared_data = self._request_graphql(variables, query_hash)

        # If there are stories present but the user is not authenticated or
        # does not have permissions no stories are returned.
        if not shared_data['data']['reels_media']:
            return []   # no stories present

        medias = []
        for media in shared_data['data']['reels_media'][0]['items']:
            media_data = {
                'owner_id': media['owner']['id'],
                'username': media['owner']['username'],
                'date': text.parse_timestamp(media['taken_at_timestamp']),
                'expires': text.parse_timestamp(media['expiring_at_timestamp']),
                'media_id': media['id'],
                'typename': media['__typename'],
            }
            if media['__typename'] == 'GraphStoryImage':
                media_data.update({
                    'display_url': media['display_url'],
                    'height': text.parse_int(media['dimensions']['height']),
                    'width': text.parse_int(media['dimensions']['width']),
                })
            elif media['__typename'] == 'GraphStoryVideo':
                vr = media['video_resources'][0]
                media_data.update({
                    'duration': text.parse_float(media['video_duration']),
                    'display_url': vr['src'],
                    'height': text.parse_int(vr['config_height']),
                    'width': text.parse_int(vr['config_width']),
                })
            medias.append(media_data)

        return medias

    def _extract_story_highlights(self, shared_data):
        graphql = shared_data['entry_data']['ProfilePage'][0]['graphql']
        variables = (
            '{{'
            '"user_id":"{}","include_chaining":true,'
            '"include_reel":true,"include_suggested_users":false,'
            '"include_logged_out_extras":false,'
            '"include_highlight_reels":true'
            '}}'
        ).format(graphql['user']['id'])

        data = self._request_graphql(
            variables,
            'aec5501414615eca36a9acf075655b1e',
            shared_data['config']['csrf_token'],
        )

        highlights = []
        for edge in data['data']['user']['edge_highlight_reels']['edges']:
            story = edge['node']
            highlights.append({
                'id'      : story['id'],
                'title'   : story['title'],
                'owner_id': story['owner']['id'],
                'username': story['owner']['username'],
                'typename': story['__typename'],
            })

        return highlights

    def _extract_page(self, shared_data, psdf):
        csrf = shared_data['config']['csrf_token']

        while True:
            # Deal with different structure of pages: the first page
            # has interesting data in `entry_data', next pages in `data'.
            if 'entry_data' in shared_data:
                base_shared_data = shared_data['entry_data'][psdf['page']][0]['graphql']

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
            shared_data = self._request_graphql(
                variables, psdf['query_hash'], csrf,
            )


class InstagramImageExtractor(InstagramExtractor):
    """Extractor for PostPage"""
    subcategory = "image"
    pattern = r"(?:https?://)?(?:www\.)?instagram\.com/(?:p|tv)/([^/?&#]+)"
    test = (
        # GraphImage
        ("https://www.instagram.com/p/BqvsDleB3lV/", {
            "pattern": r"https://[^/]+\.(cdninstagram\.com|fbcdn\.net)"
                       r"/vp/[0-9a-f]+/[0-9A-F]+/t51.2885-15/e35"
                       r"/44877605_725955034447492_3123079845831750529_n.jpg",
            "keyword": {
                "date": "type:datetime",
                "description": str,
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
            "pattern": r"/47129943_191645575115739_8539303288426725376_n\.mp4",
            "keyword": {
                "date": "type:datetime",
                "description": str,
                "height": int,
                "likes": int,
                "media_id": "1923502432034620000",
                "shortcode": "Bqxp0VSBgJg",
                "typename": "GraphVideo",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphVideo (IGTV)
        ("https://www.instagram.com/tv/BkQjCfsBIzi/", {
            "pattern": r"/10000000_1760663964018792_716207142595461120_n\.mp4",
            "keyword": {
                "date": "type:datetime",
                "description": str,
                "height": int,
                "likes": int,
                "media_id": "1806097553666903266",
                "shortcode": "BkQjCfsBIzi",
                "typename": "GraphVideo",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphSidecar with 2 embedded GraphVideo objects
        ("https://www.instagram.com/p/BtOvDOfhvRr/", {
            "count": 2,
            "keyword": {
                "sidecar_media_id": "1967717017113261163",
                "sidecar_shortcode": "BtOvDOfhvRr",
                "video_url": str,
            }
        })
    )

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.shortcode = match.group(1)

    def instagrams(self):
        url = '{}/p/{}/'.format(self.root, self.shortcode)
        return self._extract_postpage(url)


class InstagramStoriesExtractor(InstagramExtractor):
    """Extractor for StoriesPage"""
    subcategory = "stories"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/stories/([^/?&#]+)(?:/(\d+))?")
    test = (
        ("https://www.instagram.com/stories/instagram/"),
        ("https://www.instagram.com/stories/highlights/18042509488170095/"),
    )

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.username, self.highlight_id = match.groups()

    def instagrams(self):
        url = '{}/stories/{}/'.format(self.root, self.username)
        return self._extract_stories(url)


class InstagramUserExtractor(InstagramExtractor):
    """Extractor for ProfilePage"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?!p/|explore/|directory/|accounts/|stories/|tv/)"
               r"([^/?&#]+)/?$")
    test = (
        ("https://www.instagram.com/instagram/", {
            "range": "1-16",
            "count": ">= 16",
        }),
        ("https://www.instagram.com/instagram/", {
            "options": (("highlights", True),),
            "pattern": InstagramStoriesExtractor.pattern,
            "range": "1-2",
            "count": 2,
        }),
    )

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.username = match.group(1)

    def instagrams(self):
        url = '{}/{}/'.format(self.root, self.username)
        shared_data = self._extract_shared_data(url)

        if self.config('highlights'):
            yield from self._extract_story_highlights(shared_data)

        yield from self._extract_page(shared_data, {
            'page': 'ProfilePage',
            'node': 'user',
            'node_id': 'id',
            'variables_id': 'id',
            'edge_to_medias': 'edge_owner_to_timeline_media',
            'query_hash': 'f2405b236d85e8296cf30347c9f08c2a',
        })


class InstagramChannelExtractor(InstagramExtractor):
    """Extractor for ProfilePage channel"""
    subcategory = "channel"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?!p/|explore/|directory/|accounts/|stories/|tv/)"
               r"([^/?&#]+)/channel")
    test = ("https://www.instagram.com/instagram/channel/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.username = match.group(1)

    def instagrams(self):
        url = '{}/{}/channel/'.format(self.root, self.username)
        shared_data = self._extract_shared_data(url)

        return self._extract_page(shared_data, {
            'page': 'ProfilePage',
            'node': 'user',
            'node_id': 'id',
            'variables_id': 'id',
            'edge_to_medias': 'edge_felix_video_timeline',
            'query_hash': 'bc78b344a68ed16dd5d7f264681c4c76',
        })


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for TagPage"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{subcategory}", "{tag}")
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/explore/tags/([^/?&#]+)")
    test = ("https://www.instagram.com/explore/tags/instagram/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.tag = match.group(1)

    def get_metadata(self):
        return {"tag": self.tag}

    def instagrams(self):
        url = '{}/explore/tags/{}/'.format(self.root, self.tag)
        shared_data = self._extract_shared_data(url)

        return self._extract_page(shared_data, {
            'page': 'TagPage',
            'node': 'hashtag',
            'node_id': 'name',
            'variables_id': 'tag_name',
            'edge_to_medias': 'edge_hashtag_to_media',
            'query_hash': 'f12c9ec5e46a3173b2969c712ad84744',
        })

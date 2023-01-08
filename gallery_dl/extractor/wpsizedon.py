# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://wp.sizedon.com"""

from .common import Extractor, Message
from .. import text
from urllib.parse import urlparse
from os.path import split, splitext
import json

BASE_PATTERN = r'(?:https?://)?wp\.sizedon\.com'
root = 'https://wp.sizedon.com'


class WpsizedonExtractor(Extractor):
    """Base class for wpsizedon extractors"""
    category = 'wpsizedon'
    directory_fmt = ('{category}', '{author}', '{genre}', '{contributor}')
    filename_fmt = '{title} [{id}].{extension}'
    archive_fmt = '{id}'

    def __init__(self, match):
        Extractor.__init__(self, match)

    def items(self):
        for post_id in self.posts():
            post = self._parse_post(post_id)
            if post:
                yield Message.Directory, post
                yield Message.Url, post['url'], post

    def posts(self):
        """Return post IDs from the URL"""

    def metadata(self):
        """Return general metadata"""

    def _parse_post(self, post_id):
        url = '{}/{}/'.format(root, post_id)

        with self.request(url, method='GET') as response:
            page_extractor = text.extract_from(response.text)

            if 'class="wp-block-video"' in response.text:
                intermediate = text.unescape(page_extractor(
                    '<figure class="wp-block-video"><video',
                    '></video></figure>'))
                intermediate_extractor = text.extract_from(intermediate)
                media_url = text.unescape(intermediate_extractor('src="', '"'))
            elif 'class="wp-block-file"' in response.text:
                intermediate = text.unescape(page_extractor(
                    '<div class="wp-block-file">', '</a></div>'))
                intermediate_extractor = text.extract_from(intermediate)
                media_url = text.unescape(intermediate_extractor(
                    'href="', '"'))
            else:
                self.log.warning('Unable to fetch post {}: '
                                 'URL not found in page.'.format(post_id))
                return None

            basename, extension = splitext(urlparse(media_url).path)
            basename, extension = splitext(split(media_url)[1])
            extension = extension[1:]

            genre = text.extract(
                response.text, '<meta property="article:tag" content="',
                '"')[0]
            contributor = text.extract(
                response.text,
                '<meta property="article:section" content="', '"')[0]

            json_data = json.loads(
                text.extract(
                    response.text, '<script type="application/ld+json">',
                    '</script>')[0])
            title = json_data['headline']
            author = json_data['author']['name']
            description = json_data['description']
            date_published = json_data['datePublished']
            date_modified = json_data['dateModified']

            return {
                "id": text.unquote(post_id),
                "url": media_url,
                "title": title,
                "basename": basename,
                "extension": extension,
                "description": description,
                "date_published": date_published,
                "date_modified": date_modified,
                "author": author,
                "genre": genre,
                "contributor": contributor,
            }


class WpsizedonPostExtractor(WpsizedonExtractor):
    """Extractor for individual post URLs on wpsizedon"""
    subcategory = 'post'
    pattern = BASE_PATTERN + r'/([a-z0-9-_%]{5,})/?$'
    test = (
        # 動画 (video) and ゲーム (game)
        ("https://wp.sizedon.com/kyodaimusume_mmd_giantess_vore_fukubuchou/", {
            "keyword": {
                # Different aspects of extraction (URL, text.extract, JSON)
                "basename":
                "2022-04-Kyodaimusume_MMD_Giantess_Vore_Fukubuchou",
                "extension": "mp4",
                "date_modified": "2022-04-09T13:38:33+09:00",
                "genre": "動画"
            }
        }),
        ("https://wp.sizedon.com/tenoseka1-10/", {
            "keyword": {
                "basename": "2022-09-tenoseka1.10",
                "extension": "zip",
                "date_modified": "2022-09-29T22:05:12+09:00",
                "genre": "ゲーム"
            }
        }),
    )

    def __init__(self, match):
        WpsizedonExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self.post_id,)


class WpsizedonListExtractor(WpsizedonExtractor):
    """Base class for wpsizedon list extractors"""

    def __init__(self, match):
        WpsizedonExtractor.__init__(self, match)

    def posts(self):
        post_id_list = []

        def another_page_exists(page):
            if '<!-- Cocoon next -->' in page:
                return True
            else:
                return False

        def add_post_urls_from_list_page(page):
            list_div = text.extract(
                page, '<div id="list" class="list ect-entry-card '
                'front-page-type-index">', '</div><!-- .list -->')[0]
            for post_url in text.extract_iter(list_div, 'href="', '"'):
                post_id_list.append(post_url[23:-1])

        def retrieve_next_page_url(page):
            return text.extract(
                page, '<!-- Cocoon next -->\n<link rel="next" href="',
                '"')[0]

        def request_list_page(url):
            return self.request(url, method='GET').text

        page = request_list_page(self.list_url)

        while another_page_exists(page) is True:
            add_post_urls_from_list_page(page)
            page = request_list_page(retrieve_next_page_url(page))

        add_post_urls_from_list_page(page)

        return post_id_list


class WpsizedonGenreExtractor(WpsizedonListExtractor):
    """Extractor for ジャンル/genre URLs on wpsizedon

    Currently only 動画 (video) or ゲーム (game).
    """
    subcategory = 'genre'
    pattern = BASE_PATTERN + r'/tag/[a-z0-9%]+/?$'
    test = (
        ("https://wp.sizedon.com/tag/%e3%82%b2%e3%83%bc%e3%83%a0/"),
        ("https://wp.sizedon.com/tag/%e5%8b%95%e7%94%bb/"),
    )

    def __init__(self, match):
        WpsizedonListExtractor.__init__(self, match)
        self.list_url = match.group(0)


class WpsizedonContributorExtractor(WpsizedonListExtractor):
    """Extractor for 投稿者/contributor URLs on wpsizedon"""
    subcategory = 'contributor'
    pattern = BASE_PATTERN + r'/category/[a-zA-Z0-9_%]+/?$'
    test = (
        ("https://wp.sizedon.com/category/sakuragi/"),
    )

    def __init__(self, match):
        WpsizedonListExtractor.__init__(self, match)
        self.list_url = match.group(0)


class WpsizedonAuthorExtractor(WpsizedonListExtractor):
    """Extractor for author URLs on wpsizedon

    author/{AUTHOR}, currently only 契音 (author/ikusuyo)
    and will likely not change. Therefore it is a list of all posts.
    """
    subcategory = 'author'
    pattern = BASE_PATTERN + r'/author/ikusuyo/$'
    test = (
        ("https://wp.sizedon.com/author/ikusuyo/"),
    )

    def __init__(self, match):
        WpsizedonListExtractor.__init__(self, match)
        self.list_url = match.group(0)


class WpsizedonArchiveExtractor(WpsizedonListExtractor):
    """Extractor for アーカイブ/archive URLs on wpsizedon

    YYYY/MM/DD for most months/days since 2020/07.
    Month and day directory are optional, parent directories are usable.
    """
    subcategory = 'archive'
    pattern = BASE_PATTERN + r'/[0-9]{4}/?$'
    r'|/[0-9]{4}/[0-9]{2}/?$'
    r'|/[0-9]{4}/[0-9]{2}/[0-9]{2}/?$'
    test = (
        ("https://wp.sizedon.com/2020/"),
    )

    def __init__(self, match):
        WpsizedonListExtractor.__init__(self, match)
        self.list_url = match.group(0)

import base64
import urllib.parse

from .common import Message, GalleryExtractor
import sys


class SzurubooruExtractor(GalleryExtractor):
    """
    Extractor for szurubooru hosted boorus
    (https://github.com/rr-/szurubooru/)
    """
    auth_token = None
    username = None
    page_size = 40

    specifies_protocol = False
    base_url = None
    query = None

    pattern = r"((https?://)?[^/]+)/posts/query=([^#]*)"
    category = "szurubooru"
    domain = "szurubooru"
    directory_fmt = ("{domain}", "{query}")
    filename_fmt = "{id}_{version}_{tags_str}.{extension}"

    test = ("https://booru.foalcon.com/posts/query=artist%5C%3Abobdude0", {
        "pattern": r"https://booru.foalcon.com/data/posts/\d+.png",
        "count": ">=1"
    })

    def __init__(self, match):
        super().__init__(match)
        self.auth_token = self.config("token")
        self.username = self.config("username")
        self.base_url = match.group(1)
        self.specifies_protocol = match.group(2) is not None
        self.query = match.group(3)
        self.domain = urllib.parse.urlparse(self.base_url).hostname

        if self.config("page_size") is not None:
            try:
                self.page_size = int(self.config('page_size'))
            except ValueError:
                self.page_size = 40

    def items(self):
        headers = self._get_headers()

        params = {'domain': self.domain, 'query': self.query}
        yield Message.Directory, params, self.query

        try:
            offset = 0
            while True:
                page_content = self._get_page(self.query,
                                              headers=headers,
                                              offset=offset)

                offset = page_content['offset']

                for image_metadata in page_content['results']:
                    url = image_metadata['contentUrl']
                    yield Message.Url, url, image_metadata

                offset += len(page_content['results'])
                if offset >= int(page_content['total']):
                    break

        except Exception as ex:
            sys.stderr.write(ex.args[0])
            sys.stderr.write("\n")
            return

    def _get_headers(self):
        # https://github.com/rr-/szurubooru/blob/master/doc/API.md#basic-requests
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.auth_token is not None \
                and self.username is not None \
                and len(self.auth_token) > 0 and \
                len(self.username) > 0:
            # https://github.com/rr-/szurubooru/blob/master/doc/API.md#user-token-authentication

            concatenation = (str(self.username) + ":" + str(self.auth_token))
            concatenation = concatenation.encode('ascii')

            b64token = base64.b64encode(concatenation).decode("ascii")
            headers['Authorization'] = 'Token ' + b64token

        return headers

    def _get_page(self, tags, headers, offset=0) -> dict:
        api_url = self.base_url + '/api/posts/?offset=' + offset\
                                + '&limit=' + str(self.page_size)\
                                + '&query=' + str(tags)
        api_result = self.request(api_url, headers=headers).json()

        for error_tag in ['name', 'title', 'description']:
            if error_tag in api_result:
                raise Exception(api_result['name'] + " while fetching data:" +
                                api_result['title'] + " (" +
                                api_result['description'] + ")")

        for result in api_result['results']:
            if not result['contentUrl'].startswith('http'):
                # Relative path
                url = self.base_url + "/" + result['contentUrl']
                result['contentUrl'] = url
            result['extension'] = result['contentUrl'].split('.')[-1]
            tag_names = [tag['names'][0] for tag in result['tags']]
            result['tags_str'] = ','.join(tag_names)[:250]

        return api_result

from .common import BasicExtractor
from urllib.parse import unquote
import re

class Extractor(BasicExtractor):

    thread_url_fmt = "https://www.8chan.co/{0}/res/{1}.html"
    regex = r'>File: <a href="([^"]+)">([^<]+)\.[^<]+<.*?<span class="postfilename"( title="([^"]+)")?>([^<]+)<'

    def __init__(self, match, config):
        BasicExtractor.__init__(self, config)
        self.board, _, self.thread_id = match.group(1).split("/")
        self.category = "8chan"
        self.directory = self.board + "-" + self.thread_id

    def images(self):
        url  = self.thread_url_fmt.format(self.board, self.thread_id)
        text = self.request(url).text
        for match in re.finditer(self.regex, text):
            url, prefix, fullname, name = match.group(1, 2, 4, 5)
            yield ("https://www.8chan.co" + url, prefix + "-" + unquote(fullname or name))

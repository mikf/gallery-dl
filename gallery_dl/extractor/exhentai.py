from .common import BasicExtractor
from ..util import unescape
import time
import random
import json

class Extractor(BasicExtractor):

    api_url  = "http://exhentai.org/api.php"
    name_fmt = "{}_{:>04}_{}_{}"

    def __init__(self, match, config):
        BasicExtractor.__init__(self, config)
        self.url = match.group(0)
        self.gid, self.token = match.group(1).split("/")
        self.category  = "exhentai"
        self.directory = self.gid
        self.session.cookies.update(config["exhentai-cookies"])

    def images(self):
        e = self.extract

        # get gallery page
        text = self.request(self.url).text

        # get first image page
        url, pos = self.extract_all(text, "http://exhentai.org/s/", "-1")
        text = self.request(url).text

        # extract information
        _       , pos = e(text, '<div id="i3"><a onclick="return load_image(', '')
        imgkey  , pos = e(text, "'", "'", pos)
        url     , pos = e(text, '<img id="img" src="', '"', pos)
        name    , pos = e(text, '<div id="i4"><div>', ' :: ', pos)
        orgurl  , pos = e(text, 'http://exhentai.org/fullimg.php', '"', pos)
        gid     , pos = e(text, 'var gid='      ,  ';', pos)
        startkey, pos = e(text, 'var startkey="', '";', pos)
        showkey , pos = e(text, 'var showkey="' , '";', pos)

        #
        if orgurl: url = "http://exhentai.org/fullimg.php" + unescape(orgurl)
        yield url, self.name_fmt.format(self.gid, 1, startkey, name)

        # use json-api for further pages
        request = {
            "method" : "showpage",
            "gid"    : int(gid),
            "page"   : 2,
            "imgkey" : imgkey,
            "showkey": showkey,
        }

        while True:
            time.sleep( random.uniform(2, 5) )
            info = json.loads(
                self.session.post(self.api_url, data=json.dumps(request)).text
            )

            imgkey, pos = e(info["i3"], "'", "'")
            url   , pos = e(info["i3"], '<img id="img" src="', '"', pos)
            name  , pos = e(info["i" ], '<div>', ' :: ')
            orgurl, pos = e(info["i7"], '<a href="', '"')
            if orgurl: url = unescape(orgurl)
            yield url, self.name_fmt.format(gid, request["page"], request["imgkey"], name)

            if request["imgkey"] == imgkey:
                return
            request["imgkey"] = imgkey
            request["page"] += 1

from .common import AsyncExtractor
from ..util import safe_request
import re
import csv
import requests

class Extractor(AsyncExtractor):

    member_url = "http://www.pixiv.net/member_illust.php"
    illust_url = "http://www.pixiv.net/member_illust.php?mode=medium"

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.member_id = match.group(1)
        self.category = "pixiv"
        self.directory = self.member_id
        self.session.cookies.update(config["pixiv-cookies"])
        self.session.headers.update({"Referer": "http://www.pixiv.net/"})
        self.api = PixivAPI(config["pixiv-cookies"]["PHPSESSID"])

    def images(self):
        sname_fmt  = "pixiv_{1}_{0}.{2}"
        mname_fmt  = "pixiv_{1}_{0}_p{num:02}.{2}"

        singl_v1_fmt = "http://i{6[8]}.pixiv.net/img{4:>02}/img/{24}/{0}.{2}"
        manga_v1_fmt = "http://i{6[8]}.pixiv.net/img{4:>02}/img/{24}/{0}{big}_p{num}.{2}"

        singl_v2_fmt = "http://i{6[8]}.pixiv.net/img-original/img/{date}/{0}_p0.{2}"
        manga_v2_fmt = "http://i{6[8]}.pixiv.net/img-original/img/{date}/{0}_p{num}.{2}"

        date = ""
        big  = ""

        for img in self.image_ids():
            data = self.api.request(img)
            # debug
            # for i, value in enumerate(data):
                # print("{:02}: {}".format(i, value))
            # return
            # debug end

            if "うごイラ" in data[13]:
                # ugoira / animations
                try:
                    url, framelist = self.parse_ugoira(img)
                    data[2] = "zip"
                    yield (url, sname_fmt.format(*data))
                    data[2] = "txt"
                    yield (framelist, sname_fmt.format(*data))
                    continue
                except:
                    print("[Warning] failed to get ugoira url; trying fallback")

            # images
            if img > 46270949:
                date = data[6][45:64]
                url_s_fmt = singl_v2_fmt
                url_m_fmt = manga_v2_fmt
            else:
                big = "_big" if img > 11319935 else ""
                url_s_fmt = singl_v1_fmt
                url_m_fmt = manga_v1_fmt

            if not data[19]:
                yield (url_s_fmt.format(*data, date=date), sname_fmt.format(*data))
            else:
                for i in range(0, int(data[19])):
                    yield (url_m_fmt.format(*data, num=i, date=date, big=big),
                           mname_fmt.format(*data, num=i))

    def image_ids(self):
        """generator -- yield all image ids"""
        needle = '<li class="image-item"><a href="/member_illust.php?mode=medium&amp;illust_id='
        params = {"id": self.member_id, "p": 1}
        while True:
            text  = self.request(self.member_url, params=params).text
            end   = 0
            found = 0
            while True:
                pos = text.find(needle, end)
                if pos == -1:
                    break
                pos += len(needle)
                end = text.find('"', pos)
                found += 1
                yield int(text[pos:end])
            if found != 20:
                return
            params["p"] += 1

    def parse_ugoira(self, illust_id):
        # get illust page
        text = self.request(
            self.illust_url,
            params={"illust_id": illust_id},
        ).text

        # parse page
        url   , pos = self.extract(text, 'ugokuIllustFullscreenData  = {"src":"', '"')
        frames, pos = self.extract(text, '"frames":[', ']', pos)

        # fix url
        url = url.replace("\\/", "/")

        # build framelist
        framelist = "text://" + re.sub(
            r'\{"file":"([^"]+)","delay":(\d+)\},?',
            r'\1 \2\n',
            frames
        )

        return url, framelist


class PixivAPI():
    api_url = "http://spapi.pixiv.net/iphone/illust.php"

    def __init__(self, session_id):
        self.session = requests.Session()
        self.session.params["PHPSESSID"] = session_id

    def request(self, illust_id):
        while True:
            text = safe_request(
                self.session,
                self.api_url,
                params={"illust_id": illust_id}
            ).text
            if len(text) > 31:
                return next(csv.reader([text]))

# class FileDict(dict):
#
    # def __init__(self, *args):
        # super().__init__()
        # self.re = re.compile(r"pixiv_\d+_(?P<id>\d+)(?P<extra>_p\d+)?\.[a-z]{3}")
        # for arg in args:
            # self.load_from(arg)
#
    # def load_from(self, directory):
        # match = self.re.match
        # for file in os.listdir(directory):
            # m = match(file)
            # if m is None:
                # continue
            # val = True if m.group("extra") else False
            # dict.__setitem__(self, m.group("id"), val)
#
    # def __getitem__(self, key):
        # return dict.get(self, key)

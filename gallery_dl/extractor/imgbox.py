from .common import AsyncExtractor

class Extractor(AsyncExtractor):

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.url       = match.group(1)
        self.cache     = None
        self.category  = "imgbox"

        title          = self.get_title()
        self.directory = title  + " - " + self.url[3:]

    def images(self):
        text = self.cache or self.request("http://imgbox.com" + self.url).text
        pos  = 0
        while True:
            key, pos = self.extract(text, '.s.imgbox.com/', '.', pos)
            if key is None: return

            page = self.request("http://imgbox.com/"+key).text
            num , p = self.extract(page, '</a> &nbsp; ', ' of ')
            url , p = self.extract(page, '<a href="http://i.imgbox.com/', '"', p)
            name, p = self.extract(page, ' title="', '"', p)
            yield "http://i.imgbox.com/"+url, "{:>03}-{}".format(num, name)

    def get_title(self):
        text = self.request("http://imgbox.com/" + self.url).text
        title, _ = self.extract(text, "<h1>", "</h1>")

        if title:
            self.cache = text
            title = title[:title.rindex(" - ")]
        else:
            _, pos = self.extract(text, '<div class="row-fluid hidden-phone">', '')
            self.url, pos = self.extract(text, '<a href="', '">', pos)
            title, _ = self.extract(text, '', '</a>', pos)

        return title

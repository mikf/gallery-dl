from .common import AsyncExtractor

class Extractor(AsyncExtractor):

    def __init__(self, match, config):
        AsyncExtractor.__init__(self, config)
        self.category  = "imagebam"
        self.directory = self.get_title(match)  + " - " + match.group(2)

    def images(self):
        next_url = self.url
        num  = 1
        done = False
        while not done:
            # get current page
            text = self.request("http://www.imagebam.com" + next_url).text

            # get url for next page
            next_url, pos = self.extract(text, "<a class='buttonblue' href='", "'")

            # if the following text isn't "><span>next image" we are done
            if not text.startswith("><span>next image", pos):
                done = True

            # get image url
            img_url , pos = self.extract(text, 'onclick="scale(this);" src="', '"', pos)

            # extract filename from image url
            name = img_url[img_url.rindex("/")+1:]

            yield img_url, "{:>03}-{}".format(num, name)
            num += 1

    def get_title(self, match):
        if match.group(1) == "image":
            text = self.request(match.group(0)).text
            gallery_url, _ = self.extract(text, "class='gallery_title'><a href='", "'")
        else:
            gallery_url = "http://www.imagebam.com/gallery/" + match.group(2)

        text = self.request(gallery_url).text
        _       , pos = self.extract(text, "<img src='/img/icons/photos.png'", "")
        title   , pos = self.extract(text, "'> ", " <", pos)
        self.url, pos = self.extract(text, "<a href='http://www.imagebam.com", "'", pos)
        return title

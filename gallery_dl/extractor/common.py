import queue
import threading
import requests
from ..util import safe_request

class BasicExtractor():

    def __init__(self, config):
        self.session   = requests.Session()
        self.category  = ""
        self.directory = ""

    def __iter__(self):
        return self.images()

    def request(self, url, *args, **kwargs):
        return safe_request(self.session, url, *args, **kwargs)

    def enable_useragent(self):
        self.session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"

    @staticmethod
    def extract(txt, begin, end, pos=0):
        try:
            first = txt.index(begin, pos) + len(begin)
            last  = txt.index(end, first)
            return txt[first:last], last+len(end)
        except:
            return None, pos

    @staticmethod
    def extract_all(txt, begin, end, pos=0):
        try:
            first = txt.index(begin, pos)
            last  = txt.index(end, first + len(begin)) + len(end)
            return txt[first:last], last
        except:
            return None, pos

class AsyncExtractor(BasicExtractor):

    def __init__(self, config):
        super().__init__(config)
        self.__queue  = queue.Queue(maxsize=5)
        self.__thread = threading.Thread(target=self.async_images, daemon=True)

    def __iter__(self):
        get  = self.__queue.get
        done = self.__queue.task_done

        self.__thread.start()
        while True:
            task = get()
            if task is None:
                return
            yield task
            done()

    def async_images(self):
        put = self.__queue.put
        try:
            for task in self.images():
                put(task)
        except:
            import traceback
            print(traceback.format_exc())
        put(None)

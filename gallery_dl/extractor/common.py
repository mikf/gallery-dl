# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by extractor modules."""

import queue
import threading
import requests
# from ..util import safe_request

class Message():

    Version = 1
    Directory = 2
    Url = 3


class Extractor():

    def __init__(self):
        self.session = requests.Session()

    def __iter__(self):
        return self.items()

    def items(self):
        yield Message.Version, 1
        return

    def request(self, url, *args, **kwargs):
        return safe_request(self.session, url, *args, **kwargs)

    def enable_useragent(self):
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"
        )

    @staticmethod
    def extract(txt, begin, end, pos=0):
        try:
            first = txt.index(begin, pos) + len(begin)
            last = txt.index(end, first)
            return txt[first:last], last+len(end)
        except ValueError:
            return None, pos

    @staticmethod
    def extract_all(txt, begin, end, pos=0):
        try:
            first = txt.index(begin, pos)
            last = txt.index(end, first + len(begin)) + len(end)
            return txt[first:last], last
        except ValueError:
            return None, pos


class SequentialExtractor(Extractor):

    def __init__(self, _):
        Extractor.__init__(self)


class AsyncExtractor(Extractor):

    def __init__(self, config):
        Extractor.__init__(self)
        queue_size = int(config.get("queue-size", 5))
        self.__queue = queue.Queue(maxsize=queue_size)
        self.__thread = threading.Thread(target=self.async_items)
        # self.__thread = threading.Thread(target=self.async_images, daemon=True)

    def __iter__(self):
        get = self.__queue.get
        done = self.__queue.task_done

        self.__thread.start()
        while True:
            task = get()
            if task is None:
                return
            yield task
            done()

    def async_items(self):
        put = self.__queue.put
        try:
            for task in self.items():
                put(task)
        except Exception:
            import traceback
            print(traceback.format_exc())
        put(None)

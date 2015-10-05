# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by extractor modules."""

import time
import queue
import requests
import threading
from .. import config


class Message():

    Version = 1
    Directory = 2
    Url = 3
    Headers = 4
    Cookies = 5


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


class SequentialExtractor(Extractor):

    def __init__(self):
        Extractor.__init__(self)


class AsynchronousExtractor(Extractor):

    def __init__(self):
        Extractor.__init__(self)
        queue_size = int(config.get(("queue-size",), default=5))
        self.__queue = queue.Queue(maxsize=queue_size)
        self.__thread = threading.Thread(target=self.async_items, daemon=True)

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


def safe_request(session, url, method="GET", *args, **kwargs):
    tries = 0
    while True:
        # try to connect to remote source
        try:
            r = session.request(method, url, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            tries += 1
            time.sleep(1)
            if tries == 5:
                raise
            continue

        # reject error-status-codes
        if r.status_code != requests.codes.ok:
            tries += 1
            time.sleep(1)
            if tries == 5:
                r.raise_for_status()
            continue

        # everything ok -- proceed to download
        return r

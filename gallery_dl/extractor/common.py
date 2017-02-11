# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by extractor modules."""

import os
import time
import queue
import requests
import threading
from .message import Message
from .. import config


class Extractor():

    category = ""
    subcategory = ""
    directory_fmt = [""]
    filename_fmt = ""

    def __init__(self):
        self.session = requests.Session()

    def __iter__(self):
        return self.items()

    def items(self):
        yield Message.Version, 1

    def request(self, url, encoding=None, *args, **kwargs):
        response = safe_request(self.session, url, *args, **kwargs)
        if encoding:
            response.encoding = encoding
        return response


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
            if isinstance(task, Exception):
                raise task
            yield task
            done()

    def async_items(self):
        put = self.__queue.put
        try:
            for task in self.items():
                put(task)
        except Exception as e:
            put(e)
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


# The first import of requests happens inside this file.
# If we are running on Windows and the from requests expected certificate file
# is missing (which happens in a standalone executable from py2exe), the
# requests.Session object gets monkey patched to always set its 'verify'
# attribute to False to avoid an exception being thrown when attempting to
# access https:// URLs.

if os.name == "nt":
    import os.path
    import requests.certs
    import requests.packages.urllib3 as ulib3
    if not os.path.isfile(requests.certs.where()):
        def patched_init(self):
            session_init(self)
            self.verify = False
        session_init = requests.Session.__init__
        requests.Session.__init__ = patched_init
        ulib3.disable_warnings(ulib3.exceptions.InsecureRequestWarning)

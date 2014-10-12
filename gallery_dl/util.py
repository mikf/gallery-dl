import time
import requests
import html.parser

def safe_request(session, url, *args, **kwargs):
    tries = 0
    while True:
        # try to connect to remote source
        try:
            r = session.get(url, *args, **kwargs)
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

def filename_from_url(url):
    pos = url.rfind("/")
    return url[pos+1:]

unescape = html.parser.HTMLParser().unescape

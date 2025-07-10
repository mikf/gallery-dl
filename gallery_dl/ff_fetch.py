
import requests

class FFFetchHandler:
    def __init__(self, log):
        self.log = log
        self._is_ff_fetch_proxy = dict()
    
    def adjust_request(self, proxies, session, url):
        self.log.debug('FFFetchHandler.adjust_request %s proxies=%s', url, proxies)
        single_proxy = proxies
        # Special handling for the same copied proxy
        if isinstance(proxies, list) and len(set(proxies)) == 1:
            single_proxy = proxies[0]
        elif isinstance(proxies, dict):
            copied = set(v for k, v in proxies.items()
                         if k.lower() in ['http', 'https'])
            if len(copied) == 1:
                single_proxy = list(copied)[0]

        # Only single proxy specification is supported
        if not isinstance(single_proxy, str):
            return url

        # Detecting Firefox Fetcher
        if single_proxy not in self._is_ff_fetch_proxy:
            # caching the detection result
            r = requests.get(
                'http://name.nonexistent?X-FFFetch-SelfIdent',
                proxies=proxies
            )
            self._is_ff_fetch_proxy[single_proxy] = (
                r.status_code == 200
                and r.text == 'X-FFFetch-SelfIdent: OK'
            )
            if self._is_ff_fetch_proxy[single_proxy]:
                self.log.info("Using Firefox Fetcher: '%s'", single_proxy)

        if self._is_ff_fetch_proxy[single_proxy]:
            # When using Firefox Fetcher, we have to resort to HTTP since
            # HTTPS bypasses proxying and nullifies our imitation effort.
            # Do not worry, Firefox Fetcher always uses HTTPS while
            # fetching.
            if url.lower().startswith('https://'):
                url = 'http://' + url[8:]

        return url

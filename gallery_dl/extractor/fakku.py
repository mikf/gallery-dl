import base64

from .common import Extractor, Message
from .. import exception, text, util


class FakkuReadExtractor(Extractor):
    category = "fakku"
    subcategory = "read"
    root = "https://www.fakku.net"
    pattern = (r"(?:https?://)?(?:www\.)?fakku\.net/hentai/([^/]+)"
               r"(?:/read(?:/\d+)?)?")
    example = "https://www.fakku.net/hentai/couple-channel-english"
    cookies_domain = ".fakku.net"
    filename_fmt = "{category}_{title}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{title}_{num}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.title = match.group(1)

    def items(self):
        self.login()

        metadata = self._metadata()
        page_data = metadata.pop("pages")
        content = metadata.pop("content", {})
        series = content.pop("content_series", [])
        artists = content.pop("content_artists", [])
        publishers = content.pop("content_publishers", [])
        metadata.update({
            "artists": [artist.get("attribute", "") for artist in artists],
            "series": [serie.get("attribute", "") for serie in series],
            "publishers": [publisher.get("attribute", "")
                           for publisher in publishers],
            "name": self.title,
            "title": content.get("content_name", ""),
            "description": content.get("content_description", ""),
            "language": content.get("content_language", ""),
            "count": len(page_data),
            "date": content.get("content_date", 0),
            "comments": content.get("content_comments", 0),
            "ads": content.get("content_ads", False),
            "preview": content.get("content_preview", False),
        })
        yield Message.Directory, "", metadata

        # Extract password
        key_hash = metadata["key_hash"]
        fakku_zid = metadata["fakku_zid"]
        magic_string = metadata["magic_string"]
        password = fakku_zid + key_hash + magic_string

        # Decode Base64 and XOR Decrypt
        key_data = metadata["key_data"]
        raw_data = base64.b64decode(key_data).decode('utf-8')
        decrypted_json_str = "".join(self._xor_decrypt(password, raw_data))

        # Parse JSON
        # data format (legacy): { "0": [page 1 data], "1": [page 2 data] }
        try:
            data = util.json_loads(decrypted_json_str)
        except Exception:
            raise exception.ExtractionError(
                "Failed to parse decrypted JSON. Password might be wrong.")

        if self.config("page-reverse"):
            enum = util.enumerate_reversed
        else:
            enum = enumerate

        # Unshuffle and Extract Seeds
        for metadata["num"], (page_id, arr) in enum(data.items()):
            # Pop the sub-seed (the last item)
            sub_seed = arr.pop()

            # Unshuffle the rest of the array
            length = len(arr)
            unshuffled = [None] * length
            shuffle_map = generate_shuffled_map(length, sub_seed)
            for i in range(length):
                unshuffled[shuffle_map[i]] = arr[i]

            # Extract the Seed (Index 2)
            seed = unshuffled[2]

            # Extract image data (Index n XOR'd with the seed)
            url = page_data[page_id]["image"]
            metadata.update({
                "extension": "png",
                "seed": seed,
                "width": unshuffled[0] ^ seed,
                "height": unshuffled[1] ^ seed,
                "left": unshuffled[3] ^ seed,
                "top": unshuffled[4] ^ seed,
                "right": unshuffled[5] ^ seed,
                "bottom": unshuffled[6] ^ seed,
            })
            yield Message.Url, url, metadata

    def _metadata(self):
        page_url = f"{self.root}/hentai/{self.title}/read"
        resp = self.request(page_url)
        if "subscription" in resp.url:
            raise exception.ExtractionError(
                "Content is behind subscription wall")

        page = resp.text

        # Extract JS URL and fetch the JS
        regex_js = text.re(
            r"/static/reader/reader\.fakku\.embed\.min\.js\?v=(\d+)")
        match_js = regex_js.search(page)
        if not match_js:
            raise exception.ExtractionError("Unable to extract js url")

        # deobfuscate the js_page and extract the magic string.
        js_url = f"{self.root}/static/reader/reader.fakku.min.js"
        js_params = {"v": match_js.group(1)}
        js_resp = self.request(js_url, params=js_params)
        js_page = self._deobfuscate_js_page(js_resp.text)

        regex = text.re(
            r"(?sa)"
            r"var (?P<var>\w+)='(?P<zid>\w{64})'"
            r".*?"
            r"\w+=\w+===(?P=var)\?'(?P<str1>\w{64})':'(?P<str2>\w{64})'")
        match = regex.search(js_page)
        if not match:
            raise exception.ExtractionError("Unable to extract magic string")

        # Extract magic_string
        default_fakku_zid = match.group("zid")
        fakku_zid = self.cookies.get(
            "fakku_zid", default_fakku_zid, domain=self.cookies_domain
        )
        if fakku_zid == default_fakku_zid:
            magic_string = match.group("str1")
        else:
            magic_string = match.group("str2")

        # Fetch metadata from the API
        metadata_url = f"https://reader.fakku.net/hentai/{self.title}/read"
        metadata = self.request(metadata_url).json()
        metadata["fakku_zid"] = fakku_zid
        metadata["magic_string"] = magic_string
        return metadata

    def login(self):
        pass

    def _deobfuscate_js_page(self, page):
        # 1. Extract the array
        # pattern: var _0x... = ['...', '...'];
        regex = text.re(
            r"(?sa)"
            r"function (\w+)\(\)\{"
            r"var \w+=\[(.*?)\];"
            r".*?\s*\}")
        match = regex.search(page)
        if not match:
            raise exception.ExtractionError("Could not extract the array")

        func_name = match.group(1)
        array_block = match.group(2)
        regex = text.re(r"(?sa)'(.*?)'")
        arr = regex.findall(array_block)

        # 2. Setup target constraints
        offset = self._extract_offset_num(page, func_name)
        target_word, target_hex = self._extract_target(page)
        target_index = target_hex - offset

        # 3. Find the correct array rotation
        for i in range(len(arr) + 1):
            if arr[target_index] == target_word:
                break
            arr.append(arr.pop(0))
        else:
            raise exception.ExtractionError(
                "Could not find the correct rotation")

        # 4. Replace all the obfuscated calls in the code
        # pattern: _0x1d625b(0x42d)
        def replacer(match):
            hex_val = int(match.group(2), 16)
            index = hex_val - offset
            if 0 <= index < len(arr):
                real_string = arr[index]
                clean_string = real_string.replace("'", "\\'")
                return f"'{clean_string}'"
            return match.group(0)

        regex = text.re(r"(\w+)\((0x[a-f0-9]+)\)")
        return regex.sub(replacer, page)

    @staticmethod
    def _extract_offset_num(page, func_name):
        logic_regex = text.re(
            r"(?sa)"
            r"function \w+\(\w+,\w+\)\{"
            rf"var (?P<var>\w+)={func_name}\(\);"
            r"return (?P<func>\w+)=function\((?P<arg1>\w+),\w+\)\{"
            r"(?P=arg1)=(?P=arg1)-(?P<num>\w+);"
            r".*?\},"
            r"(?P=func)\(\w+,\w+\);"
            r"\}")
        match = logic_regex.search(page)
        if not match:
            raise exception.ExtractionError("Could not extract offset number")
        return int(match.group("num"), base=16)

    @staticmethod
    def _extract_target(page):
        # Standard Webpack Source:
        # __webpack_require__.o = (obj, prop) =>
        # Object.prototype.hasOwnProperty.call(obj, prop)
        # Obfuscated
        # _0x4a2c22['o'] = (_0xc27756,_0x1d244e) =>
        # Object[_0x3ae857(0x42d)][_0x3ae857(0x47f)][_0x3ae857(0x28f)]
        # (_0xc27756, _0x1d244e)
        logic_regex = text.re(
            r"(?sa)"
            r"\w+\['o'\]=\(\w+,\w+\)=>"
            r"Object\[(.+?)\]\[(.+?)\]\[(.+?)\]\(\w+,\w+\)")
        match = logic_regex.search(page)
        if not match:
            raise exception.ExtractionError("Could not extract target hex")

        target_words = ("prototype", "hasOwnProperty", "call")
        for target_word, group in zip(target_words, match.groups()):
            fname, sep, target_hex = group.partition("(")
            if not sep:
                continue
            return target_word, int(target_hex[:-1], base=16)
        raise exception.ExtractionError("Could not extract target hex")

    @staticmethod
    def _xor_decrypt(password, data):
        for i in range(len(data)):
            char_code = ord(data[i])
            pass_code = ord(password[i % len(password)])
            yield chr(char_code ^ pass_code)


class Mash:
    DEFAULT = float(0xefc8249d)

    def __init__(self):
        self.n = self.DEFAULT

    def update(self, data):
        data = str(data)

        for char in data:
            self.n += ord(char)
            h = 0.02519603282416938 * self.n

            # JS: n = h >>> 0; (Forces float to 32-bit unsigned int)
            n_trunc = int(h) & 0xFFFFFFFF

            h -= n_trunc
            h *= n_trunc

            # JS: n = h >>> 0;
            n_trunc2 = int(h) & 0xFFFFFFFF

            h -= n_trunc2
            self.n = n_trunc2 + h * 0x100000000

        # JS: return (n >>> 0) * 2.3283064365386963e-10;
        return (int(self.n) & 0xFFFFFFFF) * 2.3283064365386963e-10


class FakkuRNG:
    def __init__(self, seed):
        self.c = 1
        self.p = 48
        self.s = [0.0] * 48
        self.mash = Mash()

        # Initialize state
        for i in range(48):
            self.s[i] = self.mash.update(' ')

        self.c = 1
        self.p = 48

        # Hash the seed
        if seed is not None:
            self.hash_string(seed)

    def hash_string(self, seed):
        seed_str = str(seed)
        self.mash.update(seed_str)

        for char in seed_str:
            char_code = ord(char)
            for j in range(48):
                self.s[j] -= self.mash.update(char_code)
                if self.s[j] < 0:
                    self.s[j] += 1

    def next(self):
        self.p += 1
        if self.p >= 48:
            self.p = 0

        # JS: Multiply-With-Carry
        t = 1768863 * self.s[self.p] + self.c * 2.3283064365386963e-10

        # JS: c = t | 0; (Bitwise OR 0 forces it to a signed 32-bit int)
        c_int = int(t) & 0xFFFFFFFF
        if c_int >= 0x80000000:
            c_int -= 0x100000000

        self.c = c_int
        self.s[self.p] = t - self.c
        return self.s[self.p]

    def rand_func(self, bound):
        n1 = self.next()
        n2 = self.next()
        # 1.1102230246251565e-16 is exactly 2^-53
        return int(bound * (n1 + int(n2 * 0x200000) * 1.1102230246251565e-16))

    def random(self):
        js_max_value = 1.7976931348623157e+308
        return self.rand_func(js_max_value - 1) / js_max_value


def generate_shuffled_map(total, seed):
    rng = FakkuRNG(seed)

    # Create an array of [0, 1, 2, ..., total-1]
    arr = list(range(total))
    count = total

    # Loop backward and swap pieces randomly
    while count > 0:
        count -= 1
        rand_val = rng.random()
        idx = int(rand_val * (count + 1))  # JS: ~~ (truncate to int)
        arr[idx], arr[count] = arr[count], arr[idx]

    return arr

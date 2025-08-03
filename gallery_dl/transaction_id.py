# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

# Adapted from iSarabjitDhiman/XClientTransaction
# https://github.com/iSarabjitDhiman/XClientTransaction

# References:
# https://antibot.blog/posts/1741552025433
# https://antibot.blog/posts/1741552092462
# https://antibot.blog/posts/1741552163416

"""Twitter 'x-client-transaction-id' header generation"""

import math
import time
import random
import hashlib
import binascii
import itertools
from . import text, util
from .cache import cache


class ClientTransaction():
    __slots__ = ("key_bytes", "animation_key")

    def __getstate__(self):
        return (self.key_bytes, self.animation_key)

    def __setstate__(self, state):
        self.key_bytes, self.animation_key = state

    def initialize(self, extractor, homepage=None):
        if homepage is None:
            homepage = extractor.request("https://x.com/").text

        key = self._extract_verification_key(homepage)
        if not key:
            extractor.log.error(
                "Failed to extract 'twitter-site-verification' key")

        ondemand_s = text.extr(homepage, '"ondemand.s":"', '"')
        indices = self._extract_indices(ondemand_s, extractor)
        if not indices:
            extractor.log.error("Failed to extract KEY_BYTE indices")

        frames = self._extract_frames(homepage)
        if not frames:
            extractor.log.error("Failed to extract animation frame data")

        self.key_bytes = key_bytes = binascii.a2b_base64(key)
        self.animation_key = self._calculate_animation_key(
            frames, indices[0], key_bytes, indices[1:])

    def _extract_verification_key(self, homepage):
        pos = homepage.find('name="twitter-site-verification"')
        beg = homepage.rfind("<", 0, pos)
        end = homepage.find(">", pos)
        return text.extr(homepage[beg:end], 'content="', '"')

    @cache(maxage=36500*86400, keyarg=1)
    def _extract_indices(self, ondemand_s, extractor):
        url = (f"https://abs.twimg.com/responsive-web/client-web"
               f"/ondemand.s.{ondemand_s}a.js")
        page = extractor.request(url).text
        pattern = util.re_compile(r"\(\w\[(\d\d?)\],\s*16\)")
        return [int(i) for i in pattern.findall(page)]

    def _extract_frames(self, homepage):
        return list(text.extract_iter(
            homepage, 'id="loading-x-anim-', "</svg>"))

    def _calculate_animation_key(self, frames, row_index, key_bytes,
                                 key_bytes_indices, total_time=4096):
        frame = frames[key_bytes[5] % 4]
        array = self._generate_2d_array(frame)
        frame_row = array[key_bytes[row_index] % 16]

        frame_time = 1
        for index in key_bytes_indices:
            frame_time *= key_bytes[index] % 16
        frame_time = round_js(frame_time / 10) * 10
        target_time = frame_time / total_time

        return self.animate(frame_row, target_time)

    def _generate_2d_array(self, frame):
        split = util.re_compile(r"[^\d]+").split
        return [
            [int(x) for x in split(path) if x]
            for path in text.extr(
                frame, '</path><path d="', '"')[9:].split("C")
        ]

    def animate(self, frames, target_time):
        curve = [scale(float(frame), is_odd(index), 1.0, False)
                 for index, frame in enumerate(frames[7:])]
        cubic = cubic_value(curve, target_time)

        color_a = (float(frames[0]), float(frames[1]), float(frames[2]))
        color_b = (float(frames[3]), float(frames[4]), float(frames[5]))
        color = interpolate_list(cubic, color_a, color_b)
        color = [0.0 if c <= 0.0 else 255.0 if c >= 255.0 else c
                 for c in color]

        rotation_a = 0.0
        rotation_b = scale(float(frames[6]), 60.0, 360.0, True)
        rotation = interpolate_value(cubic, rotation_a, rotation_b)
        matrix = rotation_matrix_2d(rotation)

        result = (
            hex(round(color[0]))[2:],
            hex(round(color[1]))[2:],
            hex(round(color[2]))[2:],
            float_to_hex(abs(round(matrix[0], 2))),
            float_to_hex(abs(round(matrix[1], 2))),
            float_to_hex(abs(round(matrix[2], 2))),
            float_to_hex(abs(round(matrix[3], 2))),
            "00",
        )
        return "".join(result).replace(".", "").replace("-", "")

    def generate_transaction_id(self, method, path,
                                keyword="obfiowerehiring", rndnum=3):
        bytes_key = self.key_bytes

        nowf = time.time()
        nowi = int(nowf)
        now = nowi - 1682924400
        bytes_time = (
            (now      ) & 0xFF,  # noqa: E202
            (now >>  8) & 0xFF,  # noqa: E222
            (now >> 16) & 0xFF,
            (now >> 24) & 0xFF,
        )

        payload = f"{method}!{path}!{now}{keyword}{self.animation_key}"
        bytes_hash = hashlib.sha256(payload.encode()).digest()[:16]

        num = (random.randrange(16) << 4) + int((nowf - nowi) * 16.0)
        result = bytes(
            byte ^ num
            for byte in itertools.chain(
                (0,), bytes_key, bytes_time, bytes_hash, (rndnum,))
        )
        return binascii.b2a_base64(result).rstrip(b"=\n")


# Cubic Curve

def cubic_value(curve, t):
    if t <= 0.0:
        if curve[0] > 0.0:
            value = curve[1] / curve[0]
        elif curve[1] == 0.0 and curve[2] > 0.0:
            value = curve[3] / curve[2]
        else:
            value = 0.0
        return value * t

    if t >= 1.0:
        if curve[2] < 1.0:
            value = (curve[3] - 1.0) / (curve[2] - 1.0)
        elif curve[2] == 1.0 and curve[0] < 1.0:
            value = (curve[1] - 1.0) / (curve[0] - 1.0)
        else:
            value = 0.0
        return 1.0 + value * (t - 1.0)

    start = 0.0
    end = 1.0
    while start < end:
        mid = (start + end) / 2.0
        est = cubic_calculate(curve[0], curve[2], mid)
        if abs(t - est) < 0.00001:
            return cubic_calculate(curve[1], curve[3], mid)
        if est < t:
            start = mid
        else:
            end = mid
    return cubic_calculate(curve[1], curve[3], mid)


def cubic_calculate(a, b, m):
    m1 = 1.0 - m
    return 3.0*a*m1*m1*m + 3.0*b*m1*m*m + m*m*m


# Interpolation

def interpolate_list(x, a, b):
    return [
        interpolate_value(x, a[i], b[i])
        for i in range(len(a))
    ]


def interpolate_value(x, a, b):
    if isinstance(a, bool):
        return a if x <= 0.5 else b
    return a * (1.0 - x) + b * x


# Rotation

def rotation_matrix_2d(deg):
    rad = math.radians(deg)
    cos = math.cos(rad)
    sin = math.sin(rad)
    return [cos, -sin, sin, cos]


# Utilities

def float_to_hex(numf):
    numi = int(numf)

    fraction = numf - numi
    if not fraction:
        return hex(numi)[2:]

    result = ["."]
    while fraction > 0.0:
        fraction *= 16.0
        integer = int(fraction)
        fraction -= integer
        result.append(chr(integer + 87) if integer > 9 else str(integer))
    return hex(numi)[2:] + "".join(result)


def is_odd(num):
    return -1.0 if num % 2 else 0.0


def round_js(num):
    floor = math.floor(num)
    return floor if (num - floor) < 0.5 else math.ceil(num)


def scale(value, value_min, value_max, rounding):
    result = value * (value_max-value_min) / 255.0 + value_min
    return math.floor(result) if rounding else round(result, 2)

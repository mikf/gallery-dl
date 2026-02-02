# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""VRF generation utils

adapted from dazedcat19/FMD2
https://github.com/dazedcat19/FMD2/blob/master/lua/modules/MangaFire.lua
"""

from ... import text
import binascii


def generate(input):
    input = text.quote(input).encode()

    for key_b64, seed_b64, prefix_b64, schedule in (
        (key_l, seed_A, prefix_O, schedule_c),
        (key_g, seed_V, prefix_v, schedule_y),
        (key_B, seed_N, prefix_L, schedule_b),
        (key_m, seed_P, prefix_p, schedule_j),
        (key_F, seed_k, prefix_W, schedule_e),
    ):
        input = transform(
            rc4(binascii.a2b_base64(key_b64), input),
            binascii.a2b_base64(seed_b64),
            binascii.a2b_base64(prefix_b64),
            schedule,
        )

    return binascii.b2a_base64(bytes(input), newline=False).rstrip(
        b"=").replace(b"+", b"-").replace(b"/", b"_")


def transform(input, seed, prefix, schedule):
    prefix_len = len(prefix)

    out = []
    for idx, c in enumerate(input):
        if idx < prefix_len:
            out.append(prefix[idx] or 0)
        out.append(schedule[idx % 10]((c ^ seed[idx % 32]) & 255) & 255)
    return out


def rc4(key, input):
    lkey = len(key)

    j = 0
    s = list(range(256))
    for i in range(256):
        j = (j + s[i] + key[i % lkey]) & 255
        s[i], s[j] = s[j], s[i]

    out = []
    i = j = 0
    for c in input:
        i = (i + 1) & 255
        j = (j + s[i]) & 255
        s[i], s[j] = s[j], s[i]
        k = s[(s[i] + s[j]) & 255]
        out.append(c ^ k)
    return out


def add8(n):
    return lambda c: (c + n) & 255


def sub8(n):
    return lambda c: (c - n + 256) & 255


def xor8(n):
    return lambda c: (c ^ n) & 255


def rotl8(n):
    return lambda c: ((c << n) | (c >> (8 - n))) & 255


def rotr8(n):
    return lambda c: ((c >> n) | (c << (8 - n))) & 255


schedule_c = (
    sub8(223), rotr8(4), rotr8(4), add8(234), rotr8(7),
    rotr8(2), rotr8(7), sub8(223), rotr8(7), rotr8(6),
)
schedule_y = (
    add8(19), rotr8(7), add8(19), rotr8(6), add8(19),
    rotr8(1), add8(19), rotr8(6), rotr8(7), rotr8(4),
)
schedule_b = (
    sub8(223), rotr8(1), add8(19), sub8(223), rotl8(2),
    sub8(223), add8(19), rotl8(1), rotl8(2), rotl8(1),
)
schedule_j = (
    add8(19), rotl8(1), rotl8(1), rotr8(1), add8(234),
    rotl8(1), sub8(223), rotl8(6), rotl8(4), rotl8(1),
)
schedule_e = (
    rotr8(1), rotl8(1), rotl8(6), rotr8(1), rotl8(2),
    rotr8(4), rotl8(1), rotl8(1), sub8(223), rotl8(2),
)


key_l = "FgxyJUQDPUGSzwbAq/ToWn4/e8jYzvabE+dLMb1XU1o="
key_g = "CQx3CLwswJAnM1VxOqX+y+f3eUns03ulxv8Z+0gUyik="
key_B = "fAS+otFLkKsKAJzu3yU+rGOlbbFVq+u+LaS6+s1eCJs="
key_m = "Oy45fQVK9kq9019+VysXVlz1F9S1YwYKgXyzGlZrijo="
key_F = "aoDIdXezm2l3HrcnQdkPJTDT8+W6mcl2/02ewBHfPzg="

seed_A = "yH6MXnMEcDVWO/9a6P9W92BAh1eRLVFxFlWTHUqQ474="
seed_V = "RK7y4dZ0azs9Uqz+bbFB46Bx2K9EHg74ndxknY9uknA="
seed_N = "rqr9HeTQOg8TlFiIGZpJaxcvAaKHwMwrkqojJCpcvoc="
seed_P = "/4GPpmZXYpn5RpkP7FC/dt8SXz7W30nUZTe8wb+3xmU="
seed_k = "wsSGSBXKWA9q1oDJpjtJddVxH+evCfL5SO9HZnUDFU8="

prefix_O = "l9PavRg="
prefix_v = "Ml2v7ag1Jg=="
prefix_L = "i/Va0UxrbMo="
prefix_p = "WFjKAHGEkQM="
prefix_W = "5Rr27rWd"

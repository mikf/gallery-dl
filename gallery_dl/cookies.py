# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

# Adapted from yt-dlp's cookies module.
# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/cookies.py

import binascii
import ctypes
import logging
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
from hashlib import pbkdf2_hmac
from http.cookiejar import Cookie
from . import aes, text, util


SUPPORTED_BROWSERS_CHROMIUM = {
    "brave", "chrome", "chromium", "edge", "opera", "thorium", "vivaldi"}
SUPPORTED_BROWSERS = SUPPORTED_BROWSERS_CHROMIUM | {"firefox", "safari"}

logger = logging.getLogger("cookies")


def load_cookies(browser_specification):
    browser_name, profile, keyring, container, domain = \
        _parse_browser_specification(*browser_specification)
    if browser_name == "firefox":
        return load_cookies_firefox(profile, container, domain)
    elif browser_name == "safari":
        return load_cookies_safari(profile, domain)
    elif browser_name in SUPPORTED_BROWSERS_CHROMIUM:
        return load_cookies_chromium(browser_name, profile, keyring, domain)
    else:
        raise ValueError("unknown browser '{}'".format(browser_name))


def load_cookies_firefox(profile=None, container=None, domain=None):
    path, container_id = _firefox_cookies_database(profile, container)

    sql = ("SELECT name, value, host, path, isSecure, expiry "
           "FROM moz_cookies")
    conditions = []
    parameters = []

    if container_id is False:
        conditions.append("NOT INSTR(originAttributes,'userContextId=')")
    elif container_id:
        uid = "%userContextId={}".format(container_id)
        conditions.append("originAttributes LIKE ? OR originAttributes LIKE ?")
        parameters += (uid, uid + "&%")

    if domain:
        if domain[0] == ".":
            conditions.append("host == ? OR host LIKE ?")
            parameters += (domain[1:], "%" + domain)
        else:
            conditions.append("host == ? OR host == ?")
            parameters += (domain, "." + domain)

    if conditions:
        sql = "{} WHERE ( {} )".format(sql, " ) AND ( ".join(conditions))

    with DatabaseConnection(path) as db:
        cookies = [
            Cookie(
                0, name, value, None, False,
                domain, True if domain else False,
                domain[0] == "." if domain else False,
                path, True if path else False, secure, expires,
                False, None, None, {},
            )
            for name, value, domain, path, secure, expires in db.execute(
                sql, parameters)
        ]

    _log_info("Extracted %s cookies from Firefox", len(cookies))
    return cookies


def load_cookies_safari(profile=None, domain=None):
    """Ref.: https://github.com/libyal/dtformats/blob
             /main/documentation/Safari%20Cookies.asciidoc
    - This data appears to be out of date
      but the important parts of the database structure is the same
    - There are a few bytes here and there
      which are skipped during parsing
    """
    with _safari_cookies_database() as fp:
        data = fp.read()
    page_sizes, body_start = _safari_parse_cookies_header(data)
    p = DataParser(data[body_start:])

    cookies = []
    for page_size in page_sizes:
        _safari_parse_cookies_page(p.read_bytes(page_size), cookies)
    _log_info("Extracted %s cookies from Safari", len(cookies))
    return cookies


def load_cookies_chromium(browser_name, profile=None,
                          keyring=None, domain=None):
    config = _chromium_browser_settings(browser_name)
    path = _chromium_cookies_database(profile, config)
    _log_debug("Extracting cookies from %s", path)

    if domain:
        if domain[0] == ".":
            condition = " WHERE host_key == ? OR host_key LIKE ?"
            parameters = (domain[1:], "%" + domain)
        else:
            condition = " WHERE host_key == ? OR host_key == ?"
            parameters = (domain, "." + domain)
    else:
        condition = ""
        parameters = ()

    with DatabaseConnection(path) as db:
        db.text_factory = bytes
        cursor = db.cursor()

        try:
            meta_version = int(cursor.execute(
                "SELECT value FROM meta WHERE key = 'version'").fetchone()[0])
        except Exception as exc:
            _log_warning("Failed to get cookie database meta version (%s: %s)",
                         exc.__class__.__name__, exc)
            meta_version = 0

        try:
            rows = cursor.execute(
                "SELECT host_key, name, value, encrypted_value, path, "
                "expires_utc, is_secure FROM cookies" + condition, parameters)
        except sqlite3.OperationalError:
            rows = cursor.execute(
                "SELECT host_key, name, value, encrypted_value, path, "
                "expires_utc, secure FROM cookies" + condition, parameters)

        failed_cookies = 0
        unencrypted_cookies = 0
        decryptor = _chromium_cookie_decryptor(
            config["directory"], config["keyring"], keyring, meta_version)

        cookies = []
        for domain, name, value, enc_value, path, expires, secure in rows:

            if not value and enc_value:  # encrypted
                value = decryptor.decrypt(enc_value)
                if value is None:
                    failed_cookies += 1
                    continue
            else:
                value = value.decode()
                unencrypted_cookies += 1

            if expires:
                # https://stackoverflow.com/a/43520042
                expires = int(expires) // 1000000 - 11644473600
            else:
                expires = None

            domain = domain.decode()
            path = path.decode()
            name = name.decode()

            cookies.append(Cookie(
                0, name, value, None, False,
                domain, True if domain else False,
                domain[0] == "." if domain else False,
                path, True if path else False, secure, expires,
                False, None, None, {},
            ))

    if failed_cookies > 0:
        failed_message = " ({} could not be decrypted)".format(failed_cookies)
    else:
        failed_message = ""

    _log_info("Extracted %s cookies from %s%s",
              len(cookies), browser_name.capitalize(), failed_message)
    counts = decryptor.cookie_counts
    counts["unencrypted"] = unencrypted_cookies
    _log_debug("version breakdown: %s", counts)
    return cookies


# --------------------------------------------------------------------
# firefox

def _firefox_cookies_database(profile=None, container=None):
    if not profile:
        search_root = _firefox_browser_directory()
    elif _is_path(profile):
        search_root = profile
    else:
        search_root = os.path.join(_firefox_browser_directory(), profile)

    path = _find_most_recently_used_file(search_root, "cookies.sqlite")
    if path is None:
        raise FileNotFoundError("Unable to find Firefox cookies database in "
                                "{}".format(search_root))
    _log_debug("Extracting cookies from %s", path)

    if not container or container == "none":
        container_id = False
        _log_debug("Only loading cookies not belonging to any container")

    elif container == "all":
        container_id = None

    else:
        containers_path = os.path.join(
            os.path.dirname(path), "containers.json")

        try:
            with open(containers_path) as fp:
                identities = util.json_loads(fp.read())["identities"]
        except OSError:
            _log_error("Unable to read Firefox container database at '%s'",
                       containers_path)
            raise
        except KeyError:
            identities = ()

        for context in identities:
            if container == context.get("name") or container == text.extr(
                    context.get("l10nID", ""), "userContext", ".label"):
                container_id = context["userContextId"]
                break
        else:
            raise ValueError("Unable to find Firefox container '{}'".format(
                container))
        _log_debug("Only loading cookies from container '%s' (ID %s)",
                   container, container_id)

    return path, container_id


def _firefox_browser_directory():
    if sys.platform in ("win32", "cygwin"):
        return os.path.expandvars(
            r"%APPDATA%\Mozilla\Firefox\Profiles")
    if sys.platform == "darwin":
        return os.path.expanduser(
            "~/Library/Application Support/Firefox/Profiles")
    return os.path.expanduser("~/.mozilla/firefox")


# --------------------------------------------------------------------
# safari

def _safari_cookies_database():
    try:
        path = os.path.expanduser("~/Library/Cookies/Cookies.binarycookies")
        return open(path, "rb")
    except FileNotFoundError:
        _log_debug("Trying secondary cookie location")
        path = os.path.expanduser("~/Library/Containers/com.apple.Safari/Data"
                                  "/Library/Cookies/Cookies.binarycookies")
        return open(path, "rb")


def _safari_parse_cookies_header(data):
    p = DataParser(data)
    p.expect_bytes(b"cook", "database signature")
    number_of_pages = p.read_uint(big_endian=True)
    page_sizes = [p.read_uint(big_endian=True)
                  for _ in range(number_of_pages)]
    return page_sizes, p.cursor


def _safari_parse_cookies_page(data, cookies, domain=None):
    p = DataParser(data)
    p.expect_bytes(b"\x00\x00\x01\x00", "page signature")
    number_of_cookies = p.read_uint()
    record_offsets = [p.read_uint() for _ in range(number_of_cookies)]
    if number_of_cookies == 0:
        _log_debug("Cookies page of size %s has no cookies", len(data))
        return

    p.skip_to(record_offsets[0], "unknown page header field")

    for i, record_offset in enumerate(record_offsets):
        p.skip_to(record_offset, "space between records")
        record_length = _safari_parse_cookies_record(
            data[record_offset:], cookies, domain)
        p.read_bytes(record_length)
    p.skip_to_end("space in between pages")


def _safari_parse_cookies_record(data, cookies, host=None):
    p = DataParser(data)
    record_size = p.read_uint()
    p.skip(4, "unknown record field 1")
    flags = p.read_uint()
    is_secure = True if (flags & 0x0001) else False
    p.skip(4, "unknown record field 2")
    domain_offset = p.read_uint()
    name_offset = p.read_uint()
    path_offset = p.read_uint()
    value_offset = p.read_uint()
    p.skip(8, "unknown record field 3")
    expiration_date = _mac_absolute_time_to_posix(p.read_double())
    _creation_date = _mac_absolute_time_to_posix(p.read_double())  # noqa: F841

    try:
        p.skip_to(domain_offset)
        domain = p.read_cstring()

        if host:
            if host[0] == ".":
                if host[1:] != domain and not domain.endswith(host):
                    return record_size
            else:
                if host != domain and ("." + host) != domain:
                    return record_size

        p.skip_to(name_offset)
        name = p.read_cstring()

        p.skip_to(path_offset)
        path = p.read_cstring()

        p.skip_to(value_offset)
        value = p.read_cstring()
    except UnicodeDecodeError:
        _log_warning("Failed to parse Safari cookie")
        return record_size

    p.skip_to(record_size, "space at the end of the record")

    cookies.append(Cookie(
        0, name, value, None, False,
        domain, True if domain else False,
        domain[0] == "." if domain else False,
        path, True if path else False, is_secure, expiration_date,
        False, None, None, {},
    ))

    return record_size


# --------------------------------------------------------------------
# chromium

def _chromium_cookies_database(profile, config):
    if profile is None:
        search_root = config["directory"]
    elif _is_path(profile):
        search_root = profile
        config["directory"] = (os.path.dirname(profile)
                               if config["profiles"] else profile)
    elif config["profiles"]:
        search_root = os.path.join(config["directory"], profile)
    else:
        _log_warning("%s does not support profiles", config["browser"])
        search_root = config["directory"]

    path = _find_most_recently_used_file(search_root, "Cookies")
    if path is None:
        raise FileNotFoundError("Unable to find {} cookies database in "
                                "'{}'".format(config["browser"], search_root))
    return path


def _chromium_browser_settings(browser_name):
    # https://chromium.googlesource.com/chromium
    # /src/+/HEAD/docs/user_data_dir.md
    join = os.path.join

    if sys.platform in ("win32", "cygwin"):
        appdata_local = os.path.expandvars("%LOCALAPPDATA%")
        appdata_roaming = os.path.expandvars("%APPDATA%")
        browser_dir = {
            "brave"   : join(appdata_local,
                             R"BraveSoftware\Brave-Browser\User Data"),
            "chrome"  : join(appdata_local, R"Google\Chrome\User Data"),
            "chromium": join(appdata_local, R"Chromium\User Data"),
            "edge"    : join(appdata_local, R"Microsoft\Edge\User Data"),
            "opera"   : join(appdata_roaming, R"Opera Software\Opera Stable"),
            "thorium" : join(appdata_local, R"Thorium\User Data"),
            "vivaldi" : join(appdata_local, R"Vivaldi\User Data"),
        }[browser_name]

    elif sys.platform == "darwin":
        appdata = os.path.expanduser("~/Library/Application Support")
        browser_dir = {
            "brave"   : join(appdata, "BraveSoftware/Brave-Browser"),
            "chrome"  : join(appdata, "Google/Chrome"),
            "chromium": join(appdata, "Chromium"),
            "edge"    : join(appdata, "Microsoft Edge"),
            "opera"   : join(appdata, "com.operasoftware.Opera"),
            "thorium" : join(appdata, "Thorium"),
            "vivaldi" : join(appdata, "Vivaldi"),
        }[browser_name]

    else:
        config = (os.environ.get("XDG_CONFIG_HOME") or
                  os.path.expanduser("~/.config"))
        browser_dir = {
            "brave"   : join(config, "BraveSoftware/Brave-Browser"),
            "chrome"  : join(config, "google-chrome"),
            "chromium": join(config, "chromium"),
            "edge"    : join(config, "microsoft-edge"),
            "opera"   : join(config, "opera"),
            "thorium" : join(config, "Thorium"),
            "vivaldi" : join(config, "vivaldi"),
        }[browser_name]

    # Linux keyring names can be determined by snooping on dbus
    # while opening the browser in KDE:
    # dbus-monitor "interface="org.kde.KWallet"" "type=method_return"
    keyring_name = {
        "brave"   : "Brave",
        "chrome"  : "Chrome",
        "chromium": "Chromium",
        "edge"    : "Microsoft Edge" if sys.platform == "darwin" else
                    "Chromium",
        "opera"   : "Opera" if sys.platform == "darwin" else "Chromium",
        "thorium" : "Thorium",
        "vivaldi" : "Vivaldi" if sys.platform == "darwin" else "Chrome",
    }[browser_name]

    browsers_without_profiles = {"opera"}

    return {
        "browser"  : browser_name,
        "directory": browser_dir,
        "keyring"  : keyring_name,
        "profiles" : browser_name not in browsers_without_profiles
    }


def _chromium_cookie_decryptor(
        browser_root, browser_keyring_name, keyring=None, meta_version=0):
    if sys.platform in ("win32", "cygwin"):
        return WindowsChromiumCookieDecryptor(
            browser_root, meta_version)
    elif sys.platform == "darwin":
        return MacChromiumCookieDecryptor(
            browser_keyring_name, meta_version)
    else:
        return LinuxChromiumCookieDecryptor(
            browser_keyring_name, keyring, meta_version)


class ChromiumCookieDecryptor:
    """
    Overview:

        Linux:
        - cookies are either v10 or v11
            - v10: AES-CBC encrypted with a fixed key
            - v11: AES-CBC encrypted with an OS protected key (keyring)
            - v11 keys can be stored in various places depending on the
              activate desktop environment [2]

        Mac:
        - cookies are either v10 or not v10
            - v10: AES-CBC encrypted with an OS protected key (keyring)
              and more key derivation iterations than linux
            - not v10: "old data" stored as plaintext

        Windows:
        - cookies are either v10 or not v10
            - v10: AES-GCM encrypted with a key which is encrypted with DPAPI
            - not v10: encrypted with DPAPI

    Sources:
    - [1] https://chromium.googlesource.com/chromium/src/+/refs/heads
          /main/components/os_crypt/
    - [2] https://chromium.googlesource.com/chromium/src/+/refs/heads
          /main/components/os_crypt/key_storage_linux.cc
        - KeyStorageLinux::CreateService
    """

    def decrypt(self, encrypted_value):
        raise NotImplementedError("Must be implemented by sub classes")

    @property
    def cookie_counts(self):
        raise NotImplementedError("Must be implemented by sub classes")


class LinuxChromiumCookieDecryptor(ChromiumCookieDecryptor):
    def __init__(self, browser_keyring_name, keyring=None, meta_version=0):
        password = _get_linux_keyring_password(browser_keyring_name, keyring)
        self._empty_key = self.derive_key(b"")
        self._v10_key = self.derive_key(b"peanuts")
        self._v11_key = None if password is None else self.derive_key(password)
        self._cookie_counts = {"v10": 0, "v11": 0, "other": 0}
        self._offset = (32 if meta_version >= 24 else 0)

    @staticmethod
    def derive_key(password):
        # values from
        # https://chromium.googlesource.com/chromium/src/+/refs/heads
        # /main/components/os_crypt/os_crypt_linux.cc
        return pbkdf2_sha1(password, salt=b"saltysalt",
                           iterations=1, key_length=16)

    @property
    def cookie_counts(self):
        return self._cookie_counts

    def decrypt(self, encrypted_value):
        version = encrypted_value[:3]
        ciphertext = encrypted_value[3:]

        if version == b"v10":
            self._cookie_counts["v10"] += 1
            value = _decrypt_aes_cbc(ciphertext, self._v10_key, self._offset)

        elif version == b"v11":
            self._cookie_counts["v11"] += 1
            if self._v11_key is None:
                _log_warning("Unable to decrypt v11 cookies: no key found")
                return None
            value = _decrypt_aes_cbc(ciphertext, self._v11_key, self._offset)

        else:
            self._cookie_counts["other"] += 1
            return None

        if value is None:
            value = _decrypt_aes_cbc(ciphertext, self._empty_key, self._offset)
            if value is None:
                _log_warning("Failed to decrypt cookie (AES-CBC)")
        return value


class MacChromiumCookieDecryptor(ChromiumCookieDecryptor):
    def __init__(self, browser_keyring_name, meta_version=0):
        password = _get_mac_keyring_password(browser_keyring_name)
        self._v10_key = None if password is None else self.derive_key(password)
        self._cookie_counts = {"v10": 0, "other": 0}
        self._offset = (32 if meta_version >= 24 else 0)

    @staticmethod
    def derive_key(password):
        # values from
        # https://chromium.googlesource.com/chromium/src/+/refs/heads
        # /main/components/os_crypt/os_crypt_mac.mm
        return pbkdf2_sha1(password, salt=b"saltysalt",
                           iterations=1003, key_length=16)

    @property
    def cookie_counts(self):
        return self._cookie_counts

    def decrypt(self, encrypted_value):
        version = encrypted_value[:3]
        ciphertext = encrypted_value[3:]

        if version == b"v10":
            self._cookie_counts["v10"] += 1
            if self._v10_key is None:
                _log_warning("Unable to decrypt v10 cookies: no key found")
                return None
            return _decrypt_aes_cbc(ciphertext, self._v10_key, self._offset)

        else:
            self._cookie_counts["other"] += 1
            # other prefixes are considered "old data",
            # which were stored as plaintext
            # https://chromium.googlesource.com/chromium/src/+/refs/heads
            # /main/components/os_crypt/os_crypt_mac.mm
            return encrypted_value


class WindowsChromiumCookieDecryptor(ChromiumCookieDecryptor):
    def __init__(self, browser_root, meta_version=0):
        self._v10_key = _get_windows_v10_key(browser_root)
        self._cookie_counts = {"v10": 0, "other": 0}
        self._offset = (32 if meta_version >= 24 else 0)

    @property
    def cookie_counts(self):
        return self._cookie_counts

    def decrypt(self, encrypted_value):
        version = encrypted_value[:3]
        ciphertext = encrypted_value[3:]

        if version == b"v10":
            self._cookie_counts["v10"] += 1
            if self._v10_key is None:
                _log_warning("Unable to decrypt v10 cookies: no key found")
                return None

            # https://chromium.googlesource.com/chromium/src/+/refs/heads
            # /main/components/os_crypt/os_crypt_win.cc
            #   kNonceLength
            nonce_length = 96 // 8
            # boringssl
            #   EVP_AEAD_AES_GCM_TAG_LEN
            authentication_tag_length = 16

            raw_ciphertext = ciphertext
            nonce = raw_ciphertext[:nonce_length]
            ciphertext = raw_ciphertext[
                nonce_length:-authentication_tag_length]
            authentication_tag = raw_ciphertext[-authentication_tag_length:]

            return _decrypt_aes_gcm(
                ciphertext, self._v10_key, nonce, authentication_tag,
                self._offset)

        else:
            self._cookie_counts["other"] += 1
            # any other prefix means the data is DPAPI encrypted
            # https://chromium.googlesource.com/chromium/src/+/refs/heads
            # /main/components/os_crypt/os_crypt_win.cc
            return _decrypt_windows_dpapi(encrypted_value).decode()


# --------------------------------------------------------------------
# keyring

def _choose_linux_keyring():
    """
    https://chromium.googlesource.com/chromium/src/+/refs/heads
    /main/components/os_crypt/key_storage_util_linux.cc
    SelectBackend
    """
    desktop_environment = _get_linux_desktop_environment(os.environ)
    _log_debug("Detected desktop environment: %s", desktop_environment)
    if desktop_environment == DE_KDE:
        return KEYRING_KWALLET
    if desktop_environment == DE_OTHER:
        return KEYRING_BASICTEXT
    return KEYRING_GNOMEKEYRING


def _get_kwallet_network_wallet():
    """ The name of the wallet used to store network passwords.

    https://chromium.googlesource.com/chromium/src/+/refs/heads
    /main/components/os_crypt/kwallet_dbus.cc
    KWalletDBus::NetworkWallet
    which does a dbus call to the following function:
    https://api.kde.org/frameworks/kwallet/html/classKWallet_1_1Wallet.html
    Wallet::NetworkWallet
    """
    default_wallet = "kdewallet"
    try:
        proc, stdout = Popen_communicate(
            "dbus-send", "--session", "--print-reply=literal",
            "--dest=org.kde.kwalletd5",
            "/modules/kwalletd5",
            "org.kde.KWallet.networkWallet"
        )

        if proc.returncode != 0:
            _log_warning("Failed to read NetworkWallet")
            return default_wallet
        else:
            network_wallet = stdout.decode().strip()
            _log_debug("NetworkWallet = '%s'", network_wallet)
            return network_wallet
    except Exception as exc:
        _log_warning("Error while obtaining NetworkWallet (%s: %s)",
                     exc.__class__.__name__, exc)
        return default_wallet


def _get_kwallet_password(browser_keyring_name):
    _log_debug("Using kwallet-query to obtain password from kwallet")

    if shutil.which("kwallet-query") is None:
        _log_error(
            "kwallet-query command not found. KWallet and kwallet-query "
            "must be installed to read from KWallet. kwallet-query should be "
            "included in the kwallet package for your distribution")
        return b""

    network_wallet = _get_kwallet_network_wallet()

    try:
        proc, stdout = Popen_communicate(
            "kwallet-query",
            "--read-password", browser_keyring_name + " Safe Storage",
            "--folder", browser_keyring_name + " Keys",
            network_wallet,
        )

        if proc.returncode != 0:
            _log_error("kwallet-query failed with return code {}. "
                       "Please consult the kwallet-query man page "
                       "for details".format(proc.returncode))
            return b""

        if stdout.lower().startswith(b"failed to read"):
            _log_debug("Failed to read password from kwallet. "
                       "Using empty string instead")
            # This sometimes occurs in KDE because chrome does not check
            # hasEntry and instead just tries to read the value (which
            # kwallet returns "") whereas kwallet-query checks hasEntry.
            # To verify this:
            # dbus-monitor "interface="org.kde.KWallet"" "type=method_return"
            # while starting chrome.
            # This may be a bug, as the intended behaviour is to generate a
            # random password and store it, but that doesn't matter here.
            return b""
        else:
            if stdout[-1:] == b"\n":
                stdout = stdout[:-1]
            return stdout
    except Exception as exc:
        _log_warning("Error when running kwallet-query (%s: %s)",
                     exc.__class__.__name__, exc)
        return b""


def _get_gnome_keyring_password(browser_keyring_name):
    try:
        import secretstorage
    except ImportError:
        _log_error("'secretstorage' Python package not available")
        return b""

    # Gnome keyring does not seem to organise keys in the same way as KWallet,
    # using `dbus-monitor` during startup, it can be observed that chromium
    # lists all keys and presumably searches for its key in the list.
    # It appears that we must do the same.
    # https://github.com/jaraco/keyring/issues/556
    con = secretstorage.dbus_init()
    try:
        col = secretstorage.get_default_collection(con)
        label = browser_keyring_name + " Safe Storage"
        for item in col.get_all_items():
            if item.get_label() == label:
                return item.get_secret()
        else:
            _log_error("Failed to read from GNOME keyring")
            return b""
    finally:
        con.close()


def _get_linux_keyring_password(browser_keyring_name, keyring):
    # Note: chrome/chromium can be run with the following flags
    # to determine which keyring backend it has chosen to use
    # - chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
    #
    # Chromium supports --password-store=<basic|gnome|kwallet>
    # so the automatic detection will not be sufficient in all cases.

    if not keyring:
        keyring = _choose_linux_keyring()
    _log_debug("Chosen keyring: %s", keyring)

    if keyring == KEYRING_KWALLET:
        return _get_kwallet_password(browser_keyring_name)
    elif keyring == KEYRING_GNOMEKEYRING:
        return _get_gnome_keyring_password(browser_keyring_name)
    elif keyring == KEYRING_BASICTEXT:
        # when basic text is chosen, all cookies are stored as v10
        # so no keyring password is required
        return None
    assert False, "Unknown keyring " + keyring


def _get_mac_keyring_password(browser_keyring_name):
    _log_debug("Using find-generic-password to obtain "
               "password from OSX keychain")
    try:
        proc, stdout = Popen_communicate(
            "security", "find-generic-password",
            "-w",  # write password to stdout
            "-a", browser_keyring_name,  # match "account"
            "-s", browser_keyring_name + " Safe Storage",  # match "service"
        )

        if stdout[-1:] == b"\n":
            stdout = stdout[:-1]
        return stdout
    except Exception as exc:
        _log_warning("Error when using find-generic-password (%s: %s)",
                     exc.__class__.__name__, exc)
        return None


def _get_windows_v10_key(browser_root):
    path = _find_most_recently_used_file(browser_root, "Local State")
    if path is None:
        _log_error("Unable to find Local State file")
        return None
    _log_debug("Found Local State file at '%s'", path)
    with open(path, encoding="utf-8") as fp:
        data = util.json_loads(fp.read())
    try:
        base64_key = data["os_crypt"]["encrypted_key"]
    except KeyError:
        _log_error("Unable to find encrypted key in Local State")
        return None
    encrypted_key = binascii.a2b_base64(base64_key)
    prefix = b"DPAPI"
    if not encrypted_key.startswith(prefix):
        _log_error("Invalid Local State key")
        return None
    return _decrypt_windows_dpapi(encrypted_key[len(prefix):])


# --------------------------------------------------------------------
# utility

class ParserError(Exception):
    pass


class DataParser:
    def __init__(self, data):
        self.cursor = 0
        self._data = data

    def read_bytes(self, num_bytes):
        if num_bytes < 0:
            raise ParserError("invalid read of {} bytes".format(num_bytes))
        end = self.cursor + num_bytes
        if end > len(self._data):
            raise ParserError("reached end of input")
        data = self._data[self.cursor:end]
        self.cursor = end
        return data

    def expect_bytes(self, expected_value, message):
        value = self.read_bytes(len(expected_value))
        if value != expected_value:
            raise ParserError("unexpected value: {} != {} ({})".format(
                value, expected_value, message))

    def read_uint(self, big_endian=False):
        data_format = ">I" if big_endian else "<I"
        return struct.unpack(data_format, self.read_bytes(4))[0]

    def read_double(self, big_endian=False):
        data_format = ">d" if big_endian else "<d"
        return struct.unpack(data_format, self.read_bytes(8))[0]

    def read_cstring(self):
        buffer = []
        while True:
            c = self.read_bytes(1)
            if c == b"\x00":
                return b"".join(buffer).decode()
            else:
                buffer.append(c)

    def skip(self, num_bytes, description="unknown"):
        if num_bytes > 0:
            _log_debug("Skipping {} bytes ({}): {!r}".format(
                num_bytes, description, self.read_bytes(num_bytes)))
        elif num_bytes < 0:
            raise ParserError("Invalid skip of {} bytes".format(num_bytes))

    def skip_to(self, offset, description="unknown"):
        self.skip(offset - self.cursor, description)

    def skip_to_end(self, description="unknown"):
        self.skip_to(len(self._data), description)


class DatabaseConnection():

    def __init__(self, path):
        self.path = path
        self.database = None
        self.directory = None

    def __enter__(self):
        try:
            # https://www.sqlite.org/uri.html#the_uri_path
            path = self.path.replace("?", "%3f").replace("#", "%23")
            if util.WINDOWS:
                path = "/" + os.path.abspath(path)

            uri = "file:{}?mode=ro&immutable=1".format(path)
            self.database = sqlite3.connect(
                uri, uri=True, isolation_level=None, check_same_thread=False)
            return self.database
        except Exception as exc:
            _log_debug("Falling back to temporary database copy (%s: %s)",
                       exc.__class__.__name__, exc)

        try:
            self.directory = tempfile.TemporaryDirectory(prefix="gallery-dl-")
            path_copy = os.path.join(self.directory.name, "copy.sqlite")
            shutil.copyfile(self.path, path_copy)
            self.database = sqlite3.connect(
                path_copy, isolation_level=None, check_same_thread=False)
            return self.database
        except BaseException:
            if self.directory:
                self.directory.cleanup()
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        self.database.close()
        if self.directory:
            self.directory.cleanup()


def Popen_communicate(*args):
    proc = util.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        stdout, stderr = proc.communicate()
    except BaseException:  # Including KeyboardInterrupt
        proc.kill()
        proc.wait()
        raise
    return proc, stdout


"""
https://chromium.googlesource.com/chromium/src/+/refs/heads
/main/base/nix/xdg_util.h - DesktopEnvironment
"""
DE_OTHER = "other"
DE_CINNAMON = "cinnamon"
DE_GNOME = "gnome"
DE_KDE = "kde"
DE_PANTHEON = "pantheon"
DE_UNITY = "unity"
DE_XFCE = "xfce"


"""
https://chromium.googlesource.com/chromium/src/+/refs/heads
/main/components/os_crypt/key_storage_util_linux.h - SelectedLinuxBackend
"""
KEYRING_KWALLET = "kwallet"
KEYRING_GNOMEKEYRING = "gnomekeyring"
KEYRING_BASICTEXT = "basictext"
SUPPORTED_KEYRINGS = {"kwallet", "gnomekeyring", "basictext"}


def _get_linux_desktop_environment(env):
    """
    Ref: https://chromium.googlesource.com/chromium/src/+/refs/heads
         /main/base/nix/xdg_util.cc - GetDesktopEnvironment
    """
    xdg_current_desktop = env.get("XDG_CURRENT_DESKTOP")
    desktop_session = env.get("DESKTOP_SESSION")

    if xdg_current_desktop:
        xdg_current_desktop = (xdg_current_desktop.partition(":")[0]
                               .strip().lower())

        if xdg_current_desktop == "unity":
            if desktop_session and "gnome-fallback" in desktop_session:
                return DE_GNOME
            else:
                return DE_UNITY
        elif xdg_current_desktop == "gnome":
            return DE_GNOME
        elif xdg_current_desktop == "x-cinnamon":
            return DE_CINNAMON
        elif xdg_current_desktop == "kde":
            return DE_KDE
        elif xdg_current_desktop == "pantheon":
            return DE_PANTHEON
        elif xdg_current_desktop == "xfce":
            return DE_XFCE

    if desktop_session:
        if desktop_session in ("mate", "gnome"):
            return DE_GNOME
        if "kde" in desktop_session:
            return DE_KDE
        if "xfce" in desktop_session:
            return DE_XFCE

    if "GNOME_DESKTOP_SESSION_ID" in env:
        return DE_GNOME
    if "KDE_FULL_SESSION" in env:
        return DE_KDE
    return DE_OTHER


def _mac_absolute_time_to_posix(timestamp):
    # 978307200 is timestamp of 2001-01-01 00:00:00
    return 978307200 + int(timestamp)


def pbkdf2_sha1(password, salt, iterations, key_length):
    return pbkdf2_hmac("sha1", password, salt, iterations, key_length)


def _decrypt_aes_cbc(ciphertext, key, offset=0,
                     initialization_vector=b" " * 16):
    plaintext = aes.unpad_pkcs7(aes.aes_cbc_decrypt_bytes(
        ciphertext, key, initialization_vector))
    if offset:
        plaintext = plaintext[offset:]
    try:
        return plaintext.decode()
    except UnicodeDecodeError:
        return None


def _decrypt_aes_gcm(ciphertext, key, nonce, authentication_tag, offset=0):
    try:
        plaintext = aes.aes_gcm_decrypt_and_verify_bytes(
            ciphertext, key, authentication_tag, nonce)
        if offset:
            plaintext = plaintext[offset:]
        return plaintext.decode()
    except UnicodeDecodeError:
        _log_warning("Failed to decrypt cookie (AES-GCM Unicode)")
    except ValueError:
        _log_warning("Failed to decrypt cookie (AES-GCM MAC)")
    return None


def _decrypt_windows_dpapi(ciphertext):
    """
    References:
        - https://docs.microsoft.com/en-us/windows
          /win32/api/dpapi/nf-dpapi-cryptunprotectdata
    """
    from ctypes.wintypes import DWORD

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_char))]

    buffer = ctypes.create_string_buffer(ciphertext)
    blob_in = DATA_BLOB(ctypes.sizeof(buffer), buffer)
    blob_out = DATA_BLOB()
    ret = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),  # pDataIn
        None,  # ppszDataDescr: human readable description of pDataIn
        None,  # pOptionalEntropy: salt?
        None,  # pvReserved: must be NULL
        None,  # pPromptStruct: information about prompts to display
        0,  # dwFlags
        ctypes.byref(blob_out)  # pDataOut
    )
    if not ret:
        _log_warning("Failed to decrypt cookie (DPAPI)")
        return None

    result = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return result


def _find_most_recently_used_file(root, filename):
    # if the provided root points to an exact profile path
    # check if it contains the wanted filename
    first_choice = os.path.join(root, filename)
    if os.path.exists(first_choice):
        return first_choice

    # if there are multiple browser profiles, take the most recently used one
    paths = []
    for curr_root, dirs, files in os.walk(root):
        for file in files:
            if file == filename:
                paths.append(os.path.join(curr_root, file))
    if not paths:
        return None
    return max(paths, key=lambda path: os.lstat(path).st_mtime)


def _is_path(value):
    return os.path.sep in value


def _parse_browser_specification(
        browser, profile=None, keyring=None, container=None, domain=None):
    browser = browser.lower()
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError("Unsupported browser '{}'".format(browser))
    if keyring and keyring not in SUPPORTED_KEYRINGS:
        raise ValueError("Unsupported keyring '{}'".format(keyring))
    if profile and _is_path(profile):
        profile = os.path.expanduser(profile)
    return browser, profile, keyring, container, domain


_log_cache = set()
_log_debug = logger.debug
_log_info = logger.info


def _log_warning(msg, *args):
    if msg not in _log_cache:
        _log_cache.add(msg)
        logger.warning(msg, *args)


def _log_error(msg, *args):
    if msg not in _log_cache:
        _log_cache.add(msg)
        logger.error(msg, *args)

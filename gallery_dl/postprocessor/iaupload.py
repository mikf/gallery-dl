from __future__ import unicode_literals

import configparser
import hashlib
import itertools
import json
import optparse
import os
import re
import shlex
import time
import urllib
from collections import defaultdict
from typing import IO, BinaryIO, Dict, Optional, Set
from xml.dom.minidom import parseString

from ._attachments import ShowsProgress
from .exec import ExecPP
from ..YoutubeDL import YoutubeDL
from ..compat import compat_HTTPError
from ..downloader import FileDownloader
from ..options import instantiate_parser
from ..longname import escaped_basename, escaped_remove
from ..utils import (
    PostProcessingError,
    ThrottledDownload,
    int_or_none,
    network_exceptions,
    sanitized_Request,
    time_millis,
    traverse_obj,
    variadic,
)


def _dict_from_options_callback(
        option, opt_str, value, parser,
        allowed_keys=r'[\w-]+', delimiter=':', default_key=None, process=None, multiple_keys=True,
        process_key=str.lower, append=False):

    out_dict = dict(getattr(parser.values, option.dest))
    multiple_args = not isinstance(value, str)
    if multiple_keys:
        allowed_keys = r'(%s)(,(%s))*' % (allowed_keys, allowed_keys)
    mobj = re.match(
        r'(?i)(?P<keys>%s)%s(?P<val>.*)$' % (allowed_keys, delimiter),
        value[0] if multiple_args else value)
    if mobj is not None:
        keys, val = mobj.group('keys').split(','), mobj.group('val')
        if multiple_args:
            val = [val, *value[1:]]
    elif default_key is not None:
        keys, val = [default_key], value
    else:
        raise optparse.OptionValueError(
            'wrong %s formatting; it should be %s, not "%s"' % (opt_str, option.metavar, value))
    try:
        keys = map(process_key, keys) if process_key else keys
        val = process(val) if process else val
    except Exception as err:
        raise optparse.OptionValueError(f'wrong {opt_str} formatting; {err}')
    for key in keys:
        out_dict[key] = out_dict.get(key, []) + [val] if append else val
    setattr(parser.values, option.dest, out_dict)


iaup_options = instantiate_parser()
iaup_options.set_usage('[OPTIONS] IDENTIFIER FILE [FILE...]')

iaup_options.add_option(
    '-q', '--quiet',
    action='store_true', dest='quiet',
    help='Runs without progress. Isolated from --quiet option from the outside')
iaup_options.add_option(
    '-d', '--debug',
    action='store_true', dest='debug',
    help='Runs in debug mode')

iaup_options.add_option(
    '-c', '--config',
    action='store_true', dest='config',
    help='Path to ia.ini. Defaults to where ia command searches')
iaup_options.add_option(
    '-u', '--username',
    dest='username', metavar='USERNAME',
    help='Login to Internet Archive with this account ID')
iaup_options.add_option(
    '-p', '--password',
    dest='password', metavar='PASSWORD',
    help='Account password for Internet Archive. If this option is left out, login will not be done')

iaup_options.add_option(
    '-r', '--remote-name',
    metavar='PATH', dest='remote_name',
    help='Path to remote directory or filename')
iaup_options.add_option(
    '-m', '--metadata',
    metavar='K:V', dest='metadata', default={},
    action='callback', callback=_dict_from_options_callback,
    callback_kwargs={'multiple_keys': False, 'process_key': None},
    help='Metadata to add')
iaup_options.add_option(
    '-H', '--header', '--headers',
    metavar='K:V', dest='headers', default={},
    action='callback', callback=_dict_from_options_callback,
    callback_kwargs={'multiple_keys': False, 'process_key': None},
    help='Header to add')
iaup_options.add_option(
    '-D', '--derive',
    action='store_true', dest='derive', default=False,
    help='Enables "derive" task on IA. derive task is not enabled by default')
iaup_options.add_option(
    '-n', '--no-derive',
    action='store_false', dest='derive', default=False,
    help='Disables "derive" task on IA.')
iaup_options.add_option(
    '-R', '--retries',
    metavar='RETRIES', dest='retries', default=10000,
    help='Number of retries on SlowDown or connection being disconnected.')
iaup_options.add_option(
    '-t', '--throttled-rate',
    metavar='RATE', dest='throttle',
    help=('Same as the option with same name on yt-dlp, but for upload in this time. '
          'Upload failure caused by this option will count for -R retries.'))
iaup_options.add_option(
    '-D', '--delete',
    action='store_true', dest='delete', default=False,
    help='Deletes files after all files are successfully uploaded.')
iaup_options.add_option(
    '-C', '--conflict-resolve',
    metavar='KIND:BEHAVIOR', dest='conflict_resolve', default={},
    action='callback', callback=_dict_from_options_callback,
    help=('Specifies how to avoid/torelate errors while uploading. '
          'Allowed values for KIND are: size_overflow, no_perm. '
          'Allowed values for BEHAVIOR are: rename_ident, error, skip.'))


class Skip(PostProcessingError):
    pass


class InternetArchiveUploadPP(ExecPP):
    # memo
    #  This item total number of bytes(666) is over the per item size limit of 1099511627776. Please contact info@archive.org for help fitting your data into the archive.
    def __init__(self, downloader, exec_cmd):
        super().__init__(downloader, exec_cmd)
        self.login_cache: Dict[str, Dict] = {}
        self.conflict_cache: Dict[str, Set[str]] = {}

    def run(self, info):
        for tmpl in self.exec_cmd:
            cmd = self.parse_cmd(tmpl, info)
            self.to_screen('Processing: %s' % cmd)
            parsed = iaup_options.parse_args(shlex.split(cmd))
            self.parse_inputs(parsed)
            errors = self.process(parsed)
            if errors:
                raise PostProcessingError('There were error(s) while uploading:\n' + '\n'.join(map(str, errors)))
        return [], info

    def parse_inputs(self, opts):
        if opts.throttle is not None:
            numeric_limit = FileDownloader.parse_bytes(opts.throttle)
            if numeric_limit is None:
                self.report_warning('invalid rate limit specified')
            opts.throttle = numeric_limit

    def process(self, parsed):
        opts, args = parsed
        if not args:
            raise PostProcessingError('You have to specify identifier and files to upload.')
        ident = args[0]
        files = args[1:]
        if not files:
            raise PostProcessingError('You have specified nothing to upload!')

        # login
        cred = self.login_cache.get(ident)
        if not cred:
            if opts.username and opts.password:
                self.to_screen(f'Logging in with username and password for identifier {ident}')
                cred = self.login(opts.username, opts.password)
            else:
                self.write_debug(f'Loading config file for identifier {ident}')
                cred = self.parse_config_file(opts.config)
            self.login_cache[ident] = cred

        # create plans for upload
        rp = opts.remote_name
        if rp:
            if rp.endswith('/'):
                # upload files to a remote directory
                plans = [(rp + escaped_basename(x), x) for x in files]
            elif not rp.endswith('/') and len(files) == 1:
                # upload a file with a exact filename
                plans = [(rp, files[0])]
            else:
                raise PostProcessingError('Conflict: You have requested uploading multiple files to one remote file.')
        else:
            # no --remote-name, upload to root
            plans = [(escaped_basename(x), x) for x in files]

        # have we encountered any conflicts previously?
        try:
            ident = self.conflict_trial(opts, ident, pre=True)
        except Skip as skip:
            self.report_warning(skip)
            return []

        # generate header value for auth
        s3_ak = traverse_obj(cred, ('s3', 'access'))
        s3_sk = traverse_obj(cred, ('s3', 'secret'))
        if not s3_ak:
            raise PostProcessingError('Access Key for IAS3 is missing. You should run "ia configure"')
        if not s3_sk:
            raise PostProcessingError('Secret Key for IAS3 is missing. You should run "ia configure"')

        # upload files according to the plan
        errors = []
        for idx, (remotename, filename) in enumerate(plans):
            headers = dict(opts.headers)
            self.generate_headers(headers, opts.metadata, queue_derive=opts.derive)
            headers['Authorization'] = f'LOW {s3_ak}:{s3_sk}'
            self.write_debug(f'=== {filename} -> {remotename}')
            with open(filename, 'rb') as r:
                try:
                    self.real_upload(ident, remotename, r, headers, idx + 1, len(plans), opts.quiet, opts.retries, opts.throttle)
                except PostProcessingError as ex:
                    self.report_warning(ex)
                    errors.append(ex)

        if not errors and opts.delete:
            for _, lf in plans:
                self.write_debug(f'Removing {lf}')
                try:
                    escaped_remove(lf)
                except (IOError, OSError) as ex:
                    self.report_warning(ex)
        return errors

    def real_upload(self, ident, remotename, r, headers, index, total_plans, quiet, retries, throttle=None):
        fsize = os.stat(r.fileno()).st_size
        headers['Content-MD5'] = self.md5(r)
        headers['Content-Length'] = str(fsize)
        true_body = (QuietByteIO if quiet else ProgressByteIO)(self._downloader, r, fsize, throttle)
        true_body._PROGRESS_LABEL = f'{index}/{total_plans}'

        for retry in self.repeat_iter(retries):
            try:
                self.to_screen(f'[{index}/{total_plans}] Uploading {remotename}', prefix=False)
                true_body.start()
                # who wants to use plain HTTP nowadays?
                resp, body = self.do_put_request(f'https://s3.us.archive.org/{ident}/{remotename}', headers, true_body)
                resp_code = resp.code
                self.write_debug(body)
                # TODO: check error message and resolve conflicts
                if resp_code == 200:
                    # that's okay to return without messages
                    return
                else:
                    warn_body = self.get_s3_xml_text(body) or f'Unknown status code: {resp_code}'
                    if resp_code == 503:
                        warn_body = 'S3 is overloaded'
                    retry_remain = self.repeat_remaining(retries, retry)
                    if retry_remain == 0:
                        raise PostProcessingError(f'[{index}/{total_plans}] {warn_body}. Retry exhausted.')
                    else:
                        waittime = 30 - 29 * (1.1**(-retry))
                        self.report_warning(f'[{index}/{total_plans}] {warn_body}. Sleeping for {waittime} seconds. {retry_remain} retries left.')
                        time.sleep(waittime)
                        continue
            except PostProcessingError as ex:
                waittime = 30 - 29 * (1.1**(-retry))
                self.report_warning(f'[{index}/{total_plans}] {ex}. Sleeping for {waittime} seconds. {retry_remain} retries left.')
                time.sleep(waittime)
                continue
            finally:
                # no need to call close() as it's caller's responsiblility to close streams
                true_body.end()
        raise PostProcessingError(f'[{index}/{total_plans}] Retry exhausted')

    @staticmethod
    def md5(file_object):
        file_object.seek(0, os.SEEK_SET)
        m = hashlib.md5()
        while True:
            data = file_object.read(8192)
            if not data:
                break
            m.update(data)
        file_object.seek(0, os.SEEK_SET)
        return m.hexdigest()

    @staticmethod
    def repeat_iter(retries):
        if retries < 1 or retries == float('inf'):
            return itertools.count(0)
        else:
            return range(retries + 1)

    @staticmethod
    def repeat_remaining(retries, count):
        if retries < 1 or retries == float('inf'):
            return float('inf')
        else:
            return retries - count

    def get_s3_xml_text(xml_str):
        if not xml_str:
            return ''

        def _get_tag_text(tag_name, xml_obj):
            text = ''
            elements = xml_obj.getElementsByTagName(tag_name)
            for e in elements:
                for node in e.childNodes:
                    if node.nodeType == node.TEXT_NODE:
                        text += node.data
            return text

        try:
            p = parseString(xml_str)
            _msg = _get_tag_text('Message', p)
            _resource = _get_tag_text('Resource', p)
            # Avoid weird Resource text that contains PUT method.
            if _resource and "'PUT" not in _resource:
                return f'{_msg} - {_resource.strip()}'
            else:
                return _msg
        except KeyboardInterrupt:
            raise
        except BaseException:
            return str(xml_str)

    def generate_headers(self, headers, metadata, file_metadata=None, queue_derive=True):
        metadata = dict() if metadata is None else metadata
        file_metadata = dict() if file_metadata is None else file_metadata

        if not metadata.get('scanner'):
            from ..version import __version__
            scanner = 'ytdl-patched InternetArchiveUploadPP {0}'.format(__version__)
            metadata['scanner'] = scanner
        prepared_metadata = metadata or {}
        prepared_file_metadata = file_metadata or {}

        headers['x-archive-auto-make-bucket'] = '1'
        if 'x-archive-queue-derive' not in headers:
            if queue_derive is False:
                headers['x-archive-queue-derive'] = '0'
            else:
                headers['x-archive-queue-derive'] = '1'

        def needs_quote(s):
            try:
                s.encode('ascii')
            except (UnicodeDecodeError, UnicodeEncodeError):
                return True
            return re.search(r'\s', s) is not None

        def _prepare_metadata_headers(prepared_metadata, meta_type='meta'):
            for meta_key, meta_value in prepared_metadata.items():
                # Encode arrays into JSON strings because Archive.org does not
                # yet support complex metadata structures in
                # <identifier>_meta.xml.
                if isinstance(meta_value, dict):
                    meta_value = json.dumps(meta_value)
                # Convert the metadata value into a list if it is not already
                # iterable.
                meta_value = variadic(meta_value)
                # Convert metadata items into HTTP headers and add to
                # ``headers`` dict.
                for i, value in enumerate(meta_value):
                    if not value:
                        continue
                    header_key = 'x-archive-{0}{1:02d}-{2}'.format(meta_type, i, meta_key)
                    if (isinstance(value, str) and needs_quote(value)):
                        value = 'uri({0})'.format(urllib.parse.quote(value))
                    # because rfc822 http headers disallow _ in names, IA-S3 will
                    # translate two hyphens in a row (--) into an underscore (_).
                    header_key = header_key.replace('_', '--')
                    headers[header_key] = value

        # Parse the prepared metadata into HTTP headers,
        # and add them to the ``headers`` dict.
        _prepare_metadata_headers(prepared_metadata)
        _prepare_metadata_headers(prepared_file_metadata, meta_type='filemeta')

    def conflict_trial(self, opts, ident, pre=False):
        history = self.conflict_cache.get(ident)
        # TODO: test against size overflow beforehand here
        if not history:
            return ident
        cr = opts.conflict_resolve or {}
        resolve_methods = set(filter(None, (cr.get(cc) for cc in history)))
        if not resolve_methods:
            # no method for resolving/avoiding conflict is specified
            return ident
        if 'rename_ident' in resolve_methods:
            # split the last number and others, and increment the number specified
            m = re.fullmatch(r'(.+)(?:_(\d+))?', ident)
            assert m
            name, num = m.groups()
            num = int_or_none(num, default=1) + 1
            ident = f'{name}_{num}'
            # as we've changed the identifier, put into trial again
            return self.conflict_trial(opts, ident, pre)
        elif 'skip' in resolve_methods:
            # literally.
            raise Skip(f'Skipping because of any of errors here: {" ".join(history)}')
        elif 'error' in resolve_methods:
            # literally, again
            if pre:
                raise PostProcessingError(f'Refusing upload to identifier {ident}; {" ".join(history)}')
            else:
                raise PostProcessingError(f'Aborted uploading to identifier {ident}; {" ".join(history)}')
        return ident

    def login(self, email, password):
        j = self._get_json(
            'https://archive.org/services/xauthn/?op=login',
            {'email': email, 'password': password})
        if not j.get('success'):
            msg = traverse_obj(j, ('values', 'reason'), 'error')
            msg = {
                'account_not_found': 'Account not found, check your email and try again.',
                'account_bad_password': 'Incorrect password, try again.',
            }.get(msg) or f'Authentication failed: {msg}'
            raise PostProcessingError(msg)
        return j['values']

    def parse_config_file(self, config_file=None):
        config = configparser.RawConfigParser()

        if not config_file:
            candidates = []
            if os.environ.get('IA_CONFIG_FILE'):
                candidates.append(os.environ['IA_CONFIG_FILE'])
            xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
            if not xdg_config_home or not os.path.isabs(xdg_config_home):
                # Per the XDG Base Dir specification, this should be $HOME/.config. Unfortunately, $HOME
                # does not exist on all systems. Therefore, we use ~/.config here. On a POSIX-compliant
                # system, where $HOME must always be set, the XDG spec will be followed precisely.
                xdg_config_home = os.path.join(os.path.expanduser('~'), '.config')
            xdg_config_file = os.path.join(xdg_config_home, 'internetarchive', 'ia.ini')
            candidates.append(xdg_config_file)
            candidates.append(os.path.join(os.path.expanduser('~'), '.config', 'ia.ini'))
            candidates.append(os.path.join(os.path.expanduser('~'), '.ia'))
            for candidate in candidates:
                if os.path.isfile(candidate):
                    config_file = candidate
                    break
            else:
                # None of the candidates exist, default to IA_CONFIG_FILE if set else XDG
                config_file = os.environ.get('IA_CONFIG_FILE', xdg_config_file)
        config.read(config_file)

        if not config.has_section('s3'):
            config.add_section('s3')
            config.set('s3', 'access', None)
            config.set('s3', 'secret', None)
        if not config.has_section('cookies'):
            config.add_section('cookies')
            config.set('cookies', 'logged-in-user', None)
            config.set('cookies', 'logged-in-sig', None)

        if config.has_section('general'):
            for k, v in config.items('general'):
                if k in ['secure']:
                    config.set('general', k, config.getboolean('general', k))
            if not config.get('general', 'screenname'):
                config.set('general', 'screenname', None)
        else:
            config.add_section('general')
            config.set('general', 'screenname', None)

        return config_file, config

    def get_config(self, config=None, config_file=None):
        _config = {} if not config else config
        config_file, config = self.parse_config_file(config_file)

        if not os.path.isfile(config_file):
            return _config

        config_dict = defaultdict(dict)
        for sec in config.sections():
            try:
                for k, v in config.items(sec):
                    if k is None or v is None:
                        continue
                    config_dict[sec][k] = v
            except TypeError:
                pass

        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    r = deep_update(d.get(k, {}), v)
                    d[k] = r
                else:
                    d[k] = u[k]
            return d

        # Recursive/deep update.
        deep_update(config_dict, _config)

        return dict((k, v) for k, v in config_dict.items() if v is not None)

    def _get_json(self, url, data=None):
        # Taken from sponsorblock.py with POST support
        max_retries = self.get_param('extractor_retries', 3)
        sleep_interval = self.get_param('sleep_interval_requests') or 0
        for retries in itertools.count():
            try:
                rsp = self._downloader.urlopen(sanitized_Request(url, data=data))
                return json.loads(rsp.read().decode(rsp.info().get_param('charset') or 'utf-8'))
            except network_exceptions as e:
                if isinstance(e, compat_HTTPError) and e.code == 404:
                    return []
                if retries < max_retries:
                    self.report_warning(f'{e}. Retrying...')
                    if sleep_interval > 0:
                        self.to_screen(f'Sleeping {sleep_interval} seconds ...')
                        time.sleep(sleep_interval)
                    continue
                raise PostProcessingError(f'Unable to communicate with Internet Archive: {e}')

    def do_put_request(self, url, headers, data):
        try:
            rsp = self._downloader.urlopen(sanitized_Request(url, headers=headers, data=data))
        except network_exceptions as e:
            e.fp._error = e
            rsp = e.fp
        return rsp, rsp.read().decode(rsp.info().get_param('charset') or 'utf-8')


class QuietByteIO(BinaryIO, IO[bytes]):
    def __init__(self, ydl: YoutubeDL, stream: IO[bytes], filesize: int, throttle: Optional[int] = None) -> None:
        super().__init__()
        self.stream = stream
        self.filesize = filesize
        self.throttle = throttle
        self.counter, self.throttle_count, self.start_time = None, None, None
        self.time_and_size, self.avg_len = [], 10

    def start(self):
        self.counter, self.throttle_count = 0, 0
        self.stream.seek(0, os.SEEK_SET)
        self.start_time = time_millis()

    def report(self):
        pass

    def throttle_check(self):
        self.time_and_size.append((self.counter, time.time()))
        self.time_and_size = tsz = self.time_and_size[-self.avg_len:]
        if not self.throttle:
            return
        if len(tsz) < 4:
            return
        last, early = tsz[0], tsz[-1]
        average_speed = (early[0] - last[0]) / (early[1] - last[1])
        if average_speed < self.throttle:
            self.throttle_count += 1
        if self.throttle_count > 4:
            # throwing ThrottledDownload here could cause re-extraction, which is not desired here
            raise PostProcessingError(ThrottledDownload().msg)

    def end(self):
        pass

    def close(self) -> None:
        self.end()
        self.stream.close()

    def read(self, n: int = -1) -> bytes:
        if n <= 0:
            n = 1048576
        ret = self.stream.read(n)
        if ret:
            self.counter += len(ret)
            self.throttle_check()
            self.report()
        return ret

    def __len__(self):
        return self.filesize


class ProgressByteIO(QuietByteIO, ShowsProgress):
    def __init__(self, ydl: YoutubeDL, stream: IO[bytes], filesize: int, throttle: Optional[int] = None) -> None:
        super().__init__(ydl, stream, filesize, throttle)
        ShowsProgress.__init__(self, ydl)
        self.stream = stream
        self.filesize = filesize
        # call with all=False as this class doesn't have hooks,
        # therefore calling report_progress directly
        self._enable_progress(False)

    def start(self):
        super().start()
        self.report_progress({
            'status': 'processing',
            'elapsed': 0,
            'processed_bytes': 0,
            'total_bytes': self.filesize,
        })

    def report(self):
        tsz = self.time_and_size
        elapsed = time_millis() - self.start_time
        if len(tsz) > 1:
            last, early = tsz[0], tsz[-1]
            average_speed = (early[0] - last[0]) / (early[1] - last[1])
            eta = ((self.filesize - self.counter) / average_speed) if average_speed > 0 else None
        else:
            average_speed = None
            eta = (self.filesize - self.counter) * elapsed / self.counter
            if eta < 0:
                eta = None
        self.report_progress({
            'status': 'processing',
            'elapsed': elapsed,
            'speed': average_speed,
            'processed_bytes': self.counter,
            'eta': eta,
            'total_bytes': self.filesize,
        })

    def end(self):
        # prevent "finished" event to be emitted twice without indication
        if self.counter is None:
            return
        self.report_progress({
            'status': 'finished',
            # do not use self.filesize here since the task could fail at middle of file
            'processed_bytes': self.counter,
            'total_bytes': self.filesize,
        })
        self.counter = None

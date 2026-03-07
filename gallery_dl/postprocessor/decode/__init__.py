"""Decode scrambled image"""

from ..common import PostProcessor


class DecodePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        decoder_cls = find(job.extractor.category)
        if decoder_cls is None:
            self.log.warning("DecodePP is not available")
            return

        decoder = decoder_cls(options, self.log)
        hooks = {"file": decoder.run}
        job.register_hooks(hooks, options)


modules = [
    "fakku"
]


def find(name):
    """Return a decoder class with the given name"""
    try:
        return _cache[name]
    except KeyError:
        pass

    cls = None
    if name in modules:  # prevent unwanted imports
        try:
            module = __import__(name, globals(), None, None, 1)
        except ImportError:
            pass
        else:
            cls = module.__decoder__
    _cache[name] = cls
    return cls


_cache = {}


__postprocessor__ = DecodePP

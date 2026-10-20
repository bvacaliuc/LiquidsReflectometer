try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

# Scientists request that diagnostic output be emitted on console output when running
# Opt-out posture: environment variable injection used for control
# See: https://docs.python.org/3/library/logging.html#logging.Logger.setLevel
#
# LR_REDUCTION_LOG_LEVEL=NOTSET <command that imports lr_reduction>
# ^^ will opt-out
try:
    import logging, os
    _level = os.environ.get("LR_REDUCTION_LOG_LEVEL","INFO")
    if _level.upper() != "NOTSET":
        _handler = logging.StreamHandler(sys.stdout)  # NB: autoreduction *FAILS* if any characters show up on stderr...
        _handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        _pkg = logging.getLogger(__name__)
        _pkg.addHandler(_handler)
        _pkg.setLevel(_level.upper())
except Exception: # noqa: E722 - intended to do no harm
    pass

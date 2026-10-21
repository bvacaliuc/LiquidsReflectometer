import os
import sys
import logging

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

# Scientists request that diagnostic output be emitted on console output when running
# Opt-out posture: environment variable injection used for control
# See: https://docs.python.org/3/library/logging.html#logging.Logger.setLevel
#
# LR_REDUCTION_LOG_LEVEL=0 <command that imports lr_reduction>
# ^^ will opt-out
_pkg = logging.getLogger(__name__)
try:
    _level = os.environ.get("LR_REDUCTION_LOG_LEVEL",str(logging.INFO))
    _handler = logging.StreamHandler(sys.stdout)  # NB: autoreduction *FAILS* if any characters show up on stderr...
    _handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    _number = int(_level)
    if _number > 0:
        _pkg.addHandler(_handler)
        _pkg.setLevel(_number)
    else:
        _pkg.removeHandler(_handler)
        _pkg.setLevel(logging.NOTSET)
except Exception: # noqa: BLE001
    pass

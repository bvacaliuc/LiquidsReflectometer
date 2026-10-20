import logging
import os
import sys

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

_HANDLER_NAME = "lr_reduction.console"
_FORMAT = "%(levelname)s %(name)s: %(message)s"
_ACCEPTED = "DEBUG, INFO, WARNING, ERROR, CRITICAL, or an integer"


def configure_console_logging(value: str | None) -> logging.Handler | None:
    """Print the package's own log records on stderr when ``value`` names a level.

    ``value`` is what ``LR_REDUCTION_LOG_LEVEL`` holds: unset (``None``), empty or blank changes nothing, so
    Python's lastResort handler keeps printing WARNING and above and dropping INFO/DEBUG. A level name (any
    case) or a decimal integer attaches one stderr handler to the ``lr_reduction`` logger at that level; every
    ``lr_reduction.*`` logger propagates to it, and no other logger is touched. Any other value attaches the
    handler at INFO and says so once. Calling it again updates the level of the one handler.
    """
    if value is None or not value.strip():
        return None
    text = value.strip()
    level, invalid = None, False
    if text.isdigit():
        level = int(text)
    else:
        named = logging.getLevelName(text.upper())
        if isinstance(named, int):
            level = named
        else:
            level, invalid = logging.INFO, True
    package = logging.getLogger(__name__)
    handler = next((h for h in package.handlers if h.get_name() == _HANDLER_NAME), None)
    if handler is None:
        handler = logging.StreamHandler(sys.stderr)
        handler.set_name(_HANDLER_NAME)
        handler.setFormatter(logging.Formatter(_FORMAT))
        package.addHandler(handler)
    handler.setLevel(level)
    package.setLevel(level)
    if invalid:
        package.warning("LR_REDUCTION_LOG_LEVEL=%r is not a level name (%s); using INFO", value, _ACCEPTED)
    return handler


configure_console_logging(os.environ.get("LR_REDUCTION_LOG_LEVEL"))

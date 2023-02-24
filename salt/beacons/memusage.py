"""
Beacon to monitor memory usage.

.. versionadded:: 2016.3.0

:depends: python-psutil
"""
import logging
import re

import salt.utils.beacons

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

log = logging.getLogger(__name__)

__virtualname__ = "memusage"


def __virtual__():
    if HAS_PSUTIL is not False:
        return __virtualname__
    err_msg = "psutil library is missing."
    log.error("Unable to load %s beacon: %s", __virtualname__, err_msg)
    return False, err_msg


def validate(config):
    """
    Validate the beacon configuration
    """
    if not isinstance(config, list):
        return False, "Configuration for memusage beacon must be a list."
    config = salt.utils.beacons.list_to_dict(config)

    if "percent" not in config:
        return False, "Configuration for memusage beacon requires percent."
    return True, "Valid beacon configuration"


def beacon(config):
    """
    Monitor the memory usage of the minion

    Specify thresholds for percent used and only emit a beacon
    if it is exceeded.

    .. code-block:: yaml

        beacons:
          memusage:
            - percent: 63%
    """
    ret = []

    config = salt.utils.beacons.list_to_dict(config)

    _current_usage = psutil.virtual_memory()

    current_usage = _current_usage.percent
    monitor_usage = config["percent"]
    if isinstance(monitor_usage, str) and "%" in monitor_usage:
        monitor_usage = re.sub("%", "", monitor_usage)
    monitor_usage = float(monitor_usage)
    if current_usage >= monitor_usage:
        ret.append({"memusage": current_usage})
    return ret

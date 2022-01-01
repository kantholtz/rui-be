# -*- coding: utf-8 -*-

import enum
import logging


# special log message upon application start
changelog = logging.getLogger("changelog")
changelog.info("! initialized changelog")


class Kind(enum.Enum):

    STATE_INIT = "state initialization"


def append(kind: Kind, data: dict):
    # it uses repr() for dicts - needs to be implemented for custom objects
    changelog.info(data | {"kind": kind.value})

# -*- coding: utf-8 -*-

from threading import RLock

from draug.homag import sampling
from draug.homag.graph import Graph
from draug.homag.text import Matches
from draug.models.ranking import Predictions

import logging

from typing import BinaryIO

log = logging.getLogger(__name__)


# oh god please dont look at me and for the love of jesus christ,
# do not deploy me properly (e.g. with wsgi)


class State:

    meta: dict
    graph: Graph
    graphwriter: BinaryIO

    matches_store: Matches
    predictions_store: Predictions

    def __init__(self):
        log.info("initializing state")

        self.meta = None

        self.graph = Graph(meta=dict(name="Default"))
        self.graphwriter = None

        self.matches_store = None
        self.predictions_store = None

        self.nlp = sampling.get_nlp()

        self._lock = RLock()
        log.info("initialized state")

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, *args):
        self._lock.release()


ctx = State()

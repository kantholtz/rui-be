# -*- coding: utf-8 -*-

from threading import RLock

from draug.homag import sampling
from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches

import logging

log = logging.getLogger(__name__)


# oh god please dont look at me and for the love of jesus christ,
# do not deploy me properly (e.g. with wsgi)


class State:
    def __init__(self):
        log.info("initializing state")

        self.meta = None
        self.graphwriter = None
        self.graph = Graph(meta=dict(name="unknown"))
        self.matches_store = Matches(self.graph)
        self.predictions_store = Predictions()
        self.nlp = sampling.get_nlp()

        self._lock = RLock()
        log.info("initialized state")

    def __enter__(self):
        log.info("acquire lock")
        self._lock.acquire()
        return self

    def __exit__(self, *args):
        log.info("releasing lock")
        self._lock.release()


ctx = State()

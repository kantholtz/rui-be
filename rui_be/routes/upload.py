# -*- coding: utf-8 -*-

import yaml
import gzip
import logging
import zipfile
import tempfile
from datetime import datetime

from pathlib import Path

from draug.homag.graph import Graph
from draug.homag.text import Matches
from draug.models.ranking import Predictions

from flask import Blueprint, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

import rui_be
from rui_be.state import ctx
from rui_be import changelog

from rui_be.routes import ENDPOINT


log = logging.getLogger(__name__)
blueprint = Blueprint("upload", __name__)


def extract_zip(source_file, target_path):
    with zipfile.ZipFile(source_file, "r") as zip_ref:
        log.info(f"extracting data to {target_path}")
        zip_ref.extractall(target_path)

    path = target_path / "data"
    log.info("extracted data, populating state")

    # meta
    with (path / "meta.yml").open(mode="r") as fd:
        meta = yaml.load(fd, Loader=yaml.FullLoader)

    with ctx as state:
        # graph
        state.graph = Graph.from_dir(path=path / "graph")

        # matches
        state.matches_store = Matches.from_file(
            path=path / "matches" / "match.txt",
            graph=state.graph,
        )

        # predictions
        with (path / "predictions" / "ranking.config.yml").open(mode="r") as fd:
            predictions_config = yaml.load(fd, Loader=yaml.FullLoader)

        state.predictions_store = Predictions.from_files(
            path / "predictions" / "parent.csv",
            path / "predictions" / "synonym.csv",
        )

        # --

        log.info(f"state populated with {state.graph}")
        log.info(f"-- {state.matches_store}")
        log.info(f"-- {state.predictions_store}")

        state.meta = meta

        # --

        timestamp = datetime.now().isoformat()
        graph_fname = f'{meta["name"]}-{timestamp}.gz'.replace(" ", "_")

        graph_path = Path("data/graphs")
        graph_path.mkdir(exist_ok=True, parents=True)

        log.info(f"writing graph iterations to {graph_path / graph_fname}")
        state.graphwriter = gzip.open(graph_path / graph_fname, mode="w")

        # --

        changelog.append(
            state=state,
            kind=changelog.Kind.STATE_INIT,
            data={
                "meta": meta,
                "prediction_config": predictions_config,
                "graphs": str(graph_path / graph_fname),
            },
        )


@blueprint.route(f"{ENDPOINT}/upload", methods=["PUT"])
def put_upload() -> str:
    zip: FileStorage = request.files["zip"]

    with tempfile.TemporaryDirectory() as upload_dir:
        log.info(f"uploading zip to {upload_dir}")

        fname = secure_filename(zip.filename)
        zip_path = Path(upload_dir) / fname

        zip.save(zip_path)
        extract_zip(
            source_file=zip_path,
            target_path=upload_dir,
        )

    return ""


def _get_available():
    path = rui_be.ROOT / "data" / "storage"
    return list(path.glob("model-*"))


@blueprint.route(f"{ENDPOINT}/uploads", methods=["GET"])
def get_uploads() -> str:
    available = []
    for glob in _get_available():
        stats = glob.stat()
        available.append(
            {
                "name": glob.name,
                "created": datetime.fromtimestamp(stats.st_mtime),
                "size": -1,
                # "size": int(stats.st_size / 1024 ** 2),  # MB
            }
        )

    return {"available": available}


@blueprint.route(f"{ENDPOINT}/initialize", methods=["POST"])
def post_init() -> str:
    req = request.get_json()

    available = {glob.name: glob for glob in _get_available()}
    name = req["name"]

    if name not in available:
        return "", 500

    # with tempfile.TemporaryDirectory() as extract_dir:
    #     target_path = Path(extract_dir)
    #     extract_zip(source_file=available[name], target_path=target_path)

    path = available[name]
    log.info("populating state")

    # meta
    with (path / "meta.yml").open(mode="r") as fd:
        meta = yaml.load(fd, Loader=yaml.FullLoader)

    with ctx as state:
        # graph
        state.graph = Graph.from_dir(path=path / "graph")

        # matches
        state.matches_store = Matches.from_file(
            path=path / "matches" / "match.txt",
            graph=state.graph,
        )

        # predictions

        with (path / "predictions" / "config.yml").open(mode="r") as fd:
            ranking_config = yaml.load(fd, Loader=yaml.FullLoader)

        state.predictions_store = Predictions(
            graph=state.graph,
            preds_path=path / "predictions" / "predictions.txt.gz",
            h5_path=path / "predictions" / "rankings.h5",
            normalization=ranking_config["normalizer"],
        )

        # --

        log.info(f"state populated with {state.graph}")
        log.info(f"-- {state.matches_store}")
        log.info(f"-- {state.predictions_store}")

        state.meta = meta

        # --

        timestamp = datetime.now().isoformat()
        graph_fname = f'{meta["name"]}-{timestamp}.gz'.replace(" ", "_")

        graph_path = Path("data/graphs")
        graph_path.mkdir(exist_ok=True, parents=True)

        log.info(f"writing graph iterations to {graph_path / graph_fname}")
        state.graphwriter = gzip.open(graph_path / graph_fname, mode="w")

        # --

        changelog.append(
            state=state,
            kind=changelog.Kind.STATE_INIT,
            data={
                "meta": meta,
                "graphs": str(graph_path / graph_fname),
            },
        )

    return ""

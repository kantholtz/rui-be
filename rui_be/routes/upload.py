# -*- coding: utf-8 -*-

import yaml
import logging
import zipfile
import tempfile

from pathlib import Path

from draug.homag.graph import Graph
from draug.homag.text import Matches
from draug.homag.model import Predictions

from flask import Blueprint, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from rui_be import state
from rui_be import changelog

from rui_be.routes import ENDPOINT


log = logging.getLogger(__name__)
blueprint = Blueprint("upload", __name__)


@blueprint.route(f"{ENDPOINT}/upload", methods=["PUT"])
def put_upload() -> str:
    zip: FileStorage = request.files["symptaxUploadZip"]

    with tempfile.TemporaryDirectory() as upload_dir:
        log.info(f"uploading zip to {upload_dir}")

        fname = secure_filename(zip.filename)
        zip_path = Path(upload_dir) / fname

        zip.save(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(upload_dir)

        path = zip_path.parent / zip_path.stem
        log.info("extracted data, populating state")

        # meta
        with (path / "meta.yml").open(mode="r") as fd:
            meta = yaml.load(fd, Loader=yaml.FullLoader)

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

        changelog.append(
            kind=changelog.Kind.STATE_INIT,
            data={
                "meta": meta,
                "prediction_config": predictions_config,
            },
        )

    return ""

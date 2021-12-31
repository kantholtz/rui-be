# -*- coding: utf-8 -*-

import logging
import zipfile
import tempfile
from pathlib import Path

from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches
from flask import Blueprint, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from rui_be import state


log = logging.getLogger(__name__)
upload = Blueprint("upload", __name__)


@upload.route("/api/1.6.0/upload", methods=["PUT"])
def put_upload() -> str:
    zip: FileStorage = request.files["symptaxUploadZip"]

    with tempfile.TemporaryDirectory() as upload_dir:
        log.info(f"uploading zip to {upload_dir}")

        fname = secure_filename(zip.filename)
        zip_path = Path(fname) / fname

        zip.save(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(upload_dir)

        path = zip_path.parent / zip_path.stem
        log.info("extracted data, populating state")

        # populate state
        state.graph = Graph.from_dir(path=path)
        state.matches_store = Matches.from_file(path / "match.txt")
        state.predictions_store = Predictions.from_files(
            path / "parent.csv",
            path / "synonym.csv",
        )

        log.info("state populated")

    return ""

import os
import zipfile
from pathlib import Path

from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches
from flask import Blueprint, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from rui_be import state

upload = Blueprint("upload", __name__)


@upload.route("/api/1.6.0/upload", methods=["PUT"])
def put_upload() -> str:
    symptax_upload_zip: FileStorage = request.files["symptaxUploadZip"]

    upload_dir = Path(os.path.join(os.getcwd(), "data"))
    upload_dir.mkdir(exist_ok=True)

    upload_filename = secure_filename(symptax_upload_zip.filename)
    upload_path = os.path.join(upload_dir, upload_filename)

    symptax_upload_zip.save(upload_path)

    with zipfile.ZipFile(os.path.join(upload_dir, upload_filename), "r") as zip_ref:
        zip_ref.extractall(upload_dir)

    extracted_dir = os.path.splitext(upload_path)[0]

    # update state

    state.graph = Graph.from_dir(extracted_dir)

    match_txt: str = os.path.join(extracted_dir, "match.txt")
    state.matches_store = Matches.from_file(match_txt, state.graph)

    parent_csv: str = os.path.join(extracted_dir, "parent.csv")
    synonym_csv: str = os.path.join(extracted_dir, "synonym.csv")
    state.predictions_store = Predictions.from_files({parent_csv, synonym_csv})

    return ""

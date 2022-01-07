# -*- coding: utf-8 -*-

from flask import Blueprint, request

from rui_be import changelog
from rui_be.routes import ENDPOINT

import logging
from rui_be.state import ctx


log = logging.getLogger(__name__)
blueprint = Blueprint("tracking", __name__)


@blueprint.route(f"{ENDPOINT}/track/route", methods=["POST"])
def post_entity() -> tuple[str, int]:
    with ctx as state:
        req = request.get_json()
        log.info(f"tracking: switched to page {req['name']} {req['params']}")

        changelog.append(
            state=state,
            kind=changelog.Kind.TRACKING_ROUTE,
            data=req,
        )

        return ""

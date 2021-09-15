from flask import Blueprint, Response, request, jsonify

from src import state
from src.models.match.match import Match, MatchSchema

matches = Blueprint('matches', __name__)


@matches.route('/api/1.6.0/matches', methods=['GET'])
def get_matches() -> Response:
    #
    # Parse query params
    #

    entity = int(request.args.get('entity'))

    offset = request.args.get('offset')
    if offset:
        offset = int(offset)

    limit = request.args.get('limit')
    if limit:
        limit = int(limit)

    #
    # Get matches from draug and apply pagination
    #

    draug_matches = state.matches_store.by_eid(entity)
    matches: list[Match] = [Match(m.eid, m.ticket, m.context, m.mention, list(m.mention_idxs))
                            for m in draug_matches]

    if offset and limit:
        matches = matches[offset:(offset + limit)]
    elif offset:
        matches = matches[offset:]
    elif limit:
        matches = matches[:limit]

    return jsonify(MatchSchema(many=True).dump(matches))

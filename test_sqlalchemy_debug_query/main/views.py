from . import main
from flask_sqlalchemy import get_debug_queries
from flask import current_app, jsonify
from ..test_sqlalchemy_debug_query import Data
from .. import db
from sqlalchemy import and_


@main.after_app_request
def after_request(response):
    for query in get_debug_queries:
        if query.duration >= current_app.config['SLOW_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
            (query.statement, query.parameters, query.duration, query.context))
        return response


@main.route('/')
def main():
    query = Data.query.filter(and_(Data.temp.between(20, 30), Data.humd.between(80, 90))).count()
    return jsonify({"counts": query})


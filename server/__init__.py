"""

"""
import json
import os
from datetime import datetime
from dateutil import parser as date_parser
from werkzeug.exceptions import BadRequest
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_restful.utils import cors
from flask_mongoengine import MongoEngine
from sentiment_scraper.models.article import Article

env = os.environ.get('NEW_SENTIMENT_ENV', 'development')
if env == 'prod' or env == 'production':
    from server.config import ProdConfig as Config
else:
    from server.config import DevConfig as Config

app = Flask(__name__)
api = Api(app)
app.config.from_object(Config)
db = MongoEngine(app)
api.decorators = [cors.crossdomain(origin='*', headers=['Content-Type'])]


class ArticleRes(Resource):
    """

    """
    parser = reqparse.RequestParser()
    parser.add_argument('maxReturn', type=int)
    parser.add_argument('startDate', type=str)
    parser.add_argument('endDate', type=str)
    parser.add_argument('orderBy', type=str)
    parser.add_argument('sortOrder', type=str)

    def get(self):
        """"""
        args = self.parser.parse_args()

        # default return is 100
        max_return = 100
        if args.maxReturn is not None:
            max_return = args.maxReturn

        sort_order = '-'  # Defaults to descending
        if args.sortOrder is not None:
            if args.sortOrder == "ascending":
                sort_order = "+"
            # Else descending

        order_by = 'date'
        if args.orderBy is not None:
            order_by = args.orderBy

        try:
            start_date = date_parser.parse(args.startDate) if args.startDate is not None else None
            end_date = date_parser.parse(args.endDate) if args.endDate is not None else None
        except TypeError as ex:
            raise BadRequest(description="Date error: " + str(ex))

        # Start query / filtering
        articles = Article.objects.get_returnable().limit(max_return)

        if start_date is not None or end_date is not None:
            articles = articles.get_between(start_date, end_date)

        if order_by == 'date':
            articles = articles.order_by(sort_order + 'date')
        else:
            articles = articles

        # Thinking about adding the links into the returned set
        # articles = articles.get_returnable().get_linked()

        article_count = len(articles)

        to_return = {
            'count': article_count,
            'start': start,
            'result': articles[start:start+max_return].to_json()
        }

        return json.dumps(to_return), 200


api.add_resource(ArticleRes, '/articles')


@app.errorhandler(BadRequest)
def handle_error(error):
    print("ERROR")
    response = jsonify(error)
    response.status_code = error.status_code
    return response

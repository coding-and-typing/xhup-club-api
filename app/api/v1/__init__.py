# -*- coding: utf-8 -*-

from flask import Blueprint, Flask
from flask_restplus import Api

api_v1 = Blueprint('api.v1', __name__, url_prefix='/api')
api_rest = Api(api_v1)


def init_app(app: Flask):
    app.register_blueprint(api_v1)

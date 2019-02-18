# -*- coding: utf-8 -*-

from flask import Blueprint, Flask
from flask_restplus import Api

api_bp = Blueprint('api.v1', __name__, url_prefix='/api/v1')
api_rest = Api(api_bp)


def init_app(app: Flask):
    app.register_blueprint(api_bp)

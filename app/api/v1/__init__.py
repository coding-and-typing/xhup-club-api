# -*- coding: utf-8 -*-

from flask_rest_api import Blueprint, Api

api_bp = Blueprint(
    'api_v1', __name__, url_prefix='/api/v1',
    description="拆小鹤 RESTFul API - Version 1"
)

from .session import *
from .user import *
from .xhup import *


def init_api(api: Api):
    api_rest.register_blueprint(api_bp)

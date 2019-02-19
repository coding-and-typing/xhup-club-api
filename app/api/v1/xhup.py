# -*- coding: utf-8 -*-
import logging

from flask.views import MethodView
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest

logger = logging.getLogger(__name__)

xhup_bp = Blueprint(
    'xhup', __name__, url_prefix='/api/v1',
    description="小鹤双拼相关的功能"
)



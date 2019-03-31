# -*- coding: utf-8 -*-
from app.service.messages import on_command


@on_command("帮助", prefix="/", platform="default", group_id="default")
def usage(data):
    pass

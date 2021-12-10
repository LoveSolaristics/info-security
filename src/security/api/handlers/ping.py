from http import HTTPStatus
from aiohttp.web import json_response, Response
from .base import BaseView
from security.api.models import AppOnlineResponse


class PingView(BaseView):
    URL_PATH = '/ping'

    @staticmethod
    async def get() -> Response:
        return json_response(AppOnlineResponse().dict(), status=HTTPStatus.OK)

from http import HTTPStatus
from aiohttp.web import json_response, Response
from aiohttp import ClientSession, TCPConnector
from .base import BaseView
from security.api.models import RegisterResponse, RegisterRequest
from security.api.errors import InvalidToken


class RegisterView(BaseView):
    URL_PATH = '/user'

    async def post(self) -> Response:
        params = self.request.rel_url.query

        body = await self.request.json()
        user = RegisterRequest(**params, **body)

        self.request.app['log_manager'].logger.debug(f'{user=}')

        headers = {'Authorization': f'OAuth {user.token}'}
        conn = TCPConnector()
        async with ClientSession(trust_env=True,
                                 connector=conn) as session:
            async with session.get(
                    'https://login.yandex.ru/info?',
                    headers=headers,
                    ssl=False
            ) as resp:
                if resp.status == HTTPStatus.OK:
                    yandex_id = (await resp.json())['id']
                    await self.request.app['pg_db_manager'].user_create(
                        yandex_id, user.role == 'admin')
                else:
                    return InvalidToken()

        return json_response(RegisterResponse().dict(),
                             status=HTTPStatus.CREATED)
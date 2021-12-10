from aiohttp.web import middleware, Response, Request
from aiohttp import ClientSession, TCPConnector
from typing import Callable
from os import environ
from http import HTTPStatus
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from security.api.errors import BadParametersError, \
    AuthorizationRequired, UserNotFound, DuplicateNameError, ServiceError


@middleware
async def error_solving(request: Request, handler: Callable) -> Response:
    try:
        request.app['log_manager'].logger.debug(
            f'Handler "{handler.__name__}" has been activated.')
        response = await handler(request)
        request.app['log_manager'].logger.debug(
            f'Handler "{handler.__name__}" is finish his work.')
        return response
    except ValidationError as err:
        request.app['log_manager'].log_error(err)
        return BadParametersError(
            f"Bad parameters: "
            f"{', '.join([elem['loc'][0] for elem in err.errors()])}"
        )()
    except IntegrityError as err:
        request.app['log_manager'].log_error(err)
        return DuplicateNameError()
    except (ValueError, KeyError,) as err:
        request.app['log_manager'].log_error(err)
        return BadParametersError()()
    except Exception as err:
        request.app['log_manager'].log_error(err)
        return ServiceError()


@middleware
async def authorization(request: Request, handler: Callable):
    not_required = ['/ping', '/ping_db', '/user', '/user?role=admin']
    request.app['log_manager'].logger.debug(f"{request.rel_url=}")
    if str(request.rel_url) in not_required or environ.get("AUTH_DISABLED",
                                                           False):
        return await handler(request)
    else:
        auth_token = request.headers.get('Authorization')
        headers = {'Authorization': f'OAuth {auth_token}'}

        conn = TCPConnector()

        if auth_token:
            async with ClientSession(trust_env=True,
                                     connector=conn) as session:
                async with session.get(
                        'https://login.yandex.ru/info?',
                        headers=headers,
                        ssl=False
                ) as resp:
                    if resp.status == HTTPStatus.OK:
                        yandex_id = (await resp.json())['id']
                        user_id = await request.app[
                            'pg_db_manager'].user_get_id(yandex_id)
                        request.app['log_manager'].logger.debug(
                            f"{user_id=}")
                        is_correct = True if user_id is not None else False

            if is_correct:
                request['user_id'] = user_id
                return await handler(request)
            else:
                return UserNotFound()
        return AuthorizationRequired()

from http import HTTPStatus

from aiohttp.web import Response, json_response
from security.api.models import DefaultErrorResponse


class ClientError:
    def __init__(self, status: int, error: str):
        self._status = status
        self._error = error

    def __call__(self, info: dict = None, *args, **kwargs) -> Response:
        return json_response(
            data=DefaultErrorResponse(message=self._error, info=info).dict(
                exclude_none=True),
            status=self._status,
        )


class BadParametersError(ClientError):
    def __init__(self, error: str = 'bad-parameters'):
        super().__init__(HTTPStatus.BAD_REQUEST, error)


MethodNotAllowed = ClientError(
    HTTPStatus.METHOD_NOT_ALLOWED,
    'method-not-allowed'
)

UserNotFound = ClientError(
    HTTPStatus.NOT_FOUND,
    'user-not-found'
)

ProjectNotFound = ClientError(
    HTTPStatus.NOT_FOUND,
    'project-not-found'
)

AuthorizationRequired = ClientError(
    HTTPStatus.UNAUTHORIZED,
    'authorization-required'
)

DatabaseError = ClientError(
    HTTPStatus.BAD_REQUEST,
    'integrity-error'
)

DuplicateNameError = ClientError(
    HTTPStatus.CONFLICT,
    'duplicate-name'
)

InvalidToken = ClientError(
    HTTPStatus.BAD_REQUEST,
    'invalid-token'
)

ServiceError = ClientError(
    HTTPStatus.INTERNAL_SERVER_ERROR,
    'server-error'
)

NotEnoughRights = ClientError(
    HTTPStatus.FORBIDDEN,
    'not-enough-rights'
)

AdminNotTarget = ClientError(
    HTTPStatus.FORBIDDEN,
    "admin-can-not-be-target"
)

UpdateRightsError = ClientError(
    HTTPStatus.BAD_REQUEST,
    "error-during-update"
)


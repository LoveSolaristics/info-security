from http import HTTPStatus
from aiohttp.web import json_response, Response
from security.api.handlers.base import BaseView
from security.api.models import CreateProjectRequest, \
    CreateProjectResponse, GetProjectResponse, \
    UpdateProjectRequest, UpdateProjectResponse, Rights
from security.api.errors import ProjectNotFound, DuplicateNameError, \
    NotEnoughRights, AdminNotTarget, UserNotFound, UpdateRightsError
from aiohttp import ClientSession, TCPConnector


class ProjectView(BaseView):
    URL_PATH = '/project'

    async def post(self) -> Response:
        body = await self.request.json()
        project = CreateProjectRequest(**body)

        project_id = await self.request.app['pg_db_manager'].project_create(
            project.name)

        if project_id is None:
            return DuplicateNameError()

        await self.request.app['pg_db_manager'].access_create(
            project_id=project_id,
            user_id=self.request['user_id']
        )
        return json_response(
            CreateProjectResponse(project_id=project_id).dict(),
            status=HTTPStatus.CREATED)


class ProjectNameView(BaseView):
    URL_PATH = '/project/{project_name}'

    async def post(self) -> Response:
        body = await self.request.json()
        on_change = UpdateProjectRequest(
            project_name=self.request.match_info['project_name'],
            **body
        )

        # TODO: проверить права на редактирование

        is_admin = await self.request.app[
            'pg_db_manager'].user_get_role_by_user_id(
            self.request['user_id'])

        if is_admin:
            self.request.app['log_manager'].logger.debug(
                f"{is_admin=}")

            await self.request.app[
                'pg_db_manager'].project_update_name_by_name(
                project_name=on_change.project_name,
                new_name=on_change.new_name
            )

            return json_response(UpdateProjectResponse().dict(),
                                 status=HTTPStatus.OK)

        access = await self.request.app['pg_db_manager'] \
            .user_get_project(
            user_id=self.request['user_id'],
            project_name=self.request.match_info['project_name']
        )

        if not access:
            return NotEnoughRights()

        name, grant, write, read = \
            await self.request.app['pg_db_manager'] \
                .user_get_project_info(
                user_id=self.request['user_id'],
                project_name=self.request.match_info['project_name']
            )

        if not write:
            return NotEnoughRights()

        res = await self.request.app['pg_db_manager'].project_update_name(
            user_id=self.request['user_id'],
            project_name=on_change.project_name,
            new_name=on_change.new_name
        )

        if not res:
            return ProjectNotFound()

        return json_response(UpdateProjectResponse().dict(),
                             status=HTTPStatus.OK)

    async def patch(self) -> Response:
        body = await self.request.json()

        params = self.request.rel_url.query
        # проверяем, что у пользователя есть доступ к проекту
        name = await self.request.app['pg_db_manager'] \
            .user_get_project(
            user_id=self.request['user_id'],
            project_name=self.request.match_info['project_name']
        )

        is_admin = await self.request.app[
            'pg_db_manager'].user_get_role_by_user_id(
            self.request['user_id'])

        if name is None and not is_admin:
            return ProjectNotFound()

        # получаем информацию о правах пользоввателя на проект

        if name is not None:
            name, grant, read, write = \
                await self.request.app['pg_db_manager'] \
                    .user_get_project_info(
                    user_id=self.request['user_id'],
                    project_name=self.request.match_info['project_name']
                )
        else:
            grant, read, write = True, True, True

        if not grant:
            return NotEnoughRights()

        self.request.app['log_manager'].logger.debug(6)

        # проверяем, что target - не админ
        token = body['target_token']
        conn = TCPConnector()
        headers = {'Authorization': f'OAuth {token}'}
        async with ClientSession(trust_env=True,
                                 connector=conn) as session:
            async with session.get(
                    'https://login.yandex.ru/info?',
                    headers=headers,
                    ssl=False
            ) as resp:
                if resp.status == HTTPStatus.OK:
                    yandex_id = (await resp.json())['id']
                    user_id = await self.request.app[
                        'pg_db_manager'].user_get_id(yandex_id)
                    is_admin = await self.request.app[
                        'pg_db_manager'].user_get_role_by_yandex_id(yandex_id)

                    if is_admin:
                        self.request.app['log_manager'].logger.debug(7)
                        return AdminNotTarget()
                else:
                    self.request.app['log_manager'].logger.debug(8)
                    return UserNotFound()

        self.request.app['log_manager'].logger.debug(9)
        rights = Rights(**params)
        if (rights.read and not read) or (rights.write and not write) or (
                rights.grant and not grant):
            self.request.app['log_manager'].logger.debug(10)
            return NotEnoughRights()

        # если нет связи с проектом - добавляем
        self.request.app['log_manager'].logger.debug(11)
        is_connect = await self.request.app[
            'pg_db_manager'].user_has_project(
            user_id=user_id,
            project_name=self.request.match_info['project_name'])

        self.request.app['log_manager'].logger.debug(12)

        project_id = \
            await self.request.app['pg_db_manager'].project_get_id_by_name(
                project_name=self.request.match_info['project_name']
            )

        self.request.app['log_manager'].logger.debug(13)

        if not is_connect:
            self.request.app['log_manager'].logger.debug(14)
            await self.request.app['pg_db_manager'].access_create(
                project_id=project_id,
                user_id=user_id
            )

        is_ok = await self.request.app['pg_db_manager'].project_update_rights(
            user_id=user_id,
            project_id=project_id,
            write=rights.write,
            read=rights.read,
            grant=rights.grant
        )

        if not is_ok:
            return UpdateRightsError()
        return json_response(
            UpdateProjectResponse().dict(),
            status=HTTPStatus.OK
        )

    async def get(self) -> Response:
        params = self.request.rel_url.query

        is_admin = await self.request.app[
            'pg_db_manager'].user_get_role_by_user_id(
            self.request['user_id'])

        if is_admin:
            name, grant, read, write = await self.request.app['pg_db_manager'] \
                .user_get_project_info(
                project_name=self.request.match_info['project_name']
            )

            return json_response(
                GetProjectResponse(name=name, grant=grant, read=read,
                                   write=write).dict(),
                status=HTTPStatus.OK
            )

        name = await self.request.app['pg_db_manager'] \
            .user_get_project(
            user_id=self.request['user_id'],
            project_name=self.request.match_info['project_name']
        )

        if name is None:
            return ProjectNotFound()

        name, grant, read, write = await self.request.app['pg_db_manager'] \
            .user_get_project_info(
            user_id=self.request['user_id'],
            project_name=self.request.match_info['project_name']
        )

        return json_response(
            GetProjectResponse(name=name, grant=grant, read=read,
                               write=write).dict(),
            status=HTTPStatus.OK
        )

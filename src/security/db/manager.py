from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import logging
from security.db.schema import Project, User, UserAccess
from security.api.config import DB_CONNECTION_STR
from asyncpg.exceptions import PostgresError
import asyncio
import itertools


class DBExecution:
    """
    Класс хранящий в себе единственный на проект sqlalchemy engine,
    которому осуществяют доступ остальные классы, работающие с БД.
    """
    __instance = None

    def __init__(self):
        self.engine = create_async_engine(DB_CONNECTION_STR)
        self.session = AsyncSession(self.engine, future=True)
        self.logger = logging.Logger('db_access')

    async def execute(self, statement):
        session = AsyncSession(self.engine, future=True)
        async with session.begin():
            try:
                result = await session.execute(statement)
            except PostgresError as err:
                await session.rollback()
                raise err
            else:
                await session.commit()
                return result


class DBManager(DBExecution):
    async def user_create(self, yandex_id: str, is_admin: bool):
        query = insert(User) \
            .values(yoauth_uid=yandex_id, is_admin=is_admin) \
            .returning(User.id)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()
        return parsed_value[0]

    async def project_create(self, project_name: str) -> bool:
        query = insert(Project) \
            .values(name=project_name) \
            .returning(Project.id)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()

        return parsed_value[0] if parsed_value else None

    async def access_create(self, project_id: int, user_id: int) -> None:
        query = insert(UserAccess) \
            .values(project_id=project_id, user_id=user_id)
        await self.execute(query)

    async def project_get_id(self, user_id: int, project_name: str):
        query = select(Project.id) \
            .join(UserAccess) \
            .where(Project.name == project_name,
                   UserAccess.user_id == user_id) \
            .limit(1)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()
        return parsed_value[0] if parsed_value else None

    async def project_get_id_by_name(self, project_name: str):
        query = select(Project.id) \
            .where(Project.name == project_name) \
            .limit(1)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()
        return parsed_value[0] if parsed_value else None

    async def user_get_id(self, yandex_id: str):
        query = select(User.id).where(User.yoauth_uid == yandex_id)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()
        return parsed_value[0] if parsed_value is not None else None

    async def user_get_role_by_yandex_id(self, yandex_id: str) -> bool:
        query = select(User.is_admin).where(User.yoauth_uid == yandex_id)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()
        return parsed_value[0] if parsed_value is not None else None

    async def user_get_role_by_user_id(self, user_id: str) -> bool:
        query = select(User.is_admin).where(User.id == user_id)
        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()
        return parsed_value[0] if parsed_value is not None else None

    async def user_has_project(self, user_id: int, project_name: str) -> bool:
        return bool(await self.user_get_project(user_id, project_name))

    async def user_get_project(self, user_id, project_name: str) -> tuple:
        query = select(Project.name) \
            .join(UserAccess) \
            .filter(UserAccess.project_id == Project.id,
                    UserAccess.user_id == user_id,
                    Project.name == project_name)

        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()

        return parsed_value[0] if parsed_value else None

    async def user_get_project_info(self, user_id, project_name: str) -> tuple:
        query = select(Project.name, UserAccess.grant, UserAccess.write,
                       UserAccess.read) \
            .join(UserAccess) \
            .filter(UserAccess.project_id == Project.id,
                    UserAccess.user_id == user_id,
                    Project.name == project_name)

        returning_value = await self.execute(query)
        parsed_value = returning_value.fetchone()

        return parsed_value

    async def project_update_name(self, user_id: int, project_name: str,
                                  new_name: str):
        project_id = await self.project_get_id(user_id, project_name)
        if project_id is None:
            return False
        query = update(Project) \
            .where(Project.id == project_id) \
            .values(name=new_name)

        await self.execute(query)
        return True

    async def project_update_name_by_name(self,
                                          project_name: str,
                                          new_name: str):
        project_id = await self.project_get_id_by_name(project_name)
        if project_id is None:
            return False
        query = update(Project) \
            .where(Project.id == project_id) \
            .values(name=new_name)

        await self.execute(query)
        return True

    async def project_update_rights(self, user_id: int, project_id: int,
                                    write: bool, read: bool, grant: bool):
        if project_id is None:
            return False
        query = update(UserAccess) \
            .where(UserAccess.project_id == project_id,
                   UserAccess.user_id == user_id) \
            .values(write=write, read=read, grant=grant)

        await self.execute(query)
        return True

import asyncio
from aiohttp.web import Application
from security.api.config import DB_CONNECTION_STR, SERVICE_HOST, \
    SERVICE_PORT
from security.db.manager import DBManager
from security.api.handlers import HANDLERS
from security.api.log import LogManager
from security.api.middlewares import authorization, error_solving
from security.db import schema
from sqlalchemy.ext.asyncio import create_async_engine


async def init_db(conn_string: str = DB_CONNECTION_STR):
    app_engine = create_async_engine(conn_string)
    async with app_engine.begin() as conn:
        await conn.run_sync(schema.Base.metadata.drop_all)
        await conn.run_sync(schema.Base.metadata.create_all)


def setup_routes(app: Application):
    for handler in HANDLERS:
        app.router.add_route('*', handler.URL_PATH, handler)


def create_app() -> Application:
    log_manager = LogManager()
    logger = log_manager.logger

    app = Application(
        middlewares=[authorization, error_solving, ],
        logger=logger
    )

    app['pg_db_manager'] = DBManager()
    app['log_manager'] = log_manager

    # run_migrations()

    setup_routes(app)

    app['service_host'] = SERVICE_HOST
    app['service_port'] = SERVICE_PORT

    return app


def run_migrations():
    asyncio.run(init_db())

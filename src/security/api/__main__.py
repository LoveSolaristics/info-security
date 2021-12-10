from aiohttp.web import run_app
from security.api.app import create_app


def main():
    app = create_app()

    run_app(
        app,
        host=app['service_host'],
        port=app['service_port'],
    )


if __name__ == '__main__':
    main()

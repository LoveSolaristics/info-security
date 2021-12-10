from os import environ


DB_CONNECTION_STR = f"postgresql+asyncpg://" \
                    f"{environ.get('POSTGRES_USER', 'username')}:" \
                    f"{environ.get('POSTGRES_PWD', 'hackme')}" \
                    f"@{environ.get('POSTGRES_HOST', 'localhost')}" \
                    f":{environ.get('POSTGRES_PORT', '5432')}/" \
                    f"{environ.get('POSTGRES_DB', 'security')}"
SERVICE_HOST = environ.get('SERVICE_HOST', '0.0.0.0')
SERVICE_PORT = environ.get('SERVICE_PORT', '8080')

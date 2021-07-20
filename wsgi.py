"""App entry point."""
from application import create_app

from config import (
    DBMS,
    DATABASE_HOST, DATABASE_PORT,
    DATABASE_USERNAME, DATABASE_PASSWORD,
    DATABASE_NAME
)

app = create_app(
    f'{DBMS}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
)

if __name__ == '__main__':
    app.run()

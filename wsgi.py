"""App entry point."""
from application import create_app

from config import DBMS, DATABASE_HOST, DATABASE_PORT, \
    DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME

app = create_app(dbms=DBMS, database=DATABASE_NAME,
                 user=DATABASE_USERNAME, password=DATABASE_PASSWORD,
                 host=DATABASE_HOST, port=DATABASE_PORT)

if __name__ == '__main__':
    app.run()

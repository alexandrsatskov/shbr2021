"""The core application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(dbms, user, password,
               host, port, database):

    app = Flask(__name__)

    # Debug
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'{dbms}://{user}:{password}@{host}:{port}/{database}'

    # Init database
    db.init_app(app)

    with app.app_context():
        from . import routes

        db.create_all()

        return app

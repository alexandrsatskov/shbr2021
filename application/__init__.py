"""The core application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(db_url):

    app = Flask(__name__)

    # Debug
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.testing = True

    # Init database
    db.init_app(app)

    with app.app_context():
        from application import routes
        app.register_blueprint(routes.api)
        db.create_all()

    return app

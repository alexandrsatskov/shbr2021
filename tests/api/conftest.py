import os
import uuid
import pytest
from yarl import URL
from sqlalchemy_utils import create_database, drop_database
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from application import create_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DBMS = 'postgresql'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'
DATABASE_NAME = 'postgres'

# For local use
DATABASE_USERNAME = 'postgres'
DATABASE_PASSWORD = '123'
PG_URL = os.getenv(
    'CI_ANALYZER_PG_URL',
    f'{DBMS}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')


@pytest.fixture
def postgres():
    """
    Создает временную БД для запуска теста.
    """
    tmp_name = '.'.join([uuid.uuid4().hex, 'pytest'])
    tmp_url = str(URL(PG_URL).with_path(tmp_name))
    create_database(tmp_url)
    try:
        yield tmp_url
    finally:
        pass
        # drop_database(tmp_url)


@pytest.fixture
def api_client(postgres):
    app = create_app(postgres)

    with app.test_client() as client:
        yield client


@pytest.fixture
def postgres_connection(postgres):
    """
    Синхронное соединение со смигрированной БД.
    """
    engine = create_engine(postgres)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()


@pytest.fixture
def postgres_session(postgres):
    engine = create_engine(postgres)
    with Session(engine) as session:
        yield session
    engine.dispose()

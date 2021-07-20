import http
from datetime import datetime
from http import HTTPStatus

import pytest

from application.db_models import Courier, Order
from tests.conftest import (
    get_couriers, generate_courier, generate_couriers, post_couriers
)

LONGEST_STR = 'ё' * 256
CASES = (
    # Один курьер
    (

        # Один курьер
        [
            generate_courier(courier_id=1)
        ],
        '201 CREATED'
    ),

    # Несколько курьеров
    (
        [
            generate_courier(courier_id=1),
            generate_courier(courier_id=2),
            generate_courier(courier_id=3),
        ],
        '201 CREATED'
    ),

    # Очень много курьеров
    (
        generate_couriers(couriers_num=10000),
        '201 CREATED'
    ),

    # Пустая выгрузка
    (
        [],
        '400 BAD REQUEST'
    ),

    # courier_id не уникален в рамках выгрузки
    (
        [
            generate_courier(courier_id=1),
            generate_courier(courier_id=1),
        ],
        '400 BAD REQUEST'
    ),

    # invalid working_hours
    (
        [
            generate_courier(working_hours=["0:0-2:2"])
        ],
        '400 BAD REQUEST'
    ),
)


@pytest.mark.parametrize('couriers,expected_status', CASES)
def test_post_couriers(api_client, couriers, expected_status):
    post_couriers(api_client, couriers, expected_status)

    # Проверяем, что данные успешно импортированы
    if expected_status == '201 CREATED':
        imported_couriers = get_couriers(api_client, '200 OK')
        assert couriers == imported_couriers

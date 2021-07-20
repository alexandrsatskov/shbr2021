import http
from datetime import datetime
from http import HTTPStatus

import pytest

from application.db_models import Courier, Order
from tests.conftest import (
    get_couriers, generate_courier, generate_couriers, post_couriers, patch_courier, post_orders
)

CASES = (
    # Изменяем одно поле у курьера
    (
        generate_courier(courier_id=1),
        {
            "regions": [101, 123, 1293],
        },
        '200 OK'
    ),

    # Нельзя менять courier_id
    (
        generate_courier(courier_id=1),
        {
            "courier_id": 2,
        },
        '400 BAD REQUEST'
    ),
)


@pytest.mark.parametrize('courier,what_update,expected_status', CASES)
def test_patch_courier(api_client, courier, what_update, expected_status):
    post_couriers(api_client, [courier], '201 CREATED')

    response = patch_courier(api_client, courier['courier_id'], what_update, expected_status)
    for key, value in what_update.items():
        courier[key] = value
    # Проверяем, что данные успешно изменены
    if expected_status == '200 OK':
        assert courier == response


def test_patch_courier_noexist(api_client):
    """
    Обращение к несуществующему курьеру
    """
    patch_courier(api_client, 999, {'regions': [1, 2, 3]}, '400 BAD REQUEST')


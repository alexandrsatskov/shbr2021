import http
from datetime import datetime
from http import HTTPStatus

import pytest

from application.db_models import Courier, Order
from tests.conftest import (
    get_couriers, generate_courier, generate_couriers, post_couriers
)

datasets = [
    # Несколько курьеров
    [
        generate_courier(courier_id=1),
        generate_courier(courier_id=2),
        generate_courier(courier_id=3),
    ],

    # Один курьер
    [
        generate_courier(courier_id=1)
    ],

    # Ноль курьеров
    [],

    # Очень много курьеров
    [
        # Распаковываем, т.к. функция возвращает list
        *generate_couriers(100000)
    ]
]


@pytest.mark.parametrize('dataset', datasets)
def test_get_couriers(api_client, dataset):
    if dataset:
        post_couriers(api_client, dataset, '201 CREATED')

    actual_couriers = get_couriers(api_client, '200 OK')
    assert actual_couriers == dataset

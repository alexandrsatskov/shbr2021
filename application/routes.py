import re
from statistics import mean
from datetime import datetime
from functools import wraps


from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from marshmallow import ValidationError
from flask import request, jsonify
from flask import current_app as app


from .db_marshmallow_schemas import (
    CourierSchema, OrderSchema,
    ImportCourierSchema, ImportOrderSchema,
    ImportOrdersAssignSchema, ImportOrderCompleteSchema,
    PatchCourierSchema)
from .db_models import db, Courier, Order


def dt_correct_output(dt: datetime) -> str:
    return dt.isoformat()[:-4] + "Z"


def courier_assigned_orders(current_session, courier_id: int):
    query = current_session.query(Order) \
        .filter(and_(Order.courier_id == courier_id,
                     Order.status == 'assigned')) \
        .order_by(Order.weight)
    return query


def is_intervals_intersect(courier_time_intervals: list,
                           order_time_intervals: list) -> bool:
    """Проверяет что временные интервалы у
    курьера и заказа пересекаются
    """
    for working_hours in courier_time_intervals:

        working_start, working_end = \
            [datetime.strptime(time, '%H:%M') for time in working_hours.split('-')]

        for delivery_hours in order_time_intervals:
            delivery_start, delivery_end = \
                [datetime.strptime(time, '%H:%M') for time in delivery_hours.split('-')]

            if not ((delivery_start >= working_end) or (working_start >= delivery_end)):
                return True
    return False


def check_pk_violation(current_session, id_name: str):
    """Откатывает сессию и возвращает JSON с описанием ошибки,
    если произошло нарушение ограничения первичного ключа
    В ином случае, возвращает закомиченную сессию"""
    try:
        current_session.commit()
    except IntegrityError as err:
        current_session.rollback()
        # Ищем ID в описании IntegrityError.
        non_unique_courier_id = re.search(r"\d+", str(err.orig)).group()
        raise ValidationError(f'{id_name}: {non_unique_courier_id}: -> Индентификатор уже существует!')
    # Скорее всего здесь нужно будет убивать сессию...
    return current_session


def do_record_exists(record_id: int, property_name: str, table, current_session):
    try:
        record = current_session.query(table) \
            .filter(getattr(table, property_name) == record_id) \
            .one_or_none()
    except MultipleResultsFound:
        # Здесь должно быть логирование...
        pass
    else:
        if record is None:
            raise ValidationError(f'{property_name}: {record_id} -> Записи с данным ID не существует!')
        return record


def request_schema(marshmallow_schema, many_: bool = False):
    """Валидация JSON данных запроса"""

    def wrapper(function):
        @wraps(function)
        def inner_wrapper(*args, **kwargs):
            data = request.get_json()
            schema = marshmallow_schema(many=many_)

            try:
                # Валидация значений
                loaded_data = schema.load(data)

                # Валидация при участии БД. Из хендлера приходит ValidationError,
                # если записи не найдено, либо нарушается pk constraint.
                result = function(loaded_data, *args, **kwargs)
            except ValidationError as err:
                return jsonify({"validation_error": err.normalized_messages()}), 400
            return result

        return inner_wrapper
    return wrapper


@app.route('/couriers', methods=['GET'])
def get_couriers():
    couriers = db.session.query(Courier).all()
    print(CourierSchema(many=True).dump(couriers))
    return jsonify(CourierSchema(many=True).dump(couriers)), 200


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = db.session.query(Order).all()
    return jsonify(OrderSchema(many=True).dump(orders)), 200


@app.route('/couriers', methods=['POST'])
@request_schema(ImportCourierSchema)
def post_couriers(loaded_request_data):
    successful_response = {"couriers": []}

    # Сериализованные данные, полученные из request_schema
    couriers = loaded_request_data['data']

    for courier in couriers:
        successful_response['couriers'].append({"id": courier['courier_id']})

        db.session.add(Courier(
            courier_id=courier['courier_id'],
            courier_type=courier['courier_type'],
            regions=courier['regions'],
            working_hours=courier['working_hours']))

    # Выбрасывает ValidationError, если id уже существует,
    # обработка происходит в request_schema
    check_pk_violation(db.session, id_name='courier_id')
    return jsonify(successful_response), 201


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
@request_schema(PatchCourierSchema)
def patch_courier(loaded_request_data, courier_id):
    # Выбрасывает ValidationError если запись не найдена,
    # обработка происходит в request_schema
    courier = do_record_exists(record_id=courier_id,
                               property_name='courier_id',
                               table=Courier,
                               current_session=db.session)

    for key, value in loaded_request_data.items():
        setattr(courier, key, value)
    db.session.commit()

    successful_response = CourierSchema().dump(courier)

    assigned_orders = courier_assigned_orders(db.session, courier_id)
    is_already_assigned = \
        db.session.query(assigned_orders.exists()).scalar()

    # # Убрать в релизе
    # matching_orders = []
    if is_already_assigned:
        backpack_weight = 0
        courier_max_weight = courier.courier_type.get_weight()

        for order in assigned_orders:
            if not(((backpack_weight + order.weight) <= courier_max_weight) and
                    is_intervals_intersect(courier.working_hours, order.delivery_hours) and
                    order.region in courier.regions):
                order.status = 'available'
                order.assign_time = None
                order.courier_id = None
                db.session.commit()

                # # Убрать в релизе
                # matching_orders.append(order.order_id)

            backpack_weight += order.weight

        # successful_response.update({"Убранные заказы": [{"id": order_id} for order_id in matching_orders]})

    return jsonify(successful_response), 200


@app.route('/orders', methods=['POST'])
@request_schema(ImportOrderSchema)
def post_orders(loaded_request_data):
    successful_response = {"orders": []}
    orders = loaded_request_data['data']

    for order in orders:
        successful_response['orders'].append({"id": order['order_id']})

        db.session.add(Order(
            order_id=order['order_id'],
            weight=order['weight'],
            region=order['region'],
            delivery_hours=order['delivery_hours']))

    check_pk_violation(db.session, id_name='order_id')

    return jsonify(successful_response), 201


@app.route('/orders/assign', methods=['POST'])
@request_schema(ImportOrdersAssignSchema)
def assign_order(loaded_request_data):
    successful_response = {"orders": []}

    courier = do_record_exists(record_id=loaded_request_data['courier_id'],
                               property_name='courier_id',
                               table=Courier,
                               current_session=db.session)

    # Если курьеру уже назначены заказы:
    assigned_orders = courier_assigned_orders(db.session, courier.courier_id)
    is_already_assigned = db.session.query(assigned_orders.exists()).scalar()
    if is_already_assigned:
        successful_response['orders'].extend([{"id": order.order_id} for order in assigned_orders])
        successful_response.update({"assign_time": f'{dt_correct_output(assigned_orders[0].assign_time)}'})
        return jsonify(successful_response), 200

    # Сразу делаем проверку на соответствие
    # регионов, чтобы чуть отсеять
    available_orders = db.session.query(Order) \
        .filter(and_(Order.region.in_(courier.regions),
                     Order.status == 'available')) \
        .order_by(Order.weight)

    assign_time_ = datetime.today()
    matching_orders = []
    backpack_weight = 0
    courier_max_weight = courier.courier_type.get_weight()

    for order in available_orders:
        if ((backpack_weight + order.weight) <= courier_max_weight) and \
                is_intervals_intersect(courier.working_hours, order.delivery_hours):
            order.status = 'assigned'
            order.assign_time = assign_time_
            order.courier_id = courier.courier_id
            db.session.commit()

            matching_orders.append(order.order_id)
            backpack_weight += order.weight

    if len(matching_orders) == 0:
        return jsonify(successful_response), 200
    else:
        successful_response['orders'].extend([{"id": order} for order in matching_orders])
        successful_response.update({"assign_time": f'{dt_correct_output(assign_time_)}'})
        return jsonify(successful_response), 200


@app.route('/orders/complete', methods=['POST'])
@request_schema(ImportOrderCompleteSchema)
def complete_order(loaded_request_data):
    # т.к. передается строка с <Z> на конце, то приходится скармливать marshmallow это значение как aware datetime
    # поэтому приходится вручную убирать timezone, для банального сравнения datetime'ов
    aware_complete_time = loaded_request_data['complete_time']
    native_complete_time = aware_complete_time.replace(tzinfo=None)

    order = do_record_exists(record_id=loaded_request_data['order_id'],
                             property_name='order_id',
                             table=Order,
                             current_session=db.session)

    # Все подобные исключения перехватываюстя в request_schema
    if order.status.value == 'available':
        raise ValidationError(
            f'order_id: {order.order_id} -> Заказ с данным ID еще не назначен!')

    if order.status.value == 'completed':
        raise ValidationError(
            f'order_id: {order.order_id} -> Заказ с данным ID уже завершен!')

    if order.courier_id != loaded_request_data['courier_id']:
        raise ValidationError(
            f'order_id: {order.order_id} -> Заказ с данным ID не назначен на данного курьера!')

    if native_complete_time <= order.assign_time:
        raise ValidationError(
            f'{native_complete_time} <= {order.assign_time}'
            f' -> Дата завершения меньше или равна дате назначения!')

    order.complete_time = native_complete_time
    order.status = 'completed'
    db.session.commit()

    return jsonify({"order_id": order.order_id})


@app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_courier_stat(courier_id):
    try:
        courier = do_record_exists(record_id=courier_id,
                                   property_name='courier_id',
                                   table=Courier,
                                   current_session=db.session)
    except ValidationError as err:
        return jsonify({"validation_error": err.normalized_messages()}), 400

    successful_response = CourierSchema().dump(courier)

    courier_completed_orders = db.session.query(Order) \
        .filter(and_(Order.courier_id == courier.courier_id,
                     Order.status == 'completed'))

    delivery_times_by_region = {}

    for order in courier_completed_orders:
        if order.region not in delivery_times_by_region.keys():
            delivery_times_by_region[order.region] = []
            delivery_times_by_region[order.region].extend([order.assign_time, order.complete_time])
        else:
            delivery_times_by_region[order.region].append(order.complete_time)

    # Рассчет earnings
    n = db.session.query(Order.assign_time)\
        .filter(Order.courier_id == courier.courier_id)\
        .group_by(Order.assign_time).count()
    c = courier.courier_type.get_coefficient()
    successful_response.update({"earnings": n * 500 * c})

    # Рассчет rating
    if db.session.query(courier_completed_orders.exists()).scalar():
        delivery_times_by_region_in_seconds = {region: [] for region in delivery_times_by_region.keys()}
        for region, delivery_times in delivery_times_by_region.items():
            i = 0
            while i < len(delivery_times) - 1:
                delivery_times_by_region_in_seconds[region]\
                    .append(abs((delivery_times[i] - delivery_times[i + 1]).total_seconds()))
                i += 1

        t = min([mean(delivery_times) for delivery_times in delivery_times_by_region_in_seconds.values()])
        successful_response.update({"rating": (3600 - min(t, 3600)) / 3600 * 5})

    return jsonify(successful_response), 200

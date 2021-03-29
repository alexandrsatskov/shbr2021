"""Описание marshmallow схем
Схемы используются при валидации, и,
соответственно, при сериализации/десериализации
"""


from datetime import datetime
import re


from marshmallow import Schema, ValidationError, validates_schema
from marshmallow.fields import (
    DateTime as MarshmallowDatetime,
    Float as MarshmallowFloat,
    Int, List, Nested, Str)
from marshmallow.validate import Length, Range, Regexp
from marshmallow_enum import EnumField


from .db_enum import CourierType

# Регулярное выражения для marshmallow валидации в <schema>. Формат HH:MM-HH:MM.
TIME_PATTERN = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')

ERROR_VALIDATION = {
    "courier_type": 'Допустимые значения: foot, bike, car.',
    "empty": 'Необходимо хотя бы одно значение!',
    "time": 'Строка должна быть в формате: HH:MM-HH:MM!',
}


def validate_regions_unique(value: list):
    if len(value) != len(set(value)):
        raise ValidationError(
            f'{value} -> Регионы должны быть уникальны!')


def validate_time_intervals(time_intervals: list):
    """Проверка, что конечное время интервала
    строго больше начального времени
    """
    for time_interval in time_intervals:
        start, end = time_interval.split('-')
        start = datetime.strptime(start, '%H:%M')
        end = datetime.strptime(end, '%H:%M')
        if (end - start).total_seconds() <= 0:
            raise ValidationError(
                f'{time_interval} -> Время старта меньше (или равно) времени окончания!')


def validate_unique_id(data, property_name: str):
    """Проверка на дублирование id в post-запросе"""
    record_ids = set()
    for record in data['data']:
        if record[property_name] in record_ids:
            raise ValidationError(
                f'{property_name}: {record[property_name]} -> Индентификатор дублируется в данной выборке!'
            )
        record_ids.add(record[property_name])


class PatchCourierSchema(Schema):
    courier_type = \
        EnumField(CourierType, by_value=True, error=ERROR_VALIDATION['courier_type'])
    regions = \
        List(Int(validate=Range(min=0), strict=True),
             validate=[Length(min=1, error=ERROR_VALIDATION['empty']), validate_regions_unique])
    working_hours = \
        List(Str(validate=Regexp(TIME_PATTERN, error=ERROR_VALIDATION['time'])),
             validate=[Length(min=1, error=ERROR_VALIDATION['empty']), validate_time_intervals])


class CourierSchema(PatchCourierSchema):
    courier_id = \
        Int(validate=Range(min=0), strict=True, required=True)
    courier_type = \
        EnumField(CourierType, by_value=True, required=True,
                  error=ERROR_VALIDATION['courier_type'])
    regions = \
        List(Int(validate=Range(min=0), strict=True), required=True,
             validate=[Length(min=1, error=ERROR_VALIDATION['empty']), validate_regions_unique])
    working_hours = \
        List(Str(validate=Regexp(TIME_PATTERN, error=ERROR_VALIDATION['time'])),
             required=True, validate=[Length(min=1, error=ERROR_VALIDATION['empty']), validate_time_intervals])


class OrderSchema(Schema):
    order_id = \
        Int(validate=Range(min=0), strict=True, required=True)
    weight = \
        MarshmallowFloat(validate=Range(min=0.01, max=50), required=True)
    region = \
        Int(validate=Range(min=0), strict=True, required=True)
    delivery_hours = \
        List(Str(validate=Regexp(TIME_PATTERN, error=ERROR_VALIDATION['time'])),
             required=True, validate=[Length(min=1, error=ERROR_VALIDATION['empty']), validate_time_intervals])


class ImportOrdersAssignSchema(Schema):
    courier_id = Int(validate=Range(min=0), strict=True, required=True)


class ImportCourierSchema(Schema):
    data = Nested(CourierSchema, many=True, required=True,
                  validate=Length(min=1, error=ERROR_VALIDATION['empty']))

    @validates_schema
    def validate_unique_courier_id(self, data, **_):
        validate_unique_id(data=data, property_name='courier_id')


class ImportOrderSchema(Schema):
    data = Nested(OrderSchema, many=True, required=True,
                  validate=Length(min=1, error=ERROR_VALIDATION['empty']))

    @validates_schema
    def validate_unique_order_id(self, data, **_):
        validate_unique_id(data=data, property_name='order_id')


class ImportOrderCompleteSchema(Schema):
    courier_id = Int(validate=Range(min=0), strict=True, required=True)
    order_id = Int(validate=Range(min=0), strict=True, required=True)
    complete_time = MarshmallowDatetime(required=True)

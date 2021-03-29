"""Enum классы для db_models/db_marshmallow_schemas"""

from enum import Enum, unique


@unique
class CourierType(Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'

    def get_weight(self) -> float:
        if self is self.foot:
            return 10.
        elif self is self.bike:
            return 15.
        elif self is self.car:
            return 50.

    def get_coefficient(self) -> int:
        if self is self.foot:
            return 2
        elif self is self.bike:
            return 5
        elif self is self.car:
            return 9


@unique
class OrderStatus(Enum):
    available = 'available'
    assigned = 'assigned'
    completed = 'completed'

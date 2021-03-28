"""Enum классы для db_models/db_marshmallow_schemas"""

from enum import Enum, unique


@unique
class CourierType(Enum):
    FOOT = 'foot'
    BIKE = 'bike'
    CAR = 'car'

    def get_weight(self) -> float:
        if self is self.FOOT:
            return 10.
        elif self is self.BIKE:
            return 15.
        elif self is self.CAR:
            return 50.

    def get_coefficient(self) -> int:
        if self is self.FOOT:
            return 2
        elif self is self.BIKE:
            return 5
        elif self is self.CAR:
            return 9


@unique
class OrderStatus(Enum):
    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    COMPLETED = 'completed'

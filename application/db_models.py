"""Описание таблиц БД в представлении Flask-SQLAlchemy"""

from . import db
from .db_enum import CourierType, OrderStatus


class Courier(db.Model):
    __tablename__ = 'couriers'

    courier_id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(db.Enum(CourierType, name='courier_type'), nullable=False)
    regions = db.Column(db.ARRAY(db.Integer), nullable=False)
    working_hours = db.Column(db.ARRAY(db.String), nullable=False)

    assigned_courier = db.relationship('Order', backref='assigned_courier')


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    region = db.Column(db.Integer, nullable=False)
    delivery_hours = db.Column(db.ARRAY(db.String), nullable=False)

    status = db.Column(db.Enum(OrderStatus, name='status'), default='available', nullable=False)
    assign_time = db.Column(db.DateTime(timezone=False), nullable=True)
    complete_time = db.Column(db.DateTime(timezone=False), nullable=True)

    courier_id = db.Column(db.Integer, db.ForeignKey('couriers.courier_id'), nullable=True)

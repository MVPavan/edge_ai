from backend.tq_jobs.celery_init import celery_app
from imports import select
from .tables import get_session, Session
from backend.kite.consts.order_consts.order_crud_consts import (
    OrderUpdate
)
from backend.kite.consts.db_consts import OrdersDB
from backend.kite.consts.consolidated_consts import OrdersRead
from backend.core.order_funcs import order_history


class OrdersDbCRUD:
    def __init__(self):
        self.session: Session = get_session().__next__()

    @staticmethod
    def __fetch_kite_orders(order_id: str = None):
        orders_read: OrdersRead = order_history()
        if order_id is None:
            return orders_read
        order = [order for order in orders_read.orders if order.order_id == order_id][0]
        return order

    def __fetch_db(self, order_id: str = None):
        if order_id is None:
            _query = select(OrdersDB)
        else:
            _query = select(OrdersDB).where(OrdersDB.order_id == order_id)
        orders_db = self.session.exec(_query).all()
        return orders_db

    def __add_db(self, order_db: OrdersDB):
        self.session.add(order_db)
        self.session.commit()

    def __update(self, order_id: str):
        order_db = self.__fetch_db(order_id)[0]
        assert order_db != [], "Can't update a new order! "
        order = self.__fetch_kite_orders(order_id)
        _order_data = order.dict(exclude_unset=True)
        for key, value in _order_data.items():
            setattr(order_db, key, value)
        self.__add_db(order_db)

    def __add(self, order_id: str):
        """
        Add new order with order_id in DB
        """
        order_db = self.__fetch_db(order_id)
        assert order_db == [], "Can't have new order with already existing order id"
        order = self.__fetch_kite_orders(order_id)
        self.__add_db(OrdersDB.from_orm(order))

    def sync_order(self, order_id: str):
        order_db = self.__fetch_db(order_id)
        if not order_db:
            self.__add(order_id)
        else:
            self.__update(order_id)

    def sync_all(self):
        orders_read = self.__fetch_kite_orders()
        for _order_read in orders_read.orders:
            self.sync_order(_order_read.order_id)

    def sync_all_fast(self):
        orders_db = self.__fetch_db()
        orders_read = self.__fetch_kite_orders()
        for _order_db in orders_db:
            for _order_read in orders_read.orders:
                if _order_db.order_id != _order_read.order_id: continue
                _order_read_data = _order_read.dict(exclude_unset=True)
                for key, value in _order_read_data.items():
                    setattr(_order_db, key, value)
            self.session.add(_order_db)
        self.session.commit()
        orders_db = self.__fetch_db()
        for _order_read in orders_read.orders:
            exists = False
            for _order_db in orders_db:
                if _order_db.order_id == _order_read.order_id:
                    exists = True
            if not exists:
                self.session.add(OrdersDB.from_orm(_order_read))
        self.session.commit()


@celery_app.task
def update_order(data: dict):
    _order_update = OrderUpdate(**data)
    OrdersDbCRUD().sync_order(order_id=_order_update.order_id)


@celery_app.task
def sync_orders(order_id: str = None, quick=True):
    if order_id is not None:
        OrdersDbCRUD().sync_order(order_id)
    else:
        if not quick:
            OrdersDbCRUD().sync_all()
        else:
            OrdersDbCRUD().sync_all_fast()

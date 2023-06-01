import backend.kite.consts.consolidated_consts
from imports import (
    APIRouter
)
from backend.kite.consts.order_consts import order_crud_consts
from backend.kite.consts import consolidated_consts

from backend.core import order_funcs

orders_api_router = APIRouter()


@orders_api_router.post("/modify_order/", response_model=order_crud_consts.OrderResponse)
def modify_order(_order: order_crud_consts.ModifyOrder):
    response = order_funcs.modify_order(_order)
    return response


@orders_api_router.post("/cancel_order/", response_model=order_crud_consts.OrderResponse)
def cancel_order(_order: order_crud_consts.CancelOrder):
    response = order_funcs.cancel_order(_order)
    return response


@orders_api_router.get("/order_history/", response_model=consolidated_consts.OrdersRead)
def order_history(_order_id: str = None):
    response = order_funcs.order_history(_order_id)
    return response


@orders_api_router.get("/trade_history/", response_model=order_crud_consts.RetrieveTrades)
def trade_history(_order_id: str = None):
    response = order_funcs.trade_history(_order_id)
    return response

from imports import (
    APIRouter
)
from backend.kite.consts.order_consts import mis_consts as mc, order_crud_consts
from backend.core import order_funcs

mis_orders_api_router = APIRouter()


@mis_orders_api_router.post("/place_order/", response_model=order_crud_consts.OrderResponse)
def place_mis_order(mis_type: mc.MisType, _order: mc.PlaceMis):
    order = mc.MisFuncs.__dict__[mis_type.name].parse_obj(_order)
    response = order_funcs.place_order(order)
    return response


# @app.put("/orders/buy/{scrip}")
# def place_order(scrip: str, quantity=1, buy=True):
#     if buy:
#         transaction_type = kite.TRANSACTION_TYPE_BUY
#     else:
#         transaction_type = kite.TRANSACTION_TYPE_SELL
#
#     response = kite.place_order(
#         variety=kite.VARIETY_AMO,
#         exchange=kite.EXCHANGE_BSE,
#         tradingsymbol=scrip,
#         transaction_type=transaction_type,
#         quantity=quantity,
#         product=kite.PRODUCT_CNC,
#         order_type=kite.ORDER_TYPE_MARKET
#     )
#     print("wow")
#
#
# @app.get("/orders/get_order_id")
# def get_order_id():
#     orders = kite.orders()
#     for order in orders:
#         if "RECEIVED" in order["status"]:
#             return order["order_id"]
#
#
# @app.put("/orders/cancel/{order_id}")
# def cancel_order(order_id: str):
#     try:
#         kite.cancel_order(
#             variety=kite.VARIETY_AMO,
#             order_id=order_id
#         )
#         return True
#     except Exception as e:
#         print(e)
#         return False
#
#
# @app.get("/instruments")
# def get_instruments():
#     return kite.instruments()

from imports import (
    APIRouter
)


orders_api_router = APIRouter()


# @orders_api_router.post("/organizations/", response_model=order_crud_consts.OrderResponse)
# def modify_order(_order: order_crud_consts.ModifyOrder):
#     response = order_funcs.modify_order(_order)
#     return response


# @orders_api_router.post("/buildings/", response_model=order_crud_consts.OrderResponse)
# def cancel_order(_order: order_crud_consts.CancelOrder):
#     response = order_funcs.cancel_order(_order)
#     return response


# @orders_api_router.get("/cameras/", response_model=consolidated_consts.OrdersRead)
# def order_history(_order_id: str = None):
#     response = order_funcs.order_history(_order_id)
#     return response



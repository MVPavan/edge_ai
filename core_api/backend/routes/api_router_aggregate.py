from imports import APIRouter
# from .portfolio_router import portfolio_api_router
# from .orders_router import orders_api_router
# from .mis_orders_router import mis_orders_api_router

api_router = APIRouter()

# api_router.include_router(
#     portfolio_api_router,
#     prefix="/portfolio",
#     tags=["Portfolio"],
#     responses={404: {"description": "Not found"}},
# )

# api_router.include_router(
#     orders_api_router,
#     prefix="/orders",
#     tags=["Orders"],
#     responses={404: {"description": "Not found"}},
# )

# api_router.include_router(
#     mis_orders_api_router,
#     prefix="/orders/mis",
#     tags=["Orders/MIS"],
#     responses={404: {"description": "Not found"}},
# )

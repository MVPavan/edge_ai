from imports import (
    APIRouter
)
from backend.core import portfolio_funcs


portfolio_api_router = APIRouter()


@portfolio_api_router.get("/holdings/", response_model=portfolio_funcs.HoldingsRead)
def holdings():
    response = portfolio_funcs.get_holdings()
    return response


@portfolio_api_router.get("/positions/", response_model=portfolio_funcs.PositionsRead)
def positions():
    response = portfolio_funcs.get_positions()
    return response


from backend.tq_jobs.celery_init import celery_app
from imports import select, Union
from .tables import get_session, Session
from backend.kite.consts.db_consts import HoldingsDB, PositionsDB, PortfolioDB
from backend.kite.consts.consolidated_consts import HoldingsRead, PositionsRead, HoldingsConsts, PositionConsts
from backend.core.portfolio_funcs import get_holdings, get_positions


class PortfolioDbCRUD:
    def __init__(self):
        self.session: Session = get_session().__next__()

    @staticmethod
    def __fetch_kite_holdings():
        holdings_read: HoldingsRead = get_holdings()
        return holdings_read

    @staticmethod
    def __fetch_kite_positions():
        positions_read: PositionsRead = get_positions()
        return positions_read

    def __fetch_portfolio_db(
            self,
            portfolio_db_class=PortfolioDB.holdings_db,
            instrument_token=None,
            product=None,
            exchange=None
    ):
        if instrument_token and product and exchange:
            portfolio_db = self.session.exec(select(portfolio_db_class).where(
                portfolio_db_class.instrument_token == instrument_token,
                portfolio_db_class.product == product,
                portfolio_db_class.exchange == exchange
            )).all()
        else:
            portfolio_db = self.session.exec(select(portfolio_db_class)).all()
        return portfolio_db

    def __add_portfolio(self, portfolio_db: Union[HoldingsDB, PositionsDB], commit=True):
        self.session.add(portfolio_db)
        if commit:
            self.session.commit()

    def __update_portfolio(
            self,
            portfolio_const: Union[HoldingsConsts, PositionConsts],
            portfolio_db_class=PortfolioDB.holdings_db,
            portfolio_db_list: list[PortfolioDB.holdings_db] = None
    ):
        if portfolio_db_list is None:
            portfolio_db_list = self.__fetch_portfolio_db(
                portfolio_db_class=portfolio_db_class,
                instrument_token=portfolio_const.instrument_token,
                product=portfolio_const.product,
                exchange=portfolio_const.exchange
            )

        if len(portfolio_db_list) > 0:
            updated = False
            for portfolio_db in portfolio_db_list:
                if (
                        portfolio_db.instrument_token == portfolio_const.instrument_token and
                        portfolio_db.product == portfolio_const.product and
                        portfolio_db.exchange == portfolio_const.exchange
                ):
                    portfolio_data = portfolio_const.dict(exclude_unset=True)
                    for key, value in portfolio_data.items():
                        setattr(portfolio_db, key, value)
                    self.__add_portfolio(portfolio_db, commit=False)
                    updated = True
            if not updated:
                self.__add_portfolio(portfolio_db_class.from_orm(portfolio_const))
            self.session.commit()
        else:
            self.__add_portfolio(portfolio_db_class.from_orm(portfolio_const))

    def sync_positions(self):
        positions_read = self.__fetch_kite_positions()
        positions_db_list = self.__fetch_portfolio_db(portfolio_db_class=PortfolioDB.positions_db)

        for positions_const in positions_read.net:  # TODO: Difference btw net and day
            self.__update_portfolio(
                portfolio_const=positions_const,
                portfolio_db_class=PortfolioDB.positions_db,
                portfolio_db_list=positions_db_list
            )

    def sync_holdings(self):
        holdings_read = self.__fetch_kite_holdings()
        holdings_db_list = self.__fetch_portfolio_db(portfolio_db_class=PortfolioDB.holdings_db)

        for holdings_const in holdings_read.holdings:
            self.__update_portfolio(
                portfolio_const=holdings_const,
                portfolio_db_class=PortfolioDB.holdings_db,
                portfolio_db_list=holdings_db_list
            )


@celery_app.task
def sync_positions():
    PortfolioDbCRUD().sync_positions()


@celery_app.task
def sync_holdings():
    PortfolioDbCRUD().sync_holdings()

from trader import Trader
from portfolio import Portfolio
from datetime import datetime




def main():
    portfolio = Portfolio("Cole", 1_000_000)
    trader = Trader(portfolio, "2020-01-01", "2020-12-31")
    trader.trade([7, 14, 21, 28], [50, 100, 150, 200])


main()
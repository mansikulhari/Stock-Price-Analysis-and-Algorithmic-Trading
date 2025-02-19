import mysql.connector as mysql



class Portfolio:
    def __init__(self, portfolio_name: str, initial_cash: float):
        self.portfolio_name = portfolio_name
        self.initial_cash = initial_cash
        self.portfolio_value = initial_cash
        self.num_buys = 0
        self.num_sells = 0

        conn = mysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="easy",
            database="stock_data",
            connection_timeout=5
        )

        cursor = conn.cursor()
        portfolio_query = "SELECT symbol FROM Portfolio WHERE name = %s;"
        cursor.execute(portfolio_query, (portfolio_name,))

        stocks = [row[0] for row in cursor.fetchall()]
        self.stock_quants = {stock: 0 for stock in stocks}

    def buy(self, symbol: str, price: float, quantity=100) -> None:
        if self.portfolio_value < quantity * price:
            return
        self.portfolio_value -= quantity * price - 5
        self.stock_quants[symbol] += quantity
        self.num_buys += 1


    def sell(self, symbol: str, price: float, quantity=100) -> None:
        if self.stock_quants[symbol] < quantity:
            return
        self.portfolio_value += quantity * price - 5
        self.stock_quants[symbol] -= quantity
        self.num_sells += 1


    def calculate_roi(self) -> float:
        return 100 * (self.portfolio_value - self.initial_cash) / self.initial_cash


    def get_portfolio_value(self) -> float:
        return self.portfolio_value

    def get_stocks(self):
        return self.stock_quants.keys()


    def __repr__(self):
        return f"Portfolio: {self.portfolio_name}\nValue: ${self.portfolio_value:,.2f}\nStocks: {self.stock_quants} \
        \nROI: {self.calculate_roi():.2f}%\nBuys: {self.num_buys}\nSells: {self.num_sells}\n"




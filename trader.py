import mysql.connector as mysql
from models.rsi import calculate_rsi
from portfolio import Portfolio
from models.moving_averages import calc_moving_avg


class Trader:
    def __init__(self, portfolio: Portfolio, start: str, end: str):
        self.start = start
        self.end = end
        self.portfolio = portfolio
        self.stocks = portfolio.get_stocks()
        self.prices = dict()
        self.rsi = dict()
        self.avgs = dict()
        self._set_prices()

        for symbol, price in self.prices.items():
            print(symbol, len(price))
        print()

    def _set_prices(self) -> None:
        conn = mysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="easy",
            database="stock_data",
            connection_timeout=5
        )

        cursor = conn.cursor()
        for symbol in self.stocks:
            prices_query = "SELECT close FROM StockData WHERE symbol = '%s' AND date >= '%s' AND date <= '%s' ORDER " \
                           "BY date ASC;" % (symbol, self.start, self.end)
            cursor.execute(prices_query)
            prices = [row[0] for row in cursor.fetchall()]
            self.prices[symbol] = prices

    def _set_rsis(self, context_lengths) -> None:
        for symbol in self.stocks:
            self.rsi[symbol] = {}
            for context_length in context_lengths:
                self.rsi[symbol][f'rsi_{context_length}'] = calculate_rsi(self.prices[symbol], context_length)

    def _set_avgs(self, context_lengths) -> None:
        for symbol in self.stocks:
            self.avgs[symbol] = {}
            for context_length in context_lengths:
                self.avgs[symbol][f'avg_{context_length}'] = calc_moving_avg(self.prices[symbol], context_length)

    def trade(self, short_term_lengths, long_term_lengths) -> None:
        self._set_rsis(short_term_lengths + long_term_lengths)
        self._set_avgs(short_term_lengths + long_term_lengths)

        max_length = max(short_term_lengths + long_term_lengths)

        for symbol in self.stocks:

            # Initialize variables to keep track of the previous day's data
            prev_short_avg = {}
            prev_long_avg = {}
            prev_rsi = {}

            for length in short_term_lengths + long_term_lengths:
                prev_short_avg[length] = None
                prev_long_avg[length] = None
                prev_rsi[length] = None

            # Offset i by max_length to avoid indexing issues
            for i in range(max_length, len(self.prices[symbol])):

                # Loop through the short-term lengths for golden/death crosses and RSI
                for short in short_term_lengths:
                    short_avg = self.avgs[symbol][f'avg_{short}'][i - max_length]
                    rsi = self.rsi[symbol][f'rsi_{short}'][i - max_length]

                    # For long-term lengths, check for crosses
                    for long in long_term_lengths:
                        long_avg = self.avgs[symbol][f'avg_{long}'][i - max_length]

                        if prev_short_avg[short] is not None and prev_long_avg[long] is not None:
                            # Golden Cross
                            if prev_short_avg[short] <= prev_long_avg[long] and short_avg > long_avg:
                                self.portfolio.buy(symbol, self.prices[symbol][i])

                            # Death Cross
                            elif prev_short_avg[short] >= prev_long_avg[long] and short_avg < long_avg:
                                self.portfolio.sell(symbol, self.prices[symbol][i])

                        # Update previous averages
                        prev_short_avg[short] = short_avg
                        prev_long_avg[long] = long_avg

                    # RSI Strategy: Overbought or Oversold
                    if rsi < 30:
                        self.portfolio.buy(symbol, self.prices[symbol][i])
                    elif rsi > 40:
                        self.portfolio.sell(symbol, self.prices[symbol][i])

                    # Update previous RSI
                    prev_rsi[short] = rsi

            print(self.portfolio)

    def majority_vote(self, short_term_lengths, long_term_lengths):
        self._set_rsis(short_term_lengths + long_term_lengths)
        self._set_avgs(short_term_lengths + long_term_lengths)

        max_length = max(short_term_lengths + long_term_lengths)

        for symbol in self.stocks:

            for i in range(max_length, len(self.prices[symbol])):
                buy_votes = 0
                sell_votes = 0
                hold_votes = 0

                # Loop through the short-term lengths for golden/death crosses and RSI
                for short in short_term_lengths:
                    short_avg = self.avgs[symbol][f'avg_{short}'][i - max_length]
                    rsi = self.rsi[symbol][f'rsi_{short}'][i - max_length]

                    # For long-term lengths, check for crosses
                    for long in long_term_lengths:
                        long_avg = self.avgs[symbol][f'avg_{long}'][i - max_length]

                        # Golden Cross
                        if short_avg > long_avg:
                            buy_votes += 1

                        # Death Cross
                        elif short_avg < long_avg:
                            sell_votes += 1
                        else:
                            hold_votes += 1

                    # RSI Strategy: Overbought or Oversold
                    if rsi < 30:
                        buy_votes += 1
                    elif rsi > 40:
                        sell_votes += 1
                    else:
                        hold_votes += 1

                # Make a decision based on majority voting
                if buy_votes > max(sell_votes, hold_votes):
                    self.portfolio.buy(symbol, self.prices[symbol][i])
                elif sell_votes > max(buy_votes, hold_votes):
                    self.portfolio.sell(symbol, self.prices[symbol][i])

            print(self.portfolio)

    def get_portfolio(self) -> Portfolio:
        return self.portfolio



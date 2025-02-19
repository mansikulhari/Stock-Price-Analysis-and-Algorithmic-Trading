import mysql.connector
import yfinance as yf
import datetime
import mysql.connector


def create_tables():
    print('Trying to connect to mysql...')
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="easy",
        database="stock_data",
        connection_timeout=5
    )
    print('Connected to mysql')

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Portfolio (
                    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    symbol VARCHAR(255) NOT NULL,
                    UNIQUE (name, symbol)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS StockData (
                    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume BIGINT,
                    UNIQUE (symbol, date)
                    )''')

    conn.commit()
    conn.close()



def add_to_portfolio(name, symbols):
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="easy",
        database="stock_data",
        connection_timeout=5,
    )

    date = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor = conn.cursor()
    for symbol in symbols:
        cursor.execute('INSERT IGNORE INTO Portfolio (date, name, symbol) VALUES (%s, %s, %s)', (date, name, symbol))
    conn.commit()
    conn.close()


def fetch_and_store_stock_data(name, start_date, end_date):
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="easy",
        database="stock_data"
    )

    cursor = conn.cursor()

    cursor.execute('SELECT symbol FROM Portfolio WHERE name = %s', (name,))
    symbols = [row[0] for row in cursor.fetchall()]

    for symbol in symbols:
        print(f"start_date", start_date, "end_date", end_date)
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        for index, row in stock_data.iterrows():
            date = index.strftime('%Y-%m-%d')
            cursor.execute(
                'INSERT IGNORE INTO StockData (symbol, date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, '
                '%s, %s, %s)',
                (symbol, date, row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))

    conn.commit()
    conn.close()



if __name__ == '__main__':
    create_tables()
    # The user should have an option to create a portfolio and define a list of stocks to be included
    # in the portfolio. The script should accordingly fetch the stock price data for an input date
    # range for the list of stocks in the portfolio.
    while True:
        print("\nOptions:")
        print("1. Create new portfolio")
        print("2. Exit")

        choice = input("Choose an option: ")
        if choice == '1':
            portfolio_name = input("Enter a name for your portfolio: ")
            stocks = input("Enter the stock symbols to include in the portfolio, separated by spaces: ").split(' ')
            start_date = input("Enter the start date in YYYY-MM-DD format: ")
            end_date = input("Enter the end date in YYYY-MM-DD format: ")
            add_to_portfolio(portfolio_name, [symbol.strip().upper() for symbol in stocks])
            for symbol in stocks:
                fetch_and_store_stock_data(portfolio_name, start_date, end_date)

        elif choice == '2':
            break



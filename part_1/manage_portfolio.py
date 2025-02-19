import yfinance as yf
from part_1.create_portfolio import fetch_and_store_stock_data
import datetime
import mysql.connector


def show_stock_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="easy",
        database="stock_data"
    )
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM StockData')
    rows = cursor.fetchall()
    for row in rows:
        print(row)


def stock_is_valid(symbol):
    stock = yf.Ticker(symbol)
    return not stock.history(period='1d').empty


def create_tables():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="easy",
        database="stock_data"
    )
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Portfolio (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    symbol VARCHAR(255) NOT NULL,
                    UNIQUE KEY (name, symbol)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS StockData (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume INT,
                    UNIQUE KEY (symbol, date)
                    )''')

    conn.commit()
    conn.close()


def add_stock_to_portfolio(name, symbol):
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    if stock_is_valid(symbol):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="easy",
            database="stock_data"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO Portfolio (name, symbol) VALUES (%s, %s)", (name, symbol))
        conn.commit()
        conn.close()
        print("Stock added successfully.")
    else:
        print("Invalid stock name.")


def remove_stock_from_portfolio(name, symbol):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="easy",
        database="stock_data"
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Portfolio WHERE name = %s AND symbol = %s", (name, symbol))
    conn.commit()
    conn.close()
    print("Stock removed successfully.")


def show_all_portfolios():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="easy",
        database="stock_data"
    )
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT name FROM Portfolio')
    names = [row[0] for row in cursor.fetchall()]

    print("Portfolios:")
    for name in names:
        cursor.execute('SELECT name, symbol, date FROM Portfolio WHERE name = %s', (name,))
        symbols = [f"{row[2]}: {row[1]}\n" for row in cursor.fetchall()]
        print(f"{name}\n{''.join(symbols)}")

    conn.close()



if __name__ == '__main__':
    create_tables()
    # Write an additional script that lets the user manage their portfolio having operations such
    # as adding a stock to the portfolio, removing a stock from the portfolio, displaying all their
    # portfolios with the creation date and list of stocks in the portfolio.
    # Perform a validation check whether or not the given stock is valid and available in the
    # yfinance API before actually adding it to the portfolio and display appropriate messages to
    # the user such as: “added successfully" or “invalid stock name”, etc.

    stay = True
    while stay:
        print("\nStock Portfolio Manager:")
        print("1. Add stock to existing portfolio")
        print("2. Remove stock from portfolio")
        print("3. Fetch stock data")
        print("4. Show all portfolios")
        print("5. Exit")
        print("6. Show stock data")

        choice = input("Enter your choice: ")

        if choice == '1':
            portfolio_name = input("Enter the portfolio name: ")
            stock_symbol = input("Enter the stock symbol to add to portfolio: ").upper()
            add_stock_to_portfolio(portfolio_name, stock_symbol)

        elif choice == '2':
            portfolio_name = input("Enter the portfolio name: ")
            stock_symbol = input("Enter the stock symbol to remove: ").upper()
            remove_stock_from_portfolio(portfolio_name, stock_symbol)

        elif choice == '3':
            portfolio_name = input("Enter the name of the portfolio you'd like to fetch data for: ")
            start_date = input("Enter the start date for data fetching (YYYY-MM-DD): ")
            end_date = input("Enter the end date for data fetching (YYYY-MM-DD): ")
            fetch_and_store_stock_data(portfolio_name, start_date, end_date)
            print("Stock data fetched and stored in the database.")

        elif choice == '4':
            show_all_portfolios()

        elif choice == '5':
            stay = False

        elif choice == '6':
            show_stock_data()

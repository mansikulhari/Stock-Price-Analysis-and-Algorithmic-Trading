# Data Preprocessing
# ~ calculating the daily returns [(Today's Close Price - Yesterday's Close Price) / Yesterday's Close Price ]
# ~ calculating moving averages and adding them as columns (like 50-day moving average, 250-day moving average)
# ~ calculating the volatility measures (like the standard deviation) and adding them as columns
# ~ additional technical indicators like RSI and Bollinger Bands and adding them as columns
import mysql.connector
import pandas as pd
from scipy import stats


def preprocess_stock_data():
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",  # MySQL username here
        password="easy",  # MySQL password here
        database="stock_data"
    )
    cursor = conn.cursor()

    # Loading the data from the StockData table
    cursor.execute('SELECT * FROM StockData')
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    # DataFrame for data processing
    df = pd.DataFrame(data, columns=columns)

    # 1. DATA CLEANING
    # handling the missing data using strategies like forward/backward filling or interpolation

    # A) Checking for Missing Data:
    missing_values = df.isnull().sum()

    for column_name in df.columns:
        if missing_values[column_name] > 0:
            # i) removing the rows with missing values
            df.dropna(inplace=True)

        # ii) filling the missing values with a specific value, if possible (using mean, median or a custom value)
        for column in ['open', 'high', 'low', 'close', 'volume']:
            for stock in df['symbol'].unique():
                df[column][df['symbol'] == stock].fillna(df[column][df['symbol'] == stock].mean(), inplace=True)
                df[column].fillna(df[column].mean(), inplace=True)

    # B) Handling Outliers:
    for column in ['open', 'high', 'low', 'close', 'volume']:
        z_scores = stats.zscore(df[column])
    df = df[(z_scores < 3)]  # keeping only the data within 3 standard deviations

    # C) Data Type Conversion:
    df['date'] = pd.to_datetime(df['date'])

    # D) Duplicates:
    df.drop_duplicates(inplace=True)  # checking for and removing the suplicate rows

    # E) Data Consistency:
    df['symbol'] = df['symbol'].str.strip()  # removing the trailing/leading spaces

    # 2. CALCULATING METRICS
    # Daily Return
    df['Daily_Return'] = (df.groupby('symbol')['close'].pct_change()) * 100

    # Moving Average
    df['MA_50_Day'] = df.groupby('symbol')['close'].rolling(window=50).mean().reset_index(level=0, drop=True)
    df['MA_250_Day'] = df.groupby('symbol')['close'].rolling(window=250).mean().reset_index(level=0, drop=True)

    # Standard Deviation
    df['20_day_std'] = df.groupby('symbol')['close'].rolling(window=20).std().reset_index(level=0,
                                                                                          drop=True)  # 20-day rolling SD for each stock

    # calculating RSI for each stock, using a 14 day period
    period = 14
    delta = df.groupby('symbol')['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df['RSI'] = rsi

    # Bollinger Bands
    # BB consists of 3 lines: the middle band (SMA), the upper band (SMA + 2 * Standard Deviation) and the lower band (SMA - 2*Standard Deviation)

    # Will need to check this once for any stock-specific logical errors
    sma = df.groupby('symbol')['close'].rolling(window=20).mean()
    std = df.groupby('symbol')['close'].rolling(window=20).std()

    df['Bollinger_Middle'] = sma.values
    df['Bollinger_Upper'] = (sma + (std * 2)).values
    df['Bollinger_Lower'] = (sma - (std * 2)).values

    # 3. DATA TRANSFORMATION
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.set_index('date')

    # Replace 'nan' with None for proper SQL NULL insertion
    df.replace({pd.NaT: None, pd.NA: None}, inplace=True)

    # More sophisticated replacement depending on your logic
    # For numerical columns replace NaN with None
    for col in df.columns:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) or x == "nan" else x)
    try:
        # Defining the SQL statement to create the table
        # Drop the existing table if it exists
        # Drop the existing table if it exists
        drop_sql_table = """
        DROP TABLE IF EXISTS PreprocessedData;
        """
        cursor.execute(drop_sql_table)

        # Defining the SQL statement to create the new table
        create_sql_table = """
        CREATE TABLE PreprocessedData (
                date DATE,
                symbol VARCHAR(10),
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume FLOAT,
                Daily_Return FLOAT,
                MA_50_Day FLOAT,
                MA_250_Day FLOAT,
                20_day_std FLOAT,
                RSI FLOAT,
                Bollinger_Middle FLOAT,
                Bollinger_Upper FLOAT,
                Bollinger_Lower FLOAT,
                PRIMARY KEY(date, symbol)
        )
        """
        cursor.execute(create_sql_table)

        # Iterating through the rows in the DataFrame
        # Iterating through the rows in the DataFrame
        df.dropna(inplace=True)
        print(df.isna().sum())
        for _, row in df.iterrows():
            insert_sql = """
                    INSERT INTO PreprocessedData (date, symbol, open, high, low, close, volume, 
                                                  Daily_Return, MA_50_Day, MA_250_Day, 20_day_std, 
                                                  RSI, Bollinger_Middle, Bollinger_Upper, Bollinger_Lower)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
            values = (
                row.name.date() if row.name else None,  # Check for None
                row['symbol'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row['Daily_Return'],
                row['MA_50_Day'],
                row['MA_250_Day'],
                row['20_day_std'],
                row['RSI'],
                row['Bollinger_Middle'],
                row['Bollinger_Upper'],
                row['Bollinger_Lower']
            )
            cursor.execute(insert_sql, values)
        conn.commit()
        print("Data inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    preprocess_stock_data()

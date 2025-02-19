# Stock Price Analysis and Algorithmic Trading

A comprehensive system for stock data collection, analysis, and algorithmic trading implementation using Python and MySQL.

## Prerequisites

- Docker (Download [here](https://www.docker.com/products/docker-desktop/))
- docker-compose
- Python
- MySQL (local installation)
- Project should have permissions to access MySQL root (password is set to "easy")

### Note for Non-ARM Users
If you are not using an ARM chip, modify docker-compose.yaml:
- Line 4: Change to `image: mysql:latest`
- Line 14: Change to `image: phpmyadmin/phpmyadmin`

## Setup

1. Navigate to project directory and run:
```bash
docker-compose up -d
```

2. Install required packages:
```bash
pip3 install -r requirements.txt
```

3. Access the Database UI at:
```
http://localhost:8080/phpmyadmin
```

## Project Structure

```
├── part1/
│   ├── data_collection/
│   │   ├── stock_fetcher.py
│   │   └── portfolio_manager.py
│   ├── database/
│   │   ├── db_setup.py
│   │   └── db_operations.py
│   └── preprocessing/
│       └── data_cleaner.py
├── part2/
│   ├── algorithms/
│   │   ├── moving_average.py
│   │   ├── rsi_strategy.py
│   │   └── lstm_predictor.py
│   ├── trading/
│   │   ├── mock_environment.py
│   │   └── performance_metrics.py
│   └── visualization/
│       └── results_plotter.py
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

## Features

### Part 1: Data Collection & Storage
- Real-time stock data fetching using yfinance API
- Portfolio creation and management
- Stock validation
- Data preprocessing and cleaning
- MySQL database integration

### Part 2: Analysis & Trading
- Implementation of trading algorithms:
  - Simple Moving Average (SMA)
  - Exponential Moving Average (EMA)
  - Relative Strength Index (RSI)
  - Advanced algorithms (ARIMA, LSTM)
- Mock trading environment
- Performance metrics calculation:
  - Portfolio returns
  - Sharpe ratio
  - MAE & RMSE

## Usage

1. Create a new portfolio:
```bash
python portfolio_manager.py create --name "my_portfolio"
```

2. Add stocks to portfolio:
```bash
python portfolio_manager.py add --portfolio "my_portfolio" --symbol "AAPL,GOOGL,MSFT"
```

3. Run trading simulation:
```bash
python mock_environment.py --portfolio "my_portfolio" --initial-fund 100000 --algorithm "sma"
```

## Performance Metrics

The system calculates several key metrics:
- Total portfolio value
- Annualized returns
- Sharpe ratio
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)

## Database Schema

### Portfolio Table
```sql
CREATE TABLE portfolios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    creation_date DATETIME,
    initial_value DECIMAL(15,2)
);
```

### Stocks Table
```sql
CREATE TABLE stocks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(10),
    portfolio_id INT,
    purchase_date DATETIME,
    quantity INT,
    price DECIMAL(15,2),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);
```

## Contributing
This project is part of DSCI-560 coursework at USC.

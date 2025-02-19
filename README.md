# Stock Price Analysis and Algorithmic Trading

A comprehensive system for stock data collection, analysis, and algorithmic trading implementation using Python, MySQL, and various prediction models.

## Project Structure
```
├── models/
│   ├── moving_averages.py    # Implementation of SMA and EMA strategies
│   ├── prophet_model.py      # Facebook Prophet model implementation
│   ├── rsi.py               # Relative Strength Index calculations
│   └── time_series_transformer.py  # Time series data transformations
├── part_1/
│   └── sql-scripts/
│       ├── init.sql         # Database initialization
│       ├── create_portfolio.py
│       ├── docker-compose.yaml
│       ├── manage_portfolio.py
│       └── preprocess.py
├── main.py                  # Main application entry point
├── portfolio.py             # Portfolio management functionality
├── requirements.txt         # Python dependencies
├── trader.py               # Trading logic implementation
└── train.py                # Model training scripts
```

## Prerequisites

### Docker Installation
1. Download Docker Desktop:
   - [Docker for Windows](https://docs.docker.com/desktop/windows/install/)
   - [Docker for Mac](https://docs.docker.com/desktop/mac/install/)
   - [Docker for Linux](https://docs.docker.com/engine/install/)

2. Install docker-compose (included in Docker Desktop for Windows/Mac)

3. Verify installation:
```bash
docker --version
docker-compose --version
```

### Python Requirements
Install required Python packages:
```bash
pip install -r requirements.txt
```

## Setup

1. Database Setup
```bash
# Start Docker containers
docker-compose up -d

# Verify containers are running
docker ps
```

2. Configure MySQL:
- Default root password is set to "easy"
- Access phpMyAdmin at: http://localhost:8080/phpmyadmin

### Note for Non-ARM Users
If you're not using an ARM chip, modify docker-compose.yaml:
```yaml
# Change from:
image: mysql:latest
# To:
image: phpmyadmin/phpmyadmin
```

## Usage

### 1. Portfolio Management
```bash
# Create a new portfolio
python manage_portfolio.py create --name "my_portfolio"

# Add stocks to portfolio
python manage_portfolio.py add --portfolio "my_portfolio" --symbols "AAPL,GOOGL,MSFT"
```

### 2. Data Collection
```bash
# Fetch historical data
python main.py fetch --portfolio "my_portfolio" --days 365
```

### 3. Model Training
```bash
# Train prediction models
python train.py --model "prophet" --stock "AAPL"
```

### 4. Trading
```bash
# Run trading simulation
python trader.py --portfolio "my_portfolio" --model "moving_average"
```

## Trading Models

### 1. Moving Averages
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Customizable time periods

### 2. RSI (Relative Strength Index)
- Momentum indicator
- Overbought/Oversold signals
- Customizable period settings

### 3. Prophet Model
- Facebook's time series prediction model
- Handles seasonality
- Future trend forecasting

### 4. Time Series Transformer
- Data preprocessing
- Feature engineering
- Time series specific transformations

## Database Schema

The project uses MySQL with the following structure:

```sql
-- Portfolio Table
CREATE TABLE portfolios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stocks Table
CREATE TABLE stocks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(10) NOT NULL,
    portfolio_id INT,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- Trading History Table
CREATE TABLE trades (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT,
    type ENUM('BUY', 'SELL'),
    price DECIMAL(10,2),
    quantity INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
```

## Data Processing

1. Data Collection
   - Real-time stock data via yfinance
   - Historical data retrieval
   - Error handling for API limits

2. Preprocessing
   - Missing value handling
   - Outlier detection
   - Feature normalization
   - Time series alignment


## Acknowledgments
- Yahoo Finance API for stock data
- Facebook Prophet for time series prediction
- SQLAlchemy for database operations

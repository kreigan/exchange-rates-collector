# Exchange Rates Collector

A Python tool for collecting current exchange rates from [Fixer.io](https://fixer.io/) and saving them to CSV format.

## Overview

This project fetches current exchange rates for specified currencies against USD using the Fixer.io API and stores them in a CSV file with the current date.

## Data Provider

This tool uses [Fixer.io](https://fixer.io/) as the exchange rate data provider. Fixer.io provides real-time and historical foreign exchange rates powered by financial data sources.

- **API Documentation**: [https://fixer.io/documentation](https://fixer.io/documentation)
- **Supported Currencies**: [https://fixer.io/symbols](https://fixer.io/symbols)

## Requirements

- Python 3.8+
- pandas
- requests
- Fixer.io API key (free or paid plan)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd exchange-rates-collector
```

2. Install dependencies:

```bash
pip install pandas requests
```

or using the requirements file:

```bash
pip install -r requirements.txt
```

3. Set up your Fixer.io API key as an environment variable:

```bash
export FIXER_API_KEY="your_api_key_here"
```

## Configuration

Create a `currencies.txt` file in the project root with one currency code per line:

```text
EUR
GBP
JPY
CHF
CAD
```

## Usage

Run the script to fetch current exchange rates:

```bash
python src/fxratecollector/collect-fixer.py
```

The script will:

1. Read the currency codes from `currencies.txt`
2. Fetch current exchange rates from Fixer.io
3. Convert rates to USD base
4. Save the data to `exchange_rates_YYYY-MM-DD.csv`

## Output Format

The generated CSV file contains three columns:

- `date`: The date of the exchange rate (YYYY-MM-DD format)
- `currency`: The currency code (e.g., EUR, GBP)
- `usd_rate`: The exchange rate relative to USD

Example:

```csv
date,currency,usd_rate
2025-11-11,EUR,1.0823
2025-11-11,GBP,1.2654
2025-11-11,JPY,0.0066
```

## API Limitations

Be aware of the Fixer.io API limitations based on your plan:

- **Free Plan**: 100 requests/month, current rates only
- **Paid Plans**: Higher request limits and historical data access

One script call consumes one API request.

For Free Plan, the base currency is always EUR. The script converts rates to USD base internally. For that, the currency list must include USD to perform the conversion correctly.

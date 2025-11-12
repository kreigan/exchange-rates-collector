# Exchange Rates Collector

A Python tool for collecting exchange rates from [Fixer.io](https://fixer.io/) and
saving them to CSV format.

## Overview

This project fetches exchange rates for specified currencies against USD using the
Fixer.io API and stores them in a CSV file with the current date.

## Data Provider

This tool uses [Fixer.io](https://fixer.io/) as the exchange rate data provider.
Fixer.io provides real-time and historical foreign exchange rates powered by financial
data sources.

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

## Currency List

The script supports three ways to specify the list of currencies:

1. Using the `--currencies` command-line argument with a comma-separated list of
currency codes.
2. Using the `--currencies-file` command-line argument to specify a file containing
currency codes, one per line.
3. By default, it reads from a `currencies.txt` file in the current working directory.

## Usage

Run the script to fetch current exchange rates:

```bash
python src/fxratecollector/collect-rates.py
```

By default, the script will:

1. Read the currency codes from `currencies.txt`
2. Fetch current exchange rates from Fixer.io
3. Convert rates to USD base
4. Save the data to `exchange_rates_YYYY-MM-DD.csv`

The following flags can be used to customize the behavior:

- `--date`: if provided in `YYYY-MM-DD` format, instructs the script to fetch
historical rates for that date.
- `--output`: specifies the output CSV file path. If not provided, a default filename
with the date will be used.
- `--currencies`: specifies a comma-separated list of currency codes to fetch rates for.
Cannot be used together with `--currencies-file`.
- `--currencies-file`: specifies a file path containing currency codes, one per line.
Cannot be used together with `--currencies`.

## Usage Hints

To get multiple days of historical data, use Bash `for` loop with the `--date` flag.
For example, to get monthly rates for 2024:

```bash
for m in `seq -w 1 12`; do python src/fxratecollector/collect-rates.py --date 2024-$m-01; done
```

This will produce 12 files like `exchange_rates_2024-01-01.csv`. You can combine them in
one big file just like this:

```bash
awk 'FNR==1 && NR!=1{next;}{print}' exchange_rates_2024-??-01.csv >| ~/tmp/exchange_rates_2024.csv
```

Fixer.io has a rate limit of 5 calls in a second. The script detects this and
automatically waits if the limit is reached.

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

- **Free Plan**: 100 requests/month
- **Paid Plans**: Higher request limits

One script call consumes one API request.

For Free Plan, the base currency is always EUR. The current implementation of the
script converts rates to USD base internally.

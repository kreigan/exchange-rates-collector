import argparse
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any

import pandas as pd
import requests


class FixerException(Exception):
    def __init__(self, error_code: int, message: str):
        """Initializes a FixerException with an error code and message.

        Args:
            error_code: The error code from the Fixer.io API.
            message: A descriptive error message.
        """
        self.error_code = error_code
        self.message = message
        super().__init__(f"API error {error_code}: {message}")


class FixerClient:
    BASE_URL: str = "https://data.fixer.io/api/"
    def __init__(self, api_key: str, retries: int = 1):
        self._api_key: str = api_key
        self.retries: int = retries
        
        if not self._api_key:
            raise ValueError(
                "Fixer.io API key not found. Pass it as argument or set FIXER_API_KEY environment variable."
            )

    def _get(self, endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        url: str = f"{self.BASE_URL}{endpoint}?access_key={self._api_key}"
        
        resp: requests.Response = requests.get(url, params=params)
        data: dict[str, Any] = resp.json()
        
        if not data.get("success", False):
            error_code = int(data.get("error", {}).get("code", 0))
            error_info = data.get("error", {}).get("info", "Unknown error")
            raise FixerException(error_code, error_info)
        
        return data
        
    def _send(self, endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        retries = self.retries
        while True:
            try:
                return self._get(endpoint, params)
            except FixerException as exc:
                if exc.error_code == 106 and retries > 0:
                    print(f"Rate limit reached. Attempts left: {retries}")
                    retries -= 1
                    sleep(1)
                else:
                    raise exc
       
        
    def get_rates(self, currencies: list[str], at_date: str | None = None) -> dict[str, float]:
        """Gets current or historical exchange rates for specified currencies
        against USD. If at_date is None, pulls current rates.

        Args:
            currencies: List of currency codes to get rates for.
            at_date: The date for which to fetch rates, in 'YYYY-MM-DD' format. If None, pulls current rates.

        Returns:
            A dictionary mapping currency codes to their USD exchange rate.

        Raises:
            FixerException: If the API call is not successful or returns an error.
            ValueError: If the currencies list is empty or the date format is invalid.
        """
        if not currencies:
            raise ValueError("Currencies list cannot be empty.")

        if at_date is not None:
            try:
                datetime.strptime(at_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: {at_date}. Expected format: YYYY-MM-DD")         
        
        currencies_to_get = set(currencies)
        # Ensure USD is included for conversion purposes if using Free Plan
        currencies_to_get.add("USD")

        data: dict[str, Any] = self._send(
            'latest' if at_date is None else at_date,
            {"symbols": ",".join(currencies_to_get)}
        )

        # Free plan is EUR-based, convert to USD
        rates_eur_base: dict[str, float] = data["rates"]
        eur_to_usd_rate: float = rates_eur_base.get("USD", 0)

        if eur_to_usd_rate == 0:
            raise RuntimeError("USD rate not found in API response, cannot convert to USD base.")

        rates_usd_base: dict[str, float] = {}
        for currency, rate_eur in rates_eur_base.items():
            if currency == "USD":
                rates_usd_base[currency] = 1.0
            else:
                rates_usd_base[currency] = rate_eur / eur_to_usd_rate

        if "USD" not in currencies:
            # Remove USD if it was not originally requested
            rates_usd_base.pop("USD", None)

        return rates_usd_base


if __name__ == "__main__":
    def parse_arguments() -> argparse.Namespace:
        """Parses command-line arguments.

        Returns:
            Parsed arguments namespace.
        """
        parser = argparse.ArgumentParser(
            description="Collect exchange rates from Fixer.io API"
        )

        parser.add_argument(
            "--date",
            type=str,
            help="Date for historical rates in YYYY-MM-DD format. If not provided, fetches current rates.",
        )

        parser.add_argument(
            "--output",
            type=str,
            help="Path to the output CSV file. If not provided, a default name will be used."
        )

        currency_group = parser.add_mutually_exclusive_group()
        currency_group.add_argument(
            "--currencies",
            type=str,
            help="Comma-separated list of currency codes to fetch rates for."
        )
        currency_group.add_argument(
            "--currencies-file",
            type=str,
            help="Path to the currencies file. Default is currencies.txt in the current working folder."
        )
        return parser.parse_args()

    args = parse_arguments()
    
    API_KEY: str = os.getenv("FIXER_API_KEY", "")
    if not API_KEY:
        raise ValueError("FIXER_API_KEY environment variable must be set")

    currencies: list[str] = []
    if args.currencies:
        currencies = [c.strip() for c in args.currencies.split(",")]
    else:
        file_path = Path(args.currencies_file if args.currencies_file else "currencies.txt").expanduser()
        with open(file_path, "r") as f:
            currencies = [line.strip() for line in f if line.strip()]
    
    if len(currencies) == 0:
        print("Currency list is empty. Please add currency codes to currencies.txt.")
        exit(1)
    elif len(currencies) == 1 and currencies[0] == "USD":
        print("Currency list contains only USD. No rates to fetch.")
        exit(1)

    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {args.date}. Expected format: YYYY-MM-DD")
    
    print(f"Fetching {'historical' if args.date else 'current'} rates for {currencies}")

    fixer = FixerClient(API_KEY)
    rates: dict[str, float] = fixer.get_rates(currencies, args.date)
    
    print(f"Successfully got {len(rates)} rates")

    # Use today's date for current rates
    date_str: str = args.date or datetime.now().strftime('%Y-%m-%d')
    
    records: list[dict[str, Any]] = [
        dict(date=date_str, currency=currency, usd_rate=rate)
        for currency, rate in rates.items()
    ]

    df: pd.DataFrame = pd.DataFrame(records)
    if args.output:
        output_filename = Path(args.output).expanduser()
    else:
        output_filename = f"exchange_rates_{date_str}.csv"
    df.to_csv(output_filename, index=False)
    
    print(f"Data saved to {output_filename}")

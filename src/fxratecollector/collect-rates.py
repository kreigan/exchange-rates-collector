import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests

API_KEY: str = os.getenv("FIXER_API_KEY", "")
if not API_KEY:
    raise ValueError("FIXER_API_KEY environment variable must be set")

BASE_URL: str = "https://data.fixer.io/api/"


def load_currencies(file_path: str = "currencies.txt") -> list[str]:
    """Loads a list of currency codes from a text file.

    Each currency code is expected to be on a new line.

    Args:
        file_path: The path to the file containing currency codes.

    Returns:
        A list of currency codes.

    Raises:
        FileNotFoundError: If the currency file does not exist.
    """
    try:
        with open(file_path, "r") as f:
            currencies: list[str] = [line.strip() for line in f if line.strip()]
        if not currencies:
            raise ValueError("No currencies found in the file or file is empty.")
        return currencies
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise


CURRENCIES: list[str] = load_currencies()
CURRENT_DATE: datetime = datetime.now()


def get_current_rates() -> dict[str, float]:
    """Fetches the current exchange rates for specified currencies against USD.

    Returns:
        A dictionary mapping currency codes to their USD exchange rate.

    Raises:
        Exception: If the API call is not successful or returns an error.
    """
    url: str = f"{BASE_URL}latest?access_key={API_KEY}"
    query: dict[str, str] = {"symbols": ",".join(CURRENCIES)}

    resp: requests.Response = requests.get(url, params=query)
    data: dict[str, Any] = resp.json()
    if not data.get("success"):
        raise Exception(f"API error: {data}")

    # Free plan is EUR-based, convert to USD
    rates_eur_base: dict[str, float] = data["rates"]
    eur_to_usd_rate: float = rates_eur_base.get("USD", 0)

    if eur_to_usd_rate == 0:
        raise Exception(
            "USD rate not found in API response, cannot convert to USD base."
        )

    rates_usd_base: dict[str, float] = {}
    for currency, rate_eur in rates_eur_base.items():
        if currency == "USD":
            rates_usd_base[currency] = 1.0
        else:
            rates_usd_base[currency] = rate_eur / eur_to_usd_rate

    return rates_usd_base


rates: dict[str, float] = get_current_rates()
current_date_str: str = CURRENT_DATE.strftime("%Y-%m-%d")

# Format data for pandas
records: list[dict[str, Any]] = []
for currency, rate in rates.items():
    records.append({"date": current_date_str, "currency": currency, "usd_rate": rate})

df: pd.DataFrame = pd.DataFrame(records)
output_filename: str = f"exchange_rates_{current_date_str}.csv"
df.to_csv(output_filename, index=False)
print(f"Data saved to {output_filename}")

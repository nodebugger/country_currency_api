import httpx
from datetime import datetime
from sqlmodel import select
from .config import COUNTRIES_API_URL, EXCHANGE_API_URL, REQUEST_TIMEOUT, RANDOM_MIN, RANDOM_MAX
from .utils import pick_currency_code, compute_estimated_gdp
from .imagegen import generate_summary_image
from .models import Country
import random

def fetch_countries():
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        resp = client.get(COUNTRIES_API_URL)
        resp.raise_for_status()
        return resp.json()

def fetch_exchange_rates():
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        resp = client.get(EXCHANGE_API_URL)
        resp.raise_for_status()
        data = resp.json()
        # open.er-api returns 'rates' mapping currency->rate relative to USD
        return data.get("rates", {})

def build_country_records(countries_json, rates_map):
    records = []
    now_iso = datetime.utcnow().isoformat() + "Z"
    for c in countries_json:
        name = c.get("name")
        capital = c.get("capital")
        region = c.get("region")
        population = c.get("population") or 0
        flag_url = c.get("flag") or c.get("flags")  # safety
        currencies = c.get("currencies") or []
        currency_code = pick_currency_code(currencies)
        exchange_rate = None
        estimated_gdp = None

        if currency_code:
            # rates_map keys are currency codes; rates are value of 1 USD in that currency? open.er-api 'rates' maps currency->value where 1 USD = rates['EUR']? Typically rates currency per USD.
            # The spec expects exchange_rate like NGN -> 1600 (meaning 1 USD = 1600 NGN). That's 'rates' from open.er-api.
            exchange_rate = rates_map.get(currency_code)
            if exchange_rate is not None:
                multiplier = random.randint(RANDOM_MIN, RANDOM_MAX)
                try:
                    estimated_gdp = compute_estimated_gdp(population, multiplier, exchange_rate)
                except Exception:
                    estimated_gdp = None

        else:
            # no currency -> per spec: currency_code null, exchange_rate null, estimated_gdp 0
            exchange_rate = None
            estimated_gdp = 0

        records.append({
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": float(exchange_rate) if exchange_rate is not None else None,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag_url,
            "last_refreshed_at": now_iso
        })
    return records

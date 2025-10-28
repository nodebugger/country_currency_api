import random
from hashlib import sha256

def pick_currency_code(currencies):
    # currencies: array of objects { code, name, ... }
    if not currencies or len(currencies) == 0:
        return None
    first = currencies[0]
    return first.get("code") or None

def compute_estimated_gdp(population: int, multiplier: int, exchange_rate: float):
    if not exchange_rate:
        return None
    
    # Ensure float math
    return (population * multiplier) / float(exchange_rate)

def sha256_id(s: str) -> str:
    return sha256(s.encode("utf-8")).hexdigest()
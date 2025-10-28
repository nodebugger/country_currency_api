import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COUNTRIES_API_URL = os.getenv(
    "COUNTRIES_API_URL",
    "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
)
EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL", "https://open.er-api.com/v6/latest/USD")
RANDOM_MIN = int(os.getenv("RANDOM_MIN", "1000"))
RANDOM_MAX = int(os.getenv("RANDOM_MAX", "2000"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))  # seconds

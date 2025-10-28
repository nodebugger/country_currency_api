from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict

class CountryCreate(BaseModel):
    name: str
    population: int
    currency_code: Optional[str] = None
    capital: Optional[str] = None
    region: Optional[str] = None
    flag_url: Optional[str] = None

class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    capital: Optional[str]
    region: Optional[str]
    population: int
    currency_code: Optional[str]
    exchange_rate: Optional[float]
    estimated_gdp: Optional[float]
    flag_url: Optional[str]
    last_refreshed_at: str

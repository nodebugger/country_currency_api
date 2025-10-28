from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import datetime

class Country(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int = Field(nullable=False)
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

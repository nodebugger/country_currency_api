from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select, func
from .database import get_session, init_db, engine
from .models import Country
from .schemas import CountryOut
from .services import fetch_countries, fetch_exchange_rates, build_country_records
from .imagegen import generate_summary_image, IMAGE_PATH
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import os
import traceback

router = APIRouter()

@router.post("/countries/refresh")
def refresh_countries(session: Session = Depends(get_session)):
    # 1. Fetch external APIs first (fail early)
    try:
        countries_json = fetch_countries()
    except Exception as e:
        print(f"Error fetching countries: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=503, detail={"error":"External data source unavailable", "details": f"Could not fetch countries API: {str(e)}"})

    try:
        rates_map = fetch_exchange_rates()
    except Exception as e:
        print(f"Error fetching exchange rates: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=503, detail={"error":"External data source unavailable", "details": f"Could not fetch exchange rates API: {str(e)}"})

    # 2. Build records in memory
    try:
        records = build_country_records(countries_json, rates_map)
        print(f"Built {len(records)} country records")
    except Exception as e:
        print(f"Error building country records: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={"error":"Internal server error", "details": f"Error processing data: {str(e)}"})

    # 3. Perform DB upserts in a transaction
    try:
        for r in records:
            # match by name case-insensitive
            stmt = select(Country).where(Country.name.ilike(r["name"]))
            existing = session.exec(stmt).first()
            if existing:
                existing.capital = r["capital"]
                existing.region = r["region"]
                existing.population = r["population"]
                existing.currency_code = r["currency_code"]
                existing.exchange_rate = r["exchange_rate"]
                existing.estimated_gdp = r["estimated_gdp"]
                existing.flag_url = r["flag_url"]
                existing.last_refreshed_at = r["last_refreshed_at"]
                session.add(existing)
            else:
                obj = Country(**r)
                session.add(obj)
        session.commit()
        
        # After commit, generate image
        # get total and top5 by estimated_gdp
        total = session.exec(select(func.count()).select_from(Country)).one()
            
        top5 = session.exec(select(Country).where(Country.estimated_gdp.isnot(None)).order_by(Country.estimated_gdp.desc()).limit(5)).all()
        # convert to minimal dicts
        top5_list = [{"name": c.name, "estimated_gdp": c.estimated_gdp} for c in top5]
        
        timestamp = records[0]["last_refreshed_at"] if records else ""
        img_path = generate_summary_image(total, top5_list, timestamp)
        
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={"error":"Internal server error", "details": f"Database error: {str(e)}"})
    except Exception as e:
        session.rollback()
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={"error":"Internal server error", "details": f"Unexpected error: {str(e)}"})

    return {"message": "Refreshed", "total_countries": total, "image": img_path}

@router.get("/countries")
def list_countries(
    region: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),  # e.g. gdp_desc
    session: Session = Depends(get_session)
):
    stmt = select(Country)
    if region:
        stmt = stmt.where(Country.region == region)
    if currency:
        stmt = stmt.where(Country.currency_code == currency)
    if sort == "gdp_desc":
        stmt = stmt.order_by(Country.estimated_gdp.desc())
    results = session.exec(stmt).all()
    return [CountryOut.model_validate(r).model_dump() for r in results]

@router.get("/status")
def status(session: Session = Depends(get_session)):
    total = session.exec(select(func.count()).select_from(Country)).one()
    last = session.exec(select(Country).order_by(Country.last_refreshed_at.desc()).limit(1)).first()
    last_ts = last.last_refreshed_at if last else None
    return {"total_countries": total, "last_refreshed_at": last_ts}

@router.get("/countries/image")
def serve_image():
    if os.path.exists(IMAGE_PATH):
        from fastapi.responses import FileResponse
        return FileResponse(IMAGE_PATH, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail={"error":"Summary image not found"})

@router.get("/countries/{name}")
def get_country(name: str, session: Session = Depends(get_session)):
    stmt = select(Country).where(Country.name.ilike(name))
    c = session.exec(stmt).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error":"Country not found"})
    return CountryOut.model_validate(c).model_dump()

@router.delete("/countries/{name}", status_code=204)
def delete_country(name: str, session: Session = Depends(get_session)):
    stmt = select(Country).where(Country.name.ilike(name))
    c = session.exec(stmt).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error":"Country not found"})
    session.delete(c)
    session.commit()
    return Response(status_code=204)

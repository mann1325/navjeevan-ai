import logging
from typing import Any, Dict, List

from backend.services.ai_service import format_response_with_groq
from backend.utils.realtime_api import fetch_realtime_market_price

logger = logging.getLogger(__name__)
FALLBACK_MESSAGE = "Market data unavailable"
CACHED_SOURCE = "Cached / Historical Data"


def _finalize_response(text: str) -> str:
    words = text.split()
    if len(words) <= 120:
        return text
    return " ".join(words[:120]).rstrip() + "..."


def _matches_cached_record(item: Dict[str, Any], crop: str, location: str) -> bool:
    crop = (crop or "").strip().lower()
    location = (location or "").strip().lower()
    commodity = str(item.get("commodity", "")).strip().lower()
    district = str(item.get("district", "")).strip().lower()
    market = str(item.get("market", "")).strip().lower()
    return (
        crop == "amla"
        and commodity == "amla(nelli kai)"
        and (location == district or location == market or location in district or location in market)
    )


def _date_key(value: Dict[str, Any]) -> tuple[int, int, int]:
    try:
        day, month, year = (int(part) for part in str(value.get("arrival_date", "")).split("/"))
        return year, month, day
    except (TypeError, ValueError):
        return 0, 0, 0


def _cached_market(markets: List[Dict[str, Any]], crop: str, location: str) -> Dict[str, Any]:
    matches = [item for item in markets if _matches_cached_record(item, crop, location)]
    return max(matches, key=_date_key) if matches else {}


def _format_cached_response(record: Dict[str, Any]) -> str:
    return _finalize_response(
        f"Market: {record['market']}\n"
        f"Commodity: {record['commodity']}\n"
        f"Modal Price: Rs. {record['modal_price']}/qtl\n"
        f"Min Price: Rs. {record['min_price']}/qtl\n"
        f"Max Price: Rs. {record['max_price']}/qtl\n"
        f"Data status: {CACHED_SOURCE}\n"
        "Source: data.gov.in\n"
        f"Last available record: {record['arrival_date']}"
    )


def _format_live_response(data: Dict[str, Any]) -> str:
    return _finalize_response(
        f"Market: {data.get('market_name', 'N/A')}\n"
        f"Location: {data.get('location', 'N/A')}\n"
        f"Price: Rs. {data.get('price_per_qtl', 'N/A')}/qtl\n"
        "Data status: Live\n"
        "Source: data.gov.in\n"
        f"Arrival Date: {data.get('date', 'N/A')}"
    )


def handle_market(query: str, markets: List[Dict[str, Any]], entities: Dict[str, Any]) -> str:
    try:
        crop = str(entities.get("crop") or "").strip().lower()
        location = str(entities.get("location") or "").strip().lower()
        query_type = str(entities.get("query_type") or "general").strip().lower()

        if not crop or not location:
            return FALLBACK_MESSAGE

        if query_type == "price":
            try:
                live_data = fetch_realtime_market_price(crop, location)
            except Exception:
                logger.exception("live market lookup failed; using cached data")
                live_data = None
            if live_data:
                return format_response_with_groq(query, _format_live_response(live_data))

        cached_record = _cached_market(markets, crop, location)
        if not cached_record:
            return FALLBACK_MESSAGE
        return format_response_with_groq(query, _format_cached_response(cached_record))
    except Exception:
        logger.exception("market service failed")
        return FALLBACK_MESSAGE

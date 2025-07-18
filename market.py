from polygon import RESTClient
from dotenv import load_dotenv
import os 
from datetime import datetime
import random
from database import write_market, read_market
from functools import lru_cache

load_dotenv(override=True)

polygon_api_key = os.getenv("POLYGON_API_KEY")
polygon_plan = os.getenv("POLYGON_PLAN")

is_paid_polygon = polygon_plan == "paid"
is_realtime_polygon = polygon_plan == "realtime"

# def is_market_open() -> bool:
#     client = RESTClient(polygon_api_key)
#     market_status = client.get_market_status()
#     return market_status.market == "open"

# def is_market_open() -> bool:
#     if os.environ.get("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower() == "true":
#         return True
#     try:
#         client = RESTClient(polygon_api_key)
#         market_status = client.get_market_status()
#         return market_status.market == "open"
#     except Exception as e:
#         print(f"Polygon error: {e}. Defaulting to open.")
#         return True
def is_market_open() -> bool:
    val = os.environ.get("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower()
    print(f"[DEBUG] is_market_open() - RUN_EVEN_WHEN_MARKET_IS_CLOSED: {val}")
    if val == "true":
        print("[DEBUG] is_market_open() returns True due to env override.")
        return True
    try:
        client = RESTClient(polygon_api_key)
        market_status = client.get_market_status()
        return market_status.market == "open"
    except Exception as e:
        print(f"Polygon error: {e}. Defaulting to open.")
        return True


def get_all_share_prices_polygon_eod() -> dict[str, float]:
    client = RESTClient(polygon_api_key)

    probe = client.get_previous_close_agg("SPY")[0]
    last_close = datetime.fromtimestamp(probe.timestamp/1000).date()

    results = client.get_grouped_daily_aggs(last_close, adjusted=True, include_otc=False)
    return {result.ticker: result.close for result in results}

@lru_cache(maxsize=2)
def get_market_for_prior_date(today):
    market_data = read_market(today)
    if not market_data:
        market_data = get_all_share_prices_polygon_eod()
        write_market(today, market_data)
    return market_data
    
def get_share_price_polygon_eod(symbol) -> float:
    today = datetime.now().date().strftime("%Y-%m-%d")
    market_data = get_market_for_prior_date(today)
    return market_data.get(symbol, 0.0)

def get_share_price_polygon_min(symbol) -> float:
    client = RESTClient(polygon_api_key)
    result = client.get_snapshot_ticker("stocks", symbol)
    return result.min.close

def get_share_price_polygon(symbol) -> float:
    if is_paid_polygon:
        return get_share_price_polygon_min(symbol)
    else:
        return get_share_price_polygon_eod(symbol)
    
def get_share_price(symbol) -> float:
    if polygon_api_key:
        try:
            return get_share_price_polygon(symbol)
        except Exception as e:
            print(f"Was not able to use the polygon API due to {e}; using a random number")
    return float(random.randint(1, 100))
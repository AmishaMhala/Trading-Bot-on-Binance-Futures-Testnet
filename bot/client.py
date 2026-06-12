import time
import logging
from typing import Tuple, List, Dict, Optional
from binance.client import Client


logger = logging.getLogger(__name__)


def create_client(api_key: str, api_secret: str) -> Tuple[Optional[Client], List[str], Dict]:
    """Create and initialize a Binance Futures testnet client.

    Returns (client, symbols, account_info)
    """
    client = None
    symbols: List[str] = []
    account_info: Dict = {}

    try:
        client = Client(api_key, api_secret, testnet=True)
        client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

        # Synchronize time offset to fix timestamp errors
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        client.timestamp_offset = server_time["serverTime"] - local_time
        logger.info("Time synchronized with Binance server.")

        # Load trading symbols
        info = client.futures_exchange_info()
        symbols = [s["symbol"] for s in info["symbols"]]
        logger.info(f"Fetched {len(symbols)} symbols.")

        # Load USDT balance for display
        try:
            balances = client.futures_account_balance()
            usdt_item = next((b for b in balances if b["asset"] == "USDT"), None)
            account_info["USDT_balance"] = usdt_item["balance"] if usdt_item else "N/A"
        except Exception as e:
            account_info["USDT_balance"] = "N/A"
            logger.error(f"Error fetching USDT balance: {e}")

    except Exception as e:
        logger.error(f"API connection failed: {e}")

    return client, symbols, account_info

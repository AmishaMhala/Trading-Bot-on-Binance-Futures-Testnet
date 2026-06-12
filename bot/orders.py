import logging
from binance.exceptions import BinanceAPIException

logger = logging.getLogger(__name__)


def place_order(client, params: dict):
    """Place an order using the provided client and params.

    Raises BinanceAPIException or Exception on failure.
    Returns the order dict on success.
    """
    try:
        logger.info(f"Placing order with params: {params}")
        order = client.futures_create_order(**params)
        logger.info(f"Order response: {order}")
        return order
    except BinanceAPIException as e:
        logger.error(f"Order API error: {getattr(e, 'message', str(e))}")
        raise
    except Exception as e:
        logger.error(f"Order unexpected error: {e}")
        raise

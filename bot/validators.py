from typing import Tuple, List, Dict, Optional
from binance.enums import *


def prepare_order_params(symbol: str, order_type: str, side: str, quantity: float,
                         price: Optional[float] = None, stop_price: Optional[float] = None) -> Tuple[Dict, List[str]]:
    params = {
        "symbol": symbol,
        "side": SIDE_BUY if side == "BUY" else SIDE_SELL,
        "quantity": quantity,
        "type": None,
        "recvWindow": 5000,
    }

    errors: List[str] = []

    if order_type == "MARKET":
        params["type"] = ORDER_TYPE_MARKET
    elif order_type == "LIMIT":
        if not price or price <= 0:
            errors.append("Limit price must be greater than zero.")
        else:
            params.update(type=ORDER_TYPE_LIMIT, price=price, timeInForce=TIME_IN_FORCE_GTC)
    elif order_type == "STOP":
        if not price or price <= 0:
            errors.append("Limit price must be greater than zero.")
        if not stop_price or stop_price <= 0:
            errors.append("Stop price must be greater than zero.")
        if not errors:
            params.update(type=ORDER_TYPE_STOP, price=price, stopPrice=stop_price, timeInForce=TIME_IN_FORCE_GTC)
    else:
        errors.append("Unsupported order type.")

    return params, errors

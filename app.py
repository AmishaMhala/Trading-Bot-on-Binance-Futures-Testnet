import streamlit as st
import time
import datetime
import logging
from binance.exceptions import BinanceRequestException, BinanceAPIException

from bot.logging_config import configure_logging, get_logger
from bot.client import create_client
from bot.validators import prepare_order_params
from bot.orders import place_order

# configure logging
configure_logging()
logging = get_logger(__name__)

# --- Streamlit app configuration ---
st.set_page_config(page_title="Binance Testnet Trading Bot", layout="centered")
st.title("Enhanced Binance Futures Testnet Trading Bot")

# --- Sidebar: API credentials input ---
st.sidebar.header("API Credentials")
api_key = st.sidebar.text_input("API Key")
api_secret = st.sidebar.text_input("API Secret", type="password")

# client state
client = None
symbols = []
account_info = {}

# Initialize in-session order history
if 'order_history' not in st.session_state:
    st.session_state.order_history = []

# --- Connect to Binance Futures Testnet API and fetch symbols/account info ---
if api_key and api_secret:
    client, symbols, account_info = create_client(api_key, api_secret)
    if client and symbols:
        st.sidebar.success("API connected and symbols loaded!")
    else:
        st.sidebar.error("API Connection Error: check logs for details.")

# --- Main interface ---
if symbols:
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.selectbox("Select Trading Symbol", symbols)

        # Show live price
        current_price = None
        try:
            ticker = client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker["price"])
            st.markdown(f"### Current Price: $ {current_price:.8f}")
        except Exception as e:
            st.markdown("### Current Price: -")
            logging.error(f"Error fetching price for {symbol}: {e}")

        # Order form
        with st.form("order_form"):
            order_type = st.selectbox("Order Type", ["MARKET", "LIMIT", "STOP"])
            side = st.selectbox("Side", ["BUY", "SELL"])
            quantity = st.number_input("Quantity", min_value=0.0001, format="%.8f", value=0.01)
            price = None
            stop_price = None

            if order_type in ("LIMIT", "STOP"):
                price = st.number_input("Limit Price", min_value=0.0, format="%.8f", value=0.0)
            if order_type == "STOP":
                stop_price = st.number_input("Stop Price", min_value=0.0, format="%.8f", value=0.0)

            submitted = st.form_submit_button("Place Order")

        if submitted:
            # Validate and prepare parameters
            params, errors = prepare_order_params(symbol, order_type, side, quantity, price, stop_price)

            # Report errors if any
            if errors:
                for err in errors:
                    st.error(err)
                    logging.warning(f"Input validation error: {err}")
            else:
                try:
                    order = place_order(client, params)
                    st.success(f"Order placed successfully! Order ID: {order.get('orderId')}")

                    # Show order details in table
                    st.table({
                        "Field": ["Order ID", "Symbol", "Side", "Type", "Status", "Price", "Original Quantity", "Executed Quantity"],
                        "Value": [order.get(k, "") for k in ["orderId", "symbol", "side", "type", "status", "price", "origQty", "executedQty"]]
                    })

                    # Append order to session history
                    st.session_state.order_history.append({
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "symbol": order.get("symbol"),
                        "side": order.get("side"),
                        "type": order.get("type"),
                        "status": order.get("status"),
                        "price": order.get("price"),
                        "quantity": order.get("origQty"),
                    })

                except BinanceAPIException as e:
                    st.error(f"Order failed: {e.message}")
                    logging.error(f"Order API error: {e.message}")
                except Exception as e:
                    st.error(f"Order failed: {e}")
                    logging.error(f"Order unexpected error: {e}")

    with col2:
        usdt_balance = account_info.get('USDT_balance', "N/A")
        st.markdown(f"### USDT Balance: {usdt_balance}")

    # Show session order history
    if st.session_state.order_history:
        st.markdown("---")
        st.subheader("Order History (Session)")
        for ord in reversed(st.session_state.order_history):
            side_color = "🟢 BUY" if ord["side"] == "BUY" else "🔴 SELL"
            st.markdown(f"**[{ord['time']}] {ord['symbol']}** - {side_color} | "
                        f"Type: {ord['type']} | Status: {ord['status']} | "
                        f"Price: {ord['price']} | Qty: {ord['quantity']}")

else:
    st.info("Please enter your Binance Futures Testnet API credentials on the sidebar to connect.")

# Footer note
st.markdown(
    """
    ---
    **Note:**  
    This bot interacts with Binance Futures Testnet — safe for testing only.  
    Make sure your system time is synchronized to prevent timestamp errors.  
    Use responsibly and at your own risk.
    """
)

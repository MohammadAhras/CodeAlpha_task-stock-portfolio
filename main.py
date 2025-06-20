import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page configuration for a professional PSX-100 vibe
st.set_page_config(
    page_title="Stock Portfolio Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, PSX-inspired UI
st.markdown("""
    <style>
    .main {
        background-color: #e6f3fa;
        padding: 20px;
        border-radius: 12px;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #00695c;
        color: white;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #004d40;
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select {
        border-radius: 10px;
        border: 2px solid #00695c;
        padding: 10px;
        background-color: #ffffff;
    }
    .title {
        font-size: 3em;
        color: #003087;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.3em;
        color: #4b5e7e;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 1.8em;
        color: #003087;
        margin-top: 20px;
        font-weight: bold;
    }
    .result-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .history-box {
        background-color: #f9fafb;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Hardcoded stock prices dictionary (PSX-100 inspired stocks in PKR)
stock_prices = {
    "HBL": 120.50,   # Habib Bank Limited
    "ENGRO": 350.75, # Engro Corporation
    "OGDC": 135.20,  # Oil & Gas Development Company
    "LUCK": 900.30,  # Lucky Cement
    "PSO": 180.45    # Pakistan State Oil
}

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'history' not in st.session_state:
    st.session_state.history = []

# Function to calculate total investment
def calculate_total_investment(portfolio):
    total = 0
    for stock, quantity in portfolio:
        if stock in stock_prices:
            total += stock_prices[stock] * quantity
    return total

# Function to save portfolio to CSV
def save_to_csv(portfolio, total_investment):
    data = [{"Stock": stock, "Quantity": quantity, "Price per Share (PKR)": stock_prices.get(stock, 0), 
             "Total Value (PKR)": stock_prices.get(stock, 0) * quantity} for stock, quantity in portfolio]
    data.append({"Stock": "Total", "Quantity": "", "Price per Share (PKR)": "", "Total Value (PKR)": total_investment})
    df = pd.DataFrame(data)
    df.to_csv("psx_portfolio.csv", index=False)
    return df

# Function to add transaction to history
def add_to_history(action, stock, quantity, price, total_value):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({
        "Timestamp": timestamp,
        "Action": action,
        "Stock": stock,
        "Quantity": quantity,
        "Price per Share (PKR)": price,
        "Total Value (PKR)": total_value
    })

# Main title and subtitle
st.markdown('<div class="title">STOCK PORTFOLIO TRACKER</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Manage your investments like a pro with a PSX-inspired dashboard!</div>', unsafe_allow_html=True)

# Sidebar for Buy/Sell Stocks
with st.sidebar:
    st.header("Trade Stocks")
    action = st.radio("Action", ["Buy Stock", "Sell Stock"], help="Choose to buy or sell stocks")
    stock_name = st.selectbox("Select Stock", options=[""] + list(stock_prices.keys()), help="Select a PSX-100 stock")
    quantity = st.number_input("Quantity", min_value=0, step=1, help="Enter number of shares")
    trade_button = st.button("Execute Trade")

    # Handle Buy/Sell actions
    if trade_button and stock_name and quantity > 0:
        if action == "Buy Stock":
            st.session_state.portfolio.append((stock_name, quantity))
            add_to_history("Buy", stock_name, quantity, stock_prices[stock_name], stock_prices[stock_name] * quantity)
            st.success(f"Bought {quantity} shares of {stock_name}")
        else:  # Sell Stock
            current_shares = sum(q for s, q in st.session_state.portfolio if s == stock_name)
            if current_shares >= quantity:
                new_portfolio = []
                remaining_quantity = quantity
                for stock, qty in st.session_state.portfolio:
                    if stock == stock_name and remaining_quantity > 0:
                        if qty > remaining_quantity:
                            new_portfolio.append((stock, qty - remaining_quantity))
                            remaining_quantity = 0
                        elif qty == remaining_quantity:
                            remaining_quantity = 0
                        else:
                            remaining_quantity -= qty
                    else:
                        new_portfolio.append((stock, qty))
                st.session_state.portfolio = new_portfolio
                add_to_history("Sell", stock_name, quantity, stock_prices[stock_name], stock_prices[stock_name] * quantity)
                st.success(f"Sold {quantity} shares of {stock_name}")
            else:
                st.error(f"Not enough shares of {stock_name}. You own {current_shares} shares.")

# Portfolio Section
st.markdown('<div class="section-header">Your Portfolio</div>', unsafe_allow_html=True)
if st.session_state.portfolio:
    portfolio_df = pd.DataFrame(st.session_state.portfolio, columns=["Stock", "Quantity"])
    portfolio_df = portfolio_df.groupby("Stock").sum().reset_index()  # Aggregate same stocks
    portfolio_df["Price per Share (PKR)"] = portfolio_df["Stock"].map(stock_prices)
    portfolio_df["Total Value (PKR)"] = portfolio_df["Quantity"] * portfolio_df["Price per Share (PKR)"]
    
    # Display portfolio
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.table(portfolio_df)
    total_investment = calculate_total_investment(st.session_state.portfolio)
    st.markdown(f"**Total Portfolio Value: PKR {total_investment:,.2f}**")
    st.markdown('</div>', unsafe_allow_html=True)

    # Save to CSV button
    if st.button("Save Portfolio to CSV"):
        df = save_to_csv(st.session_state.portfolio, total_investment)
        st.success("Portfolio saved to 'psx_portfolio.csv'")
        st.download_button(
            label="Download Portfolio CSV",
            data=df.to_csv(index=False),
            file_name="psx_portfolio.csv",
            mime="text/csv"
        )

    # Clear portfolio button
    if st.button("Clear Portfolio"):
        st.session_state.portfolio = []
        st.session_state.history = []
        st.experimental_rerun()
else:
    st.info("Your portfolio is empty. Use the sidebar to buy stocks.")

# Transaction History Section
st.markdown('<div class="section-header">Transaction History</div>', unsafe_allow_html=True)
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.table(history_df)
    st.markdown('</div>', unsafe_allow_html=True)
    # Download history as CSV
    if st.button("Download Transaction History"):
        history_df.to_csv("transaction_history.csv", index=False)
        st.download_button(
            label="Download History CSV",
            data=history_df.to_csv(index=False),
            file_name="transaction_history.csv",
            mime="text/csv"
        )
else:
    st.info("No transactions yet. Buy or sell stocks to see history.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | Inspired by PSX-100 | Prices are hardcoded for demo purposes.")
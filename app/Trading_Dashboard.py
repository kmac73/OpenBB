import streamlit as st

st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Trading Dashboard")
st.markdown("### Available Strategies")

# Simple strategy list with links
st.markdown("**[SP500 Strategy Baseline](SP500_Strategy_Baseline)** - S&P 500 intraday momentum trading strategy")

st.markdown("---")
st.markdown("*Click a strategy above to configure and run it.*")
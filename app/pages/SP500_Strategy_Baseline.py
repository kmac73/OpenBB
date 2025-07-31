import streamlit as st
from datetime import datetime

# Back link
st.markdown("**[← Back to Trading Dashboard](../)**")
st.markdown("---")

st.title("📈 SP500 Strategy Baseline")

# Simple sidebar parameters (using text inputs to avoid crashes)
st.sidebar.header("Strategy Parameters")

symbols = st.sidebar.multiselect("Symbols", ["SPX"], default=["SPX"])

start_date = st.sidebar.text_input("Start Date (YYYY-MM-DD)", "2021-01-01")
end_date = st.sidebar.text_input("End Date (YYYY-MM-DD)", "2024-07-29")

frequency = st.sidebar.selectbox("Frequency", ["1M", "5M", "15M", "30M", "1H"], index=1)

entry_threshold = st.sidebar.number_input("Entry Threshold", value=0.0002, format="%.4f")
stop_loss = st.sidebar.number_input("Stop Loss", value=0.0075, format="%.4f")
profit_target = st.sidebar.number_input("Profit Target", value=0.0003, format="%.4f")

run_strategy = st.sidebar.button("🚀 Run Strategy", type="primary")

# Main content area
if run_strategy:
    st.success("Strategy configured!")
    st.write("**Parameters:**")
    st.write(f"- Symbols: {symbols}")
    st.write(f"- Start Date: {start_date}")
    st.write(f"- End Date: {end_date}")
    st.write(f"- Frequency: {frequency}")
    st.write(f"- Entry Threshold: {entry_threshold}")
    st.write(f"- Stop Loss: {stop_loss}")
    st.write(f"- Profit Target: {profit_target}")
else:
    st.info("Configure parameters in sidebar and click 'Run Strategy'")
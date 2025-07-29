import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy import stats
import warnings
from market_data import Retrieve

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="S&P 500 Intraday Momentum Strategy",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📈 S&P 500 Intraday Momentum Trading Strategy")
st.markdown("### Comprehensive Backtest and Analysis Dashboard")

st.markdown("""
This application implements and analyzes the S&P 500 intraday momentum strategy with:
- Complete strategy implementation with configurable parameters
- Performance analytics and interactive visualization
- Risk analysis and comprehensive reporting
- CSV export of trade data
""")

# Sidebar for parameters
st.sidebar.header("Strategy Parameters")

# Input parameters with default values
my_symbols = st.sidebar.multiselect(
    "Symbols",
    options=["SPX", "NDX", "RUT"],
    default=["SPX"],
    help="Select the symbols to trade"
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=datetime(2021, 1, 1),
    help="Start date for backtesting"
)

end_date = st.sidebar.date_input(
    "End Date", 
    value=datetime(2024, 7, 29),
    help="End date for backtesting"
)

frequency = st.sidebar.selectbox(
    "Frequency",
    options=["1M", "5M", "15M", "30M", "1H"],
    index=1,  # Default to "5M"
    help="Data frequency for backtesting"
)

# Strategy parameters
st.sidebar.subheader("Trading Parameters")

entry_threshold = st.sidebar.number_input(
    "Entry Threshold (bps)",
    min_value=0.0001,
    max_value=0.01,
    value=0.0002,
    step=0.0001,
    format="%.4f",
    help="Entry threshold in basis points (0.0002 = 2 bps)"
)

stop_loss = st.sidebar.number_input(
    "Stop Loss (bps)",
    min_value=0.001,
    max_value=0.02,
    value=0.0075,
    step=0.0005,
    format="%.4f",
    help="Stop loss in basis points (0.0075 = 75 bps)"
)

profit_target = st.sidebar.number_input(
    "Profit Target (bps)",
    min_value=0.0001,
    max_value=0.01,
    value=0.0003,
    step=0.0001,
    format="%.4f",
    help="Profit target in basis points (0.0003 = 3 bps)"
)

transaction_cost = st.sidebar.number_input(
    "Transaction Cost ($)",
    min_value=0.1,
    max_value=10.0,
    value=0.445,
    step=0.005,
    format="%.3f",
    help="Transaction cost per trade in dollars"
)

tick_value = st.sidebar.number_input(
    "Tick Value ($)",
    min_value=1,
    max_value=1000,
    value=100,
    step=1,
    help="Dollar value per tick movement"
)

# Run button
run_strategy = st.sidebar.button("🚀 Run Strategy", type="primary")

# Strategy implementation function
@st.cache_data
def implement_intraday_momentum_strategy(data, entry_threshold, stop_loss, profit_target, transaction_cost, tick_value):
    """
    Implement the S&P 500 Intraday Momentum Strategy
    """
    df = data.copy()
    date_col = 'date' if 'date' in df.columns else df.columns[0]
    df = df.sort_values(date_col).reset_index(drop=True)
    
    # Initialize tracking arrays
    trades = []
    current_position = None
    baseline_price = None
    entry_price = None
    position_type = None
    
    # Simulate intraday trading using daily high/low data
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        prev_close = df.iloc[i-1]['close']
        
        # Set baseline to previous day close if no position
        if current_position is None:
            baseline_price = prev_close
        
        # Calculate price movements as percentage of baseline
        high_move = (current_row['high'] - baseline_price) / baseline_price
        low_move = (current_row['low'] - baseline_price) / baseline_price
        close_move = (current_row['close'] - baseline_price) / baseline_price
        
        # Check for position entry
        if current_position is None:
            # LONG entry: price moves up threshold from baseline
            if high_move >= entry_threshold:
                current_position = 'LONG'
                entry_price = baseline_price * (1 + entry_threshold)
                position_type = 'LONG'
                
            # SHORT entry: price moves down threshold from baseline  
            elif low_move <= -entry_threshold:
                current_position = 'SHORT'
                entry_price = baseline_price * (1 - entry_threshold)
                position_type = 'SHORT'
        
        # Check for position exit if we have an open position
        if current_position is not None:
            exit_price = None
            exit_reason = None
            pnl = 0
            
            if current_position == 'LONG':
                # Stop loss: price moves back toward baseline
                stop_price = entry_price * (1 - stop_loss)
                # Profit target: target above entry
                target_price = entry_price * (1 + profit_target)
                
                # Check exits
                if current_row['low'] <= stop_price:
                    exit_price = stop_price
                    exit_reason = 'STOP_LOSS'
                elif current_row['high'] >= target_price:
                    exit_price = target_price
                    exit_reason = 'PROFIT_TARGET'
                else:
                    # Exit at close if no other exit triggered
                    exit_price = current_row['close']
                    exit_reason = 'CLOSE'
                
                # Calculate P&L for LONG position
                pnl = (exit_price - entry_price) / entry_price * baseline_price * tick_value
                
            elif current_position == 'SHORT':
                # Stop loss: price moves away from baseline (up)
                stop_price = entry_price * (1 + stop_loss)
                # Profit target: target below entry
                target_price = entry_price * (1 - profit_target)
                
                # Check exits
                if current_row['high'] >= stop_price:
                    exit_price = stop_price
                    exit_reason = 'STOP_LOSS'
                elif current_row['low'] <= target_price:
                    exit_price = target_price
                    exit_reason = 'PROFIT_TARGET'
                else:
                    # Exit at close if no other exit triggered
                    exit_price = current_row['close']
                    exit_reason = 'CLOSE'
                
                # Calculate P&L for SHORT position
                pnl = (entry_price - exit_price) / entry_price * baseline_price * tick_value
            
            # Record the trade
            net_pnl = pnl - transaction_cost
            trades.append({
                'date': current_row[date_col],
                'type': position_type,
                'baseline_price': baseline_price,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'exit_reason': exit_reason,
                'gross_pnl': pnl,
                'transaction_cost': transaction_cost,
                'net_pnl': net_pnl
            })
            
            # Reset for next trade
            baseline_price = exit_price
            current_position = None
            entry_price = None
            position_type = None
    
    # Convert trades to DataFrame
    trades_df = pd.DataFrame(trades)
    
    if len(trades_df) == 0:
        return None
    
    # Calculate summary statistics
    summary = {
        'total_trades': len(trades_df),
        'long_trades': len(trades_df[trades_df['type'] == 'LONG']),
        'short_trades': len(trades_df[trades_df['type'] == 'SHORT']),
        'winning_trades': len(trades_df[trades_df['net_pnl'] > 0]),
        'losing_trades': len(trades_df[trades_df['net_pnl'] < 0]),
        'win_rate': len(trades_df[trades_df['net_pnl'] > 0]) / len(trades_df) * 100,
        'total_pnl': trades_df['net_pnl'].sum(),
        'gross_pnl': trades_df['gross_pnl'].sum(),
        'total_transaction_costs': trades_df['transaction_cost'].sum(),
        'avg_pnl_per_trade': trades_df['net_pnl'].mean(),
        'avg_winning_trade': trades_df[trades_df['net_pnl'] > 0]['net_pnl'].mean() if len(trades_df[trades_df['net_pnl'] > 0]) > 0 else 0,
        'avg_losing_trade': trades_df[trades_df['net_pnl'] < 0]['net_pnl'].mean() if len(trades_df[trades_df['net_pnl'] < 0]) > 0 else 0,
        'profit_factor': abs(trades_df[trades_df['net_pnl'] > 0]['net_pnl'].sum()) / abs(trades_df[trades_df['net_pnl'] < 0]['net_pnl'].sum()) if trades_df[trades_df['net_pnl'] < 0]['net_pnl'].sum() != 0 else float('inf')
    }
    
    return {
        'trades_df': trades_df,
        'summary': summary
    }

# Function to create interactive charts
def create_interactive_charts(results):
    """Create interactive Plotly charts for the strategy results"""
    if not results:
        return None
    
    trades_df = results['trades_df']
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=[
            'Cumulative P&L', 'Trade P&L Distribution', 'Long vs Short P&L',
            'Exit Reason Breakdown', 'Win/Loss by Position Type', 'P&L Over Time',
            'Gross P&L Distribution', 'Entry vs Exit Price', 'Monthly P&L'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
               [{"type": "pie"}, {"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Cumulative P&L
    cumulative_pnl = trades_df['net_pnl'].cumsum()
    fig.add_trace(
        go.Scatter(x=list(range(len(cumulative_pnl))), y=cumulative_pnl,
                  mode='lines', name='Cumulative P&L', line=dict(color='green', width=2)),
        row=1, col=1
    )
    
    # 2. Trade P&L Distribution
    fig.add_trace(
        go.Histogram(x=trades_df['net_pnl'], nbinsx=50, name='P&L Distribution',
                    marker=dict(color='steelblue', opacity=0.7)),
        row=1, col=2
    )
    
    # 3. Long vs Short P&L
    long_pnl = trades_df[trades_df['type'] == 'LONG']['net_pnl'].sum()
    short_pnl = trades_df[trades_df['type'] == 'SHORT']['net_pnl'].sum()
    fig.add_trace(
        go.Bar(x=['LONG', 'SHORT'], y=[long_pnl, short_pnl],
               marker=dict(color=['green' if x > 0 else 'red' for x in [long_pnl, short_pnl]]),
               name='Position P&L'),
        row=1, col=3
    )
    
    # 4. Exit Reason Pie Chart
    exit_counts = trades_df['exit_reason'].value_counts()
    fig.add_trace(
        go.Pie(labels=exit_counts.index, values=exit_counts.values, name="Exit Reasons"),
        row=2, col=1
    )
    
    # 5. Win/Loss by Position Type
    for pos_type in ['LONG', 'SHORT']:
        pos_data = trades_df[trades_df['type'] == pos_type]
        wins = len(pos_data[pos_data['net_pnl'] > 0])
        losses = len(pos_data[pos_data['net_pnl'] <= 0])
        fig.add_trace(
            go.Bar(x=[f'{pos_type}_Wins', f'{pos_type}_Losses'], y=[wins, losses],
                   marker=dict(color=['green', 'red']), name=f'{pos_type} Trades'),
            row=2, col=2
        )
    
    # 6. P&L Over Time
    fig.add_trace(
        go.Scatter(x=list(range(len(cumulative_pnl))), y=cumulative_pnl,
                  fill='tonexty', mode='lines', name='Cumulative P&L Progress',
                  line=dict(color='blue', width=2)),
        row=2, col=3
    )
    
    # 7. Gross P&L Distribution
    fig.add_trace(
        go.Histogram(x=trades_df['gross_pnl'], nbinsx=30, name='Gross P&L Distribution',
                    marker=dict(color='orange', opacity=0.7)),
        row=3, col=1
    )
    
    # 8. Entry vs Exit Price Scatter
    fig.add_trace(
        go.Scatter(x=trades_df['entry_price'], y=trades_df['exit_price'],
                  mode='markers', name='Entry vs Exit',
                  marker=dict(color=trades_df['net_pnl'], colorscale='RdYlGn', size=5)),
        row=3, col=2
    )
    
    # 9. Monthly P&L
    if 'date' in trades_df.columns:
        trades_df['month'] = pd.to_datetime(trades_df['date']).dt.to_period('M')
        monthly_pnl = trades_df.groupby('month')['net_pnl'].sum()
        fig.add_trace(
            go.Bar(x=[str(m) for m in monthly_pnl.index], y=monthly_pnl.values,
                   marker=dict(color='purple', opacity=0.7), name='Monthly P&L'),
            row=3, col=3
        )
    
    fig.update_layout(height=1000, showlegend=False, title_text="Strategy Performance Dashboard")
    return fig

# Main execution
if run_strategy:
    if my_symbols:  # Only run if symbols are selected
        with st.spinner('Loading market data and running strategy...'):
            try:
                # Load market data
                market_df = Retrieve.from_file(
                    symbols=my_symbols,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    freq=frequency
                )
                
                # Run strategy
                results = implement_intraday_momentum_strategy(
                    market_df, entry_threshold, stop_loss, profit_target, transaction_cost, tick_value
                )
                
                # Store results in session state
                st.session_state['results'] = results
                st.session_state['market_df'] = market_df
                
            except Exception as e:
                st.error(f"Error running strategy: {str(e)}")
                st.stop()
    else:
        st.warning("Please select at least one symbol to run the strategy.")
        st.stop()

# Display results if available
if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']
    summary = results['summary']
    trades_df = results['trades_df']
    
    # Performance Summary
    st.header("📊 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", f"{summary['total_trades']:,}")
        st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
    
    with col2:
        st.metric("Total P&L", f"${summary['total_pnl']:,.2f}")
        st.metric("Avg P&L/Trade", f"${summary['avg_pnl_per_trade']:.2f}")
    
    with col3:
        st.metric("Long Trades", f"{summary['long_trades']:,}")
        st.metric("Short Trades", f"{summary['short_trades']:,}")
    
    with col4:
        st.metric("Profit Factor", f"{summary['profit_factor']:.2f}")
        st.metric("Transaction Costs", f"${summary['total_transaction_costs']:,.2f}")
    
    # Detailed Statistics
    st.header("📈 Detailed Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trade Statistics")
        stats_data = {
            "Metric": ["Winning Trades", "Losing Trades", "Average Winning Trade", "Average Losing Trade", "Gross P&L"],
            "Value": [
                f"{summary['winning_trades']:,}",
                f"{summary['losing_trades']:,}",
                f"${summary['avg_winning_trade']:.2f}",
                f"${summary['avg_losing_trade']:.2f}",
                f"${summary['gross_pnl']:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), hide_index=True)
    
    with col2:
        st.subheader("Exit Reason Breakdown")
        exit_breakdown = trades_df['exit_reason'].value_counts()
        breakdown_data = {
            "Exit Reason": exit_breakdown.index,
            "Count": exit_breakdown.values,
            "Percentage": [f"{(count / len(trades_df)) * 100:.1f}%" for count in exit_breakdown.values]
        }
        st.dataframe(pd.DataFrame(breakdown_data), hide_index=True)
    
    # Statistical Significance
    st.subheader("Statistical Analysis")
    t_stat, p_value = stats.ttest_1samp(trades_df['net_pnl'], 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("T-Statistic", f"{t_stat:.3f}")
    with col2:
        st.metric("P-Value", f"{p_value:.6f}")
    with col3:
        significance = "✅ Significant (p < 0.05)" if p_value < 0.05 else "⚠️ Not Significant (p ≥ 0.05)"
        st.write(f"**Result:** {significance}")
    
    # Interactive Charts
    st.header("📊 Interactive Charts")
    
    # Create and display the comprehensive chart
    fig = create_interactive_charts(results)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional individual charts for better visibility
    st.subheader("Cumulative P&L Chart")
    cumulative_pnl = trades_df['net_pnl'].cumsum()
    fig_cumulative = go.Figure()
    fig_cumulative.add_trace(go.Scatter(
        x=list(range(len(cumulative_pnl))),
        y=cumulative_pnl,
        mode='lines',
        name='Cumulative P&L',
        line=dict(color='green', width=3)
    ))
    fig_cumulative.update_layout(
        title="Cumulative P&L Over Time",
        xaxis_title="Trade Number",
        yaxis_title="Cumulative P&L ($)",
        height=400
    )
    st.plotly_chart(fig_cumulative, use_container_width=True)
    
    # Trade data export
    st.header("📋 Trade Data")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Recent Trades (First 100)")
        display_trades = trades_df.head(100).copy()
        display_trades['date'] = pd.to_datetime(display_trades['date']).dt.strftime('%Y-%m-%d %H:%M')
        display_trades = display_trades.round(2)
        st.dataframe(display_trades, hide_index=True)
    
    with col2:
        st.subheader("Export Data")
        
        # CSV download
        csv_data = trades_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Trades (CSV)",
            data=csv_data,
            file_name=f"sp500_strategy_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Download complete trade data as CSV file"
        )
        
        st.info(f"Total trades: {len(trades_df):,}")

else:
    st.info("👈 Configure parameters in the sidebar and click 'Run Strategy' to start the analysis.")

# Footer
st.markdown("---")
st.markdown("**S&P 500 Intraday Momentum Strategy Dashboard** | Built with Streamlit")
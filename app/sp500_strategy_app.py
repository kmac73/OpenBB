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
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
from io import BytesIO
import base64

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="S&P 500 Intraday Momentum Strategy",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for sidebar visibility and report history
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

# Initialize report history
if 'report_history' not in st.session_state:
    st.session_state.report_history = []

# Title and description
col1, col2 = st.columns([8, 1])
with col1:
    st.title("📈 S&P 500 Intraday Momentum Trading Strategy")
    st.markdown("### Comprehensive Backtest and Analysis Dashboard")

with col2:
    if st.button("⚙️" if not st.session_state.sidebar_collapsed else "📊", 
                 help="Toggle Parameters Panel",
                 key="toggle_sidebar"):
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.rerun()

st.markdown("""
This application implements and analyzes the S&P 500 intraday momentum strategy with:
- Complete strategy implementation with configurable parameters
- Performance analytics and interactive visualization
- Risk analysis and comprehensive reporting
- CSV export of trade data
""")

# Parameters panel (conditional)
if not st.session_state.sidebar_collapsed:
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
else:
    # Use default values when sidebar is collapsed
    my_symbols = ["SPX"]
    start_date = datetime(2021, 1, 1).date()
    end_date = datetime(2024, 7, 29).date()
    frequency = "5M"
    entry_threshold = 0.0002
    stop_loss = 0.0075
    profit_target = 0.0003
    transaction_cost = 0.445
    tick_value = 100
    
    # Compact parameter display
    st.info(f"📊 Running with: {my_symbols[0]} | {start_date} to {end_date} | {frequency} | Entry: {entry_threshold*10000:.0f}bps")
    run_strategy = st.button("🚀 Run Strategy", type="primary")

# Strategy implementation function
@st.cache_data(show_spinner=False, hash_funcs={pd.DataFrame: lambda df: str(df.shape)})
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
    
    # Calculate daily performance metrics
    trades_df['date_only'] = pd.to_datetime(trades_df['date']).dt.date
    daily_pnl = trades_df.groupby('date_only')['net_pnl'].sum()
    daily_trades = trades_df.groupby('date_only').size()
    
    profitable_days = len(daily_pnl[daily_pnl > 0])
    total_days = len(daily_pnl)
    profitable_days_pct = (profitable_days / total_days) * 100 if total_days > 0 else 0
    
    max_daily_gain = daily_pnl.max() if len(daily_pnl) > 0 else 0
    max_daily_loss = daily_pnl.min() if len(daily_pnl) > 0 else 0
    avg_daily_pnl = daily_pnl.mean() if len(daily_pnl) > 0 else 0
    daily_volatility = daily_pnl.std() if len(daily_pnl) > 0 else 0
    
    # Calculate Sharpe ratio (assuming risk-free rate of 0)
    sharpe_ratio = avg_daily_pnl / daily_volatility if daily_volatility != 0 else 0
    
    # Calculate VaR (95% confidence)
    var_95 = daily_volatility * 1.645 if daily_volatility > 0 else 0
    
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
        'profit_factor': abs(trades_df[trades_df['net_pnl'] > 0]['net_pnl'].sum()) / abs(trades_df[trades_df['net_pnl'] < 0]['net_pnl'].sum()) if trades_df[trades_df['net_pnl'] < 0]['net_pnl'].sum() != 0 else float('inf'),
        # Daily performance metrics
        'profitable_days': profitable_days,
        'total_days': total_days,
        'profitable_days_pct': profitable_days_pct,
        'max_daily_gain': max_daily_gain,
        'max_daily_loss': max_daily_loss,
        'avg_daily_pnl': avg_daily_pnl,
        'daily_volatility': daily_volatility,
        'sharpe_ratio': sharpe_ratio,
        'var_95': var_95,
        # Additional metrics
        'daily_pnl': daily_pnl,
        'daily_trades': daily_trades
    }
    
    return {
        'trades_df': trades_df,
        'summary': summary
    }

# Function to create interactive charts
def create_interactive_charts(results):
    """Create interactive Plotly charts for the strategy results with enhanced labels and tooltips"""
    if not results:
        return None
    
    trades_df = results['trades_df']
    
    # Create subplots with enhanced titles
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=[
            'Cumulative P&L ($)', 'Trade P&L Distribution', 'Position Type Performance ($)',
            'Exit Reason Breakdown (%)', 'Win/Loss Count by Position', 'Cumulative Performance Trend',
            'Gross P&L Distribution', 'Entry vs Exit Price Correlation', 'Monthly P&L Performance ($)'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
               [{"type": "pie"}, {"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Cumulative P&L with enhanced tooltips
    cumulative_pnl = trades_df['net_pnl'].cumsum()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(cumulative_pnl))), 
            y=cumulative_pnl,
            mode='lines', 
            name='Cumulative P&L', 
            line=dict(color='green', width=2),
            hovertemplate='Trade #: %{x}<br>Cumulative P&L: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Trade P&L Distribution
    fig.add_trace(
        go.Histogram(
            x=trades_df['net_pnl'], 
            nbinsx=50, 
            name='P&L Distribution',
            marker=dict(color='steelblue', opacity=0.7),
            hovertemplate='P&L Range: $%{x}<br>Count: %{y}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Long vs Short P&L with enhanced tooltips
    long_pnl = trades_df[trades_df['type'] == 'LONG']['net_pnl'].sum()
    short_pnl = trades_df[trades_df['type'] == 'SHORT']['net_pnl'].sum()
    fig.add_trace(
        go.Bar(
            x=['LONG', 'SHORT'], 
            y=[long_pnl, short_pnl],
            marker=dict(color=['green' if x > 0 else 'red' for x in [long_pnl, short_pnl]]),
            name='Position P&L',
            hovertemplate='Position: %{x}<br>Net P&L: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=3
    )
    
    # 4. Exit Reason Pie Chart with percentages
    exit_counts = trades_df['exit_reason'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=exit_counts.index, 
            values=exit_counts.values, 
            name="Exit Reasons",
            hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 5. Win/Loss by Position Type - Fixed formatting
    long_data = trades_df[trades_df['type'] == 'LONG']
    short_data = trades_df[trades_df['type'] == 'SHORT']
    
    long_wins = len(long_data[long_data['net_pnl'] > 0])
    long_losses = len(long_data[long_data['net_pnl'] <= 0])
    short_wins = len(short_data[short_data['net_pnl'] > 0])
    short_losses = len(short_data[short_data['net_pnl'] <= 0])
    
    # Add wins
    fig.add_trace(
        go.Bar(
            x=['LONG', 'SHORT'], 
            y=[long_wins, short_wins],
            name='Wins',
            marker=dict(color='green'),
            hovertemplate='%{x} Wins: %{y}<extra></extra>',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Add losses
    fig.add_trace(
        go.Bar(
            x=['LONG', 'SHORT'], 
            y=[long_losses, short_losses],
            name='Losses',
            marker=dict(color='red'),
            hovertemplate='%{x} Losses: %{y}<extra></extra>',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # 6. P&L Over Time with area fill
    fig.add_trace(
        go.Scatter(
            x=list(range(len(cumulative_pnl))), 
            y=cumulative_pnl,
            fill='tonexty', 
            mode='lines', 
            name='Cumulative Trend',
            line=dict(color='blue', width=2),
            hovertemplate='Trade #: %{x}<br>Cumulative P&L: $%{y:,.2f}<extra></extra>'
        ),
        row=2, col=3
    )
    
    # 7. Gross P&L Distribution
    fig.add_trace(
        go.Histogram(
            x=trades_df['gross_pnl'], 
            nbinsx=30, 
            name='Gross P&L Distribution',
            marker=dict(color='orange', opacity=0.7),
            hovertemplate='Gross P&L Range: $%{x}<br>Count: %{y}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # 8. Entry vs Exit Price Scatter with color coding
    fig.add_trace(
        go.Scatter(
            x=trades_df['entry_price'], 
            y=trades_df['exit_price'],
            mode='markers', 
            name='Entry vs Exit',
            marker=dict(
                color=trades_df['net_pnl'], 
                colorscale='RdYlGn', 
                size=6,
                colorbar=dict(title="P&L ($)")
            ),
            hovertemplate='Entry: $%{x:.2f}<br>Exit: $%{y:.2f}<br>P&L: $%{marker.color:.2f}<extra></extra>'
        ),
        row=3, col=2
    )
    
    # 9. Monthly P&L with enhanced formatting
    if 'date' in trades_df.columns:
        trades_df_copy = trades_df.copy()
        trades_df_copy['month'] = pd.to_datetime(trades_df_copy['date']).dt.to_period('M')
        monthly_pnl = trades_df_copy.groupby('month')['net_pnl'].sum()
        fig.add_trace(
            go.Bar(
                x=[str(m) for m in monthly_pnl.index], 
                y=monthly_pnl.values,
                marker=dict(
                    color=['green' if x > 0 else 'red' for x in monthly_pnl.values], 
                    opacity=0.7
                ), 
                name='Monthly P&L',
                hovertemplate='Month: %{x}<br>P&L: $%{y:,.2f}<extra></extra>'
            ),
            row=3, col=3
        )
    
    # Update axis labels
    fig.update_xaxes(title_text="Trade Number", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative P&L ($)", row=1, col=1)
    
    fig.update_xaxes(title_text="P&L per Trade ($)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)
    
    fig.update_xaxes(title_text="Position Type", row=1, col=3)
    fig.update_yaxes(title_text="Net P&L ($)", row=1, col=3)
    
    fig.update_xaxes(title_text="Trade Outcome", row=2, col=2)
    fig.update_yaxes(title_text="Number of Trades", row=2, col=2)
    
    fig.update_xaxes(title_text="Trade Number", row=2, col=3)
    fig.update_yaxes(title_text="Cumulative P&L ($)", row=2, col=3)
    
    fig.update_xaxes(title_text="Gross P&L ($)", row=3, col=1)
    fig.update_yaxes(title_text="Frequency", row=3, col=1)
    
    fig.update_xaxes(title_text="Entry Price ($)", row=3, col=2)
    fig.update_yaxes(title_text="Exit Price ($)", row=3, col=2)
    
    fig.update_xaxes(title_text="Month", row=3, col=3)
    fig.update_yaxes(title_text="Monthly P&L ($)", row=3, col=3)
    
    fig.update_layout(
        height=1200, 
        showlegend=False, 
        title_text="📊 Comprehensive Strategy Performance Dashboard",
        title_font_size=16
    )
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
                
                # Add to report history
                report_entry = {
                    'timestamp': datetime.now(),
                    'parameters': {
                        'symbols': my_symbols,
                        'start_date': str(start_date),
                        'end_date': str(end_date),
                        'frequency': frequency,
                        'entry_threshold': entry_threshold,
                        'stop_loss': stop_loss,
                        'profit_target': profit_target,
                        'transaction_cost': transaction_cost,
                        'tick_value': tick_value
                    },
                    'results_summary': {
                        'total_pnl': results['summary']['total_pnl'],
                        'total_trades': results['summary']['total_trades'],
                        'win_rate': results['summary']['win_rate'],
                        'profit_factor': results['summary']['profit_factor'],
                        'sharpe_ratio': results['summary']['sharpe_ratio']
                    },
                    'results': results  # Store full results for PDF generation
                }
                
                # Add to beginning of list (most recent first) and limit to 20 entries
                st.session_state.report_history.insert(0, report_entry)
                if len(st.session_state.report_history) > 20:
                    st.session_state.report_history = st.session_state.report_history[:20]
                
            except Exception as e:
                st.error(f"Error running strategy: {str(e)}")
                st.stop()
    else:
        st.warning("Please select at least one symbol to run the strategy.")
        st.stop()

# Helper function to create downloadable CSV
def create_download_csv(data, filename_prefix):
    csv_data = data.to_csv(index=False)
    return st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

# Function to create charts for PDF using matplotlib
def create_pdf_charts(results):
    """Create matplotlib charts for PDF inclusion"""
    charts = {}
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from io import BytesIO
        
        trades_df = results['trades_df']
        summary = results['summary']
        
        # Set style
        plt.style.use('default')
        
        # 1. Cumulative P&L Chart
        fig, ax = plt.subplots(figsize=(10, 6))
        cumulative_pnl = trades_df['net_pnl'].cumsum()
        ax.plot(range(len(cumulative_pnl)), cumulative_pnl, 'g-', linewidth=2)
        ax.set_title('Cumulative P&L Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Trade Number')
        ax.set_ylabel('Cumulative P&L ($)')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['cumulative_pnl'] = buf.getvalue()
        plt.close()
        
        # 2. P&L Distribution Histogram
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(trades_df['net_pnl'], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        ax.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('P&L per Trade ($)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        ax.axvline(x=0, color='r', linestyle='--', alpha=0.7, label='Break-even')
        ax.axvline(x=trades_df['net_pnl'].mean(), color='g', linestyle='--', alpha=0.7, label=f'Mean: ${trades_df["net_pnl"].mean():.2f}')
        ax.legend()
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['pnl_distribution'] = buf.getvalue()
        plt.close()
        
        # 3. Long vs Short Performance
        fig, ax = plt.subplots(figsize=(8, 6))
        long_pnl = trades_df[trades_df['type'] == 'LONG']['net_pnl'].sum()
        short_pnl = trades_df[trades_df['type'] == 'SHORT']['net_pnl'].sum()
        
        bars = ax.bar(['LONG', 'SHORT'], [long_pnl, short_pnl], 
                     color=['green' if x > 0 else 'red' for x in [long_pnl, short_pnl]], alpha=0.7)
        ax.set_title('Long vs Short Position Performance', fontsize=14, fontweight='bold')
        ax.set_ylabel('Total P&L ($)')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, [long_pnl, short_pnl]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (abs(height)*0.01),
                   f'${value:,.0f}', ha='center', va='bottom' if height > 0 else 'top')
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['long_vs_short'] = buf.getvalue()
        plt.close()
        
        # 4. Exit Reason Pie Chart
        fig, ax = plt.subplots(figsize=(8, 8))
        exit_counts = trades_df['exit_reason'].value_counts()
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        wedges, texts, autotexts = ax.pie(exit_counts.values, labels=exit_counts.index, autopct='%1.1f%%',
                                         colors=colors[:len(exit_counts)], startangle=90)
        ax.set_title('Exit Reason Breakdown', fontsize=14, fontweight='bold')
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['exit_reasons'] = buf.getvalue()
        plt.close()
        
        # 5. Win/Loss Count by Position Type
        fig, ax = plt.subplots(figsize=(8, 6))
        long_data = trades_df[trades_df['type'] == 'LONG']
        short_data = trades_df[trades_df['type'] == 'SHORT']
        
        long_wins = len(long_data[long_data['net_pnl'] > 0])
        long_losses = len(long_data[long_data['net_pnl'] <= 0])
        short_wins = len(short_data[short_data['net_pnl'] > 0])
        short_losses = len(short_data[short_data['net_pnl'] <= 0])
        
        x = np.arange(2)
        width = 0.35
        
        bars1 = ax.bar(x - width/2, [long_wins, short_wins], width, label='Wins', color='green', alpha=0.7)
        bars2 = ax.bar(x + width/2, [long_losses, short_losses], width, label='Losses', color='red', alpha=0.7)
        
        ax.set_title('Win/Loss Count by Position Type', fontsize=14, fontweight='bold')
        ax.set_xlabel('Position Type')
        ax.set_ylabel('Number of Trades')
        ax.set_xticks(x)
        ax.set_xticklabels(['LONG', 'SHORT'])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(height)}', ha='center', va='bottom')
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(height)}', ha='center', va='bottom')
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['win_loss_by_position'] = buf.getvalue()
        plt.close()
        
        # 6. Gross P&L Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(trades_df['gross_pnl'], bins=50, alpha=0.7, color='orange', edgecolor='black')
        ax.set_title('Gross P&L Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Gross P&L per Trade ($)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        ax.axvline(x=0, color='r', linestyle='--', alpha=0.7, label='Break-even')
        ax.axvline(x=trades_df['gross_pnl'].mean(), color='g', linestyle='--', alpha=0.7, label=f'Mean: ${trades_df["gross_pnl"].mean():.2f}')
        ax.legend()
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['gross_pnl_distribution'] = buf.getvalue()
        plt.close()
        
        # 7. Entry vs Exit Price Correlation
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['green' if pnl > 0 else 'red' for pnl in trades_df['net_pnl']]
        scatter = ax.scatter(trades_df['entry_price'], trades_df['exit_price'], 
                           c=colors, alpha=0.6, s=30)
        
        # Add diagonal line for reference (entry = exit)
        min_price = min(trades_df['entry_price'].min(), trades_df['exit_price'].min())
        max_price = max(trades_df['entry_price'].max(), trades_df['exit_price'].max())
        ax.plot([min_price, max_price], [min_price, max_price], 'k--', alpha=0.5, label='Entry = Exit')
        
        ax.set_title('Entry vs Exit Price Correlation', fontsize=14, fontweight='bold')
        ax.set_xlabel('Entry Price ($)')
        ax.set_ylabel('Exit Price ($)')
        ax.grid(True, alpha=0.3)
        ax.legend(['Entry = Exit', 'Winning Trades', 'Losing Trades'])
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        charts['entry_exit_correlation'] = buf.getvalue()
        plt.close()
        
        # 8. Monthly Performance (simplified to avoid datetime issues)
        if 'date' in trades_df.columns and len(trades_df) > 0:
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Simple approach: just show cumulative P&L over time instead of complex monthly grouping
                cumulative_pnl = trades_df['net_pnl'].cumsum()
                ax.plot(range(len(cumulative_pnl)), cumulative_pnl, 'b-', linewidth=2, marker='o', markersize=4)
                ax.set_title('Performance Over Time', fontsize=14, fontweight='bold')
                ax.set_xlabel('Trade Sequence')
                ax.set_ylabel('Cumulative P&L ($)')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
                
                # Format y-axis as currency
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                
                buf = BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')  # Reduced DPI
                buf.seek(0)
                charts['monthly_performance'] = buf.getvalue()
                plt.close()
            except Exception as e:
                print(f"Monthly performance chart error: {e}")
                # Skip this chart if it fails
            
    except Exception as e:
        print(f"Error creating charts: {e}")
        # Return empty charts dict if matplotlib fails
        return {}
    
    return charts

# Enhanced PDF generation with charts
def generate_pdf_report(results, parameters):
    """Generate a comprehensive PDF report with charts"""
    buffer = BytesIO()
    temp_files = []
    
    try:
        # Try to use reportlab for professional PDF
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, alignment=1, spaceAfter=30)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceAfter=15)
        
        # Title
        story.append(Paragraph("S&P 500 Intraday Momentum Strategy", title_style))
        story.append(Paragraph("Comprehensive Performance Report", styles['Heading2']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Strategy Parameters Table
        story.append(Paragraph("Strategy Parameters", heading_style))
        param_data = [
            ['Parameter', 'Value'],
            ['Symbols', ', '.join(parameters['symbols'])],
            ['Date Range', f"{parameters['start_date']} to {parameters['end_date']}"],
            ['Frequency', parameters['frequency']],
            ['Entry Threshold', f"{parameters['entry_threshold']*10000:.1f} bps"],
            ['Stop Loss', f"{parameters['stop_loss']*10000:.1f} bps"],
            ['Profit Target', f"{parameters['profit_target']*10000:.1f} bps"],
            ['Transaction Cost', f"${parameters['transaction_cost']:.3f}"],
            ['Tick Value', f"${parameters['tick_value']:,}"]
        ]
        
        param_table = Table(param_data, colWidths=[3*inch, 3*inch])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(param_table)
        story.append(Spacer(1, 30))
        
        # =============================================================
        # SUMMARY TAB - Performance Summary Table  
        # =============================================================
        summary = results['summary']
        trades_df = results['trades_df']
        
        story.append(Paragraph("Summary", heading_style))
        
        # Performance Summary Table (from tab1)
        story.append(Paragraph("Performance Summary", styles['Heading3']))
        perf_data = [
            ['Metric', 'Value'],
            ['Net P&L', f"${summary['total_pnl']:,.2f}"],
            ['Gross P&L', f"${summary['gross_pnl']:,.2f}"],
            ['Total Trades', f"{summary['total_trades']:,}"],
            ['Win Rate', f"{summary['win_rate']:.2f}%"],
            ['Average P&L per Trade', f"${summary['avg_pnl_per_trade']:.2f}"],
            ['Profit Factor', f"{summary['profit_factor']:.2f}"],
            ['Sharpe Ratio', f"{summary['sharpe_ratio']:.3f}"],
            ['Transaction Costs', f"${summary['total_transaction_costs']:,.2f}"],
            ['Long Trades', f"{summary['long_trades']:,} ({summary['long_trades']/summary['total_trades']*100:.1f}%)"],
            ['Short Trades', f"{summary['short_trades']:,} ({summary['short_trades']/summary['total_trades']*100:.1f}%)"]
        ]
        
        perf_table = Table(perf_data, colWidths=[3*inch, 3*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Daily Performance Metrics Table (from tab1)
        story.append(Paragraph("Daily Performance Metrics", styles['Heading3']))
        daily_data = [
            ['Metric', 'Value'],
            ['Profitable Days', f"{summary['profitable_days']:,}"],
            ['Total Trading Days', f"{summary['total_days']:,}"],
            ['Profitable Days %', f"{summary['profitable_days_pct']:.1f}%"],
            ['Maximum Daily Gain', f"${summary['max_daily_gain']:,.2f}"],
            ['Maximum Daily Loss', f"${summary['max_daily_loss']:,.2f}"],
            ['Average Daily P&L', f"${summary['avg_daily_pnl']:,.2f}"],
            ['Daily Volatility', f"${summary['daily_volatility']:,.2f}"],
            ['95% VaR (Daily)', f"${summary['var_95']:,.2f}"]
        ]
        
        daily_table = Table(daily_data, colWidths=[3*inch, 3*inch])
        daily_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(daily_table)
        story.append(PageBreak())
        
        # =============================================================
        # PERFORMANCE ANALYSIS TAB - Trade Statistics & Statistical Analysis
        # =============================================================
        story.append(Paragraph("Performance Analysis", heading_style))
        
        # Trade Statistics Table (from tab2)
        story.append(Paragraph("Trade Statistics", styles['Heading3']))
        trade_stats_data = [
            ['Metric', 'Value'],
            ['Winning Trades', f"{summary['winning_trades']:,}"],
            ['Losing Trades', f"{summary['losing_trades']:,}"],
            ['Average Winning Trade', f"${summary['avg_winning_trade']:.2f}"],
            ['Average Losing Trade', f"${summary['avg_losing_trade']:.2f}"],
            ['Largest Win', f"${trades_df['net_pnl'].max():.2f}"],
            ['Largest Loss', f"${trades_df['net_pnl'].min():.2f}"]
        ]
        
        trade_stats_table = Table(trade_stats_data, colWidths=[3*inch, 3*inch])
        trade_stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(trade_stats_table)
        story.append(Spacer(1, 20))
        
        # Risk Management Summary - Exit Reason Breakdown (from tab2)
        story.append(Paragraph("Risk Management Summary", styles['Heading3']))
        exit_breakdown = trades_df['exit_reason'].value_counts()
        breakdown_data = [['Exit Reason', 'Count', 'Percentage']]
        for reason, count in exit_breakdown.items():
            breakdown_data.append([reason, f"{count:,}", f"{(count / len(trades_df)) * 100:.1f}%"])
        
        breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(breakdown_table)
        story.append(Spacer(1, 20))
        
        # Statistical Analysis Table (from tab2)
        story.append(Paragraph("Statistical Analysis", styles['Heading3']))
        pnl_data = trades_df['net_pnl'].values
        n = len(pnl_data)
        mean_pnl = np.mean(pnl_data)
        std_pnl = np.std(pnl_data, ddof=1)
        se_pnl = std_pnl / np.sqrt(n)
        t_stat = mean_pnl / se_pnl if se_pnl != 0 else 0
        df = n - 1
        
        # Import scipy stats once at the beginning
        from scipy import stats as scipy_stats
        
        if abs(t_stat) > 8:
            p_value_str = "< 1e-15"
        else:
            p_value = 2 * (1 - scipy_stats.t.cdf(abs(t_stat), df))
            if p_value < 1e-10:
                p_value_str = f"< 1e-10"
            elif p_value < 1e-6:
                p_value_str = f"{p_value:.2e}"
            else:
                p_value_str = f"{p_value:.6f}"
        
        cohens_d = mean_pnl / std_pnl if std_pnl != 0 else 0
        alpha = 0.05
        t_critical = scipy_stats.t.ppf(1 - alpha/2, df)
        ci_lower = mean_pnl - t_critical * se_pnl
        ci_upper = mean_pnl + t_critical * se_pnl
        
        statistical_data = [
            ['Statistical Test', 'Value'],
            ['Sample Size (n)', f"{n:,}"],
            ['Mean P&L per Trade', f"${mean_pnl:.2f}"],
            ['Standard Deviation', f"${std_pnl:.2f}"],
            ['Standard Error', f"${se_pnl:.2f}"],
            ['T-Statistic', f"{t_stat:.2f}"],
            ['P-Value (two-tailed)', p_value_str],
            ['Degrees of Freedom', f"{df:,}"],
            ['95% Confidence Interval', f"${ci_lower:.2f} to ${ci_upper:.2f}"],
            ['Effect Size (Cohen\'s d)', f"{cohens_d:.2f}"]
        ]
        
        statistical_table = Table(statistical_data, colWidths=[3*inch, 3*inch])
        statistical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(statistical_table)
        story.append(PageBreak())
        
        # =============================================================
        # REPORTS TAB - Long/Short, Transaction Cost, VaR Analysis
        # =============================================================
        story.append(Paragraph("Comprehensive Reports", heading_style))
        
        # Long/Short Exposure Analysis (from tab3)
        story.append(Paragraph("Long/Short Exposure Analysis", styles['Heading3']))
        long_short_data = [
            ['Position Type', 'Count', 'Percentage', 'Net P&L', 'Avg P&L'],
            ['Long Trades', f"{summary['long_trades']:,}", f"{(summary['long_trades']/summary['total_trades']*100):.1f}%", 
             f"${trades_df[trades_df['type'] == 'LONG']['net_pnl'].sum():.2f}", 
             f"${trades_df[trades_df['type'] == 'LONG']['net_pnl'].mean():.2f}"],
            ['Short Trades', f"{summary['short_trades']:,}", f"{(summary['short_trades']/summary['total_trades']*100):.1f}%", 
             f"${trades_df[trades_df['type'] == 'SHORT']['net_pnl'].sum():.2f}", 
             f"${trades_df[trades_df['type'] == 'SHORT']['net_pnl'].mean():.2f}"]
        ]
        
        long_short_table = Table(long_short_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1.3*inch, 1*inch])
        long_short_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(long_short_table)
        story.append(Spacer(1, 20))
        
        # Transaction Cost Analysis (from tab3)
        story.append(Paragraph("Transaction Cost Analysis", styles['Heading3']))
        transaction_cost = parameters['transaction_cost']
        cost_scenarios_data = [
            ['Scenario', 'Cost per Trade', 'Total Costs', 'Net P&L', 'Impact'],
            ['Current', f"${transaction_cost:.3f}", f"${summary['total_transaction_costs']:.2f}", 
             f"${summary['total_pnl']:.2f}", "Baseline"],
            ['+20% Increase', f"${transaction_cost * 1.2:.3f}", f"${summary['total_transaction_costs'] * 1.2:.2f}", 
             f"${summary['total_pnl'] - (summary['total_transaction_costs'] * 0.2):.2f}", 
             f"{-((summary['total_transaction_costs'] * 0.2) / summary['total_pnl'] * 100):.2f}%"],
            ['+50% Increase', f"${transaction_cost * 1.5:.3f}", f"${summary['total_transaction_costs'] * 1.5:.2f}", 
             f"${summary['total_pnl'] - (summary['total_transaction_costs'] * 0.5):.2f}", 
             f"{-((summary['total_transaction_costs'] * 0.5) / summary['total_pnl'] * 100):.2f}%"],
            ['Double Costs', f"${transaction_cost * 2:.3f}", f"${summary['total_transaction_costs'] * 2:.2f}", 
             f"${summary['total_pnl'] - summary['total_transaction_costs']:.2f}", 
             f"{-(summary['total_transaction_costs'] / summary['total_pnl'] * 100):.2f}%"]
        ]
        
        cost_scenarios_table = Table(cost_scenarios_data, colWidths=[1.3*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.1*inch])
        cost_scenarios_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(cost_scenarios_table)
        story.append(Spacer(1, 20))
        
        # Risk Management Analysis - Daily VaR (from tab3)
        story.append(Paragraph("Risk Management Analysis - Value at Risk (VaR)", styles['Heading3']))
        daily_std = summary['daily_volatility']
        var_90 = daily_std * 1.282
        var_95 = daily_std * 1.645  
        var_99 = daily_std * 2.326
        
        var_analysis_data = [
            ['Risk Metric', 'Value', 'Calculation'],
            ['Daily P&L Standard Deviation', f"${daily_std:,.2f}", "√(Σ(daily_pnl - mean)²/(n-1))"],
            ['1-Day VaR (90% confidence)', f"${var_90:,.2f}", "1.282 × Daily Std Dev"],
            ['1-Day VaR (95% confidence)', f"${var_95:,.2f}", "1.645 × Daily Std Dev"],
            ['1-Day VaR (99% confidence)', f"${var_99:,.2f}", "2.326 × Daily Std Dev"],
            ['Maximum Historical Daily Loss', f"${abs(summary['max_daily_loss']):,.2f}", "Observed maximum loss"],
            ['VaR as % of Average Daily P&L', f"{(var_95/abs(summary['avg_daily_pnl'])*100):.1f}%" if summary['avg_daily_pnl'] != 0 else "N/A", "95% VaR / Avg Daily P&L"]
        ]
        
        var_analysis_table = Table(var_analysis_data, colWidths=[2.2*inch, 1.5*inch, 2.3*inch])
        var_analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(var_analysis_table)
        story.append(PageBreak())
        
        # =============================================================
        # CHARTS & ANALYSIS - All Charts from Tab 4
        # =============================================================
        story.append(Paragraph("Charts & Analysis", heading_style))
        
        # Generate and add charts
        charts = create_pdf_charts(results)
        
        if charts:
            story.append(Paragraph("Performance Charts", heading_style))
            
            # Add each chart with description (in order they appear in Charts & Analysis tab)
            chart_descriptions = {
                'cumulative_pnl': 'Cumulative P&L progression showing overall strategy performance over time',
                'pnl_distribution': 'Distribution of individual trade P&L showing frequency of wins and losses',
                'long_vs_short': 'Comparison of total profits from long versus short positions',
                'exit_reasons': 'Breakdown of how trades were closed (stop loss, profit target, market close)',
                'win_loss_by_position': 'Win/Loss count comparison between long and short position types',
                'gross_pnl_distribution': 'Distribution of gross P&L (before transaction costs) per trade',
                'entry_exit_correlation': 'Scatter plot showing relationship between entry and exit prices with profit/loss indicators',
                'monthly_performance': 'Monthly P&L performance showing seasonal patterns and trends'
            }
            
            for chart_name, chart_data in charts.items():
                if chart_name in chart_descriptions:
                    # Add chart description
                    story.append(Paragraph(chart_descriptions[chart_name], styles['Normal']))
                    story.append(Spacer(1, 10))
                    
                    # Create temporary file for chart (keep file open until PDF is built)
                    import tempfile
                    import os
                    
                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    tmp_file.write(chart_data)
                    tmp_file.close()
                    temp_files.append(tmp_file.name)
                    
                    # Add chart to PDF
                    img = Image(tmp_file.name, width=6*inch, height=3.6*inch)
                    story.append(img)
                    story.append(Spacer(1, 20))
        
        # Risk Analysis Table
        story.append(Paragraph("Risk Analysis", heading_style))
        daily_std = summary['daily_volatility']
        risk_data = [
            ['Risk Metric', 'Value'],
            ['Daily Volatility', f"${daily_std:,.2f}"],
            ['95% VaR (Daily)', f"${daily_std * 1.645:,.2f}"],
            ['Max Daily Loss', f"${abs(summary['max_daily_loss']):,.2f}"],
            ['Profitable Days', f"{summary['profitable_days']} ({summary['profitable_days_pct']:.1f}%)"]
        ]
        
        risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(risk_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated with S&P 500 Intraday Momentum Strategy Dashboard", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                import os
                os.unlink(temp_file_path)
            except:
                pass
        
        return pdf_bytes
        
    except ImportError as e:
        # Fallback to simple text if reportlab not available
        return generate_simple_text_report(results, parameters)
    except Exception as e:
        # Error fallback
        return generate_error_report(str(e), results, parameters)

def generate_simple_text_report(results, parameters):
    """Fallback text report if PDF libraries unavailable"""
    buffer = BytesIO()
    summary = results['summary']
    
    text_content = f"""S&P 500 Intraday Momentum Strategy Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STRATEGY PARAMETERS
==================
Symbols: {', '.join(parameters['symbols'])}
Date Range: {parameters['start_date']} to {parameters['end_date']}
Entry Threshold: {parameters['entry_threshold']*10000:.1f} bps
Net P&L: ${summary['total_pnl']:,.2f}
Total Trades: {summary['total_trades']:,}
Win Rate: {summary['win_rate']:.2f}%
Profit Factor: {summary['profit_factor']:.2f}
Sharpe Ratio: {summary['sharpe_ratio']:.3f}

Note: PDF generation requires additional libraries.
This is a simplified text version of the report.
"""
    
    buffer.write(text_content.encode('utf-8'))
    buffer.seek(0)
    return buffer.getvalue()

def generate_error_report(error_msg, results, parameters):
    """Generate error report if PDF generation fails"""
    buffer = BytesIO()
    
    error_content = f"""ERROR REPORT - S&P 500 Strategy
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PDF Generation Error: {error_msg}

Basic Results:
Net P&L: ${results['summary']['total_pnl']:,.2f}
Total Trades: {results['summary']['total_trades']:,}
Win Rate: {results['summary']['win_rate']:.2f}%

Please contact support for assistance with PDF generation.
"""
    
    buffer.write(error_content.encode('utf-8'))
    buffer.seek(0)
    return buffer.getvalue()

def generate_simple_pdf_fallback(results, parameters, buffer):
    """Simple fallback when reportlab is not available"""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'S&P 500 Intraday Momentum Strategy Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Parameters
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Strategy Parameters:', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for key, value in parameters.items():
            if key == 'symbols':
                pdf.cell(0, 8, f"Symbols: {', '.join(value)}", 0, 1)
            else:
                pdf.cell(0, 8, f"{key.replace('_', ' ').title()}: {value}", 0, 1)
        
        pdf.ln(5)
        
        # Performance Summary
        summary = results['summary']
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Performance Summary:', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(0, 8, f"Net P&L: ${summary['total_pnl']:,.2f}", 0, 1)
        pdf.cell(0, 8, f"Total Trades: {summary['total_trades']:,}", 0, 1)
        pdf.cell(0, 8, f"Win Rate: {summary['win_rate']:.2f}%", 0, 1)
        pdf.cell(0, 8, f"Profit Factor: {summary['profit_factor']:.2f}", 0, 1)
        pdf.cell(0, 8, f"Sharpe Ratio: {summary['sharpe_ratio']:.3f}", 0, 1)
        
        # Output to buffer
        pdf_content = pdf.output(dest='S').encode('latin-1')
        buffer.write(pdf_content)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        # Final fallback - plain text
        text_content = f"""S&P 500 Intraday Momentum Strategy Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Strategy Parameters:
{chr(10).join([f'{k}: {v}' for k, v in parameters.items()])}

Performance Summary:
Net P&L: ${results['summary']['total_pnl']:,.2f}
Total Trades: {results['summary']['total_trades']:,}
Win Rate: {results['summary']['win_rate']:.2f}%
Profit Factor: {results['summary']['profit_factor']:.2f}
Sharpe Ratio: {results['summary']['sharpe_ratio']:.3f}
"""
        buffer.write(text_content.encode('utf-8'))
        buffer.seek(0)
        return buffer.getvalue()


# Display results if available
if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']
    summary = results['summary']
    trades_df = results['trades_df']
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Summary", "📈 Performance Analysis", "📋 Reports", "🎯 Charts & Analysis", "📥 Download Report"])
    
    with tab1:
        st.header("Performance Summary")
        
        # Performance Summary Table
        col1, col2 = st.columns([2, 1])
        
        with col1:
            performance_data = {
                "Metric": [
                    "Net P&L", "Gross P&L", "Total Trades", "Win Rate", 
                    "Average P&L per Trade", "Profit Factor", "Sharpe Ratio",
                    "Transaction Costs", "Long Trades", "Short Trades"
                ],
                "Value": [
                    f"${summary['total_pnl']:,.2f}",
                    f"${summary['gross_pnl']:,.2f}",
                    f"{summary['total_trades']:,}",
                    f"{summary['win_rate']:.2f}%",
                    f"${summary['avg_pnl_per_trade']:.2f}",
                    f"{summary['profit_factor']:.2f}",
                    f"{summary['sharpe_ratio']:.3f}",
                    f"${summary['total_transaction_costs']:,.2f}",
                    f"{summary['long_trades']:,} ({summary['long_trades']/summary['total_trades']*100:.1f}%)",
                    f"{summary['short_trades']:,} ({summary['short_trades']/summary['total_trades']*100:.1f}%)"
                ]
            }
            performance_df = pd.DataFrame(performance_data)
            st.dataframe(performance_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(performance_df, "performance_summary")
            
        # Daily Performance Metrics
        st.subheader("Daily Performance Metrics")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            daily_data = {
                "Metric": [
                    "Profitable Days", "Total Trading Days", "Profitable Days %",
                    "Maximum Daily Gain", "Maximum Daily Loss", "Average Daily P&L",
                    "Daily Volatility", "95% VaR (Daily)"
                ],
                "Value": [
                    f"{summary['profitable_days']:,}",
                    f"{summary['total_days']:,}",
                    f"{summary['profitable_days_pct']:.1f}%",
                    f"${summary['max_daily_gain']:,.2f}",
                    f"${summary['max_daily_loss']:,.2f}",
                    f"${summary['avg_daily_pnl']:,.2f}",
                    f"${summary['daily_volatility']:,.2f}",
                    f"${summary['var_95']:,.2f}"
                ]
            }
            daily_df = pd.DataFrame(daily_data)
            st.dataframe(daily_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(daily_df, "daily_performance")
    
    with tab2:
        st.header("Performance Analysis")
        
        # Trade Statistics
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Trade Statistics")
            trade_stats_data = {
                "Metric": [
                    "Winning Trades", "Losing Trades", "Average Winning Trade", 
                    "Average Losing Trade", "Largest Win", "Largest Loss"
                ],
                "Value": [
                    f"{summary['winning_trades']:,}",
                    f"{summary['losing_trades']:,}",
                    f"${summary['avg_winning_trade']:.2f}",
                    f"${summary['avg_losing_trade']:.2f}",
                    f"${trades_df['net_pnl'].max():.2f}",
                    f"${trades_df['net_pnl'].min():.2f}"
                ]
            }
            trade_stats_df = pd.DataFrame(trade_stats_data)
            st.dataframe(trade_stats_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(trade_stats_df, "trade_statistics")
        
        # Exit Reason Breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Risk Management Summary")
            exit_breakdown = trades_df['exit_reason'].value_counts()
            breakdown_data = {
                "Exit Reason": exit_breakdown.index,
                "Count": exit_breakdown.values,
                "Percentage": [f"{(count / len(trades_df)) * 100:.1f}%" for count in exit_breakdown.values]
            }
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(breakdown_df, "exit_reason_breakdown")
        
        # Statistical Significance
        st.subheader("Statistical Analysis")
        
        # Enhanced statistical analysis
        pnl_data = trades_df['net_pnl'].values
        n = len(pnl_data)
        mean_pnl = np.mean(pnl_data)
        std_pnl = np.std(pnl_data, ddof=1)  # Sample standard deviation
        se_pnl = std_pnl / np.sqrt(n)  # Standard error
        
        # T-test against zero
        t_stat = mean_pnl / se_pnl if se_pnl != 0 else 0
        
        # Calculate p-value more carefully
        df = n - 1  # degrees of freedom
        if abs(t_stat) > 8:  # Very large t-statistic
            p_value_str = "< 1e-15"
            p_value_for_calc = 1e-15
        else:
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))  # Two-tailed test
            p_value_for_calc = p_value
            if p_value < 1e-10:
                p_value_str = f"< 1e-10"
            elif p_value < 1e-6:
                p_value_str = f"{p_value:.2e}"
            else:
                p_value_str = f"{p_value:.6f}"
        
        # Effect size (Cohen's d)
        cohens_d = mean_pnl / std_pnl if std_pnl != 0 else 0
        
        # Confidence intervals
        alpha = 0.05  # For 95% CI
        t_critical = stats.t.ppf(1 - alpha/2, df)
        ci_lower = mean_pnl - t_critical * se_pnl
        ci_upper = mean_pnl + t_critical * se_pnl
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            statistical_data = {
                "Statistical Test": [
                    "Sample Size (n)",
                    "Mean P&L per Trade",
                    "Standard Deviation", 
                    "Standard Error",
                    "T-Statistic",
                    "P-Value (two-tailed)",
                    "Degrees of Freedom",
                    "95% Confidence Interval",
                    "Effect Size (Cohen's d)",
                    "Statistical Power"
                ],
                "Value": [
                    f"{n:,}",
                    f"${mean_pnl:.2f}",
                    f"${std_pnl:.2f}",
                    f"${se_pnl:.4f}",
                    f"{t_stat:.3f}",
                    p_value_str,
                    f"{df:,}",
                    f"${ci_lower:.2f} to ${ci_upper:.2f}",
                    f"{cohens_d:.3f}",
                    "> 99.9%" if abs(t_stat) > 3.3 else "> 95%" if abs(t_stat) > 1.96 else "< 80%"
                ],
                "Interpretation": [
                    "Number of trades analyzed",
                    "Average profit per trade",
                    "Variability of trade outcomes",
                    "Precision of mean estimate",
                    "Test statistic for significance",
                    "Probability of observing this if H₀ true",
                    "Sample size - 1",
                    "Range likely to contain true mean",
                    "Large effect (>0.8), Medium (0.5-0.8), Small (<0.5)",
                    "Probability of detecting true effect"
                ]
            }
            statistical_df = pd.DataFrame(statistical_data)
            st.dataframe(statistical_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(statistical_df, "statistical_analysis")
            
        # Interpretation
        if p_value_for_calc < 0.001:
            significance = "✅ Highly Significant (p < 0.001)"
            interpretation = "Very strong evidence that the strategy has a positive edge"
        elif p_value_for_calc < 0.01:
            significance = "✅ Very Significant (p < 0.01)" 
            interpretation = "Strong evidence that the strategy has a positive edge"
        elif p_value_for_calc < 0.05:
            significance = "✅ Significant (p < 0.05)"
            interpretation = "Significant evidence that the strategy has a positive edge"
        else:
            significance = "⚠️ Not Significant (p ≥ 0.05)"
            interpretation = "Insufficient evidence that the strategy has a consistent edge"
            
        st.success(f"**{significance}**")
        st.info(f"**Interpretation**: {interpretation}")
        
        # Additional insights
        if cohens_d > 0.8:
            effect_interpretation = "Very large practical effect"
        elif cohens_d > 0.5:
            effect_interpretation = "Large practical effect"
        elif cohens_d > 0.2:
            effect_interpretation = "Medium practical effect"
        else:
            effect_interpretation = "Small practical effect"
            
        st.info(f"**Effect Size**: {effect_interpretation} (Cohen's d = {cohens_d:.3f})")

    with tab3:
        st.header("Comprehensive Reports")
        
        # Long/Short Exposure Analysis
        st.subheader("Long/Short Exposure Analysis")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            long_short_data = {
                "Position Type": ["Long Trades", "Short Trades"],
                "Count": [summary['long_trades'], summary['short_trades']],
                "Percentage": [
                    f"{(summary['long_trades']/summary['total_trades']*100):.1f}%",
                    f"{(summary['short_trades']/summary['total_trades']*100):.1f}%"
                ],
                "Net P&L": [
                    f"${trades_df[trades_df['type'] == 'LONG']['net_pnl'].sum():.2f}",
                    f"${trades_df[trades_df['type'] == 'SHORT']['net_pnl'].sum():.2f}"
                ],
                "Avg P&L": [
                    f"${trades_df[trades_df['type'] == 'LONG']['net_pnl'].mean():.2f}",
                    f"${trades_df[trades_df['type'] == 'SHORT']['net_pnl'].mean():.2f}"
                ]
            }
            long_short_df = pd.DataFrame(long_short_data)
            st.dataframe(long_short_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(long_short_df, "long_short_analysis")
        
        # Transaction Cost Analysis
        st.subheader("Transaction Cost Analysis")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            cost_data = {
                "Scenario": ["Current", "+20% Increase", "+50% Increase", "Double Costs"],
                "Cost per Trade": [
                    f"${transaction_cost:.3f}",
                    f"${transaction_cost * 1.2:.3f}",
                    f"${transaction_cost * 1.5:.3f}",
                    f"${transaction_cost * 2:.3f}"
                ],
                "Total Costs": [
                    f"${summary['total_transaction_costs']:.2f}",
                    f"${summary['total_transaction_costs'] * 1.2:.2f}",
                    f"${summary['total_transaction_costs'] * 1.5:.2f}",
                    f"${summary['total_transaction_costs'] * 2:.2f}"
                ],
                "Net P&L": [
                    f"${summary['total_pnl']:.2f}",
                    f"${summary['total_pnl'] - (summary['total_transaction_costs'] * 0.2):.2f}",
                    f"${summary['total_pnl'] - (summary['total_transaction_costs'] * 0.5):.2f}",
                    f"${summary['total_pnl'] - summary['total_transaction_costs']:.2f}"
                ],
                "Impact": [
                    "Baseline",
                    f"{-((summary['total_transaction_costs'] * 0.2) / summary['total_pnl'] * 100):.2f}%",
                    f"{-((summary['total_transaction_costs'] * 0.5) / summary['total_pnl'] * 100):.2f}%",
                    f"{-(summary['total_transaction_costs'] / summary['total_pnl'] * 100):.2f}%"
                ]
            }
            cost_df = pd.DataFrame(cost_data)
            st.dataframe(cost_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(cost_df, "transaction_cost_analysis")
        
        # Risk Management Analysis - Daily VaR
        st.subheader("Risk Management Analysis - Value at Risk (VaR)")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Calculate VaR components
            daily_std = summary['daily_volatility']
            var_90 = daily_std * 1.282  # 90% confidence
            var_95 = daily_std * 1.645  # 95% confidence  
            var_99 = daily_std * 2.326  # 99% confidence
            
            var_data = {
                "Risk Metric": [
                    "Daily P&L Standard Deviation",
                    "1-Day VaR (90% confidence)", 
                    "1-Day VaR (95% confidence)",
                    "1-Day VaR (99% confidence)",
                    "Maximum Historical Daily Loss",
                    "VaR as % of Average Daily P&L"
                ],
                "Value": [
                    f"${daily_std:,.2f}",
                    f"${var_90:,.2f}",
                    f"${var_95:,.2f}",
                    f"${var_99:,.2f}",
                    f"${abs(summary['max_daily_loss']):,.2f}",
                    f"{(var_95/abs(summary['avg_daily_pnl'])*100):.1f}%" if summary['avg_daily_pnl'] != 0 else "N/A"
                ],
                "Calculation": [
                    "√(Σ(daily_pnl - mean)²/(n-1))",
                    "1.282 × Daily Std Dev",
                    "1.645 × Daily Std Dev", 
                    "2.326 × Daily Std Dev",
                    "Historical minimum",
                    "95% VaR / Avg Daily P&L"
                ]
            }
            var_df = pd.DataFrame(var_data)
            st.dataframe(var_df, hide_index=True, use_container_width=True)
            
        with col2:
            create_download_csv(var_df, "risk_analysis_var")
            
        st.info(f"**VaR Interpretation**: With 95% confidence, daily losses should not exceed ${var_95:,.2f}")

        # Monthly Performance Breakdown
        if 'date' in trades_df.columns:
            monthly_trades = trades_df.copy()
            monthly_trades['month'] = pd.to_datetime(monthly_trades['date']).dt.to_period('M')
            monthly_summary = monthly_trades.groupby('month').agg({
                'net_pnl': ['sum', 'mean', 'count'],
                'gross_pnl': 'sum',
                'transaction_cost': 'sum'
            }).round(2)
            
            st.subheader("Monthly Performance Breakdown")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                monthly_data = []
                for month in monthly_summary.index:
                    monthly_data.append({
                        "Month": str(month),
                        "Net P&L": f"${monthly_summary.loc[month, ('net_pnl', 'sum')]:.2f}",
                        "Gross P&L": f"${monthly_summary.loc[month, ('gross_pnl', 'sum')]:.2f}",
                        "Trades": int(monthly_summary.loc[month, ('net_pnl', 'count')]),
                        "Avg Daily P&L": f"${monthly_summary.loc[month, ('net_pnl', 'mean')]:.2f}",
                        "Transaction Costs": f"${monthly_summary.loc[month, ('transaction_cost', 'sum')]:.2f}"
                    })
                
                monthly_df = pd.DataFrame(monthly_data)
                st.dataframe(monthly_df, hide_index=True, use_container_width=True)
                
            with col2:
                create_download_csv(monthly_df, "monthly_performance")

    with tab4:
        st.header("Charts & Analysis")
        
        st.markdown("""
        **Chart Explanations:**
        - **Cumulative P&L**: Shows the running total of profits/losses over time, indicating overall strategy performance
        - **Trade P&L Distribution**: Histogram showing the frequency of different profit/loss amounts per trade
        - **Long vs Short P&L**: Compares total profits from long positions vs short positions
        - **Exit Reason Breakdown**: Pie chart showing how trades ended (stop loss, profit target, or market close)
        - **Win/Loss by Position Type**: Bar chart comparing winning vs losing trades for long and short positions
        - **Monthly P&L**: Bar chart showing monthly performance trends
        """)
        
        # Enhanced individual charts with better labeling
        st.subheader("Cumulative P&L Over Time")
        cumulative_pnl = trades_df['net_pnl'].cumsum()
        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Scatter(
            x=list(range(len(cumulative_pnl))),
            y=cumulative_pnl,
            mode='lines',
            name='Cumulative P&L',
            line=dict(color='green', width=3),
            hovertemplate='Trade #: %{x}<br>Cumulative P&L: $%{y:,.2f}<extra></extra>'
        ))
        fig_cumulative.update_layout(
            title="Strategy Performance: Cumulative Profit & Loss",
            xaxis_title="Trade Number (Sequential)",
            yaxis_title="Cumulative P&L (USD)",
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig_cumulative, use_container_width=True)
        
        # Create and display the comprehensive chart
        fig = create_interactive_charts(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Trade data export
        st.subheader("Trade Data Export")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**Recent Trades (First 100)**")
            display_trades = trades_df.head(100).copy()
            display_trades['date'] = pd.to_datetime(display_trades['date']).dt.strftime('%Y-%m-%d %H:%M')
            display_trades = display_trades.round(2)
            st.dataframe(display_trades, hide_index=True, use_container_width=True)
        
        with col2:
            st.write("**Export Options**")
            
            # All trades CSV download
            csv_data = trades_df.to_csv(index=False)
            st.download_button(
                label="📥 Download All Trades (CSV)",
                data=csv_data,
                file_name=f"sp500_strategy_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download complete trade data as CSV file"
            )
            
            st.info(f"Total trades available: {len(trades_df):,}")

    with tab5:
        st.header("Download Report")
        
        # Current Report Section
        if 'results' in st.session_state and st.session_state['results']:
            st.subheader("📄 Current Analysis Report")
            
            # Prepare parameters for PDF generation
            parameters = {
                'symbols': my_symbols,
                'start_date': str(start_date),
                'end_date': str(end_date),
                'frequency': frequency,
                'entry_threshold': entry_threshold,
                'stop_loss': stop_loss,
                'profit_target': profit_target,
                'transaction_cost': transaction_cost,
                'tick_value': tick_value
            }
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Current Run Summary:**")
                st.write(f"• Symbols: {', '.join(parameters['symbols'])}")
                st.write(f"• Date Range: {parameters['start_date']} to {parameters['end_date']}")
                st.write(f"• Entry Threshold: {parameters['entry_threshold']*10000:.1f} bps")
                st.write(f"• Net P&L: ${summary['total_pnl']:,.2f}")
                st.write(f"• Total Trades: {summary['total_trades']:,}")
                st.write(f"• Win Rate: {summary['win_rate']:.2f}%")
                
            with col2:
                # PDF Download Button for current results
                try:
                    pdf_data = generate_pdf_report(results, parameters)
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_data,
                        file_name=f"sp500_strategy_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        help="Download comprehensive PDF report with charts and analysis",
                        use_container_width=True
                    )
                    st.success("✅ PDF ready for download")
                    
                except Exception as e:
                    st.error(f"❌ PDF generation failed: {str(e)}")
                    st.info("📋 Note: PDF generation requires reportlab and matplotlib libraries")
        
        # Report History Section
        st.subheader("📋 Report History")
        
        if len(st.session_state.report_history) > 0:
            st.write(f"**{len(st.session_state.report_history)} previous runs available:**")
            
            # Create a table of all previous runs
            history_data = []
            for i, entry in enumerate(st.session_state.report_history):
                params = entry['parameters']
                summary_data = entry['results_summary']
                
                history_data.append({
                    'Run #': i + 1,
                    'Timestamp': entry['timestamp'].strftime('%Y-%m-%d %H:%M'),
                    'Symbols': ', '.join(params['symbols']),
                    'Date Range': f"{params['start_date']} to {params['end_date']}",
                    'Entry Threshold (bps)': f"{params['entry_threshold']*10000:.1f}",
                    'Stop Loss (bps)': f"{params['stop_loss']*10000:.1f}",
                    'Profit Target (bps)': f"{params['profit_target']*10000:.1f}",
                    'Net P&L': f"${summary_data['total_pnl']:,.2f}",
                    'Total Trades': f"{summary_data['total_trades']:,}",
                    'Win Rate %': f"{summary_data['win_rate']:.2f}",
                    'Profit Factor': f"{summary_data['profit_factor']:.2f}",
                    'Sharpe Ratio': f"{summary_data['sharpe_ratio']:.3f}"
                })
            
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, hide_index=True, use_container_width=True)
            
            # Download options for history
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Select a previous run to download its report:**")
                
                # Create selection dropdown
                run_options = []
                for i, entry in enumerate(st.session_state.report_history):
                    params = entry['parameters']
                    summary_data = entry['results_summary']
                    option_text = f"Run #{i+1}: {entry['timestamp'].strftime('%Y-%m-%d %H:%M')} - {', '.join(params['symbols'])} - P&L: ${summary_data['total_pnl']:,.2f}"
                    run_options.append((i, option_text))
                
                if run_options:
                    selected_run_idx = st.selectbox(
                        "Choose a run:",
                        options=[idx for idx, _ in run_options],
                        format_func=lambda idx: run_options[idx][1],
                        key="history_run_selector"
                    )
                    
            with col2:
                st.write("**Download Selected Run:**")
                
                if run_options and selected_run_idx is not None:
                    selected_entry = st.session_state.report_history[selected_run_idx]
                    
                    try:
                        # Generate PDF for selected historical run
                        historical_pdf_data = generate_pdf_report(
                            selected_entry['results'], 
                            selected_entry['parameters']
                        )
                        
                        st.download_button(
                            label=f"📥 Download Run #{selected_run_idx + 1}",
                            data=historical_pdf_data,
                            file_name=f"sp500_strategy_run_{selected_run_idx + 1}_{selected_entry['timestamp'].strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            help=f"Download report for run #{selected_run_idx + 1}",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"Error generating historical report: {str(e)}")
            
            # Option to clear history
            st.write("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("**Manage History:**")
            with col2:
                if st.button("🗑️ Clear History", help="Clear all saved reports"):
                    st.session_state.report_history = []
                    st.success("History cleared!")
                    st.rerun()
            
            # Export all history as CSV
            if st.button("📊 Export History as CSV", use_container_width=True):
                history_csv = history_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download History CSV",
                    data=history_csv,
                    file_name=f"sp500_strategy_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    key="history_csv_download"
                )
                
        else:
            st.info("📝 No previous runs saved yet. Run the strategy with different parameters to build your report history!")
            st.write("**Report history will include:**")
            st.write("• All parameter combinations you've tested")
            st.write("• Performance results for each run")  
            st.write("• Ability to download reports from any previous run")
            st.write("• Comparison table of all your experiments")

else:
    st.info("👈 Configure parameters in the sidebar and click 'Run Strategy' to start the analysis.")

# Footer
st.markdown("---")
st.markdown("**S&P 500 Intraday Momentum Strategy Dashboard** | Built with Streamlit")
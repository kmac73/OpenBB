"""
SPX CFD Backtest Application - Phase 3 Implementation
Professional Streamlit interface for SPX CFD backtesting with 2bps trigger strategy
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from pathlib import Path
import sys
import time

# Add common directory to path for imports
sys.path.append(str(Path(__file__).parent / "common"))

from cfd_engine import CFDTradingEngine
from backtest_analyzer import BacktestAnalyzer  
from market_data import Retrieve
from pdf_generator import SPXBacktestPDFGenerator
from error_handler import JupyterStyleErrorHandler
from performance_timer import PerformanceTimer
from ui_helpers import (
    StreamlitProgressTracker, validate_parameters, 
    create_parameter_summary, ParameterPresets, 
    add_parameter_presets_to_sidebar
)

# Page configuration
st.set_page_config(
    page_title="SPX CFD Backtest System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def auto_detect_date_range(frequency: str):
    """Auto-detect available date ranges from data file"""
    try:
        project_root = Path(__file__).parent.parent
        filepath = project_root / "market_data" / "historical" / "SPX" / f"{frequency}.txt"
        
        if not filepath.exists():
            return date(2024, 6, 24), date(2024, 6, 28)  # Fallback dates
            
        # Read first and last lines efficiently
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()
            
            # Seek to end and find last line
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(max(file_size - 1024, 0))
            lines = f.readlines()
            last_line = lines[-1].strip()
            
        start_date = pd.to_datetime(first_line.split(',')[0]).date()
        end_date = pd.to_datetime(last_line.split(',')[0]).date()
        
        return start_date, end_date
        
    except Exception as e:
        st.error(f"Error detecting date range: {e}")
        return date(2024, 6, 24), date(2024, 6, 28)

def setup_sidebar():
    """Enhanced parameter sidebar with text box editing for all CFD parameters"""
    st.sidebar.title("🎯 CFD Strategy Parameters")
    
    # Data Settings Section
    st.sidebar.subheader("📊 Data Settings")
    
    frequency = st.sidebar.selectbox(
        "Data Frequency",
        ["1M", "5M", "30M", "1H", "1D"],
        index=1,  # Default to 5M
        help="Higher frequency provides more detailed analysis but longer processing time"
    )
    
    # Auto-detect date range
    available_start, available_end = auto_detect_date_range(frequency)
    
    # Default to single day for debugging
    default_start = available_end - timedelta(days=1)
    default_end = available_end
    
    start_date = st.sidebar.date_input(
        "Start Date",
        value=default_start,
        min_value=available_start,
        max_value=available_end,
        help="Beginning of backtest period"
    )
    
    end_date = st.sidebar.date_input(
        "End Date", 
        value=default_end,
        min_value=available_start,
        max_value=available_end,
        help="End of backtest period"
    )
    
    # Validate date range
    if start_date >= end_date:
        st.sidebar.error("❌ End date must be after start date")
        return None
    
    st.sidebar.markdown("---")
    
    # Risk & Position Sizing Section
    st.sidebar.subheader("💰 Risk & Position Sizing")
    
    account_balance = st.sidebar.text_input(
        "Account Balance ($)",
        value="10000.0",
        help="Starting account balance for backtesting"
    )
    
    risk_pct = st.sidebar.text_input(
        "Account Risk per Trade (%)",
        value="2.0",
        help="Percentage of account balance risked per trade"
    )
    
    initial_stop_loss = st.sidebar.text_input(
        "Initial Stop-Loss Distance ($)",
        value="50.0",
        help="Distance from entry price for initial stop loss (always from 9:30 open)"
    )
    
    st.sidebar.markdown("**Calculated Values:**")
    try:
        acc_bal = float(account_balance)
        risk_pct_val = float(risk_pct)
        stop_loss_dist = float(initial_stop_loss)
        
        risk_per_trade = acc_bal * (risk_pct_val / 100)
        risk_per_contract = stop_loss_dist  # Risk per contract is the stop loss distance
        position_size = risk_per_trade / risk_per_contract if risk_per_contract > 0 else 0
        
        st.sidebar.write(f"Risk per Trade ($): ${risk_per_trade:.2f}")
        st.sidebar.write(f"Risk per Contract ($): ${risk_per_contract:.2f}")
        st.sidebar.write(f"Position Size (CFDs): {position_size:.4f}")
    except ValueError:
        st.sidebar.error("Please enter valid numbers above")
    
    st.sidebar.markdown("---")
    
    # Trade Setup Section  
    st.sidebar.subheader("⚙️ Trade Setup")
    
    margin_rate = st.sidebar.text_input(
        "Margin Rate (%)",
        value="5.0",
        help="CFD margin requirement as percentage"
    )
    
    st.sidebar.markdown("**Calculated Values:**")
    try:
        margin_rate_val = float(margin_rate)
        leverage_ratio = 100 / margin_rate_val if margin_rate_val > 0 else 0
        
        # These will be calculated during actual trade entry
        st.sidebar.write(f"Leverage Ratio: {leverage_ratio:.2f}x")
        st.sidebar.write("Notional Position Value: (calculated at entry)")
        st.sidebar.write("Margin Required: (calculated at entry)")
    except ValueError:
        st.sidebar.error("Please enter valid margin rate")
    
    st.sidebar.markdown("---")
    
    # Scenario Analysis Section
    st.sidebar.subheader("📈 Scenario Analysis")
    
    risk_reward_ratio = st.sidebar.text_input(
        "Risk/Reward Ratio",
        value="2.0",
        help="Profit target as multiple of risk (2.0 = 2:1 reward:risk)"
    )
    
    trailing_stop_pct = st.sidebar.text_input(
        "Trailing Stop Percentage (%)",
        value="2.0",
        help="Trailing stop percentage for profit protection"
    )
    
    transaction_cost = st.sidebar.text_input(
        "Round Trip Transaction Cost ($)",
        value="5.0",
        help="Total cost for entering and exiting position"
    )
    
    st.sidebar.markdown("**Calculated Values:**")
    try:
        rr_ratio = float(risk_reward_ratio)
        stop_dist = float(initial_stop_loss)
        profit_target_dist = stop_dist * rr_ratio
        
        st.sidebar.write(f"Profit Target Distance ($): ${profit_target_dist:.2f}")
        st.sidebar.write("Active Trailing Stop: (calculated during trade)")
        st.sidebar.write("Final Exit Price: (determined at exit)")
    except ValueError:
        st.sidebar.error("Please enter valid risk/reward ratio")
    
    st.sidebar.markdown("---")
    
    # Final Results Section (for display only)
    st.sidebar.subheader("📊 Final Results")
    st.sidebar.write("Gross Profit/Loss: (calculated at exit)")
    st.sidebar.write("Net Profit: (calculated at exit)")
    st.sidebar.write("Return on Margin: (calculated at exit)")
    
    st.sidebar.markdown("---")
    
    # Additional Parameters
    st.sidebar.subheader("🔧 Additional Parameters")
    
    risk_free_rate = st.sidebar.text_input(
        "Risk-Free Rate (%)",
        value="3.0",
        help="Risk-free rate for Sharpe ratio calculation"
    )
    
    # Convert all parameters to proper types
    try:
        parameters = {
            'frequency': frequency,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'account_balance': float(account_balance),
            'risk_pct': float(risk_pct),
            'transaction_cost': float(transaction_cost),
            'stop_loss_distance': float(initial_stop_loss),
            'risk_reward_ratio': float(risk_reward_ratio),
            'trailing_stop_pct': float(trailing_stop_pct),
            'margin_rate': float(margin_rate),
            'risk_free_rate': float(risk_free_rate)
        }
        
        # Validate parameters
        errors, warnings = validate_parameters(parameters)
        
        # Display validation results
        if errors:
            for error in errors:
                st.sidebar.error(f"❌ {error}")
        
        if warnings:
            for warning in warnings:
                st.sidebar.warning(f"⚠️ {warning}")
        
        return parameters if not errors else None
        
    except ValueError as e:
        st.sidebar.error(f"❌ Invalid parameter values: {str(e)}")
        return None

def create_basic_charts(results):
    """Create basic performance charts"""
    if not results or 'daily_summaries' not in results:
        return None, None
        
    daily_summaries = results['daily_summaries']
    
    # Daily P&L Chart
    dates = [summary['date'] for summary in daily_summaries]
    daily_pnl = [summary.get('daily_net_pnl', 0) for summary in daily_summaries]
    cumulative_pnl = pd.Series(daily_pnl).cumsum()
    
    pnl_fig = go.Figure()
    pnl_fig.add_trace(go.Scatter(
        x=dates, 
        y=cumulative_pnl,
        mode='lines',
        name='Cumulative P&L',
        line=dict(color='#00CC96' if cumulative_pnl.iloc[-1] >= 0 else '#FF6B6B', width=2)
    ))
    
    pnl_fig.update_layout(
        title="Cumulative P&L Performance",
        xaxis_title="Date",
        yaxis_title="Cumulative P&L ($)",
        template="plotly_white",
        height=400
    )
    
    # Equity Curve
    starting_balance = results.get('parameters', {}).get('account_balance', 10000)
    equity_curve = starting_balance + cumulative_pnl
    
    equity_fig = go.Figure()
    equity_fig.add_trace(go.Scatter(
        x=dates,
        y=equity_curve, 
        mode='lines',
        name='Account Equity',
        line=dict(color='#1f77b4', width=2),
        fill='tonexty' if equity_curve.iloc[-1] >= starting_balance else None
    ))
    
    # Add starting balance line
    equity_fig.add_hline(
        y=starting_balance, 
        line_dash="dash", 
        line_color="gray",
        annotation_text="Starting Balance"
    )
    
    equity_fig.update_layout(
        title="Account Equity Curve", 
        xaxis_title="Date",
        yaxis_title="Account Value ($)",
        template="plotly_white",
        height=400
    )
    
    return pnl_fig, equity_fig

def display_performance_metrics(metrics):
    """Display all 22 performance metrics in organized sections"""
    if not metrics:
        return
        
    # Organize metrics into sections
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Basic Metrics")
        st.metric("Total Trades", f"{metrics.get('total_trades', 0):,}")
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
        st.metric("Winning Trades", f"{metrics.get('winning_trades', 0):,}")
        st.metric("Losing Trades", f"{metrics.get('losing_trades', 0):,}")
        
        st.markdown("**Direction Split:**")
        st.write(f"• Long Trades: {metrics.get('total_long_trades', 0):,}")
        st.write(f"• Short Trades: {metrics.get('total_short_trades', 0):,}")
    
    with col2:
        st.subheader("💰 P&L Metrics") 
        total_pnl = metrics.get('total_pnl', 0)
        st.metric(
            "Total P&L", 
            f"${total_pnl:,.2f}",
            delta=f"{((total_pnl / 10000) * 100):.2f}% of account" if total_pnl else None
        )
        st.metric("Gross P&L", f"${metrics.get('gross_pnl', 0):,.2f}")
        st.metric("Total Costs", f"${metrics.get('total_costs', 0):,.2f}")
        st.metric("Average Win", f"${metrics.get('avg_win', 0):,.2f}")
        st.metric("Average Loss", f"${metrics.get('avg_loss', 0):,.2f}")
    
    with col3:
        st.subheader("⚡ Risk & Performance")
        st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2f}%")
        st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.3f}")
        st.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
        st.metric("VaR (95%, 1-day)", f"${metrics.get('value_at_risk', 0):,.2f}")
        
        st.markdown("**Additional Metrics:**")
        st.write(f"• Avg Drawdown: {metrics.get('avg_drawdown', 0):.2f}%") 
        st.write(f"• Cost Ratio: {metrics.get('cost_ratio', 0):.3f}")
    
    # Duration and Return Metrics
    st.markdown("---")
    col4, col5 = st.columns(2)
    
    with col4:
        st.subheader("⏱️ Duration Metrics")
        st.write(f"**Shortest Trade:** {metrics.get('shortest_trade_minutes', 0)} minutes")
        st.write(f"**Longest Trade:** {metrics.get('longest_trade_minutes', 0)} minutes") 
        st.write(f"**Average Duration:** {metrics.get('avg_trade_duration_minutes', 0):.1f} minutes")
    
    with col5:
        st.subheader("📈 Return Metrics")
        st.write(f"**Total Return:** {metrics.get('total_return', 0):.2f}%")
        st.write(f"**Final Equity:** ${metrics.get('final_equity', 0):,.2f}")

def display_detailed_trade_analysis(trades):
    """Display comprehensive trade-by-trade analysis"""
    if not trades:
        st.info("No trades to analyze")
        return
    
    st.subheader("🔍 Detailed Trade Analysis")
    st.markdown(f"**Complete analysis of all {len(trades)} trades executed:**")
    
    # Create detailed trade data
    trade_data = []
    for i, trade in enumerate(trades, 1):
        # Calculate trade profit/loss percentage
        if trade.direction == "LONG":
            pnl_pct = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100 if trade.exit_price else 0
        else:  # SHORT
            pnl_pct = ((trade.entry_price - trade.exit_price) / trade.entry_price) * 100 if trade.exit_price else 0
        
        # Format duration
        duration_str = f"{trade.duration_minutes}min" if hasattr(trade, 'duration_minutes') else "N/A"
        if hasattr(trade, 'duration_minutes') and trade.duration_minutes >= 60:
            hours = trade.duration_minutes / 60
            duration_str = f"{hours:.1f}h"
        
        trade_data.append({
            '#': i,
            'Direction': f"{'🔴 SHORT' if trade.direction == 'SHORT' else '🟢 LONG'}",
            'Entry Time': trade.entry_time.strftime('%Y-%m-%d %H:%M:%S') if trade.entry_time else 'N/A',
            'Entry Price': f"${trade.entry_price:.2f}",
            'Exit Time': trade.exit_time.strftime('%Y-%m-%d %H:%M:%S') if trade.exit_time else 'Open',
            'Exit Price': f"${trade.exit_price:.2f}" if trade.exit_price else "Open",
            'Stop Loss': f"${trade.stop_loss:.2f}",
            'Profit Target': f"${trade.profit_target:.2f}",
            'Position Size': f"{trade.position_size:.2f}",
            'Duration': duration_str,
            'Gross P&L': f"${trade.gross_pnl:.2f}" if hasattr(trade, 'gross_pnl') else "N/A",
            'Net P&L': f"${trade.net_pnl:.2f}" if hasattr(trade, 'net_pnl') else "N/A",
            'P&L %': f"{pnl_pct:+.3f}%",
            'Costs': f"${trade.costs:.2f}",
            'Exit Reason': getattr(trade, 'exit_reason', 'N/A')
        })
    
    # Display as DataFrame
    df = pd.DataFrame(trade_data)
    
    # Color code the DataFrame based on P&L
    def highlight_pnl(row):
        if 'Net P&L' in row and row['Net P&L'] != 'N/A':
            pnl_value = float(row['Net P&L'].replace('$', '').replace(',', ''))
            if pnl_value > 0:
                return ['background-color: rgba(0, 255, 0, 0.1)'] * len(row)
            elif pnl_value < 0:
                return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)
        return [''] * len(row)
    
    # Display the styled dataframe
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Trade summary
    winning_trades = [t for t in trades if hasattr(t, 'net_pnl') and t.net_pnl > 0]
    losing_trades = [t for t in trades if hasattr(t, 'net_pnl') and t.net_pnl < 0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Winning Trades", len(winning_trades), delta=f"{len(winning_trades)/len(trades)*100:.1f}%")
    with col2:
        st.metric("Losing Trades", len(losing_trades), delta=f"{len(losing_trades)/len(trades)*100:.1f}%")
    with col3:
        avg_win = sum(t.net_pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        st.metric("Avg Win", f"${avg_win:.2f}")
    with col4:
        avg_loss = sum(t.net_pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        st.metric("Avg Loss", f"${avg_loss:.2f}")
    
    # Trade execution insights
    st.markdown("### 📋 Trade Execution Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**🎯 Entry Analysis:**")
        long_trades = [t for t in trades if t.direction == "LONG"]
        short_trades = [t for t in trades if t.direction == "SHORT"]
        st.write(f"• Long entries: {len(long_trades)} trades")
        st.write(f"• Short entries: {len(short_trades)} trades")
        st.write(f"• Direction balance: {len(long_trades)/len(trades)*100:.1f}% Long, {len(short_trades)/len(trades)*100:.1f}% Short")
    
    with insights_col2:
        st.markdown("**⏰ Exit Analysis:**")
        exit_reasons = {}
        for trade in trades:
            reason = getattr(trade, 'exit_reason', 'Unknown')
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
        
        for reason, count in exit_reasons.items():
            st.write(f"• {reason}: {count} trades ({count/len(trades)*100:.1f}%)")
    
    # Performance by direction
    if long_trades and short_trades:
        st.markdown("### 📊 Performance by Direction")
        
        long_pnl = sum(getattr(t, 'net_pnl', 0) for t in long_trades)
        short_pnl = sum(getattr(t, 'net_pnl', 0) for t in short_trades)
        long_wins = sum(1 for t in long_trades if getattr(t, 'net_pnl', 0) > 0)
        short_wins = sum(1 for t in short_trades if getattr(t, 'net_pnl', 0) > 0)
        
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.markdown("**🟢 Long Trades:**")
            st.write(f"• Total P&L: ${long_pnl:.2f}")
            st.write(f"• Win Rate: {long_wins/len(long_trades)*100:.1f}% ({long_wins}/{len(long_trades)})")
            st.write(f"• Avg P&L: ${long_pnl/len(long_trades):.2f}")
        
        with perf_col2:
            st.markdown("**🔴 Short Trades:**")
            st.write(f"• Total P&L: ${short_pnl:.2f}")
            st.write(f"• Win Rate: {short_wins/len(short_trades)*100:.1f}% ({short_wins}/{len(short_trades)})")
            st.write(f"• Avg P&L: ${short_pnl/len(short_trades):.2f}")

def create_trade_execution_chart(data, trades):
    """Create trade execution visualization chart with entry/exit points"""
    if not trades or data.empty:
        st.info("No trades or price data available for visualization")
        return None
    
    st.subheader("📊 Trade Execution Visualization")
    st.markdown("**Price action with entry/exit points for all trades:**")
    
    # Create the main price chart
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['close'],
        mode='lines',
        name='SPX Price',
        line=dict(color='#1f77b4', width=1.5),
        opacity=0.8
    ))
    
    # Color palette for trades
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    # Add trade markers
    for i, trade in enumerate(trades):
        color = colors[i % len(colors)]
        trade_alpha = 0.8
        
        # Entry marker
        if trade.entry_time and trade.entry_price:
            marker_symbol = 'triangle-up' if trade.direction == 'LONG' else 'triangle-down'
            marker_color = '#00CC96' if trade.direction == 'LONG' else '#FF6B6B'
            
            fig.add_trace(go.Scatter(
                x=[trade.entry_time],
                y=[trade.entry_price],
                mode='markers',
                name=f'Trade {i+1} Entry ({trade.direction})',
                marker=dict(
                    symbol=marker_symbol,
                    size=12,
                    color=marker_color,
                    line=dict(width=2, color='white')
                ),
                opacity=trade_alpha,
                hovertemplate=f'<b>Trade {i+1} Entry</b><br>' +
                             f'Direction: {trade.direction}<br>' +
                             f'Time: %{{x}}<br>' +
                             f'Price: ${trade.entry_price:.2f}<br>' +
                             f'Position: {trade.position_size:.2f}<extra></extra>'
            ))
        
        # Exit marker
        if trade.exit_time and trade.exit_price:
            exit_symbol = 'triangle-down' if trade.direction == 'LONG' else 'triangle-up'
            # Color based on profitability
            pnl = getattr(trade, 'net_pnl', 0)
            exit_color = '#00CC96' if pnl > 0 else '#FF6B6B'
            
            fig.add_trace(go.Scatter(
                x=[trade.exit_time],
                y=[trade.exit_price],
                mode='markers',
                name=f'Trade {i+1} Exit ({"WIN" if pnl > 0 else "LOSS"})',
                marker=dict(
                    symbol=exit_symbol,
                    size=12,
                    color=exit_color,
                    line=dict(width=2, color='white')
                ),
                opacity=trade_alpha,
                hovertemplate=f'<b>Trade {i+1} Exit</b><br>' +
                             f'Direction: {trade.direction}<br>' +
                             f'Time: %{{x}}<br>' +
                             f'Price: ${trade.exit_price:.2f}<br>' +
                             f'P&L: ${pnl:.2f}<br>' +
                             f'Exit: {getattr(trade, "exit_reason", "N/A")}<extra></extra>'
            ))
            
            # Connect entry and exit with a line
            if trade.entry_time and trade.entry_price:
                fig.add_trace(go.Scatter(
                    x=[trade.entry_time, trade.exit_time],
                    y=[trade.entry_price, trade.exit_price],
                    mode='lines',
                    name=f'Trade {i+1} Path',
                    line=dict(
                        color=color,
                        width=2,
                        dash='dot'
                    ),
                    opacity=0.5,
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    # Update layout
    fig.update_layout(
        title=f"SPX Price Action with {len(trades)} Trade Executions",
        xaxis_title="Time",
        yaxis_title="SPX Price ($)",
        template="plotly_white",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    # Add range selector
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="7D", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig

def main():
    """Main Streamlit application"""
    # Header
    st.title("📈 SPX CFD Backtest System")
    st.markdown("**Professional 2 Basis Point Trigger Strategy Analysis**")
    st.markdown("---")
    
    # Sidebar parameters
    parameters = setup_sidebar()
    if not parameters:
        st.error("Please fix parameter validation errors in the sidebar")
        return
    
    # Main content area
    if st.sidebar.button("🚀 Run Backtest", type="primary", use_container_width=True):
        
        # Enhanced progress tracking
        progress_tracker = StreamlitProgressTracker()
        progress_tracker.initialize("Initializing backtest...")
        
        try:
            # Initialize error handler and timer
            error_handler = JupyterStyleErrorHandler()
            timer = PerformanceTimer()
            timer.start_backtest()
            
            # Step 1: Load data
            progress_tracker.update(
                10, 
                "Loading market data...",
                f"📊 Loading {parameters['frequency']} data from {parameters['start_date']} to {parameters['end_date']}"
            )
            
            data = Retrieve.from_file(
                ['SPX'], 
                parameters['start_date'],
                parameters['end_date'],
                parameters['frequency']
            )
            
            if data.empty:
                progress_tracker.error("No data found for selected date range and frequency")
                return
            
            progress_tracker.update(30, f"Loaded {len(data)} data points...", f"✅ Successfully loaded {len(data):,} data points")
            
            # Step 2: Initialize trading engine
            progress_tracker.update(40, "Initializing trading engine...", "🔧 Setting up CFD trading engine with parameters")
            
            engine = CFDTradingEngine(**parameters)
            
            # Step 3: Run backtest
            progress_tracker.update(50, "Running backtest simulation...", f"🚀 Processing {len(data):,} market ticks")
            
            # Process each tick
            total_ticks = len(data)
            for idx, (_, row) in enumerate(data.iterrows()):
                if idx % 100 == 0:  # Update progress every 100 ticks for better performance
                    progress = 50 + int((idx / total_ticks) * 40)
                    progress_tracker.update(
                        progress, 
                        f"Processing tick {idx+1:,}/{total_ticks:,}",
                        f"⚡ Simulation running - {((idx+1)/total_ticks)*100:.1f}% complete"
                    )
                
                tick_data = {
                    'open': row['open'],
                    'high': row['high'], 
                    'low': row['low'],
                    'close': row['close']
                }
                
                engine.process_market_tick(row['date'], tick_data)
            
            progress_tracker.update(90, "Analyzing performance...", f"📊 Calculating metrics for {len(engine.all_trades)} trades")
            
            # Step 4: Analyze results
            analyzer = BacktestAnalyzer(risk_free_rate=parameters['risk_free_rate']/100)
            
            # Get daily summaries
            daily_summaries = []
            current_date = None
            daily_trades = []
            
            for trade in engine.all_trades:
                trade_date = trade.entry_time.date()
                if current_date is None:
                    current_date = trade_date
                elif trade_date != current_date:
                    # Process previous day
                    if daily_trades:
                        daily_pnl = sum(t.net_pnl for t in daily_trades)
                        daily_summaries.append({
                            'date': current_date,
                            'trades_count': len(daily_trades),
                            'daily_net_pnl': daily_pnl,
                            'daily_gross_pnl': sum(t.gross_pnl for t in daily_trades)
                        })
                    daily_trades = []
                    current_date = trade_date
                
                daily_trades.append(trade)
            
            # Process final day
            if daily_trades:
                daily_pnl = sum(t.net_pnl for t in daily_trades)
                daily_summaries.append({
                    'date': current_date,
                    'trades_count': len(daily_trades),
                    'daily_net_pnl': daily_pnl,
                    'daily_gross_pnl': sum(t.gross_pnl for t in daily_trades)
                })
            
            # Calculate equity curve for metrics
            equity_curve = [parameters['account_balance']]
            for summary in daily_summaries:
                equity_curve.append(equity_curve[-1] + summary['daily_net_pnl'])
            
            metrics = analyzer.calculate_all_metrics(engine.all_trades, daily_summaries, equity_curve)
            
            # Performance summary
            performance_report = timer.end_backtest()
            
            # Complete progress tracking
            progress_tracker.complete(f"Backtest completed in {performance_report.get('total_processing_time_seconds', 0):.2f}s")
            
            # Results display
            st.success(f"🎉 Backtest Complete - Processed {len(data)} data points, Generated {len(engine.all_trades)} trades")
            
            # Performance metrics
            display_performance_metrics(metrics)
            
            # Detailed trade analysis
            st.markdown("---")
            display_detailed_trade_analysis(engine.all_trades)
            
            # Trade execution visualization chart
            st.markdown("---") 
            execution_chart = create_trade_execution_chart(data, engine.all_trades)
            if execution_chart:
                st.plotly_chart(execution_chart, use_container_width=True)
            
            # Charts
            st.markdown("---")
            st.subheader("📊 Performance Charts")
            
            results = {
                'parameters': parameters,
                'metrics': metrics,
                'trades': engine.all_trades,
                'daily_summaries': daily_summaries
            }
            
            pnl_fig, equity_fig = create_basic_charts(results)
            
            if pnl_fig and equity_fig:
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.plotly_chart(pnl_fig, use_container_width=True)
                with chart_col2:
                    st.plotly_chart(equity_fig, use_container_width=True)
            
            # PDF Generation
            st.markdown("---")
            st.subheader("📄 Report Generation")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Generate a comprehensive PDF report with all parameters, metrics, and charts.")
            with col2:
                if st.button("📄 Generate PDF Report", type="secondary"):
                    with st.spinner("Generating PDF report..."):
                        try:
                            pdf_generator = SPXBacktestPDFGenerator()
                            pdf_data = pdf_generator.generate_complete_report(
                                parameters, 
                                metrics, 
                                {'pnl_chart': pnl_fig, 'equity_chart': equity_fig}
                            )
                            
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=pdf_data,
                                file_name=f"SPX_CFD_Backtest_{parameters['start_date']}_to_{parameters['end_date']}.pdf",
                                mime="application/pdf"
                            )
                            st.success("✅ PDF report generated successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating PDF: {e}")
            
        except Exception as e:
            progress_tracker.error(f"Backtest failed: {str(e)}")
            error_handler.handle_graceful_failure(e, streamlit_context=True)
    
    else:
        # Instructions when not running
        st.info("👈 Configure your backtest parameters in the sidebar, then click 'Run Backtest' to begin analysis.")
        
        # Quick info about the strategy
        with st.expander("ℹ️ About the 2 Basis Point Strategy"):
            st.markdown("""
            **Strategy Overview:**
            - **Entry Trigger**: Long when price rises ≥2 basis points from opening price, Short when price falls ≤-2 basis points
            - **Market Hours**: Entry allowed 9:30 AM - 3:30 PM EST, Force close at 4:00 PM EST
            - **Opening Price Reset**: Daily at 9:30 AM opening, and after each trade exit
            - **Position Management**: One active trade at a time, no pyramiding
            - **Risk Management**: Configurable stop loss, profit targets, and position sizing
            
            **Key Features:**
            - Real market data processing (no synthetic data)
            - Complete 22-metric performance analysis
            - Professional PDF report generation
            - Multiple timeframe support (1M, 5M, 30M, 1H, 1D)
            """)

if __name__ == "__main__":
    main()
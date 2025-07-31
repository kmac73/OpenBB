import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, time
from scipy import stats
import warnings
from market_data import Retrieve
import math
import os
from datetime import datetime as dt

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="SP500 CFD Strategy v1 - Baseline",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 SP500 CFD Strategy - Version 1 (Baseline)")
st.markdown("### Basic Implementation with Standard Analytics")

class CFDStrategyV1:
    def __init__(self, params):
        self.params = params
        self.trades = []
        self.daily_pnl = []
        self.positions = []
        
    def calculate_position_size(self, account_equity, risk_per_trade, stop_loss_points):
        """Calculate position size based on risk management"""
        risk_amount = account_equity * (risk_per_trade / 100)
        cfd_multiplier = 1.0  # $1 per point for S&P 500 CFDs
        max_position = risk_amount / (stop_loss_points * cfd_multiplier)
        return int(max_position)
    
    def get_opening_range(self, data, date):
        """Get opening range for the trading day"""
        day_data = data[data.index.date == date.date()]
        if len(day_data) == 0:
            return None, None
            
        # Opening range: 9:30-10:00 AM EST (first 30 minutes)
        opening_minutes = self.params['opening_range_minutes']
        start_time = time(9, 30)
        
        # Calculate end time properly handling hour overflow
        total_minutes = 30 + opening_minutes
        end_hour = 9 + (total_minutes // 60)
        end_minute = total_minutes % 60
        end_time = time(end_hour, end_minute)
        
        opening_data = day_data[
            (day_data.index.time >= start_time) & 
            (day_data.index.time <= end_time)
        ]
        
        if len(opening_data) == 0:
            return None, None
            
        return opening_data['High'].max(), opening_data['Low'].min()
    
    def check_momentum_confirmation(self, data, current_idx, direction):
        """Basic momentum confirmation using volume and price action"""
        if current_idx < 2:
            return False
            
        current = data.iloc[current_idx]
        prev = data.iloc[current_idx - 1]
        prev2 = data.iloc[current_idx - 2]
        
        # Volume confirmation
        volume_confirm = current['Volume'] > prev['Volume'] * 1.1
        
        # Price momentum confirmation
        if direction == 'LONG':
            momentum_confirm = (current['Close'] > prev['Close']) and (prev['Close'] > prev2['Close'])
        else:  # SHORT
            momentum_confirm = (current['Close'] < prev['Close']) and (prev['Close'] < prev2['Close'])
            
        return volume_confirm and momentum_confirm
    
    def apply_directional_bias(self, direction, base_size, current_price, prev_close):
        """Apply 7.8x short advantage directional bias"""
        bias_multiplier = self.params['directional_bias_multiplier']
        
        if direction == 'SHORT' and current_price < prev_close:
            return int(base_size * bias_multiplier)
        return base_size
    
    def calculate_transaction_costs(self, position_size):
        """Calculate realistic transaction costs"""
        spread_cost = position_size * self.params['spread_points']
        commission = self.params['commission_per_trade']
        return spread_cost + commission
    
    def run_backtest(self, data):
        """Execute the CFD strategy backtest"""
        account_equity = self.params['initial_capital']
        max_positions = self.params['max_concurrent_positions']
        active_positions = []
        
        # Trading hours: 9:45 AM - 3:30 PM EST
        start_trading = time(9, 45)
        stop_trading = time(15, 30)
        close_positions = time(16, 0)
        
        for i in range(len(data)):
            current_time = data.index[i].time()
            current_date = data.index[i]
            current_price = data.iloc[i]['Close']
            
            # Skip if outside trading hours
            if current_time < start_trading or current_time > stop_trading:
                continue
                
            # Get opening range for the day
            opening_high, opening_low = self.get_opening_range(data, current_date)
            if opening_high is None:
                continue
                
            # Check for entry signals
            if len(active_positions) < max_positions:
                entry_threshold = self.params['entry_threshold_points']
                
                # LONG entry: price breaks above opening range high
                if current_price > opening_high + entry_threshold:
                    if self.check_momentum_confirmation(data, i, 'LONG'):
                        position_size = self.calculate_position_size(
                            account_equity, 
                            self.params['risk_per_trade'],
                            self.params['stop_loss_points']
                        )
                        
                        # Apply directional bias
                        prev_close = data.iloc[i-1]['Close'] if i > 0 else current_price
                        position_size = self.apply_directional_bias('LONG', position_size, current_price, prev_close)
                        
                        transaction_cost = self.calculate_transaction_costs(position_size)
                        
                        position = {
                            'entry_time': current_date,
                            'entry_price': current_price,
                            'direction': 'LONG',
                            'size': position_size,
                            'stop_loss': current_price - self.params['stop_loss_points'],
                            'profit_target': current_price + self.params['profit_target_points'],
                            'transaction_cost': transaction_cost
                        }
                        active_positions.append(position)
                
                # SHORT entry: price breaks below opening range low
                elif current_price < opening_low - entry_threshold:
                    if self.check_momentum_confirmation(data, i, 'SHORT'):
                        position_size = self.calculate_position_size(
                            account_equity, 
                            self.params['risk_per_trade'],
                            self.params['stop_loss_points']
                        )
                        
                        # Apply directional bias (shorts get advantage)
                        prev_close = data.iloc[i-1]['Close'] if i > 0 else current_price
                        position_size = self.apply_directional_bias('SHORT', position_size, current_price, prev_close)
                        
                        transaction_cost = self.calculate_transaction_costs(position_size)
                        
                        position = {
                            'entry_time': current_date,
                            'entry_price': current_price,
                            'direction': 'SHORT',
                            'size': position_size,
                            'stop_loss': current_price + self.params['stop_loss_points'],
                            'profit_target': current_price - self.params['profit_target_points'],
                            'transaction_cost': transaction_cost
                        }
                        active_positions.append(position)
            
            # Check for exits on active positions
            positions_to_remove = []
            for pos_idx, position in enumerate(active_positions):
                exit_triggered = False
                exit_reason = ""
                exit_price = current_price
                
                # Check stop loss and profit target
                if position['direction'] == 'LONG':
                    if current_price <= position['stop_loss']:
                        exit_triggered = True
                        exit_reason = "Stop Loss"
                    elif current_price >= position['profit_target']:
                        exit_triggered = True
                        exit_reason = "Profit Target"
                elif position['direction'] == 'SHORT':
                    if current_price >= position['stop_loss']:
                        exit_triggered = True
                        exit_reason = "Stop Loss"
                    elif current_price <= position['profit_target']:
                        exit_triggered = True
                        exit_reason = "Profit Target"
                
                # Force close at 4:00 PM
                if current_time >= close_positions:
                    exit_triggered = True
                    exit_reason = "End of Day"
                
                if exit_triggered:
                    # Calculate P&L
                    if position['direction'] == 'LONG':
                        gross_pnl = (exit_price - position['entry_price']) * position['size']
                    else:
                        gross_pnl = (position['entry_price'] - exit_price) * position['size']
                    
                    net_pnl = gross_pnl - position['transaction_cost']
                    
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_date,
                        'direction': position['direction'],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'size': position['size'],
                        'gross_pnl': gross_pnl,
                        'transaction_cost': position['transaction_cost'],
                        'net_pnl': net_pnl,
                        'exit_reason': exit_reason,
                        'duration': current_date - position['entry_time']
                    }
                    
                    self.trades.append(trade)
                    account_equity += net_pnl
                    positions_to_remove.append(pos_idx)
            
            # Remove closed positions
            for idx in reversed(positions_to_remove):
                active_positions.pop(idx)
        
        return account_equity
    
    def generate_analytics(self):
        """Generate comprehensive analytics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'gross_pnl': 0,
                'total_costs': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_drawdown': 0,
                'total_return': 0,
                'final_equity': self.params['initial_capital'],
                'profit_factor': 0,
                'cost_ratio': 0
            }
            
        trades_df = pd.DataFrame(self.trades)
        
        # Basic performance metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['net_pnl'] > 0])
        losing_trades = len(trades_df[trades_df['net_pnl'] <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = trades_df['net_pnl'].sum()
        gross_pnl = trades_df['gross_pnl'].sum()
        total_costs = trades_df['transaction_cost'].sum()
        
        avg_win = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['net_pnl'] <= 0]['net_pnl'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        trades_df['cumulative_pnl'] = trades_df['net_pnl'].cumsum()
        peak = trades_df['cumulative_pnl'].cummax()
        drawdown = trades_df['cumulative_pnl'] - peak
        max_drawdown = drawdown.min()
        
        # Return metrics
        initial_capital = self.params['initial_capital']
        final_equity = initial_capital + total_pnl
        total_return = (total_pnl / initial_capital) * 100
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'gross_pnl': gross_pnl,
            'total_costs': total_costs,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'total_return': total_return,
            'final_equity': final_equity,
            'profit_factor': abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 and avg_loss != 0 else 0,
            'cost_ratio': (total_costs / abs(gross_pnl)) * 100 if gross_pnl != 0 else 0
        }

# Sidebar Parameters
st.sidebar.header("📋 Strategy Parameters")

# Account & Risk Parameters
st.sidebar.subheader("💰 Account Settings")
initial_capital = st.sidebar.selectbox("Initial Capital", [10000, 25000, 50000], index=1)
risk_per_trade = st.sidebar.slider("Risk Per Trade (%)", 0.5, 2.0, 1.0, 0.1)
max_concurrent_positions = st.sidebar.selectbox("Max Concurrent Positions", [1, 2, 3], index=0)

# Trading Parameters
st.sidebar.subheader("📈 Trading Rules")
opening_range_minutes = st.sidebar.slider("Opening Range (minutes)", 15, 30, 30, 5)
entry_threshold_points = st.sidebar.slider("Entry Threshold (points)", 1.0, 3.0, 2.0, 0.5)
stop_loss_points = st.sidebar.slider("Stop Loss (points)", 3.0, 6.0, 4.0, 0.5)
profit_target_points = st.sidebar.slider("Profit Target (points)", 6.0, 12.0, 8.0, 0.5)

# Directional Bias
st.sidebar.subheader("🎯 Directional Bias")
directional_bias_multiplier = st.sidebar.slider("Short Bias Multiplier", 1.0, 2.0, 1.5, 0.1)

# Transaction Costs
st.sidebar.subheader("💸 Transaction Costs")
spread_points = st.sidebar.slider("Spread (points)", 0.4, 1.5, 1.0, 0.1)
commission_per_trade = st.sidebar.slider("Commission ($)", 0.5, 2.0, 1.0, 0.1)

# Data Parameters
st.sidebar.subheader("📊 Data Settings")
start_date = st.sidebar.text_input("Start Date (YYYY-MM-DD)", "2021-01-01")
end_date = st.sidebar.text_input("End Date (YYYY-MM-DD)", "2024-07-29")
frequency = st.sidebar.selectbox("Frequency", ["1M", "5M", "30M", "1H", "1D"], index=1)
symbol = st.sidebar.selectbox("Symbol", ["SPX"], index=0)

# Debug Section
st.sidebar.subheader("🐛 Debug Tools")
save_params = st.sidebar.button("💾 Save Parameters", help="Save current parameters to file for debugging")

# Load Parameters Section
st.sidebar.subheader("📂 Load Parameters")
uploaded_file = st.sidebar.file_uploader("Choose parameter file", type=['txt'])
load_params = st.sidebar.button("📥 Load Saved Parameters", help="Load parameters from previously saved file")

# Run Strategy Button
run_strategy = st.sidebar.button("🚀 Run CFD Strategy", type="primary")

# Handle Save Parameters functionality
if save_params:
    try:
        # Collect all parameters
        debug_params = {
            'timestamp': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategy_version': 'V1 - Baseline',
            'initial_capital': initial_capital,
            'risk_per_trade': risk_per_trade,
            'max_concurrent_positions': max_concurrent_positions,
            'opening_range_minutes': opening_range_minutes,
            'entry_threshold_points': entry_threshold_points,
            'stop_loss_points': stop_loss_points,
            'profit_target_points': profit_target_points,
            'directional_bias_multiplier': directional_bias_multiplier,
            'spread_points': spread_points,
            'commission_per_trade': commission_per_trade,
            'start_date': start_date,
            'end_date': end_date,
            'frequency': frequency,
            'symbol': symbol
        }
        
        # Create filename with timestamp
        filename = f"debug_params_v1_{dt.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Write parameters to file
        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("SP500 CFD STRATEGY V1 - DEBUG PARAMETERS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {debug_params['timestamp']}\n")
            f.write(f"Strategy: {debug_params['strategy_version']}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("ACCOUNT SETTINGS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Initial Capital: ${debug_params['initial_capital']:,}\n")
            f.write(f"Risk Per Trade: {debug_params['risk_per_trade']}%\n")
            f.write(f"Max Concurrent Positions: {debug_params['max_concurrent_positions']}\n\n")
            
            f.write("TRADING RULES:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Opening Range Minutes: {debug_params['opening_range_minutes']}\n")
            f.write(f"Entry Threshold Points: {debug_params['entry_threshold_points']}\n")
            f.write(f"Stop Loss Points: {debug_params['stop_loss_points']}\n")
            f.write(f"Profit Target Points: {debug_params['profit_target_points']}\n")
            f.write(f"Risk-Reward Ratio: {debug_params['profit_target_points']/debug_params['stop_loss_points']:.1f}:1\n\n")
            
            f.write("DIRECTIONAL BIAS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Short Bias Multiplier: {debug_params['directional_bias_multiplier']}x\n\n")
            
            f.write("TRANSACTION COSTS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Spread Points: {debug_params['spread_points']}\n")
            f.write(f"Commission Per Trade: ${debug_params['commission_per_trade']}\n\n")
            
            f.write("DATA SETTINGS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Symbol: {debug_params['symbol']}\n")
            f.write(f"Start Date: {debug_params['start_date']}\n")
            f.write(f"End Date: {debug_params['end_date']}\n")
            f.write(f"Frequency: {debug_params['frequency']}\n\n")
            
            f.write("CALCULATED VALUES:\n")
            f.write("-" * 20 + "\n")
            sample_position_size = int((debug_params['initial_capital'] * debug_params['risk_per_trade'] / 100) / debug_params['stop_loss_points'])
            f.write(f"Sample Position Size: {sample_position_size} CFDs\n")
            f.write(f"Sample Risk Amount: ${debug_params['initial_capital'] * debug_params['risk_per_trade'] / 100:.2f}\n")
            sample_transaction_cost = sample_position_size * debug_params['spread_points'] + debug_params['commission_per_trade']
            f.write(f"Sample Transaction Cost: ${sample_transaction_cost:.2f}\n")
            f.write(f"Cost as % of Risk: {sample_transaction_cost / (debug_params['initial_capital'] * debug_params['risk_per_trade'] / 100) * 100:.1f}%\n\n")
            
            f.write("SYSTEM INFO:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Working Directory: {os.getcwd()}\n")
            f.write(f"Parameter File: {filename}\n")
            f.write(f"Python Version: {os.sys.version.split()[0]}\n")
        
        st.sidebar.success(f"✅ Parameters saved to: {filename}")
        st.sidebar.info(f"📁 Location: {os.getcwd()}")
        
    except Exception as e:
        st.sidebar.error(f"❌ Error saving parameters: {str(e)}")

# Handle Load Parameters functionality
if load_params and uploaded_file is not None:
    try:
        # Read the uploaded file
        file_content = uploaded_file.read().decode('utf-8')
        lines = file_content.split('\n')
        
        # Parse parameters from file
        loaded_params = {}
        for line in lines:
            if ':' in line and not line.startswith('=') and not line.startswith('-'):
                key_value = line.split(':', 1)
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    
                    # Map file keys to parameter names
                    if 'Initial Capital' in key:
                        loaded_params['initial_capital'] = float(value.replace('$', '').replace(',', ''))
                    elif 'Risk Per Trade' in key:
                        loaded_params['risk_per_trade'] = float(value.replace('%', ''))
                    elif 'Max Concurrent Positions' in key:
                        loaded_params['max_concurrent_positions'] = int(value)
                    elif 'Opening Range Minutes' in key:
                        loaded_params['opening_range_minutes'] = int(value)
                    elif 'Entry Threshold Points' in key:
                        loaded_params['entry_threshold_points'] = float(value)
                    elif 'Stop Loss Points' in key:
                        loaded_params['stop_loss_points'] = float(value)
                    elif 'Profit Target Points' in key:
                        loaded_params['profit_target_points'] = float(value)
                    elif 'Short Bias Multiplier' in key:
                        loaded_params['directional_bias_multiplier'] = float(value.replace('x', ''))
                    elif 'Spread Points' in key:
                        loaded_params['spread_points'] = float(value)
                    elif 'Commission Per Trade' in key:
                        loaded_params['commission_per_trade'] = float(value.replace('$', ''))
                    elif 'Start Date' in key:
                        loaded_params['start_date'] = value
                    elif 'End Date' in key:
                        loaded_params['end_date'] = value
                    elif 'Frequency' in key:
                        loaded_params['frequency'] = value
                    elif 'Symbol' in key:
                        loaded_params['symbol'] = value
        
        # Update session state with loaded parameters
        if loaded_params:
            for key, value in loaded_params.items():
                st.session_state[key] = value
            
            st.sidebar.success(f"✅ Parameters loaded successfully!")
            st.sidebar.info("🔄 Please refresh the page to see loaded parameters in the UI")
            st.sidebar.json(loaded_params)
        else:
            st.sidebar.warning("⚠️ No valid parameters found in file")
            
    except Exception as e:
        st.sidebar.error(f"❌ Error loading parameters: {str(e)}")

elif load_params and uploaded_file is None:
    st.sidebar.warning("⚠️ Please select a parameter file first")

if run_strategy:
    with st.spinner("Running CFD Strategy Analysis..."):
        # Prepare parameters
        params = {
            'initial_capital': initial_capital,
            'risk_per_trade': risk_per_trade,
            'max_concurrent_positions': max_concurrent_positions,
            'opening_range_minutes': opening_range_minutes,
            'entry_threshold_points': entry_threshold_points,
            'stop_loss_points': stop_loss_points,
            'profit_target_points': profit_target_points,
            'directional_bias_multiplier': directional_bias_multiplier,
            'spread_points': spread_points,
            'commission_per_trade': commission_per_trade
        }
        
        # Load market data
        try:
            data_retriever = Retrieve()
            data = data_retriever.get_data(symbol, start_date, end_date, frequency)
            
            if data is not None and not data.empty:
                # Run strategy
                strategy = CFDStrategyV1(params)
                final_equity = strategy.run_backtest(data)
                analytics = strategy.generate_analytics()
                
                # Display Results
                st.success("✅ Strategy Analysis Complete!")
                
                # Key Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Return", f"{analytics['total_return']:.1f}%")
                with col2:
                    st.metric("Win Rate", f"{analytics['win_rate']:.1f}%")
                with col3:
                    st.metric("Total Trades", analytics['total_trades'])
                with col4:
                    st.metric("Max Drawdown", f"${analytics['max_drawdown']:.2f}")
                
                # Performance Summary
                st.subheader("📊 Performance Summary")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Trading Results:**")
                    st.write(f"• Final Equity: ${analytics['final_equity']:,.2f}")
                    st.write(f"• Total P&L: ${analytics['total_pnl']:,.2f}")
                    st.write(f"• Winning Trades: {analytics['winning_trades']}")
                    st.write(f"• Losing Trades: {analytics['losing_trades']}")
                    st.write(f"• Average Win: ${analytics['avg_win']:.2f}")
                    st.write(f"• Average Loss: ${analytics['avg_loss']:.2f}")
                
                with col2:
                    st.write("**Cost Analysis:**")
                    st.write(f"• Gross P&L: ${analytics['gross_pnl']:,.2f}")
                    st.write(f"• Total Costs: ${analytics['total_costs']:,.2f}")
                    st.write(f"• Cost Ratio: {analytics['cost_ratio']:.1f}%")
                    st.write(f"• Profit Factor: {analytics['profit_factor']:.2f}")
                    st.write(f"• Risk-Reward: {profit_target_points/stop_loss_points:.1f}:1")
                
                # Trade Analysis
                if strategy.trades:
                    st.subheader("📈 Trade Analysis")
                    trades_df = pd.DataFrame(strategy.trades)
                    
                    # P&L Chart
                    trades_df['cumulative_pnl'] = trades_df['net_pnl'].cumsum()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=trades_df['exit_time'],
                        y=trades_df['cumulative_pnl'],
                        mode='lines',
                        name='Cumulative P&L',
                        line=dict(color='green')
                    ))
                    fig.update_layout(
                        title="Cumulative P&L Over Time",
                        xaxis_title="Date",
                        yaxis_title="Cumulative P&L ($)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Recent Trades Table
                    st.subheader("📋 Recent Trades")
                    recent_trades = trades_df.tail(10)
                    st.dataframe(recent_trades[['entry_time', 'direction', 'entry_price', 'exit_price', 'net_pnl', 'exit_reason']])
                
            else:
                st.error("❌ Failed to load market data. Please check your date range and symbol.")
                
        except Exception as e:
            st.error(f"❌ Error running strategy: {str(e)}")

else:
    st.info("👈 Configure parameters in the sidebar and click 'Run CFD Strategy' to start the analysis.")

# Footer
st.markdown("---")
st.markdown("**SP500 CFD Strategy v1 - Baseline Implementation**")
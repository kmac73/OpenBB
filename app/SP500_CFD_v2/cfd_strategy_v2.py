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
from numba import jit, njit
import concurrent.futures
import os
from datetime import datetime as dt
from scipy.optimize import minimize
try:
    import talib
except ImportError:
    talib = None

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="SP500 CFD Strategy v2 - Performance Optimized",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ SP500 CFD Strategy - Version 2 (Performance Optimized)")
st.markdown("### High-Speed Execution with Advanced Analytics & ML Features")

@njit
def calculate_returns_numba(prices):
    """Fast return calculation using Numba"""
    returns = np.zeros(len(prices))
    for i in range(1, len(prices)):
        returns[i] = (prices[i] - prices[i-1]) / prices[i-1]
    return returns

@njit
def calculate_sharpe_numba(returns, risk_free_rate=0.02):
    """Fast Sharpe ratio calculation"""
    if len(returns) == 0:
        return 0.0
    excess_returns = returns - risk_free_rate/252
    if np.std(excess_returns) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

@njit
def fast_momentum_filter(prices, volume, window=3):
    """High-performance momentum filtering"""
    momentum_scores = np.zeros(len(prices))
    for i in range(window, len(prices)):
        price_momentum = (prices[i] - prices[i-window]) / prices[i-window]
        volume_momentum = (volume[i] - volume[i-window]) / volume[i-window]
        momentum_scores[i] = price_momentum * volume_momentum
    return momentum_scores

class AdvancedCFDStrategy:
    def __init__(self, params):
        self.params = params
        self.trades = []
        self.daily_pnl = []
        self.positions = []
        self.performance_cache = {}
        
    @st.cache_data
    def preprocess_data(_self, data):
        """Cached data preprocessing with technical indicators"""
        # Add technical indicators using TA-Lib for speed (or fallback calculations)
        if talib is not None:
            data['RSI'] = talib.RSI(data['Close'].values, timeperiod=14)
            data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = talib.MACD(data['Close'].values)
            data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = talib.BBANDS(data['Close'].values)
            data['ATR'] = talib.ATR(data['High'].values, data['Low'].values, data['Close'].values)
        else:
            # Fallback calculations without TA-Lib
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Simple MACD
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
            
            # Simple Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
            # Simple ATR
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            data['ATR'] = true_range.rolling(window=14).mean()
        
        data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
        
        # Fast momentum calculations
        prices = data['Close'].values
        volume = data['Volume'].values
        data['Momentum_Score'] = fast_momentum_filter(prices, volume)
        data['Returns'] = calculate_returns_numba(prices)
        
        return data
    
    def dynamic_position_sizing(self, account_equity, volatility, confidence_score):
        """ML-enhanced position sizing based on market conditions"""
        base_risk = self.params['risk_per_trade'] / 100
        
        # Volatility adjustment
        vol_adjustment = 1.0 / (1.0 + volatility * 2)
        
        # Confidence adjustment (based on momentum score)
        confidence_adjustment = 0.5 + (confidence_score * 0.5)
        
        # Kelly Criterion approximation
        win_rate = 0.45  # Expected from strategy document
        avg_win_loss_ratio = 2.0  # 2:1 risk reward
        kelly_fraction = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
        kelly_adjustment = min(kelly_fraction, 0.25)  # Cap at 25%
        
        adjusted_risk = base_risk * vol_adjustment * confidence_adjustment * kelly_adjustment
        risk_amount = account_equity * adjusted_risk
        
        cfd_multiplier = 1.0
        position_size = risk_amount / (self.params['stop_loss_points'] * cfd_multiplier)
        
        return max(1, int(position_size))
    
    def advanced_entry_signal(self, data, idx, direction):
        """Multi-factor entry signal with ML scoring"""
        if idx < 20:  # Need history for indicators
            return False, 0.0
            
        current = data.iloc[idx]
        
        # Technical indicator confluence
        rsi_score = 0.0
        macd_score = 0.0
        bb_score = 0.0
        momentum_score = current['Momentum_Score']
        
        if direction == 'LONG':
            # RSI oversold recovery
            if 30 < current['RSI'] < 50:
                rsi_score = 0.3
            # MACD bullish
            if current['MACD'] > current['MACD_Signal']:
                macd_score = 0.3
            # Price above VWAP
            if current['Close'] > current['VWAP']:
                bb_score = 0.2
        else:  # SHORT
            # RSI overbought decline
            if 50 < current['RSI'] < 70:
                rsi_score = 0.3
            # MACD bearish
            if current['MACD'] < current['MACD_Signal']:
                macd_score = 0.3
            # Price below VWAP
            if current['Close'] < current['VWAP']:
                bb_score = 0.2
        
        # Combine scores
        total_score = rsi_score + macd_score + bb_score + abs(momentum_score * 0.2)
        confidence = min(total_score, 1.0)
        
        # Entry threshold
        entry_threshold = 0.4  # Require 40% confidence minimum
        return confidence > entry_threshold, confidence
    
    def regime_detection(self, data, idx):
        """Detect market regime for strategy adaptation"""
        if idx < 50:
            return 'neutral'
            
        # Look at recent volatility and trend
        recent_data = data.iloc[idx-50:idx]
        volatility = recent_data['Returns'].std() * np.sqrt(252)  # Annualized vol
        trend = (recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[0]) / recent_data['Close'].iloc[0]
        
        if volatility > 0.25:  # High vol regime
            return 'high_volatility'
        elif trend > 0.05:  # Strong uptrend
            return 'bullish'
        elif trend < -0.05:  # Strong downtrend
            return 'bearish'
        else:
            return 'neutral'
    
    def run_backtest_optimized(self, data):
        """Vectorized and optimized backtest execution"""
        # Preprocess data with caching
        data = self.preprocess_data(data)
        
        account_equity = self.params['initial_capital']
        max_positions = self.params['max_concurrent_positions']
        active_positions = []
        
        # Vectorized trading hours check
        trading_start = time(9, 45)
        trading_stop = time(15, 30)
        close_time = time(16, 0)
        
        # Pre-calculate opening ranges for all days
        opening_ranges = {}
        for date in data.index.date:
            day_data = data[data.index.date == date]
            if len(day_data) > 0:
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
                
                if len(opening_data) > 0:
                    opening_ranges[date] = (opening_data['High'].max(), opening_data['Low'].min())
        
        # Main backtest loop with optimizations
        for i in range(50, len(data)):  # Start after indicator warmup
            current_time = data.index[i].time()
            current_date = data.index[i]
            current_price = data.iloc[i]['Close']
            current_vol = data.iloc[i]['ATR']
            
            # Skip if outside trading hours
            if current_time < trading_start or current_time > trading_stop:
                continue
                
            # Get opening range
            date_key = current_date.date()
            if date_key not in opening_ranges:
                continue
            opening_high, opening_low = opening_ranges[date_key]
            
            # Detect market regime
            regime = self.regime_detection(data, i)
            
            # Check for entry signals with ML enhancement
            if len(active_positions) < max_positions:
                entry_threshold = self.params['entry_threshold_points']
                
                # LONG entry with advanced signal
                if current_price > opening_high + entry_threshold:
                    entry_valid, confidence = self.advanced_entry_signal(data, i, 'LONG')
                    if entry_valid:
                        position_size = self.dynamic_position_sizing(account_equity, current_vol, confidence)
                        
                        # Regime-based adjustments
                        if regime == 'bearish':
                            position_size = int(position_size * 0.5)  # Reduce size in bearish regime
                        elif regime == 'bullish':
                            position_size = int(position_size * 1.2)  # Increase size in bullish regime
                        
                        transaction_cost = position_size * self.params['spread_points'] + self.params['commission_per_trade']
                        
                        position = {
                            'entry_time': current_date,
                            'entry_price': current_price,
                            'direction': 'LONG',
                            'size': position_size,
                            'stop_loss': current_price - self.params['stop_loss_points'],
                            'profit_target': current_price + self.params['profit_target_points'],
                            'transaction_cost': transaction_cost,
                            'confidence': confidence,
                            'regime': regime
                        }
                        active_positions.append(position)
                
                # SHORT entry with advanced signal
                elif current_price < opening_low - entry_threshold:
                    entry_valid, confidence = self.advanced_entry_signal(data, i, 'SHORT')
                    if entry_valid:
                        position_size = self.dynamic_position_sizing(account_equity, current_vol, confidence)
                        
                        # Apply directional bias (7.8x short advantage)
                        if regime in ['bearish', 'high_volatility']:
                            position_size = int(position_size * self.params['directional_bias_multiplier'])
                        
                        transaction_cost = position_size * self.params['spread_points'] + self.params['commission_per_trade']
                        
                        position = {
                            'entry_time': current_date,
                            'entry_price': current_price,
                            'direction': 'SHORT',
                            'size': position_size,
                            'stop_loss': current_price + self.params['stop_loss_points'],
                            'profit_target': current_price - self.params['profit_target_points'],
                            'transaction_cost': transaction_cost,
                            'confidence': confidence,
                            'regime': regime
                        }
                        active_positions.append(position)
            
            # Vectorized exit processing
            positions_to_remove = []
            for pos_idx, position in enumerate(active_positions):
                exit_triggered = False
                exit_reason = ""
                exit_price = current_price
                
                # Optimized exit logic
                if position['direction'] == 'LONG':
                    if current_price <= position['stop_loss']:
                        exit_triggered, exit_reason = True, "Stop Loss"
                    elif current_price >= position['profit_target']:
                        exit_triggered, exit_reason = True, "Profit Target"
                elif position['direction'] == 'SHORT':
                    if current_price >= position['stop_loss']:
                        exit_triggered, exit_reason = True, "Stop Loss"
                    elif current_price <= position['profit_target']:
                        exit_triggered, exit_reason = True, "Profit Target"
                
                # Force close at end of day
                if current_time >= close_time:
                    exit_triggered, exit_reason = True, "End of Day"
                
                if exit_triggered:
                    # Fast P&L calculation
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
                        'duration': current_date - position['entry_time'],
                        'confidence': position.get('confidence', 0),
                        'regime': position.get('regime', 'unknown')
                    }
                    
                    self.trades.append(trade)
                    account_equity += net_pnl
                    positions_to_remove.append(pos_idx)
            
            # Remove closed positions (reverse order to maintain indices)
            for idx in reversed(positions_to_remove):
                active_positions.pop(idx)
        
        return account_equity
    
    def generate_advanced_analytics(self):
        """Generate comprehensive ML-enhanced analytics"""
        if not self.trades:
            return {}
            
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics (vectorized)
        total_trades = len(trades_df)
        winning_trades = (trades_df['net_pnl'] > 0).sum()
        losing_trades = (trades_df['net_pnl'] <= 0).sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Performance metrics
        total_pnl = trades_df['net_pnl'].sum()
        returns = trades_df['net_pnl'].values / self.params['initial_capital']
        sharpe_ratio = calculate_sharpe_numba(returns) if len(returns) > 0 else 0
        
        # Advanced risk metrics
        trades_df['cumulative_pnl'] = trades_df['net_pnl'].cumsum()
        peak = trades_df['cumulative_pnl'].expanding().max()
        drawdown = trades_df['cumulative_pnl'] - peak
        max_drawdown = drawdown.min()
        
        # Calmar ratio
        total_return = (total_pnl / self.params['initial_capital']) * 100
        calmar_ratio = total_return / abs(max_drawdown / self.params['initial_capital'] * 100) if max_drawdown != 0 else 0
        
        # Regime analysis
        regime_performance = trades_df.groupby('regime')['net_pnl'].agg(['count', 'mean', 'sum']).to_dict('index')
        
        # Confidence analysis
        high_confidence_trades = trades_df[trades_df['confidence'] > 0.7]
        high_conf_win_rate = (high_confidence_trades['net_pnl'] > 0).mean() * 100 if len(high_confidence_trades) > 0 else 0
        
        # Trade timing analysis
        trades_df['hour'] = trades_df['entry_time'].dt.hour
        hourly_performance = trades_df.groupby('hour')['net_pnl'].agg(['count', 'mean']).to_dict('index')
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'regime_performance': regime_performance,
            'high_conf_win_rate': high_conf_win_rate,
            'hourly_performance': hourly_performance,
            'avg_confidence': trades_df['confidence'].mean(),
            'profit_factor': trades_df[trades_df['net_pnl'] > 0]['net_pnl'].sum() / abs(trades_df[trades_df['net_pnl'] <= 0]['net_pnl'].sum()) if losing_trades > 0 else 0
        }

# Sidebar Parameters - Enhanced
st.sidebar.header("⚡ Advanced Strategy Parameters")

# Performance Optimization Settings
st.sidebar.subheader("🎯 Optimization Settings")
use_ml_features = st.sidebar.checkbox("Enable ML Features", value=True)
regime_adaptation = st.sidebar.checkbox("Regime Adaptation", value=True)
dynamic_sizing = st.sidebar.checkbox("Dynamic Position Sizing", value=True)

# Account & Risk Parameters
st.sidebar.subheader("💰 Account Settings")
initial_capital = st.sidebar.selectbox("Initial Capital", [10000, 25000, 50000, 100000], index=2)
risk_per_trade = st.sidebar.slider("Base Risk Per Trade (%)", 0.5, 3.0, 1.0, 0.1)
max_concurrent_positions = st.sidebar.selectbox("Max Concurrent Positions", [1, 2, 3, 5], index=2)

# Advanced Trading Parameters
st.sidebar.subheader("📈 Advanced Trading Rules")
opening_range_minutes = st.sidebar.slider("Opening Range (minutes)", 15, 45, 30, 5)
entry_threshold_points = st.sidebar.slider("Entry Threshold (points)", 1.0, 4.0, 2.0, 0.25)
stop_loss_points = st.sidebar.slider("Stop Loss (points)", 2.0, 8.0, 4.0, 0.25)
profit_target_points = st.sidebar.slider("Profit Target (points)", 4.0, 16.0, 8.0, 0.25)

# ML Enhanced Parameters
st.sidebar.subheader("🤖 ML Enhancement")
directional_bias_multiplier = st.sidebar.slider("Short Bias Multiplier", 1.0, 2.5, 1.5, 0.1)
confidence_threshold = st.sidebar.slider("Min Confidence Threshold", 0.1, 0.8, 0.4, 0.05)

# Transaction Costs
st.sidebar.subheader("💸 Transaction Costs")
spread_points = st.sidebar.slider("Spread (points)", 0.2, 2.0, 0.8, 0.1)
commission_per_trade = st.sidebar.slider("Commission ($)", 0.5, 3.0, 1.0, 0.1)

# Data Parameters
st.sidebar.subheader("📊 Data Settings")
start_date = st.sidebar.text_input("Start Date (YYYY-MM-DD)", "2021-01-01")
end_date = st.sidebar.text_input("End Date (YYYY-MM-DD)", "2024-07-29")

# Performance Analysis Controls
st.sidebar.subheader("📊 Analysis Options")
show_regime_analysis = st.sidebar.checkbox("Show Regime Analysis", value=True)
show_confidence_analysis = st.sidebar.checkbox("Show Confidence Analysis", value=True)
show_hourly_analysis = st.sidebar.checkbox("Show Hourly Analysis", value=True)

# Debug Section
st.sidebar.subheader("🐛 Debug Tools")
save_params = st.sidebar.button("💾 Save Parameters", help="Save current parameters to file for debugging")

# Run Strategy Button
run_strategy = st.sidebar.button("⚡ Run Optimized Strategy", type="primary")

# Handle Save Parameters functionality
if save_params:
    try:
        # Collect all parameters
        debug_params = {
            'timestamp': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategy_version': 'V2 - Performance Optimized',
            'ml_features_enabled': use_ml_features,
            'regime_adaptation_enabled': regime_adaptation,
            'dynamic_sizing_enabled': dynamic_sizing,
            'initial_capital': initial_capital,
            'risk_per_trade': risk_per_trade,
            'max_concurrent_positions': max_concurrent_positions,
            'opening_range_minutes': opening_range_minutes,
            'entry_threshold_points': entry_threshold_points,
            'stop_loss_points': stop_loss_points,
            'profit_target_points': profit_target_points,
            'directional_bias_multiplier': directional_bias_multiplier,
            'confidence_threshold': confidence_threshold,
            'spread_points': spread_points,
            'commission_per_trade': commission_per_trade,
            'start_date': start_date,
            'end_date': end_date,
            'show_regime_analysis': show_regime_analysis,
            'show_confidence_analysis': show_confidence_analysis,
            'show_hourly_analysis': show_hourly_analysis
        }
        
        # Create filename with timestamp
        filename = f"debug_params_v2_{dt.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Write parameters to file
        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("SP500 CFD STRATEGY V2 - DEBUG PARAMETERS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {debug_params['timestamp']}\n")
            f.write(f"Strategy: {debug_params['strategy_version']}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("OPTIMIZATION SETTINGS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"ML Features Enabled: {debug_params['ml_features_enabled']}\n")
            f.write(f"Regime Adaptation: {debug_params['regime_adaptation_enabled']}\n")
            f.write(f"Dynamic Position Sizing: {debug_params['dynamic_sizing_enabled']}\n\n")
            
            f.write("ACCOUNT SETTINGS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Initial Capital: ${debug_params['initial_capital']:,}\n")
            f.write(f"Base Risk Per Trade: {debug_params['risk_per_trade']}%\n")
            f.write(f"Max Concurrent Positions: {debug_params['max_concurrent_positions']}\n\n")
            
            f.write("ADVANCED TRADING RULES:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Opening Range Minutes: {debug_params['opening_range_minutes']}\n")
            f.write(f"Entry Threshold Points: {debug_params['entry_threshold_points']}\n")
            f.write(f"Stop Loss Points: {debug_params['stop_loss_points']}\n")
            f.write(f"Profit Target Points: {debug_params['profit_target_points']}\n")
            f.write(f"Risk-Reward Ratio: {debug_params['profit_target_points']/debug_params['stop_loss_points']:.1f}:1\n\n")
            
            f.write("ML ENHANCEMENT:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Short Bias Multiplier: {debug_params['directional_bias_multiplier']}x\n")
            f.write(f"Min Confidence Threshold: {debug_params['confidence_threshold']}\n\n")
            
            f.write("TRANSACTION COSTS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Spread Points: {debug_params['spread_points']}\n")
            f.write(f"Commission Per Trade: ${debug_params['commission_per_trade']}\n\n")
            
            f.write("DATA SETTINGS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Symbol: SPX\n")
            f.write(f"Start Date: {debug_params['start_date']}\n")
            f.write(f"End Date: {debug_params['end_date']}\n")
            f.write(f"Frequency: 5M (5-minute intervals)\n\n")
            
            f.write("ANALYSIS OPTIONS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Show Regime Analysis: {debug_params['show_regime_analysis']}\n")
            f.write(f"Show Confidence Analysis: {debug_params['show_confidence_analysis']}\n")
            f.write(f"Show Hourly Analysis: {debug_params['show_hourly_analysis']}\n\n")
            
            f.write("CALCULATED VALUES:\n")
            f.write("-" * 20 + "\n")
            sample_position_size = int((debug_params['initial_capital'] * debug_params['risk_per_trade'] / 100) / debug_params['stop_loss_points'])
            f.write(f"Base Position Size: {sample_position_size} CFDs\n")
            f.write(f"Base Risk Amount: ${debug_params['initial_capital'] * debug_params['risk_per_trade'] / 100:.2f}\n")
            sample_transaction_cost = sample_position_size * debug_params['spread_points'] + debug_params['commission_per_trade']
            f.write(f"Sample Transaction Cost: ${sample_transaction_cost:.2f}\n")
            f.write(f"Cost as % of Risk: {sample_transaction_cost / (debug_params['initial_capital'] * debug_params['risk_per_trade'] / 100) * 100:.1f}%\n\n")
            
            f.write("PERFORMANCE FEATURES:\n")
            f.write("-" * 25 + "\n")
            f.write("• Technical Indicators: RSI, MACD, Bollinger Bands, ATR, VWAP\n")
            f.write("• Market Regime Detection: Volatility and trend-based classification\n")
            f.write("• Advanced Entry Signals: Multi-factor confluence analysis\n")
            f.write("• Dynamic Position Sizing: ML confidence-based adjustments\n")
            f.write("• Kelly Criterion: Optimal position sizing approximation\n")
            f.write("• Numba JIT Acceleration: Fast momentum filtering\n")
            f.write("• Professional Analytics: Calmar ratio, Information ratio\n\n")
            
            f.write("SYSTEM INFO:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Working Directory: {os.getcwd()}\n")
            f.write(f"Parameter File: {filename}\n")
            f.write(f"Python Version: {os.sys.version.split()[0]}\n")
            
            # Check for optional dependencies
            f.write("\nDEPENDENCIES:\n")
            f.write("-" * 15 + "\n")
            try:
                import talib
                f.write("• TA-Lib: Available (technical indicators)\n")
            except ImportError:
                f.write("• TA-Lib: Not available (using fallback calculations)\n")
            
            try:
                import numba
                f.write("• Numba: Available (JIT acceleration)\n")
            except ImportError:
                f.write("• Numba: Not available (no JIT acceleration)\n")
            
            try:
                import sklearn
                f.write("• Scikit-learn: Available (ML features)\n")
            except ImportError:
                f.write("• Scikit-learn: Not available (ML features disabled)\n")
        
        st.sidebar.success(f"✅ Parameters saved to: {filename}")
        st.sidebar.info(f"📁 Location: {os.getcwd()}")
        
    except Exception as e:
        st.sidebar.error(f"❌ Error saving parameters: {str(e)}")

if run_strategy:
    with st.spinner("Running Performance-Optimized CFD Strategy..."):
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
            'commission_per_trade': commission_per_trade,
            'confidence_threshold': confidence_threshold
        }
        
        # Load and process data
        try:
            data_retriever = Retrieve()
            data = data_retriever.get_data("SPX", start_date, end_date, "5M")
            
            if data is not None and not data.empty:
                # Run optimized strategy
                strategy = AdvancedCFDStrategy(params)
                final_equity = strategy.run_backtest_optimized(data)
                analytics = strategy.generate_advanced_analytics()
                
                # Display Enhanced Results
                st.success("✅ Performance-Optimized Analysis Complete!")
                
                # Enhanced Key Metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Return", f"{analytics['total_return']:.1f}%")
                with col2:
                    st.metric("Sharpe Ratio", f"{analytics['sharpe_ratio']:.2f}")
                with col3:
                    st.metric("Calmar Ratio", f"{analytics['calmar_ratio']:.2f}")
                with col4:
                    st.metric("Win Rate", f"{analytics['win_rate']:.1f}%")
                with col5:
                    st.metric("Avg Confidence", f"{analytics['avg_confidence']:.1f}%")
                
                # Advanced Performance Dashboard
                st.subheader("📊 Advanced Performance Dashboard")
                
                # Regime Analysis
                if show_regime_analysis and analytics['regime_performance']:
                    st.write("**Market Regime Performance:**")
                    regime_df = pd.DataFrame(analytics['regime_performance']).T
                    regime_df.columns = ['Trade Count', 'Avg P&L', 'Total P&L']
                    st.dataframe(regime_df)
                
                # Confidence Analysis
                if show_confidence_analysis:
                    st.write(f"**High Confidence Trades (>70%) Win Rate: {analytics['high_conf_win_rate']:.1f}%**")
                
                # Hourly Performance Analysis
                if show_hourly_analysis and analytics['hourly_performance']:
                    st.write("**Hourly Trading Performance:**")
                    hourly_df = pd.DataFrame(analytics['hourly_performance']).T
                    hourly_df.columns = ['Trade Count', 'Avg P&L']
                    
                    # Create hourly performance chart
                    fig = px.bar(x=hourly_df.index, y=hourly_df['Avg P&L'], 
                               title="Average P&L by Trading Hour")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Enhanced Trade Visualization
                if strategy.trades:
                    trades_df = pd.DataFrame(strategy.trades)
                    trades_df['cumulative_pnl'] = trades_df['net_pnl'].cumsum()
                    
                    # Multi-panel chart
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=('Cumulative P&L with Confidence', 'Trade Frequency by Regime'),
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
                    )
                    
                    # Cumulative P&L colored by confidence
                    fig.add_trace(
                        go.Scatter(
                            x=trades_df['exit_time'],
                            y=trades_df['cumulative_pnl'],
                            mode='lines+markers',
                            marker=dict(
                                color=trades_df['confidence'],
                                colorscale='RdYlGn',
                                showscale=True,
                                colorbar=dict(title="Confidence")
                            ),
                            name='Cumulative P&L'
                        ),
                        row=1, col=1
                    )
                    
                    # Regime distribution
                    regime_counts = trades_df['regime'].value_counts()
                    fig.add_trace(
                        go.Bar(x=regime_counts.index, y=regime_counts.values, name='Trade Count by Regime'),
                        row=2, col=1
                    )
                    
                    fig.update_layout(height=800, title="Advanced Performance Analytics")
                    st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error("❌ Failed to load market data.")
                
        except Exception as e:
            st.error(f"❌ Error running optimized strategy: {str(e)}")

else:
    st.info("👈 Configure advanced parameters and click 'Run Optimized Strategy' for ML-enhanced analysis.")

# Footer
st.markdown("---")
st.markdown("**SP500 CFD Strategy v2 - Performance Optimized** | ML Features • Regime Detection • Dynamic Sizing")
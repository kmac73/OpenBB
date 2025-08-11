"""
UI Helper Functions for Streamlit Interface
Provides utility functions for enhanced user experience
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

class StreamlitProgressTracker:
    """Enhanced progress tracking for long-running operations"""
    
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
        self.start_time = None
    
    def initialize(self, title="Processing..."):
        """Initialize progress tracking"""
        self.progress_bar = st.progress(0, text=title)
        self.status_text = st.empty()
        self.start_time = time.time()
    
    def update(self, progress, message, details=None):
        """Update progress with message"""
        if self.progress_bar:
            self.progress_bar.progress(progress, text=message)
        
        if details and self.status_text:
            self.status_text.info(details)
    
    def complete(self, success_message="Complete!"):
        """Mark as complete and clean up"""
        if self.progress_bar:
            self.progress_bar.progress(100, text=success_message)
        
        if self.status_text:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            self.status_text.success(f"✅ {success_message} (completed in {elapsed_time:.2f}s)")
        
        # Clean up after short delay
        time.sleep(1)
        if self.progress_bar:
            self.progress_bar.empty()
    
    def error(self, error_message):
        """Handle error state"""
        if self.progress_bar:
            self.progress_bar.empty()
        if self.status_text:
            self.status_text.error(f"❌ {error_message}")

def validate_parameters(params):
    """Comprehensive parameter validation"""
    errors = []
    warnings = []
    
    # Date validation
    try:
        start_date = pd.to_datetime(params['start_date']).date()
        end_date = pd.to_datetime(params['end_date']).date()
        
        if start_date >= end_date:
            errors.append("End date must be after start date")
        
        days_diff = (end_date - start_date).days
        if days_diff < 2:
            warnings.append("Very short backtest period may not provide reliable results")
        elif days_diff > 365:
            warnings.append(f"Large date range ({days_diff} days) will require more processing time")
    
    except Exception:
        errors.append("Invalid date format")
    
    # Financial parameter validation
    if params.get('account_balance', 0) < 1000:
        warnings.append("Small account balance may limit position sizing accuracy")
    
    if params.get('risk_pct', 0) > 5.0:
        warnings.append("High risk percentage (>5%) may be aggressive")
    
    if params.get('transaction_cost', 0) > 20:
        warnings.append("High transaction costs may significantly impact returns")
    
    # Risk management validation
    if params.get('risk_reward_ratio', 0) < 1.0:
        warnings.append("Risk/reward ratio below 1.0 means risking more than potential reward")
    
    return errors, warnings

def create_parameter_summary(params):
    """Create formatted parameter summary for display"""
    summary = f"""
    **📊 Data Configuration**
    - Frequency: {params.get('frequency', 'N/A')}
    - Date Range: {params.get('start_date', 'N/A')} to {params.get('end_date', 'N/A')}
    
    **💰 Account Settings**
    - Starting Balance: ${params.get('account_balance', 0):,.2f}
    - Risk per Trade: {params.get('risk_pct', 0):.1f}%
    - Transaction Cost: ${params.get('transaction_cost', 0):.2f}
    
    **⚙️ Strategy Parameters**
    - Stop Loss Distance: ${params.get('stop_loss_distance', 0):.2f}
    - Risk/Reward Ratio: {params.get('risk_reward_ratio', 0):.1f}:1
    - Trailing Stop: {params.get('trailing_stop_pct', 0):.1f}%
    """
    return summary

def display_data_info(data):
    """Display information about loaded data"""
    if data.empty:
        st.error("❌ No data loaded")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Points", f"{len(data):,}")
    
    with col2:
        date_range = (data['date'].max() - data['date'].min()).days
        st.metric("Date Range", f"{date_range} days")
    
    with col3:
        # Calculate average price for the period
        avg_price = data['close'].mean()
        st.metric("Avg Price", f"${avg_price:.2f}")
    
    with col4:
        # Price volatility (std dev)
        price_volatility = data['close'].std()
        st.metric("Volatility", f"${price_volatility:.2f}")
    
    # Data quality indicators
    st.markdown("**📈 Data Overview:**")
    col5, col6 = st.columns(2)
    
    with col5:
        st.write(f"• First Tick: {data['date'].min()}")
        st.write(f"• Price Range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    with col6:
        st.write(f"• Last Tick: {data['date'].max()}")
        # Check for data gaps (simple check)
        expected_intervals = len(data) - 1
        time_diff = data['date'].max() - data['date'].min()
        st.write(f"• Data Quality: {'✅ Good' if len(data) > 100 else '⚠️ Limited'}")

def create_performance_summary_card(metrics):
    """Create a summary performance card"""
    if not metrics:
        return
    
    # Determine overall performance
    total_pnl = metrics.get('total_pnl', 0)
    win_rate = metrics.get('win_rate', 0)
    total_trades = metrics.get('total_trades', 0)
    
    # Performance assessment
    if total_pnl > 0 and win_rate >= 50:
        performance_emoji = "🟢"
        performance_text = "Positive Performance"
        performance_color = "green"
    elif total_pnl > 0:
        performance_emoji = "🟡"
        performance_text = "Mixed Performance"
        performance_color = "orange"
    else:
        performance_emoji = "🔴"
        performance_text = "Negative Performance"
        performance_color = "red"
    
    st.markdown(f"""
    <div style="
        border: 2px solid {performance_color};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: rgba(255,255,255,0.1);
    ">
        <h3>{performance_emoji} {performance_text}</h3>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>Total P&L:</strong> ${total_pnl:,.2f}<br>
                <strong>Win Rate:</strong> {win_rate:.1f}%<br>
                <strong>Total Trades:</strong> {total_trades:,}
            </div>
            <div style="font-size: 48px;">
                {performance_emoji}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def format_duration(minutes):
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes:.0f} min"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes / 60
        return f"{hours:.1f} hrs"
    else:
        days = minutes / 1440
        return f"{days:.1f} days"

def create_trade_summary_table(trades, max_trades=10):
    """Create a formatted table of recent trades"""
    if not trades:
        st.info("No trades to display")
        return
    
    # Convert trades to DataFrame for display
    trade_data = []
    for i, trade in enumerate(trades[-max_trades:], 1):  # Show last N trades
        trade_data.append({
            '#': len(trades) - max_trades + i if len(trades) > max_trades else i,
            'Direction': trade.direction,
            'Entry': f"${trade.entry_price:.2f}",
            'Exit': f"${trade.exit_price:.2f}" if trade.exit_price else "Open",
            'P&L': f"${trade.net_pnl:.2f}" if hasattr(trade, 'net_pnl') else "N/A",
            'Duration': format_duration(trade.duration_minutes) if hasattr(trade, 'duration_minutes') else "N/A",
            'Exit Reason': getattr(trade, 'exit_reason', 'N/A')
        })
    
    if trade_data:
        df = pd.DataFrame(trade_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if len(trades) > max_trades:
            st.caption(f"Showing last {max_trades} of {len(trades)} total trades")

class ParameterPresets:
    """Predefined parameter sets for common strategies"""
    
    @staticmethod
    def get_conservative():
        """Conservative trading parameters"""
        return {
            'risk_pct': 1.0,
            'stop_loss_distance': 75.0,
            'risk_reward_ratio': 3.0,
            'trailing_stop_pct': 1.5,
            'transaction_cost': 5.0
        }
    
    @staticmethod
    def get_balanced():
        """Balanced trading parameters (default)"""
        return {
            'risk_pct': 2.0,
            'stop_loss_distance': 50.0,
            'risk_reward_ratio': 2.0,
            'trailing_stop_pct': 2.0,
            'transaction_cost': 5.0
        }
    
    @staticmethod
    def get_aggressive():
        """Aggressive trading parameters"""
        return {
            'risk_pct': 3.0,
            'stop_loss_distance': 30.0,
            'risk_reward_ratio': 1.5,
            'trailing_stop_pct': 2.5,
            'transaction_cost': 5.0
        }
    
    @staticmethod
    def get_preset_names():
        """Get list of available preset names"""
        return ["Conservative", "Balanced", "Aggressive"]
    
    @staticmethod
    def get_preset(name):
        """Get preset by name"""
        presets = {
            "Conservative": ParameterPresets.get_conservative(),
            "Balanced": ParameterPresets.get_balanced(),
            "Aggressive": ParameterPresets.get_aggressive()
        }
        return presets.get(name, ParameterPresets.get_balanced())

def add_parameter_presets_to_sidebar():
    """Add parameter presets selector to sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Parameter Presets")
    
    preset_names = ["Custom"] + ParameterPresets.get_preset_names()
    selected_preset = st.sidebar.selectbox(
        "Quick Presets",
        preset_names,
        help="Pre-configured parameter sets for different risk profiles"
    )
    
    if selected_preset != "Custom":
        preset_params = ParameterPresets.get_preset(selected_preset)
        st.sidebar.info(f"📋 {selected_preset} preset loaded. You can still adjust individual parameters above.")
        return preset_params
    
    return None
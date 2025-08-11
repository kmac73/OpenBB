"""
SPX Strategy Engine - Professional Trading Strategy Execution
============================================================

High-performance strategy execution engine for SPX CFD trading with comprehensive
position management, risk controls, and performance tracking.

Based on optimized parameters discovered through statistical analysis:
- Entry: 1 BPS triggers (micro-move detection)
- Profit: 6 BPS targets (frequent achievable wins) 
- Stop: 15 BPS limits (controlled loss management)
- Leverage: 20x amplification of small moves

Author: Claude Code Analysis System
Date: August 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class SPXStrategyEngine:
    """
    Professional SPX strategy execution engine with comprehensive metrics tracking.
    
    Features:
    - Intrabar High/Low exit detection
    - Dynamic position tracking and risk management  
    - Comprehensive trade recording with all performance metrics
    - Proper leverage and margin calculations
    - Transaction cost modeling
    """
    
    def __init__(self, params: Dict):
        """
        Initialize strategy engine with user parameters.
        
        Args:
            params: Dictionary containing all strategy parameters
        """
        self.params = params
        self.reset_session()
        
    def reset_session(self):
        """Reset all session variables for new analysis."""
        # Market baseline for entry signals
        self.baseline_price = None
        
        # Position state variables
        self.position_active = False
        self.position_direction = None
        self.position_entry_price = None
        self.position_entry_time = None
        self.current_position_size = None  # Dynamic position sizing
        self.position_stop_loss = None
        self.position_profit_target = None
        self.position_highest_price = None
        self.position_lowest_price = None
        
        # Account balance protection
        self.current_account_balance = self.params['account_balance']
        self.min_account_balance = 0.0  # Prevent going below $0
        self.balance_protection_active = True
        self.trades_blocked_by_balance = 0
        
        # Results tracking
        self.completed_trades = []
        self.tick_data = []
        
    def calculate_bps_change(self, current_price: float, baseline: float) -> float:
        """
        Calculate basis points change between prices.
        
        Args:
            current_price: Current market price
            baseline: Reference price for comparison
            
        Returns:
            Basis points change (positive = price increase)
        """
        if baseline <= 0:
            return 0.0
        return ((current_price - baseline) / baseline) * 10000
    
    def is_trading_hours(self, timestamp: datetime) -> bool:
        """
        Check if timestamp falls within configured trading hours.
        
        Args:
            timestamp: Market data timestamp
            
        Returns:
            True if within trading hours, False otherwise
        """
        time_str = timestamp.strftime('%H:%M')
        return self.params['trading_start'] <= time_str <= self.params['trading_end']
    
    def is_session_end(self, timestamp: datetime) -> bool:
        """
        Check if timestamp is at or after session end time.
        Used to force position closure at end of trading day.
        
        Args:
            timestamp: Market data timestamp
            
        Returns:
            True if at/after session end, False otherwise
        """
        time_str = timestamp.strftime('%H:%M')
        return time_str >= self.params['trading_end']
    
    def can_afford_new_position(self, entry_price: float) -> bool:
        """
        Check if account can afford a new position without risking margin call.
        
        Args:
            entry_price: Proposed entry price for new position
            
        Returns:
            True if position is affordable, False if would risk margin call
        """
        if not self.balance_protection_active:
            return True
            
        # Calculate position size dynamically based on current price
        position_size = self.calculate_position_size(entry_price)
        
        if position_size <= 0:
            return False
            
        # Calculate maximum possible loss for this position
        max_loss_per_position = (
            (self.params['stop_loss_bps'] * entry_price / 10000) *  # BPS to dollar loss per contract
            position_size *                                          # Number of contracts (dynamic)
            self.params['leverage'] +                                # Leverage multiplier
            self.params['round_trip_cost']                          # Transaction costs
        )
        
        # Check if account can survive worst-case scenario
        potential_balance = self.current_account_balance - max_loss_per_position
        
        if potential_balance < self.min_account_balance:
            return False
            
        return True
    
    def calculate_position_size(self, entry_price: float) -> float:
        """
        Calculate appropriate position size based on current market price and risk parameters.
        
        Args:
            entry_price: Current market price for position sizing
            
        Returns:
            Position size in contracts that respects risk management rules
        """
        # Get risk parameters
        risk_per_trade = self.current_account_balance * (self.params.get('account_risk_pct', 2.0) / 100)
        stop_loss_bps = self.params['stop_loss_bps']
        leverage = self.params['leverage']
        
        # Calculate risk per contract: (BPS * Price) / 10000 * leverage
        risk_per_contract = (stop_loss_bps * entry_price / 10000) * leverage
        
        # Position size = Risk budget / Risk per contract
        if risk_per_contract > 0:
            position_size = risk_per_trade / risk_per_contract
        else:
            position_size = 0
            
        # Ensure minimum position size of 1 contract if we can afford it
        if position_size > 0 and position_size < 1:
            if risk_per_contract <= risk_per_trade:
                position_size = 1
            else:
                position_size = 0
                
        return position_size
    
    def update_account_balance(self, pnl: float):
        """
        Update current account balance after trade completion.
        
        Args:
            pnl: Net profit/loss from completed trade
        """
        self.current_account_balance += pnl
        
        # Ensure balance doesn't go below minimum (safety check)
        if self.current_account_balance < self.min_account_balance:
            self.current_account_balance = self.min_account_balance
    
    def check_entry_signal(self, current_price: float) -> Optional[str]:
        """
        Determine if current price triggers entry signal based on BPS movement.
        
        Args:
            current_price: Current market close price
            
        Returns:
            'LONG' for upward breakout, 'SHORT' for downward breakout, None for no signal
        """
        if self.position_active:
            return None
            
        # Check if account can afford new position (balance protection)
        if not self.can_afford_new_position(current_price):
            self.trades_blocked_by_balance += 1
            return None
            
        bps_change = self.calculate_bps_change(current_price, self.baseline_price)
        
        if bps_change >= self.params['entry_trigger_bps']:
            return "LONG"
        elif bps_change <= -self.params['entry_trigger_bps']:
            return "SHORT" 
        return None
    
    def check_exit_conditions(self, high: float, low: float, close: float) -> Optional[Dict]:
        """
        Check for exit conditions using intrabar High/Low analysis.
        
        This is critical for accurate backtesting - uses the actual high/low
        of each bar to detect if stops or targets were hit during the period.
        
        Args:
            high: Bar high price
            low: Bar low price  
            close: Bar close price
            
        Returns:
            Dictionary with exit details if exit triggered, None otherwise
        """
        if not self.position_active:
            return None
            
        if self.position_direction == "LONG":
            # LONG POSITION: Check profit target first (priority), then stop loss
            
            # 1. Profit target: Check if HIGH reached target
            if high >= self.position_profit_target:
                return {
                    'exit_price': self.position_profit_target,
                    'exit_reason': 'PROFIT_TARGET',
                    'triggered_by': f'HIGH {high:.2f} >= TARGET {self.position_profit_target:.2f}'
                }
            
            # 2. Stop loss: Check if LOW hit stop
            elif low <= self.position_stop_loss:
                return {
                    'exit_price': self.position_stop_loss,
                    'exit_reason': 'STOP_LOSS',
                    'triggered_by': f'LOW {low:.2f} <= STOP {self.position_stop_loss:.2f}'
                }
                
        else:  # SHORT POSITION
            # SHORT POSITION: Profit target on downside, stop loss on upside
            
            # 1. Profit target: Check if LOW reached target
            if low <= self.position_profit_target:
                return {
                    'exit_price': self.position_profit_target,
                    'exit_reason': 'PROFIT_TARGET',
                    'triggered_by': f'LOW {low:.2f} <= TARGET {self.position_profit_target:.2f}'
                }
            
            # 2. Stop loss: Check if HIGH hit stop
            elif high >= self.position_stop_loss:
                return {
                    'exit_price': self.position_stop_loss,
                    'exit_reason': 'STOP_LOSS',
                    'triggered_by': f'HIGH {high:.2f} >= STOP {self.position_stop_loss:.2f}'
                }
        
        return None
    
    def calculate_unrealized_pnl(self, current_price: float, include_costs: bool = False) -> float:
        """
        Calculate current unrealized P&L with proper leverage application.
        
        Args:
            current_price: Current market price for P&L calculation
            include_costs: Whether to include transaction costs (for final P&L)
            
        Returns:
            Unrealized P&L in dollars
        """
        if not self.position_active:
            return 0.0
        
        # Calculate raw price difference
        if self.position_direction == "LONG":
            price_diff = current_price - self.position_entry_price
        else:  # SHORT
            price_diff = self.position_entry_price - current_price
        
        # Apply position size and leverage
        gross_pnl = price_diff * self.current_position_size * self.params['leverage']
        
        # Include transaction costs if requested (typically only at trade completion)
        if include_costs:
            return gross_pnl - self.params['round_trip_cost']
        else:
            return gross_pnl
    
    def open_position(self, direction: str, price: float, timestamp: datetime):
        """
        Open new position with calculated stop loss and profit target levels.
        
        Args:
            direction: 'LONG' or 'SHORT'
            price: Entry price
            timestamp: Entry time
        """
        # Calculate position size dynamically based on entry price
        self.current_position_size = self.calculate_position_size(price)
        
        self.position_active = True
        self.position_direction = direction
        self.position_entry_price = price
        self.position_entry_time = timestamp
        self.position_highest_price = price
        self.position_lowest_price = price
        
        # Calculate stop loss and profit target levels using BPS
        stop_loss_bps = self.params['stop_loss_bps']
        profit_target_bps = self.params['profit_target_bps']
        
        if direction == "LONG":
            # LONG: Stop below entry, target above entry
            self.position_stop_loss = price - (stop_loss_bps * price / 10000)
            self.position_profit_target = price + (profit_target_bps * price / 10000)
        else:  # SHORT
            # SHORT: Stop above entry, target below entry  
            self.position_stop_loss = price + (stop_loss_bps * price / 10000)
            self.position_profit_target = price - (profit_target_bps * price / 10000)
            
    def close_position(self, exit_price: float, exit_reason: str, timestamp: datetime, triggered_by: str = ""):
        """
        Close position and record comprehensive trade details.
        
        Args:
            exit_price: Price at which position was closed
            exit_reason: Reason for exit ('PROFIT_TARGET', 'STOP_LOSS', 'END_OF_SESSION')
            timestamp: Exit time
            triggered_by: Detailed trigger description
        """
        if not self.position_active:
            return
            
        # Calculate P&L with and without transaction costs
        gross_pnl = self.calculate_unrealized_pnl(exit_price, include_costs=False)
        net_pnl = self.calculate_unrealized_pnl(exit_price, include_costs=True)
        
        # Calculate additional performance metrics
        duration = timestamp - self.position_entry_time
        duration_minutes = duration.total_seconds() / 60
        
        # Calculate percentage returns
        margin_used = self.params['account_balance'] * (self.params['margin_rate'] / 100)
        pnl_percentage = (net_pnl / margin_used) * 100 if margin_used > 0 else 0
        
        # Determine win/loss
        is_winner = net_pnl > 0
        
        # Record comprehensive trade details
        trade_record = {
            # Basic Trade Info
            'trade_number': len(self.completed_trades) + 1,
            'direction': self.position_direction,
            'entry_time': self.position_entry_time,
            'entry_price': self.position_entry_price,
            'exit_time': timestamp,
            'exit_price': exit_price,
            'duration_minutes': duration_minutes,
            
            # Position Details
            'stop_loss': self.position_stop_loss,
            'profit_target': self.position_profit_target,
            'position_size': self.current_position_size,
            
            # P&L Analysis
            'gross_pnl': gross_pnl,
            'net_pnl': net_pnl,
            'pnl_percentage': pnl_percentage,
            'transaction_costs': self.params['round_trip_cost'],
            'is_winner': is_winner,
            
            # Exit Analysis
            'exit_reason': exit_reason,
            'triggered_by': triggered_by,
            
            # Risk Metrics (per trade)
            'risk_amount': abs(self.position_entry_price - self.position_stop_loss) * self.current_position_size * self.params['leverage'],
            'reward_amount': abs(self.position_profit_target - self.position_entry_price) * self.current_position_size * self.params['leverage'],
            
            # Position Extremes
            'position_high': self.position_highest_price,
            'position_low': self.position_lowest_price,
            
            # Market Context
            'baseline_before': self.baseline_price,
            'baseline_after': exit_price  # Reset baseline to exit price
        }
        
        self.completed_trades.append(trade_record)
        
        # Update account balance with trade P&L (balance protection)
        self.update_account_balance(net_pnl)
        
        # Reset baseline price to exit price for next signal
        self.baseline_price = exit_price
        
        # Clear position state
        self.position_active = False
        self.position_direction = None
        self.position_entry_price = None
        self.position_entry_time = None
        self.position_stop_loss = None
        self.position_profit_target = None
        self.position_highest_price = None
        self.position_lowest_price = None
        
    def update_position_tracking(self, high: float, low: float):
        """
        Update position extreme price tracking for trailing stops and analysis.
        
        Args:
            high: Current bar high
            low: Current bar low
        """
        if not self.position_active:
            return
            
        # Track position extremes
        if self.position_highest_price is None:
            self.position_highest_price = high
        else:
            self.position_highest_price = max(self.position_highest_price, high)
            
        if self.position_lowest_price is None:
            self.position_lowest_price = low
        else:
            self.position_lowest_price = min(self.position_lowest_price, low)
    
    def run_strategy(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Execute strategy on market data and return comprehensive results.
        
        Args:
            data: Market data DataFrame with columns ['Datetime', 'Open', 'High', 'Low', 'Close']
            
        Returns:
            Tuple of (tick_by_tick_results_df, completed_trades_list)
        """
        self.reset_session()
        
        if data.empty:
            print("❌ No market data provided")
            return pd.DataFrame(), []
        
        # Initialize baseline price (typically previous day close, here use first open)
        self.baseline_price = data.iloc[0]['Open']
        
        total_bars = len(data)
        trading_bars = 0
        
        # Process each market bar
        for idx, row in data.iterrows():
            # Convert datetime if needed
            if isinstance(row['Datetime'], str):
                current_time = pd.to_datetime(row['Datetime'])
            else:
                current_time = row['Datetime']
            
            # FORCE SESSION END CLOSURE - Close any active positions at session end
            if self.position_active and self.is_session_end(current_time):
                current_close = row['Close']
                self.close_position(
                    current_close,
                    'END_OF_SESSION',
                    current_time,
                    f'Session end at {current_time.strftime("%H:%M")} - position forced closed'
                )
                # Reset baseline for next session
                self.baseline_price = current_close
            
            # Skip bars outside trading hours (after checking for session end closure)
            if not self.is_trading_hours(current_time):
                continue
                
            trading_bars += 1
            current_open = row['Open']
            current_high = row['High']
            current_low = row['Low'] 
            current_close = row['Close']
            
            # POSITION MANAGEMENT SECTION
            if self.position_active:
                # Update position tracking first
                self.update_position_tracking(current_high, current_low)
                
                # Check for exit conditions using High/Low data
                exit_result = self.check_exit_conditions(current_high, current_low, current_close)
                
                if exit_result:
                    # Exit triggered - close position
                    self.close_position(
                        exit_result['exit_price'],
                        exit_result['exit_reason'], 
                        current_time,
                        exit_result['triggered_by']
                    )
                    # Position is now closed, continue to check for new entry
            
            # ENTRY SIGNAL SECTION
            if not self.position_active:
                # Check for new entry signal
                signal = self.check_entry_signal(current_close)
                if signal:
                    self.open_position(signal, current_close, current_time)
            
            # TICK DATA RECORDING
            # Record current market state for analysis
            current_unrealized = self.calculate_unrealized_pnl(current_close) if self.position_active else 0.0
            
            tick_record = {
                'datetime': current_time,
                'open': current_open,
                'high': current_high, 
                'low': current_low,
                'close': current_close,
                'position_active': self.position_active,
                'position_direction': self.position_direction,
                'entry_price': self.position_entry_price if self.position_active else None,
                'stop_loss': self.position_stop_loss if self.position_active else None,
                'profit_target': self.position_profit_target if self.position_active else None,
                'unrealized_pnl': current_unrealized,
                'baseline_price': self.baseline_price,
                'bps_from_baseline': self.calculate_bps_change(current_close, self.baseline_price)
            }
            
            self.tick_data.append(tick_record)
        
        # HANDLE END-OF-SESSION POSITION
        if self.position_active:
            last_row = data.iloc[-1]
            last_time = pd.to_datetime(last_row['Datetime']) if isinstance(last_row['Datetime'], str) else last_row['Datetime']
            
            self.close_position(
                last_row['Close'],
                'END_OF_SESSION',
                last_time,
                'Trading session ended with active position'
            )
        
        # Convert results to DataFrames
        tick_df = pd.DataFrame(self.tick_data)
        
        # Execution summary
        total_trades = len(self.completed_trades)
        print(f"📊 Strategy Execution Summary:")
        print(f"   Total Bars Processed: {total_bars:,}")
        print(f"   Trading Hours Bars: {trading_bars:,}")
        print(f"   Trades Completed: {total_trades}")
        
        if total_trades > 0:
            winners = len([t for t in self.completed_trades if t['is_winner']])
            win_rate = (winners / total_trades) * 100
            total_pnl = sum([t['net_pnl'] for t in self.completed_trades])
            
            print(f"   Win Rate: {win_rate:.1f}% ({winners}/{total_trades})")
            print(f"   Total Net P&L: ${total_pnl:,.2f}")
            
        # Balance protection summary
        if self.balance_protection_active:
            print(f"\n💰 ACCOUNT BALANCE PROTECTION:")
            print(f"   Starting Balance: ${self.params['account_balance']:,.2f}")
            print(f"   Final Balance: ${self.current_account_balance:,.2f}")
            print(f"   Minimum Allowed: ${self.min_account_balance:,.2f}")
            print(f"   Trades Blocked by Balance: {self.trades_blocked_by_balance}")
            
            if self.current_account_balance <= self.min_account_balance:
                print(f"   ⚠️ BALANCE PROTECTION TRIGGERED - Trading stopped to prevent margin call")
            else:
                print(f"   ✅ Account protected from margin call")
        
        return tick_df, self.completed_trades


class StrategyPerformanceAnalyzer:
    """
    Comprehensive performance analysis for strategy results.
    
    Calculates professional-grade metrics including Sharpe ratio, VaR,
    drawdown analysis, and risk-adjusted returns.
    """
    
    @staticmethod
    def calculate_comprehensive_metrics(trades: List[Dict], account_balance: float, margin_rate: float) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            trades: List of completed trade dictionaries
            account_balance: Total account capital
            margin_rate: Margin requirement percentage
            
        Returns:
            Dictionary containing all performance metrics
        """
        if not trades:
            return {"error": "No trades to analyze", "total_trades": 0}
        
        # Convert trades to DataFrame for easier analysis
        trades_df = pd.DataFrame(trades)
        
        # BASIC TRADE STATISTICS
        total_trades = len(trades)
        winning_trades = len(trades_df[trades_df['net_pnl'] > 0])
        losing_trades = len(trades_df[trades_df['net_pnl'] <= 0])
        win_rate = (winning_trades / total_trades) * 100
        
        # P&L METRICS
        gross_pnl = trades_df['gross_pnl'].sum()
        net_pnl = trades_df['net_pnl'].sum()
        transaction_costs = trades_df['transaction_costs'].sum()
        
        avg_win = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['net_pnl'] <= 0]['net_pnl'].mean() if losing_trades > 0 else 0
        
        largest_win = trades_df['net_pnl'].max()
        largest_loss = trades_df['net_pnl'].min()
        
        # RISK-ADJUSTED METRICS
        returns = trades_df['net_pnl'].values
        avg_return = returns.mean()
        return_std = returns.std() if len(returns) > 1 else 0
        sharpe_ratio = avg_return / return_std if return_std > 0 else 0
        
        # VALUE AT RISK (95% confidence level)
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
        
        # RETURN ON MARGIN
        margin_required = account_balance * (margin_rate / 100)
        return_on_margin = (net_pnl / margin_required) * 100 if margin_required > 0 else 0
        
        # PROFIT FACTOR
        gross_profit = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].sum()
        gross_loss = abs(trades_df[trades_df['net_pnl'] <= 0]['net_pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # DRAWDOWN ANALYSIS
        cumulative_pnl = trades_df['net_pnl'].cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdown = cumulative_pnl - running_max
        max_drawdown = drawdown.min()
        
        # DURATION ANALYSIS
        avg_duration = trades_df['duration_minutes'].mean()
        max_duration = trades_df['duration_minutes'].max()
        min_duration = trades_df['duration_minutes'].min()
        
        # EXPECTANCY
        expectancy = avg_return  # Expected value per trade
        
        return {
            # Basic Statistics
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            
            # P&L Metrics  
            'gross_pnl': gross_pnl,
            'net_pnl': net_pnl,
            'transaction_costs': transaction_costs,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            
            # Risk Metrics
            'sharpe_ratio': sharpe_ratio,
            'var_95': var_95,
            'return_on_margin': return_on_margin,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            
            # Duration Metrics
            'avg_duration_minutes': avg_duration,
            'max_duration_minutes': max_duration,
            'min_duration_minutes': min_duration,
            
            # Additional Metrics
            'expectancy': expectancy,
            'risk_reward_ratio': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
            'return_std': return_std
        }


if __name__ == "__main__":
    print("SPX Strategy Engine - Professional Trading System")
    print("=" * 50)
    print("Ready for import and execution")
    print("\nUsage:")
    print("  from SPX_Strategy_Engine import SPXStrategyEngine, StrategyPerformanceAnalyzer")
    print("  engine = SPXStrategyEngine(params)")
    print("  results, trades = engine.run_strategy(data)")
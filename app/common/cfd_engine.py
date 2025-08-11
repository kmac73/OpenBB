"""
CFD Trading Engine - Core Implementation
Implements 2 basis point trigger strategy with opening price reset logic
"""
import pandas as pd
from datetime import datetime, time, date
from typing import Dict, List, Optional, Any
import numpy as np


class Trade:
    """Individual trade representation"""
    
    def __init__(self, direction: str, entry_price: float, entry_time: datetime,
                 stop_loss: float, profit_target: float, position_size: float, costs: float):
        self.direction = direction
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.stop_loss = stop_loss
        self.profit_target = profit_target
        self.position_size = position_size
        self.costs = costs
        
        # Set on exit
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.exit_reason: str = ""
        self.duration_minutes: int = 0
        self.gross_pnl: float = 0.0
        self.net_pnl: float = 0.0
        
    def close_trade(self, exit_price: float, exit_time: datetime, exit_reason: str):
        """Close the trade and calculate P&L"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = exit_reason
        
        # Calculate duration
        self.duration_minutes = int((exit_time - self.entry_time).total_seconds() / 60)
        
        # Calculate P&L
        if self.direction == "LONG":
            price_diff = exit_price - self.entry_price
        else:  # SHORT
            price_diff = self.entry_price - exit_price
            
        self.gross_pnl = price_diff * self.position_size
        self.net_pnl = self.gross_pnl - self.costs


class CFDTradingEngine:
    """
    CFD Trading Engine implementing 2 basis point trigger strategy
    
    Key Features:
    - 2bps trigger for LONG/SHORT entries
    - Opening price reset daily + after trade exits
    - Market hours enforcement (9:30-15:30 entry, 16:00 force close)
    - Risk management with stop loss and profit targets
    """
    
    def __init__(self, account_balance: float, risk_pct: float, transaction_cost: float,
                 stop_loss_distance: float = 50.0, risk_reward_ratio: float = 2.0,
                 trailing_stop_pct: float = 1.0, margin_rate: float = 0.05,
                 risk_free_rate: float = 3.0, frequency: str = "5M",
                 start_date: str = None, end_date: str = None):
        
        # Account parameters
        self.account_balance = float(account_balance)
        self.risk_pct = float(risk_pct)
        self.transaction_cost = float(transaction_cost)
        self.stop_loss_distance = float(stop_loss_distance)
        self.risk_reward_ratio = float(risk_reward_ratio)
        self.trailing_stop_pct = float(trailing_stop_pct)
        self.margin_rate = float(margin_rate)
        self.risk_free_rate = float(risk_free_rate)
        self.frequency = frequency
        self.start_date = start_date
        self.end_date = end_date
        
        # Trading state
        self.opening_price: Optional[float] = None
        self.current_date: Optional[date] = None
        self.position_active: bool = False
        self.current_position: Optional[Trade] = None
        
        # Trade tracking
        self.all_trades: List[Trade] = []
        self.daily_trades: List[Trade] = []
        
        # Market hours
        self.market_open = time(9, 30)
        self.entry_cutoff = time(15, 30)  # Last entry time
        self.force_close = time(16, 0)    # Force close time
        
    def process_market_tick(self, timestamp: datetime, tick_data: Dict[str, float]):
        """Process a single market tick"""
        tick_time = timestamp.time()
        tick_date = timestamp.date()
        
        # LOG EVERY TICK OF PRICE CHANGE
        print(f"📊 TICK: {timestamp} | Open: ${tick_data['open']:.2f} | High: ${tick_data['high']:.2f} | Low: ${tick_data['low']:.2f} | Close: ${tick_data['close']:.2f}")
        if self.opening_price is not None:
            price_change = tick_data['open'] - self.opening_price
            bps_change = (price_change / self.opening_price) * 10000
            print(f"   📈 vs Opening ${self.opening_price:.2f}: Change ${price_change:+.2f} ({bps_change:+.2f} bps)")
        
        # Detect new trading day - only process opening price on the first 9:30 AM tick of new day
        if self.current_date is None or tick_date != self.current_date:
            if tick_time == self.market_open:  # 9:30 AM tick
                self.detect_new_trading_day(timestamp, tick_data['open'])
                # Do NOT check for signals on the same tick as opening price reset
                # The opening price must be established first before measuring 2bps movement
                return
        
        # Force close at 4:00 PM - use open price for consistency
        if tick_time == self.force_close and self.position_active:
            print(f"🕐 FORCE CLOSE TIME: {tick_time}")
            self._force_close_position(tick_data['open'], timestamp)
            
        # Check for trade signals if no active position
        # Only check after opening price has been established (not on the 9:30 AM opening tick)
        # Use OPEN price throughout the strategy, not close price
        if not self.position_active and self.can_enter_new_trade(timestamp) and self.opening_price is not None:
            signal = self.check_2bps_trigger(tick_data['open'])
            if signal:
                self._enter_position(signal, tick_data['open'], timestamp)
                
        # Check exit conditions if position is active
        elif self.position_active:
            self._check_exit_conditions(tick_data, timestamp)
    
    def detect_new_trading_day(self, timestamp: datetime, opening_price: float) -> bool:
        """Detect new trading day and reset opening price"""
        new_date = timestamp.date()
        
        # Assert no active position when day changes (should be handled by force close)
        assert not self.position_active, "Active position detected at day change - should have been force closed"
        
        print(f"\n🌅 NEW TRADING DAY: {new_date}")
        print(f"📈 Opening price set to: ${opening_price:.2f}")
        
        # Reset for new day
        self.current_date = new_date
        self.opening_price = opening_price
        self.daily_trades = []
        
        return True
    
    def check_2bps_trigger(self, current_price: float) -> Optional[str]:
        """Check for 2 basis point trigger conditions"""
        if self.opening_price is None:
            return None
            
        # Calculate basis points change
        bps_change = ((current_price - self.opening_price) / self.opening_price) * 10000
        
        # Debug output for trigger detection
        print(f"🎯 2bps Trigger Check: ${current_price:.2f} vs Opening ${self.opening_price:.2f}")
        print(f"   BPS Change: {bps_change:.2f} (LONG >=2.0, SHORT <=-2.0)")
        
        # Check for LONG trigger (price up 2+ bps)
        if bps_change >= 2.0:
            print(f"✅ LONG TRIGGER HIT! {bps_change:.2f} bps >= 2.0 bps")
            return "LONG"
            
        # Check for SHORT trigger (price down 2+ bps)  
        elif bps_change <= -2.0:
            print(f"✅ SHORT TRIGGER HIT! {bps_change:.2f} bps <= -2.0 bps")
            return "SHORT"
        
        print(f"⏳ No trigger: {bps_change:.2f} bps not >= 2.0 or <= -2.0")    
        return None
    
    def can_enter_new_trade(self, timestamp: datetime) -> bool:
        """Check if new trades can be entered (market hours enforcement)"""
        current_time = timestamp.time()
        return self.market_open <= current_time <= self.entry_cutoff
    
    def calculate_position_size(self, entry_price: float = None, stop_loss: float = None, 
                              stop_loss_distance: float = None) -> float:
        """
        Calculate position size based on risk percentage
        
        Can be called with either:
        1. entry_price and stop_loss parameters
        2. stop_loss_distance parameter (uses default risk calculation)
        """
        risk_amount = self.account_balance * (self.risk_pct / 100)
        
        if stop_loss_distance is not None:
            # Test interface: use stop_loss_distance directly
            price_risk = stop_loss_distance
        elif entry_price is not None and stop_loss is not None:
            # Production interface: calculate from entry and stop prices
            price_risk = abs(entry_price - stop_loss)
        else:
            raise ValueError("Must provide either (entry_price, stop_loss) or stop_loss_distance")
        
        if price_risk <= 0:
            raise ValueError("Invalid stop loss: price risk must be positive")
            
        position_size = risk_amount / price_risk
        return position_size
    
    def _enter_position(self, direction: str, entry_price: float, timestamp: datetime):
        """Enter a new position"""
        # Prevent multiple active positions
        if self.position_active:
            return  # Do not enter new position if one is already active
            
        print(f"\n=== ENTERING {direction} POSITION ===")
        print("**Risk & Position Sizing**")
        print(f"Account Balance ($)|input: ${self.account_balance:,.2f}")
        print(f"Account Risk per Trade (%)|input: {self.risk_pct:.2f}%")
        print(f"Initial Stop-Loss Distance ($)|input: ${self.stop_loss_distance:.2f}")
        
        # Calculate stop loss and profit target
        if direction == "LONG":
            stop_loss = entry_price - self.stop_loss_distance
            profit_target = entry_price + (self.stop_loss_distance * self.risk_reward_ratio)
        else:  # SHORT
            stop_loss = entry_price + self.stop_loss_distance
            profit_target = entry_price - (self.stop_loss_distance * self.risk_reward_ratio)
            
        # Calculate risk amounts
        risk_per_trade = self.account_balance * (self.risk_pct / 100)
        risk_per_contract = abs(entry_price - stop_loss)
        position_size = self.calculate_position_size(entry_price, stop_loss)
        
        print(f"Risk per Trade ($)|calculated: ${risk_per_trade:.2f}")
        print(f"Risk per Contract ($)|calculated: ${risk_per_contract:.2f}")
        print(f"Position Size (Number of CFDs)|calculated: {position_size:.4f}")
        
        print("**Trade Setup**")
        print(f"Opening Price ($)|input: ${self.opening_price:.2f}")
        print(f"Margin Rate (%)|input: {self.margin_rate:.2f}%")
        
        leverage_ratio = 1 / (self.margin_rate / 100)
        notional_position_value = position_size * entry_price
        margin_required = notional_position_value * (self.margin_rate / 100)
        
        print(f"Leverage Ratio|calculated: {leverage_ratio:.2f}x")
        print(f"Notional Position Value ($)|calculated: ${notional_position_value:.2f}")
        print(f"Margin Required ($)|calculated: ${margin_required:.2f}")
        
        print("**Scenario Analysis**")
        print(f"Current Market Price ($)|input: ${entry_price:.2f}")
        print(f"Risk/Reward Ratio|input: {self.risk_reward_ratio:.2f}")
        print(f"Profit Target Price ($)|calculated: ${profit_target:.2f}")
        print(f"Initial Stop-Loss Price ($)|calculated: ${stop_loss:.2f}")
        print(f"Trailing Stop Percentage (%)|input: {self.trailing_stop_pct:.2f}%")
        
        # Create trade
        trade = Trade(
            direction=direction,
            entry_price=entry_price,
            entry_time=timestamp,
            stop_loss=stop_loss,
            profit_target=profit_target,
            position_size=position_size,
            costs=self.transaction_cost
        )
        
        self.current_position = trade
        self.position_active = True
        
        print(f"✅ {direction} position entered at ${entry_price:.2f} on {timestamp}")
        print(f"   Stop Loss: ${stop_loss:.2f} | Profit Target: ${profit_target:.2f}")
        print("=" * 50)
    
    def _check_exit_conditions(self, tick_data: Dict[str, float], timestamp: datetime):
        """Check exit conditions for active position - using open price only"""
        if not self.position_active or not self.current_position:
            return
            
        current_price = tick_data['open']  # Use open price consistently
        direction = self.current_position.direction
        
        # Monitor position status on every tick (since we're debugging single day)
        print(f"   🎯 {direction} Position: Stop ${self.current_position.stop_loss:.2f} | Target ${self.current_position.profit_target:.2f}")
        if direction == "LONG":
            stop_hit = current_price <= self.current_position.stop_loss
            target_hit = current_price >= self.current_position.profit_target
            print(f"   📊 LONG Check: Stop({stop_hit}) Target({target_hit})")
        else:
            stop_hit = current_price >= self.current_position.stop_loss  
            target_hit = current_price <= self.current_position.profit_target
            print(f"   📊 SHORT Check: Stop({stop_hit}) Target({target_hit})")
        
        # Check profit target and stop loss using open price only
        if self.current_position.direction == "LONG":
            if current_price >= self.current_position.profit_target:
                print(f"🎯 PROFIT TARGET HIT! Price ${current_price:.2f} >= Target ${self.current_position.profit_target:.2f}")
                self._exit_position(self.current_position.profit_target, timestamp, "PROFIT_TARGET")
                return
            elif current_price <= self.current_position.stop_loss:
                print(f"🛑 STOP LOSS HIT! Price ${current_price:.2f} <= Stop ${self.current_position.stop_loss:.2f}")
                self._exit_position(self.current_position.stop_loss, timestamp, "STOP_LOSS")
                return
        else:  # SHORT
            if current_price <= self.current_position.profit_target:
                print(f"🎯 PROFIT TARGET HIT! Price ${current_price:.2f} <= Target ${self.current_position.profit_target:.2f}")
                self._exit_position(self.current_position.profit_target, timestamp, "PROFIT_TARGET")
                return
            elif current_price >= self.current_position.stop_loss:
                print(f"🛑 STOP LOSS HIT! Price ${current_price:.2f} >= Stop ${self.current_position.stop_loss:.2f}")
                self._exit_position(self.current_position.stop_loss, timestamp, "STOP_LOSS")
                return
    
    def _exit_position(self, exit_price: float, timestamp: datetime, exit_reason: str):
        """Exit the current position"""
        if not self.current_position:
            return
            
        # Close the trade
        self.current_position.close_trade(exit_price, timestamp, exit_reason)
        
        print(f"\n=== EXITING POSITION: {exit_reason} ===")
        print("**Scenario Analysis**")
        print(f"Highest/Lowest Price Reached ($)|input: ${exit_price:.2f}")
        print(f"Final Exit Price ($)|calculated: ${exit_price:.2f}")
        
        print("**Final Results**")
        print(f"Gross Profit / Loss ($)|calculated: ${self.current_position.gross_pnl:.2f}")
        print(f"Round Trip Transaction Cost|input: ${self.transaction_cost:.2f}")
        print(f"Net Profit|calculated: ${self.current_position.net_pnl:.2f}")
        
        # Calculate return on margin
        notional_value = self.current_position.position_size * self.current_position.entry_price
        margin_used = notional_value * (self.margin_rate / 100)
        return_on_margin = (self.current_position.net_pnl / margin_used) * 100 if margin_used > 0 else 0
        print(f"Return on Margin (%)|calculated: {return_on_margin:.2f}%")
        
        # Add to completed trades
        self.all_trades.append(self.current_position)
        self.daily_trades.append(self.current_position)
        
        # Reset opening price to exit price (as specified in requirements)
        old_opening_price = self.opening_price
        self.opening_price = exit_price
        
        print(f"🔄 Opening price reset: ${old_opening_price:.2f} → ${self.opening_price:.2f}")
        print(f"❌ Position closed: {self.current_position.direction} from ${self.current_position.entry_price:.2f} to ${exit_price:.2f}")
        print(f"   Duration: {self.current_position.duration_minutes} minutes | P&L: ${self.current_position.net_pnl:.2f}")
        print("=" * 50)
        
        # Clear position
        self.current_position = None
        self.position_active = False
    
    def _force_close_position(self, close_price: float, timestamp: datetime):
        """Force close position at end of day"""
        if self.position_active:
            self._exit_position(close_price, timestamp, "END_OF_DAY_FORCE_CLOSE")
    
    def end_of_day_summary(self) -> Dict[str, Any]:
        """Generate end of day summary"""
        if not self.daily_trades:
            return None
            
        daily_gross_pnl = sum(trade.gross_pnl for trade in self.daily_trades)
        daily_net_pnl = sum(trade.net_pnl for trade in self.daily_trades)
        
        return {
            'date': self.current_date,
            'trades_count': len(self.daily_trades),
            'daily_gross_pnl': daily_gross_pnl,
            'daily_net_pnl': daily_net_pnl
        }
    
    # Public methods for testing interface compatibility
    def enter_trade(self, direction: str, entry_price: float, timestamp: datetime):
        """Public interface to enter trade - calls private implementation"""
        return self._enter_position(direction, entry_price, timestamp)
    
    def close_position(self, exit_price: float, exit_reason: str, timestamp: datetime):
        """Public interface to close position - calls private implementation"""
        return self._exit_position(exit_price, timestamp, exit_reason)
    
    def force_close_position(self, close_price: float, timestamp: datetime):
        """Public interface to force close position - calls private implementation"""
        return self._force_close_position(close_price, timestamp)
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
        
        # Detect new trading day
        if self.current_date is None or tick_date != self.current_date:
            if tick_time == self.market_open:  # 9:30 AM tick
                self.detect_new_trading_day(timestamp, tick_data['open'])
        
        # Force close at 4:00 PM
        if tick_time == self.force_close and self.position_active:
            self._force_close_position(tick_data['close'], timestamp)
            
        # Check for trade signals if no active position
        if not self.position_active and self.can_enter_new_trade(timestamp):
            signal = self.check_2bps_trigger(tick_data['close'])
            if signal:
                self._enter_position(signal, tick_data['close'], timestamp)
                
        # Check exit conditions if position is active
        elif self.position_active:
            self._check_exit_conditions(tick_data, timestamp)
    
    def detect_new_trading_day(self, timestamp: datetime, opening_price: float) -> bool:
        """Detect new trading day and reset opening price"""
        new_date = timestamp.date()
        
        # Assert no active position when day changes (should be handled by force close)
        assert not self.position_active, "Active position detected at day change - should have been force closed"
        
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
        
        # Check for LONG trigger (price up 2+ bps)
        if bps_change >= 2.0:
            return "LONG"
            
        # Check for SHORT trigger (price down 2+ bps)  
        elif bps_change <= -2.0:
            return "SHORT"
            
        return None
    
    def can_enter_new_trade(self, timestamp: datetime) -> bool:
        """Check if new trades can be entered (market hours enforcement)"""
        current_time = timestamp.time()
        return self.market_open <= current_time <= self.entry_cutoff
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk percentage"""
        risk_amount = self.account_balance * (self.risk_pct / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            raise ValueError("Invalid stop loss: must be different from entry price")
            
        position_size = risk_amount / price_risk
        return position_size
    
    def _enter_position(self, direction: str, entry_price: float, timestamp: datetime):
        """Enter a new position"""
        # Calculate stop loss and profit target
        if direction == "LONG":
            stop_loss = entry_price - self.stop_loss_distance
            profit_target = entry_price + (self.stop_loss_distance * self.risk_reward_ratio)
        else:  # SHORT
            stop_loss = entry_price + self.stop_loss_distance
            profit_target = entry_price - (self.stop_loss_distance * self.risk_reward_ratio)
            
        # Calculate position size
        position_size = self.calculate_position_size(entry_price, stop_loss)
        
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
    
    def _check_exit_conditions(self, tick_data: Dict[str, float], timestamp: datetime):
        """Check exit conditions for active position"""
        if not self.position_active or not self.current_position:
            return
            
        current_price = tick_data['close']
        high = tick_data['high']
        low = tick_data['low']
        
        # Check profit target (use high/low for more realistic fills)
        if self.current_position.direction == "LONG":
            if high >= self.current_position.profit_target:
                self._exit_position(self.current_position.profit_target, timestamp, "PROFIT_TARGET")
                return
            elif low <= self.current_position.stop_loss:
                self._exit_position(self.current_position.stop_loss, timestamp, "STOP_LOSS")
                return
        else:  # SHORT
            if low <= self.current_position.profit_target:
                self._exit_position(self.current_position.profit_target, timestamp, "PROFIT_TARGET")
                return
            elif high >= self.current_position.stop_loss:
                self._exit_position(self.current_position.stop_loss, timestamp, "STOP_LOSS")
                return
    
    def _exit_position(self, exit_price: float, timestamp: datetime, exit_reason: str):
        """Exit the current position"""
        if not self.current_position:
            return
            
        # Close the trade
        self.current_position.close_trade(exit_price, timestamp, exit_reason)
        
        # Add to completed trades
        self.all_trades.append(self.current_position)
        self.daily_trades.append(self.current_position)
        
        # Reset opening price to exit price (as specified in requirements)
        self.opening_price = exit_price
        
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
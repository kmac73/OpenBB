"""
Limited Debug Logger - Phase 1 Implementation
Implements limited console output with full file logging
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import os
from pathlib import Path


class LimitedDebugLogger:
    """
    Limited debug logger with console output restriction
    
    Features:
    - Maximum 5 trades per day to console
    - Unlimited file logging
    - Overflow message when limit exceeded
    - Performance-optimized with enable/disable
    """
    
    def __init__(self, enabled: bool = True, max_daily_trades: int = 5, log_file_path: Optional[str] = None):
        self.enabled = enabled
        self.max_daily_trades = max_daily_trades
        self.console_count = 0
        self.current_date: Optional[date] = None
        self.overflow_shown = False
        
        # File logging
        self.log_file_path = log_file_path or "logs/backtest_debug.log"
        self.file_lines: List[str] = []
        self.console_lines: List[str] = []
        
        # Ensure log directory exists
        Path(self.log_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    def log_trade_event(self, timestamp: datetime, message: str):
        """Log a trade event with console/file routing"""
        if not self.enabled:
            return
            
        # Reset counter for new day
        if self.current_date != timestamp.date():
            self.current_date = timestamp.date()
            self.console_count = 0
            self.overflow_shown = False
            
        # Always log to file
        self._log_to_file(timestamp, message)
        
        # Log to console only if under daily limit
        if self.console_count < self.max_daily_trades:
            self._log_to_console(message)
            self.console_count += 1
        elif not self.overflow_shown:
            self._log_to_console("... [Additional trades logged to file only]")
            self.overflow_shown = True
    
    def _log_to_file(self, timestamp: datetime, message: str):
        """Log message to file"""
        timestamped_message = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        self.file_lines.append(timestamped_message)
        
        # Write to actual file
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(timestamped_message + '\n')
        except Exception:
            pass  # Gracefully handle file write errors
    
    def _log_to_console(self, message: str):
        """Log message to console"""
        self.console_lines.append(message)
        print(message)  # Actual console output
    
    def log_entry(self, timestamp: datetime, direction: str, price: float, bps_change: float):
        """Log trade entry"""
        message = f"ENTRY: {direction} @{price:.2f} [2bps trigger: {bps_change:+.1f}bps]"
        self.log_trade_event(timestamp, message)
    
    def log_exit(self, timestamp: datetime, direction: str, entry_price: float, 
                exit_price: float, pnl: float, reason: str):
        """Log trade exit"""
        pnl_str = f"{pnl:+.2f}" if pnl != 0 else f"{pnl:.2f}"
        message = f"EXIT: {direction} {entry_price:.2f}->{exit_price:.2f}, P&L: ${pnl_str}, [{reason}]"
        self.log_trade_event(timestamp, message)
    
    def log_day_close(self, timestamp: datetime, trade_count: int, gross_pnl: float, net_pnl: float):
        """Log end of day summary"""
        message = f"DAY_CLOSE: {trade_count} trades, Gross P&L: ${gross_pnl:+.2f}, Net P&L: ${net_pnl:+.2f}"
        self.log_trade_event(timestamp, message)
    
    def get_console_output(self) -> List[str]:
        """Get console output lines for testing"""
        return self.console_lines.copy()
    
    def get_file_output(self) -> List[str]:
        """Get file output lines for testing"""
        return self.file_lines.copy()
    
    def reset_daily_counters(self):
        """Reset daily counters (called automatically on date change)"""
        self.console_count = 0
        self.overflow_shown = False
        self.current_date = None
    
    def set_enabled(self, enabled: bool):
        """Enable or disable logging"""
        self.enabled = enabled


class DebugOutputFormatter:
    """Format debug output messages consistently"""
    
    @staticmethod
    def format_entry(timestamp: datetime, direction: str, price: float, bps_change: float) -> str:
        """Format entry message"""
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{time_str} - ENTRY: {direction} @{price:.2f} [2bps trigger: {bps_change:+.1f}bps]"
    
    @staticmethod
    def format_exit(timestamp: datetime, direction: str, entry_price: float, 
                   exit_price: float, pnl: float, reason: str) -> str:
        """Format exit message"""
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        pnl_str = f"{pnl:+.2f}" if pnl != 0 else f"{pnl:.2f}"
        return f"{time_str} - EXIT: {direction} {entry_price:.2f}->{exit_price:.2f}, P&L: ${pnl_str}, [{reason}]"
    
    @staticmethod
    def format_day_close(timestamp: datetime, trade_count: int, gross_pnl: float, net_pnl: float) -> str:
        """Format day close message"""
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{time_str} - DAY_CLOSE: {trade_count} trades, Gross P&L: ${gross_pnl:+.2f}, Net P&L: ${net_pnl:+.2f}"
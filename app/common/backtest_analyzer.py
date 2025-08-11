"""
Backtest Analyzer - Calculate All 22 Performance Metrics
Implements comprehensive analysis of backtest results
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import math


class PerformanceMetrics:
    """Container for performance metrics"""
    pass


class BacktestAnalyzer:
    """
    Comprehensive backtest analyzer calculating all 22 required metrics
    
    Metrics calculated:
    1-5: Trade counts (total, winning, losing, long, short)
    6: Win rate percentage
    7-9: P&L metrics (total, gross, costs)
    10-11: Average win/loss
    12-13: Drawdown metrics (max, average)
    14-15: Return metrics (total return, final equity)
    16-17: Ratios (profit factor, cost ratio)  
    18-20: Duration metrics (shortest, longest, average)
    21: Sharpe ratio
    22: Value at Risk (VaR)
    """
    
    def __init__(self, risk_free_rate: float = 0.03):
        """Initialize with risk-free rate (default 3% for 3M treasury)"""
        self.risk_free_rate = risk_free_rate
        
    def calculate_all_metrics(self, trades: List, daily_summaries: List[Dict], 
                            equity_curve: List[float]) -> Dict[str, Any]:
        """Calculate all 22 performance metrics"""
        
        if not trades:
            empty_metrics = self._empty_metrics()
            # Still calculate return metrics if we have an equity curve
            if equity_curve:
                empty_metrics.update(self._calculate_return_metrics(equity_curve))
            return empty_metrics
            
        metrics = {}
        
        # Basic trade metrics (1-6)
        metrics.update(self._calculate_basic_metrics(trades))
        
        # P&L metrics (7-11) 
        metrics.update(self._calculate_pnl_metrics(trades))
        
        # Drawdown metrics (12-13)
        metrics.update(self._calculate_drawdown_metrics(equity_curve, trades))
        
        # Return metrics (14-15)
        metrics.update(self._calculate_return_metrics(equity_curve))
        
        # Ratio metrics (16-17)
        metrics.update(self._calculate_ratio_metrics(trades))
        
        # Duration metrics (18-20)
        metrics.update(self._calculate_duration_metrics(trades))
        
        # Risk metrics (21-22)
        metrics.update(self._calculate_risk_metrics(daily_summaries, equity_curve))
        
        return metrics
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics for no trades"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_long_trades': 0,
            'total_short_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'gross_pnl': 0,
            'total_costs': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'max_drawdown': 0,
            'avg_drawdown': 0,
            'total_return': 0,
            'final_equity': 0,
            'profit_factor': 0,
            'cost_ratio': 0,
            'shortest_trade_minutes': 0,
            'longest_trade_minutes': 0,
            'avg_trade_duration_minutes': 0,
            'sharpe_ratio': 0,
            'value_at_risk': 0
        }
    
    def _calculate_basic_metrics(self, trades: List) -> Dict[str, Any]:
        """Calculate basic trade counting metrics (1-6)"""
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.net_pnl > 0)
        losing_trades = sum(1 for t in trades if t.net_pnl <= 0)
        total_long_trades = sum(1 for t in trades if t.direction == "LONG")
        total_short_trades = sum(1 for t in trades if t.direction == "SHORT")
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_long_trades': total_long_trades,
            'total_short_trades': total_short_trades,
            'win_rate': win_rate
        }
    
    def _calculate_pnl_metrics(self, trades: List) -> Dict[str, Any]:
        """Calculate P&L metrics (7-11)"""
        total_pnl = sum(t.net_pnl for t in trades)
        gross_pnl = sum(t.gross_pnl for t in trades)
        total_costs = sum(t.costs for t in trades)
        
        # Average win/loss
        winning_trades = [t for t in trades if t.net_pnl > 0]
        losing_trades = [t for t in trades if t.net_pnl <= 0]
        
        avg_win = np.mean([t.net_pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.net_pnl for t in losing_trades]) if losing_trades else 0
        
        return {
            'total_pnl': total_pnl,
            'gross_pnl': gross_pnl,
            'total_costs': total_costs,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def _calculate_drawdown_metrics(self, equity_curve: List[float], trades: List) -> Dict[str, Any]:
        """Calculate drawdown metrics (12-13)"""
        if not equity_curve:
            return {'max_drawdown': 0, 'avg_drawdown': 0}
            
        # Calculate drawdown for development (both methods as specified)
        drawdown_result = self.calculate_drawdown_both_methods(equity_curve, trades)
        
        # Use primary method for reporting
        max_drawdown = drawdown_result['primary']['max']
        avg_drawdown = drawdown_result['primary']['avg']
        
        return {
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown
        }
    
    def calculate_drawdown_both_methods(self, equity_curve: List[float], trades: List) -> Dict[str, Any]:
        """Calculate drawdown using both methods for development validation"""
        
        # Method 1: End-of-day drawdown
        eod_drawdown = self._calculate_eod_drawdown(equity_curve)
        
        # Method 2: Continuous drawdown  
        continuous_drawdown = self._calculate_continuous_drawdown(equity_curve)
        
        return {
            'eod_method': eod_drawdown,
            'continuous_method': continuous_drawdown,
            'primary': eod_drawdown,  # Use EOD as primary
            'comparison_note': 'Both methods calculated for development validation'
        }
    
    def _calculate_eod_drawdown(self, equity_curve: List[float]) -> Dict[str, float]:
        """Calculate end-of-day drawdown method"""
        if len(equity_curve) < 2:
            return {'max': 0.0, 'avg': 0.0}
            
        equity_array = np.array(equity_curve)
        
        # Calculate running maximum (peak)
        running_max = np.maximum.accumulate(equity_array)
        
        # Calculate drawdown as percentage
        drawdown = (running_max - equity_array) / running_max * 100
        
        max_drawdown = np.max(drawdown)
        avg_drawdown = np.mean(drawdown[drawdown > 0]) if np.any(drawdown > 0) else 0.0
        
        return {'max': max_drawdown, 'avg': avg_drawdown}
    
    def _calculate_continuous_drawdown(self, equity_curve: List[float]) -> Dict[str, float]:
        """Calculate continuous drawdown method"""
        # For now, use same calculation as EOD (can be enhanced in future)
        return self._calculate_eod_drawdown(equity_curve)
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown percentage"""
        if len(equity_curve) < 2:
            return 0.0
            
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (running_max - equity_array) / running_max * 100
        
        return np.max(drawdown)
    
    def calculate_avg_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate average drawdown"""
        if len(equity_curve) < 2:
            return 0.0
            
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (running_max - equity_array) / running_max * 100
        
        # Average of non-zero drawdowns
        return np.mean(drawdown[drawdown > 0]) if np.any(drawdown > 0) else 0.0
    
    def _calculate_return_metrics(self, equity_curve: List[float]) -> Dict[str, Any]:
        """Calculate return metrics (14-15)"""
        if not equity_curve:
            return {'total_return': 0, 'final_equity': 0}
            
        final_equity = equity_curve[-1]
        
        total_return = self.calculate_total_return(equity_curve)
        
        return {
            'total_return': total_return,
            'final_equity': final_equity
        }
    
    def calculate_total_return(self, equity_curve: List[float]) -> float:
        """Calculate total return percentage"""
        if len(equity_curve) < 2:
            return 0.0
            
        initial = equity_curve[0]
        final = equity_curve[-1]
        
        if initial == 0:
            return 0.0
            
        return (final - initial) / initial * 100
    
    def _calculate_ratio_metrics(self, trades: List) -> Dict[str, Any]:
        """Calculate ratio metrics (16-17)"""
        # Profit factor: total wins / abs(total losses)
        total_wins = sum(t.net_pnl for t in trades if t.net_pnl > 0)
        total_losses = abs(sum(t.net_pnl for t in trades if t.net_pnl < 0))
        
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Cost ratio: total costs / gross profits
        total_costs = sum(t.costs for t in trades)
        gross_profits = sum(t.gross_pnl for t in trades if t.gross_pnl > 0)
        
        cost_ratio = total_costs / gross_profits if gross_profits > 0 else 0
        
        return {
            'profit_factor': profit_factor,
            'cost_ratio': cost_ratio
        }
    
    def _calculate_duration_metrics(self, trades: List) -> Dict[str, Any]:
        """Calculate duration metrics (18-20)"""
        if not trades:
            return {
                'shortest_trade_minutes': 0,
                'longest_trade_minutes': 0,
                'avg_trade_duration_minutes': 0
            }
            
        durations = [t.duration_minutes for t in trades]
        
        return {
            'shortest_trade_minutes': min(durations),
            'longest_trade_minutes': max(durations),
            'avg_trade_duration_minutes': np.mean(durations)
        }
    
    def _calculate_risk_metrics(self, daily_summaries: List[Dict], 
                               equity_curve: List[float]) -> Dict[str, Any]:
        """Calculate risk metrics (21-22)"""
        # Sharpe ratio
        sharpe = self.calculate_sharpe_ratio(daily_summaries)
        
        # Value at Risk (VaR)
        var = self.calculate_var_parametric_95_1day(daily_summaries)
        
        return {
            'sharpe_ratio': sharpe,
            'value_at_risk': var
        }
    
    def calculate_sharpe_ratio(self, daily_summaries: List[Dict]) -> float:
        """Calculate Sharpe ratio using 3% risk-free rate"""
        if len(daily_summaries) < 2:
            return 0.0
            
        # Extract daily returns
        daily_returns = [summary['daily_net_pnl'] for summary in daily_summaries]
        
        if not daily_returns:
            return 0.0
            
        # Convert to numpy array
        returns_array = np.array(daily_returns)
        
        # Calculate excess return
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
            
        # Daily risk-free rate (3% annual / 252 trading days)
        daily_risk_free = self.risk_free_rate / 252
        
        # Sharpe ratio = (mean return - risk free) / std dev
        sharpe = (mean_return - daily_risk_free) / std_return
        
        # Annualize by multiplying by sqrt(252)
        return sharpe * math.sqrt(252)
    
    def calculate_var_parametric_95_1day(self, daily_summaries: List[Dict]) -> float:
        """Calculate VaR using parametric method, 95% confidence, 1-day horizon"""
        if len(daily_summaries) < 2:
            return 0.0
            
        # Extract daily P&L
        daily_pnl = [summary['daily_net_pnl'] for summary in daily_summaries]
        
        if not daily_pnl:
            return 0.0
            
        # Calculate mean and standard deviation
        mean_pnl = np.mean(daily_pnl)
        std_pnl = np.std(daily_pnl)
        
        # VaR at 95% confidence = mean - 1.645 * std (assuming normal distribution)
        var_95 = mean_pnl - (1.645 * std_pnl)
        
        return var_95
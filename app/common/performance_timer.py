"""
Performance Timer - Track backtest execution performance
"""
import time
import psutil
import os
from typing import Dict, Any, Optional
from datetime import datetime


class PerformanceTimer:
    """
    Track performance metrics during backtest execution
    
    Features:
    - Execution time tracking
    - Memory usage monitoring
    - Processing rate calculation
    """
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.initial_memory: Optional[float] = None
        self.final_memory: Optional[float] = None
        
    def start_backtest(self):
        """Start timing the backtest"""
        self.start_time = time.time()
        
        # Get initial memory usage
        try:
            process = psutil.Process(os.getpid())
            self.initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        except:
            self.initial_memory = 0
    
    def end_backtest(self) -> Dict[str, Any]:
        """End timing and return performance report"""
        self.end_time = time.time()
        
        # Get final memory usage
        try:
            process = psutil.Process(os.getpid())
            self.final_memory = process.memory_info().rss / 1024 / 1024  # MB
        except:
            self.final_memory = self.initial_memory or 0
            
        # Calculate metrics
        execution_time = (self.end_time - self.start_time) if self.start_time else 0
        memory_increase = (self.final_memory - self.initial_memory) if self.initial_memory else 0
        
        return {
            'total_processing_time_seconds': execution_time,
            'memory_usage_increase_mb': memory_increase,
            'initial_memory_mb': self.initial_memory or 0,
            'final_memory_mb': self.final_memory or 0,
            'timestamp': datetime.now()
        }
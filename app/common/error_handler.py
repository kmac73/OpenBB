"""
Jupyter-Style Error Handler - Phase 1 Implementation
Provides graceful error handling with context preservation
"""
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path


class JupyterStyleErrorHandler:
    """
    Jupyter-style error handler for graceful failure management
    
    Features:
    - Context preservation through debug log
    - Graceful failure handling
    - Streamlit-compatible error display
    - Non-breaking execution flow
    """
    
    def __init__(self, max_debug_lines: int = 50):
        self.max_debug_lines = max_debug_lines
        self.debug_log_lines: List[str] = []
        self.error_history: List[Dict[str, Any]] = []
        
    def log_debug_line(self, message: str, timestamp: Optional[datetime] = None):
        """Log a debug line for context preservation"""
        if timestamp is None:
            timestamp = datetime.now()
            
        timestamped_message = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        self.debug_log_lines.append(timestamped_message)
        
        # Keep only recent lines for memory efficiency
        if len(self.debug_log_lines) > self.max_debug_lines:
            self.debug_log_lines = self.debug_log_lines[-self.max_debug_lines:]
    
    def handle_graceful_failure(self, exception: Exception, streamlit_context: bool = True) -> Dict[str, Any]:
        """
        Handle graceful failure with context preservation
        
        Args:
            exception: The exception that occurred
            streamlit_context: Whether running in Streamlit context
            
        Returns:
            Error context dictionary
        """
        
        # Capture error details
        error_info = {
            'timestamp': datetime.now(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
            'context_lines': self.debug_log_lines[-10:].copy(),  # Last 10 debug lines
            'streamlit_context': streamlit_context
        }
        
        # Add to error history
        self.error_history.append(error_info)
        
        # Display error appropriately
        if streamlit_context:
            self._display_streamlit_error(error_info)
        else:
            self._display_console_error(error_info)
            
        return error_info
    
    def _display_streamlit_error(self, error_info: Dict[str, Any]):
        """Display error in Streamlit-friendly format"""
        try:
            import streamlit as st
            
            st.error(f"**Error Occurred:** {error_info['exception_type']}")
            st.write(f"**Message:** {error_info['exception_message']}")
            
            # Show recent context
            if error_info['context_lines']:
                st.write("**Recent Operations:**")
                for line in error_info['context_lines']:
                    st.write(f"- {line}")
                    
            # Expandable detailed traceback
            with st.expander("Detailed Error Information"):
                st.code(error_info['traceback'])
                
        except ImportError:
            # Fallback if streamlit not available
            self._display_console_error(error_info)
    
    def _display_console_error(self, error_info: Dict[str, Any]):
        """Display error in console format"""
        print("\n" + "="*60)
        print("GRACEFUL FAILURE DETECTED")
        print("="*60)
        print(f"Time: {error_info['timestamp']}")
        print(f"Error Type: {error_info['exception_type']}")
        print(f"Message: {error_info['exception_message']}")
        
        if error_info['context_lines']:
            print("\nRecent Operations:")
            for line in error_info['context_lines']:
                print(f"  {line}")
        
        print(f"\nDetailed Traceback:")
        print(error_info['traceback'])
        print("="*60 + "\n")
    
    def log_operation_start(self, operation_name: str, parameters: Dict[str, Any] = None):
        """Log the start of an operation for context"""
        params_str = f" with {parameters}" if parameters else ""
        self.log_debug_line(f"Starting operation: {operation_name}{params_str}")
    
    def log_operation_complete(self, operation_name: str, result_summary: str = None):
        """Log completion of an operation"""
        summary_str = f" - {result_summary}" if result_summary else ""
        self.log_debug_line(f"Completed operation: {operation_name}{summary_str}")
    
    def log_data_processing(self, data_description: str, record_count: int = None):
        """Log data processing operations"""
        count_str = f" ({record_count} records)" if record_count is not None else ""
        self.log_debug_line(f"Processing data: {data_description}{count_str}")
    
    def log_calculation(self, calculation_name: str, input_summary: str, result_summary: str):
        """Log calculations for debugging"""
        self.log_debug_line(f"Calculation: {calculation_name} | Input: {input_summary} | Result: {result_summary}")
    
    def log_trade_execution(self, action: str, details: Dict[str, Any]):
        """Log trade execution for context"""
        details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
        self.log_debug_line(f"Trade execution: {action} | {details_str}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        if not self.error_history:
            return {'total_errors': 0, 'recent_errors': []}
            
        return {
            'total_errors': len(self.error_history),
            'recent_errors': self.error_history[-5:],  # Last 5 errors
            'error_types': list(set(e['exception_type'] for e in self.error_history))
        }
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
    
    def clear_debug_log(self):
        """Clear debug log"""
        self.debug_log_lines.clear()
    
    def export_debug_context(self, file_path: str = None) -> str:
        """Export debug context to file for analysis"""
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"logs/debug_context_{timestamp}.txt"
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write("DEBUG CONTEXT EXPORT\n")
            f.write("="*50 + "\n")
            f.write(f"Export Time: {datetime.now()}\n")
            f.write(f"Debug Lines Count: {len(self.debug_log_lines)}\n")
            f.write(f"Error History Count: {len(self.error_history)}\n\n")
            
            f.write("DEBUG LOG:\n")
            f.write("-"*30 + "\n")
            for line in self.debug_log_lines:
                f.write(line + "\n")
            
            if self.error_history:
                f.write("\nERROR HISTORY:\n")
                f.write("-"*30 + "\n")
                for i, error in enumerate(self.error_history):
                    f.write(f"\nError {i+1}:\n")
                    f.write(f"  Time: {error['timestamp']}\n")
                    f.write(f"  Type: {error['exception_type']}\n")
                    f.write(f"  Message: {error['exception_message']}\n")
                    f.write(f"  Traceback:\n{error['traceback']}\n")
        
        return file_path
    
    def validate_operation_context(self, required_context: List[str]) -> bool:
        """Validate that required context is available"""
        recent_log = " ".join(self.debug_log_lines[-10:])
        
        for context_item in required_context:
            if context_item not in recent_log:
                return False
        
        return True
    
    def suggest_recovery_actions(self, exception: Exception) -> List[str]:
        """Suggest recovery actions based on error type"""
        suggestions = []
        
        exception_type = type(exception).__name__
        
        if exception_type == "FileNotFoundError":
            suggestions.append("Check that all required data files exist")
            suggestions.append("Verify file paths are correct")
            suggestions.append("Ensure proper permissions for file access")
            
        elif exception_type == "ValueError":
            suggestions.append("Validate input parameters")
            suggestions.append("Check data format and ranges")
            suggestions.append("Verify calculation inputs are valid")
            
        elif exception_type == "KeyError":
            suggestions.append("Check dictionary keys exist")
            suggestions.append("Verify data structure matches expected format")
            suggestions.append("Validate column names in dataframes")
            
        elif exception_type == "ZeroDivisionError":
            suggestions.append("Check for zero denominators in calculations")
            suggestions.append("Validate position sizing parameters")
            suggestions.append("Ensure non-zero account balance")
            
        else:
            suggestions.append("Review recent operations in debug log")
            suggestions.append("Check input parameters for validity")
            suggestions.append("Verify system requirements are met")
        
        return suggestions
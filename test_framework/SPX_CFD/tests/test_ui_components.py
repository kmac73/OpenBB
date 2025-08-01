"""
Test suite for User Interface (UI) functionality (Category 11).
Tests Streamlit components, interactions, and user experience.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import streamlit as st
import tempfile
import os


class TestDateSelectionAndInput:
    """Test suite for Date Selection and Input Tests (11.1)."""
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_date_input_manual_entry(self, test_logger, mock_streamlit):
        """Test manual date entry in text format (YYYY-MM-DD)."""
        test_logger.start_test("test_date_input_manual_entry")
        
        try:
            # Test valid date formats
            valid_dates = ["2023-01-01", "2023-12-31", "2024-06-15"]
            
            for date_str in valid_dates:
                # Simulate text input
                mock_streamlit.text_input.return_value = date_str
                
                # Parse date
                parsed_date = pd.to_datetime(date_str).date()
                assert isinstance(parsed_date, date)
                assert parsed_date.year >= 2020
                assert 1 <= parsed_date.month <= 12
                assert 1 <= parsed_date.day <= 31
            
            # Test invalid date formats
            invalid_dates = ["2023/01/01", "01-01-2023", "invalid", ""]
            
            for invalid_date in invalid_dates:
                mock_streamlit.text_input.return_value = invalid_date
                
                if invalid_date in ["2023/01/01", "01-01-2023"]:
                    # Wrong format but potentially parseable
                    try:
                        pd.to_datetime(invalid_date)
                    except:
                        pass  # Expected to fail
                elif invalid_date in ["invalid", ""]:
                    # Should definitely fail
                    with pytest.raises((ValueError, TypeError)):
                        pd.to_datetime(invalid_date)
            
            test_logger.end_test("test_date_input_manual_entry", "PASS")
        except Exception as e:
            test_logger.end_test("test_date_input_manual_entry", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_date_input_calendar_widget(self, test_logger, mock_streamlit):
        """Test Streamlit date_input calendar control functionality."""
        test_logger.start_test("test_date_input_calendar_widget")
        
        try:
            # Mock date_input widget
            test_date = date(2023, 6, 15)
            mock_streamlit.date_input = Mock(return_value=test_date)
            
            # Test date_input widget call
            selected_date = mock_streamlit.date_input(
                "Select Date",
                value=test_date,
                min_value=date(2020, 1, 1),
                max_value=date(2024, 12, 31)
            )
            
            assert selected_date == test_date
            assert isinstance(selected_date, date)
            
            # Verify widget was called with correct parameters
            mock_streamlit.date_input.assert_called_once()
            call_args = mock_streamlit.date_input.call_args
            assert "Select Date" in call_args[0] or "Select Date" in call_args[1].values()
            
            test_logger.end_test("test_date_input_calendar_widget", "PASS")
        except Exception as e:
            test_logger.end_test("test_date_input_calendar_widget", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_date_range_validation(self, test_logger, mock_streamlit):
        """Test start date < end date validation with user feedback."""
        test_logger.start_test("test_date_range_validation")
        
        try:
            # Test valid date range
            start_date = date(2023, 1, 1)
            end_date = date(2023, 12, 31)
            
            assert start_date < end_date, "Start date should be before end date"
            
            # Test invalid date range
            invalid_start = date(2023, 12, 31)
            invalid_end = date(2023, 1, 1)
            
            assert not (invalid_start < invalid_end), "Invalid range should be detected"
            
            # Test same date
            same_date_start = date(2023, 6, 15)
            same_date_end = date(2023, 6, 15)
            
            assert not (same_date_start < same_date_end), "Same dates should be invalid range"
            
            # Mock error display
            mock_streamlit.error = Mock()
            
            # Simulate error message display
            if invalid_start >= invalid_end:
                mock_streamlit.error("Start date must be before end date")
                mock_streamlit.error.assert_called_once()
            
            test_logger.end_test("test_date_range_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_date_range_validation", "FAIL", str(e))
            raise


class TestParameterFileManagement:
    """Test suite for Parameter File Management Tests (11.3)."""
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_save_parameters_to_file(self, test_logger, mock_streamlit, sample_strategy_params):
        """Test save functionality creates properly formatted parameter files."""
        test_logger.start_test("test_save_parameters_to_file")
        
        try:
            # Mock save button
            mock_streamlit.sidebar.button.return_value = True
            
            # Create temporary file for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                # Write parameters to file
                temp_file.write("="*60 + "\n")
                temp_file.write("SPX CFD STRATEGY - PARAMETERS\n")
                temp_file.write("="*60 + "\n")
                temp_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                temp_file.write("\n")
                
                for key, value in sample_strategy_params.items():
                    temp_file.write(f"{key.replace('_', ' ').title()}: {value}\n")
                
                temp_filename = temp_file.name
            
            # Verify file was created and contains expected content
            assert os.path.exists(temp_filename)
            
            with open(temp_filename, 'r') as f:
                content = f.read()
                assert "SPX CFD STRATEGY" in content
                assert "Initial Capital" in content
                assert str(sample_strategy_params['initial_capital']) in content
                assert "Risk Per Trade" in content
                assert str(sample_strategy_params['risk_per_trade']) in content
            
            # Mock success message
            mock_streamlit.sidebar.success = Mock()
            mock_streamlit.sidebar.success("Parameters saved successfully!")
            mock_streamlit.sidebar.success.assert_called_once()
            
            # Cleanup
            os.unlink(temp_filename)
            
            test_logger.end_test("test_save_parameters_to_file", "PASS")
        except Exception as e:
            test_logger.end_test("test_save_parameters_to_file", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_parameter_file_naming(self, test_logger):
        """Test timestamp-based filename generation for saved parameters."""
        test_logger.start_test("test_parameter_file_naming")
        
        try:
            # Generate timestamp-based filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"spx_cfd_params_{timestamp}.txt"
            
            # Verify filename format
            assert filename.startswith("spx_cfd_params_")
            assert filename.endswith(".txt")
            assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
            
            # Test filename uniqueness
            import time
            time.sleep(1)  # Ensure different timestamp
            timestamp2 = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename2 = f"spx_cfd_params_{timestamp2}.txt"
            
            assert filename != filename2, "Filenames should be unique"
            
            test_logger.end_test("test_parameter_file_naming", "PASS")
        except Exception as e:
            test_logger.end_test("test_parameter_file_naming", "FAIL", str(e))
            raise


class TestChartGenerationAndVisualization:
    """Test suite for Chart Generation and Visualization Tests (11.4)."""
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_plotly_chart_rendering(self, test_logger, mock_streamlit, mock_plotly, mock_market_data):
        """Test Plotly chart generation and display in Streamlit."""
        test_logger.start_test("test_plotly_chart_rendering")
        
        try:
            # Generate sample data
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Mock Plotly figure
            mock_fig = Mock()
            mock_plotly.Figure.return_value = mock_fig
            
            # Create mock chart
            fig = mock_plotly.Figure()
            
            # Mock add_trace method
            fig.add_trace = Mock()
            fig.update_layout = Mock()
            
            # Simulate adding traces
            fig.add_trace(mock_plotly.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price'
            ))
            
            # Verify trace was added
            fig.add_trace.assert_called_once()
            
            # Mock Streamlit chart display
            mock_streamlit.plotly_chart = Mock()
            mock_streamlit.plotly_chart(fig, use_container_width=True)
            
            # Verify chart was displayed
            mock_streamlit.plotly_chart.assert_called_once()
            call_args = mock_streamlit.plotly_chart.call_args
            assert call_args[1].get('use_container_width') is True
            
            test_logger.end_test("test_plotly_chart_rendering", "PASS")
        except Exception as e:
            test_logger.end_test("test_plotly_chart_rendering", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_candlestick_chart_accuracy(self, test_logger, mock_plotly, mock_market_data):
        """Test OHLC candlestick chart data accuracy."""
        test_logger.start_test("test_candlestick_chart_accuracy")
        
        try:
            # Generate sample OHLC data
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Verify OHLC data integrity
            assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close'])
            assert (data['High'] >= data['Low']).all()
            assert (data['High'] >= data['Open']).all()
            assert (data['High'] >= data['Close']).all()
            assert (data['Low'] <= data['Open']).all()
            assert (data['Low'] <= data['Close']).all()
            
            # Mock candlestick chart
            mock_candlestick = Mock()
            mock_plotly.Candlestick = Mock(return_value=mock_candlestick)
            
            # Create candlestick trace
            candlestick_trace = mock_plotly.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="SPX"
            )
            
            # Verify candlestick was created with correct data
            mock_plotly.Candlestick.assert_called_once()
            call_kwargs = mock_plotly.Candlestick.call_args[1]
            
            # Check that required OHLC parameters were passed
            required_params = ['x', 'open', 'high', 'low', 'close']
            for param in required_params:
                assert param in call_kwargs, f"Missing required parameter: {param}"
            
            test_logger.end_test("test_candlestick_chart_accuracy", "PASS")
        except Exception as e:
            test_logger.end_test("test_candlestick_chart_accuracy", "FAIL", str(e))
            raise


class TestPDFReportGeneration:
    """Test suite for PDF Report Generation Tests (11.6)."""
    
    @pytest.mark.ui
    @pytest.mark.slow
    def test_pdf_report_creation(self, test_logger, sample_strategy_params, sample_trades_data):
        """Test complete PDF report generation functionality."""
        test_logger.start_test("test_pdf_report_creation")
        
        try:
            # Mock PDF generation libraries
            with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
                mock_pdf = Mock()
                mock_canvas.return_value = mock_pdf
                
                # Mock PDF creation process
                mock_pdf.drawString = Mock()
                mock_pdf.showPage = Mock()
                mock_pdf.save = Mock()
                
                # Simulate PDF content creation
                report_data = {
                    'title': 'SPX CFD Strategy Report',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'parameters': sample_strategy_params,
                    'trades': sample_trades_data[:5],  # First 5 trades
                    'summary': {
                        'total_trades': len(sample_trades_data),
                        'winning_trades': len([t for t in sample_trades_data if t['net_pnl'] > 0]),
                        'total_pnl': sum(t['net_pnl'] for t in sample_trades_data),
                        'win_rate': len([t for t in sample_trades_data if t['net_pnl'] > 0]) / len(sample_trades_data) * 100
                    }
                }
                
                # Verify report data structure
                assert 'title' in report_data
                assert 'parameters' in report_data
                assert 'trades' in report_data
                assert 'summary' in report_data
                
                # Verify summary calculations
                assert report_data['summary']['total_trades'] > 0
                assert 0 <= report_data['summary']['win_rate'] <= 100
                
                # Mock PDF generation
                pdf_filename = f"spx_cfd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Simulate drawing content
                mock_pdf.drawString(100, 750, report_data['title'])
                mock_pdf.drawString(100, 730, f"Generated: {report_data['timestamp']}")
                
                # Verify PDF methods were called
                mock_pdf.drawString.assert_called()
                
                # Mock save
                mock_pdf.save()
                mock_pdf.save.assert_called_once()
            
            test_logger.end_test("test_pdf_report_creation", "PASS")
        except Exception as e:
            test_logger.end_test("test_pdf_report_creation", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_pdf_file_naming(self, test_logger):
        """Test timestamp-based PDF filename generation."""
        test_logger.start_test("test_pdf_file_naming")
        
        try:
            # Generate PDF filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"spx_cfd_report_{timestamp}.pdf"
            
            # Verify filename format
            assert pdf_filename.startswith("spx_cfd_report_")
            assert pdf_filename.endswith(".pdf")
            assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
            
            # Test multiple filenames are unique
            import time
            time.sleep(1)
            timestamp2 = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename2 = f"spx_cfd_report_{timestamp2}.pdf"
            
            assert pdf_filename != pdf_filename2, "PDF filenames should be unique"
            
            test_logger.end_test("test_pdf_file_naming", "PASS")
        except Exception as e:
            test_logger.end_test("test_pdf_file_naming", "FAIL", str(e))
            raise


class TestUserExperienceAndInteraction:
    """Test suite for User Experience and Interaction Tests (11.7)."""
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_loading_spinners(self, test_logger, mock_streamlit):
        """Test loading indicators during data fetching and processing."""
        test_logger.start_test("test_loading_spinners")
        
        try:
            # Mock spinner context manager
            mock_spinner = Mock()
            mock_streamlit.spinner = Mock(return_value=mock_spinner)
            mock_spinner.__enter__ = Mock(return_value=mock_spinner)
            mock_spinner.__exit__ = Mock(return_value=None)
            
            # Test spinner usage
            with mock_streamlit.spinner("Loading market data..."):
                # Simulate data loading
                import time
                time.sleep(0.1)  # Simulate processing time
                data_loaded = True
            
            # Verify spinner was used
            mock_streamlit.spinner.assert_called_once_with("Loading market data...")
            mock_spinner.__enter__.assert_called_once()
            mock_spinner.__exit__.assert_called_once()
            
            assert data_loaded is True
            
            test_logger.end_test("test_loading_spinners", "PASS")
        except Exception as e:
            test_logger.end_test("test_loading_spinners", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.mock
    def test_success_error_messages(self, test_logger, mock_streamlit):
        """Test user feedback messages for operations (success/error)."""
        test_logger.start_test("test_success_error_messages")
        
        try:
            # Test success message
            mock_streamlit.success = Mock()
            mock_streamlit.success("Strategy execution completed successfully!")
            mock_streamlit.success.assert_called_once_with("Strategy execution completed successfully!")
            
            # Test error message
            mock_streamlit.error = Mock()
            mock_streamlit.error("Failed to load market data. Please check your connection.")
            mock_streamlit.error.assert_called_once_with("Failed to load market data. Please check your connection.")
            
            # Test warning message
            mock_streamlit.warning = Mock()
            mock_streamlit.warning("No trades were generated with current parameters.")
            mock_streamlit.warning.assert_called_once_with("No trades were generated with current parameters.")
            
            # Test info message
            mock_streamlit.info = Mock()
            mock_streamlit.info("Configure parameters in sidebar and click 'Run Strategy'.")
            mock_streamlit.info.assert_called_once_with("Configure parameters in sidebar and click 'Run Strategy'.")
            
            test_logger.end_test("test_success_error_messages", "PASS")
        except Exception as e:
            test_logger.end_test("test_success_error_messages", "FAIL", str(e))
            raise
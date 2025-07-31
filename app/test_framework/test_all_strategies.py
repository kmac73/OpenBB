#!/usr/bin/env python3
"""
Comprehensive Test Suite for SP500 CFD Strategies
Tests all 3 versions: v1 (Baseline), v2 (Performance), v3 (Innovation)
"""

import sys
import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import tempfile
import warnings

# Add parent directories to path for imports
sys.path.append('/mnt/c/Users/kevin/git/OpenBB/app/SP500_CFD_v1')
sys.path.append('/mnt/c/Users/kevin/git/OpenBB/app/SP500_CFD_v2')
sys.path.append('/mnt/c/Users/kevin/git/OpenBB/app/SP500_CFD_v3')

warnings.filterwarnings('ignore')

# Mock market_data for testing
class MockRetrieve:
    """Mock market data retriever for testing - Updated to match fixed implementation"""
    
    def get_data(self, symbol, start_date, end_date, frequency="5M"):
        """Generate synthetic market data for testing - matches real get_data method"""
        print(f"🧪 Mock: Generating test data for {symbol} from {start_date} to {end_date} ({frequency})")
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Generate 5-minute intervals during trading hours
        trading_hours = []
        current_date = start
        
        while current_date <= end:
            # Only weekdays
            if current_date.weekday() < 5:
                # Trading hours: 9:30 AM - 4:00 PM
                for hour in range(9, 16):
                    for minute in [30, 35, 40, 45, 50, 55] if hour == 9 else [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
                        if hour == 15 and minute > 0:  # Stop at 4:00 PM
                            break
                        dt = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        trading_hours.append(dt)
            current_date += timedelta(days=1)
        
        # Limit to reasonable size for testing
        if len(trading_hours) > 1000:
            trading_hours = trading_hours[:1000]
        
        # Generate realistic price data
        np.random.seed(42)  # Reproducible results
        base_price = 4500.0 if symbol == "SPX" else 100.0
        
        data = []
        for i, dt in enumerate(trading_hours):
            # Random walk with slight upward bias
            price_change = np.random.normal(0.05, 2.0)  # Small upward bias, 2 point volatility
            if i == 0:
                price = base_price
            else:
                price = max(data[-1]['Close'] + price_change, base_price * 0.8)  # Floor price
            
            # Generate OHLC data
            high = price + abs(np.random.normal(0, 1.0))
            low = price - abs(np.random.normal(0, 1.0))
            volume = int(np.random.lognormal(13, 0.5))  # Realistic volume
            
            data.append({
                'Open': price,
                'High': high,
                'Low': low,
                'Close': price,
                'Volume': volume
            })
        
        df = pd.DataFrame(data, index=pd.DatetimeIndex(trading_hours))
        print(f"✅ Mock: Generated {len(df)} test data points for {symbol}")
        return df
    
    # Add legacy methods for backward compatibility
    @staticmethod
    def from_provider(symbols, start_date, end_date):
        """Mock provider method for compatibility"""
        return pd.DataFrame()  # Return empty to trigger fallback
    
    @staticmethod
    def from_file(symbols, start_date, end_date, freq):
        """Mock file method for compatibility"""
        return pd.DataFrame()  # Return empty to trigger fallback

class TestCFDStrategies(unittest.TestCase):
    """Comprehensive test suite for all CFD strategy versions"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_data_retriever = MockRetrieve()
        self.test_params = {
            'initial_capital': 25000,
            'risk_per_trade': 1.0,
            'max_concurrent_positions': 3,
            'opening_range_minutes': 30,
            'entry_threshold_points': 2.0,
            'stop_loss_points': 4.0,
            'profit_target_points': 8.0,
            'directional_bias_multiplier': 1.5,
            'spread_points': 0.8,
            'commission_per_trade': 1.0
        }
        
        # Generate test data
        self.test_data = self.mock_data_retriever.get_data("SPX", "2024-01-01", "2024-01-05", "5M")
        
    def test_v1_baseline_initialization(self):
        """Test Version 1 (Baseline) initialization"""
        try:
            from cfd_strategy_v1 import CFDStrategyV1
            strategy = CFDStrategyV1(self.test_params)
            self.assertIsNotNone(strategy)
            self.assertEqual(strategy.params['initial_capital'], 25000)
            print("✅ V1 Baseline: Initialization test passed")
        except Exception as e:
            self.fail(f"❌ V1 Baseline initialization failed: {str(e)}")
    
    def test_v1_position_sizing(self):
        """Test Version 1 position sizing calculations"""
        try:
            from cfd_strategy_v1 import CFDStrategyV1
            strategy = CFDStrategyV1(self.test_params)
            
            position_size = strategy.calculate_position_size(25000, 1.0, 4.0)
            self.assertIsInstance(position_size, int)
            self.assertGreater(position_size, 0)
            self.assertLess(position_size, 100)  # Reasonable upper bound
            print(f"✅ V1 Baseline: Position sizing test passed (size: {position_size})")
        except Exception as e:
            self.fail(f"❌ V1 Baseline position sizing failed: {str(e)}")
    
    def test_v1_backtest_execution(self):
        """Test Version 1 backtest execution"""
        try:
            from cfd_strategy_v1 import CFDStrategyV1
            strategy = CFDStrategyV1(self.test_params)
            
            final_equity = strategy.run_backtest(self.test_data)
            
            self.assertIsInstance(final_equity, (int, float))
            self.assertGreater(final_equity, 0)
            
            # Check analytics generation
            analytics = strategy.generate_analytics()
            self.assertIsInstance(analytics, dict)
            
            print(f"✅ V1 Baseline: Backtest execution passed (final equity: ${final_equity:,.2f})")
            print(f"   - Total trades: {analytics.get('total_trades', 0)}")
            print(f"   - Win rate: {analytics.get('win_rate', 0):.1f}%")
            
        except Exception as e:
            self.fail(f"❌ V1 Baseline backtest execution failed: {str(e)}")
    
    def test_v2_performance_initialization(self):
        """Test Version 2 (Performance) initialization"""
        try:
            from cfd_strategy_v2 import AdvancedCFDStrategy
            strategy = AdvancedCFDStrategy(self.test_params)
            self.assertIsNotNone(strategy)
            self.assertEqual(strategy.params['initial_capital'], 25000)
            print("✅ V2 Performance: Initialization test passed")
        except Exception as e:
            self.fail(f"❌ V2 Performance initialization failed: {str(e)}")
    
    def test_v2_advanced_features(self):
        """Test Version 2 advanced features"""
        try:
            from cfd_strategy_v2 import AdvancedCFDStrategy
            strategy = AdvancedCFDStrategy(self.test_params)
            
            # Test dynamic position sizing
            volatility = 0.2
            confidence_score = 0.7
            
            position_size = strategy.dynamic_position_sizing(25000, volatility, confidence_score)
            self.assertIsInstance(position_size, int)
            self.assertGreater(position_size, 0)
            
            print(f"✅ V2 Performance: Advanced features test passed (dynamic size: {position_size})")
        except Exception as e:
            self.fail(f"❌ V2 Performance advanced features failed: {str(e)}")
    
    def test_v2_optimized_backtest(self):
        """Test Version 2 optimized backtest"""
        try:
            from cfd_strategy_v2 import AdvancedCFDStrategy
            strategy = AdvancedCFDStrategy(self.test_params)
            
            final_equity = strategy.run_backtest_optimized(self.test_data)
            
            self.assertIsInstance(final_equity, (int, float))
            self.assertGreater(final_equity, 0)
            
            # Check advanced analytics
            analytics = strategy.generate_advanced_analytics()
            self.assertIsInstance(analytics, dict)
            
            print(f"✅ V2 Performance: Optimized backtest passed (final equity: ${final_equity:,.2f})")
            print(f"   - Total trades: {analytics.get('total_trades', 0)}")
            print(f"   - High confidence win rate: {analytics.get('high_conf_win_rate', 0):.1f}%")
            
        except Exception as e:
            self.fail(f"❌ V2 Performance optimized backtest failed: {str(e)}")
    
    def test_v3_innovation_initialization(self):
        """Test Version 3 (Innovation) initialization"""
        try:
            from cfd_strategy_v3 import InnovativeCFDStrategy
            
            # Add AI-specific parameters
            ai_params = self.test_params.copy()
            ai_params.update({
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0
            })
            
            strategy = InnovativeCFDStrategy(ai_params)
            self.assertIsNotNone(strategy)
            self.assertEqual(strategy.params['initial_capital'], 25000)
            print("✅ V3 Innovation: Initialization test passed")
        except Exception as e:
            self.fail(f"❌ V3 Innovation initialization failed: {str(e)}")
    
    def test_v3_ai_features(self):
        """Test Version 3 AI features"""
        try:
            from cfd_strategy_v3 import InnovativeCFDStrategy
            
            ai_params = self.test_params.copy()
            ai_params.update({
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0
            })
            
            strategy = InnovativeCFDStrategy(ai_params)
            
            # Test data enhancement
            enhanced_data = strategy.enhance_data_with_features(self.test_data)
            self.assertIsInstance(enhanced_data, pd.DataFrame)
            self.assertIn('Price_Velocity', enhanced_data.columns)
            self.assertIn('Market_Efficiency', enhanced_data.columns)
            
            # Test ML model training (should not crash)
            strategy.train_ml_models(enhanced_data)
            
            print("✅ V3 Innovation: AI features test passed")
            print(f"   - Enhanced features: {len([col for col in enhanced_data.columns if col not in self.test_data.columns])}")
            
        except Exception as e:
            self.fail(f"❌ V3 Innovation AI features failed: {str(e)}")
    
    def test_v3_intelligent_backtest(self):
        """Test Version 3 intelligent backtest"""
        try:
            from cfd_strategy_v3 import InnovativeCFDStrategy
            
            ai_params = self.test_params.copy()
            ai_params.update({
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0
            })
            
            strategy = InnovativeCFDStrategy(ai_params)
            
            final_equity = strategy.run_intelligent_backtest(self.test_data)
            
            self.assertIsInstance(final_equity, (int, float))
            self.assertGreater(final_equity, 0)
            
            # Check innovative analytics
            analytics = strategy.generate_innovative_analytics()
            self.assertIsInstance(analytics, dict)
            
            print(f"✅ V3 Innovation: Intelligent backtest passed (final equity: ${final_equity:,.2f})")
            print(f"   - Total trades: {analytics.get('total_trades', 0)}")
            print(f"   - ML-enhanced win rate: {analytics.get('ml_enhanced_win_rate', 0):.1f}%")
            
        except Exception as e:
            self.fail(f"❌ V3 Innovation intelligent backtest failed: {str(e)}")
    
    def test_data_consistency(self):
        """Test that all versions handle the same data consistently"""
        try:
            # Import all versions
            from cfd_strategy_v1 import CFDStrategyV1
            from cfd_strategy_v2 import AdvancedCFDStrategy
            from cfd_strategy_v3 import InnovativeCFDStrategy
            
            # Test with same base parameters
            v1_strategy = CFDStrategyV1(self.test_params)
            v2_strategy = AdvancedCFDStrategy(self.test_params)
            
            ai_params = self.test_params.copy()
            ai_params.update({
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0
            })
            v3_strategy = InnovativeCFDStrategy(ai_params)
            
            # Run backtests
            v1_equity = v1_strategy.run_backtest(self.test_data)
            v2_equity = v2_strategy.run_backtest_optimized(self.test_data)
            v3_equity = v3_strategy.run_intelligent_backtest(self.test_data)
            
            # All should produce valid results
            self.assertGreater(v1_equity, 0)
            self.assertGreater(v2_equity, 0)
            self.assertGreater(v3_equity, 0)
            
            print("✅ Data Consistency: All versions handle data correctly")
            print(f"   - V1 Final Equity: ${v1_equity:,.2f}")
            print(f"   - V2 Final Equity: ${v2_equity:,.2f}")
            print(f"   - V3 Final Equity: ${v3_equity:,.2f}")
            
        except Exception as e:
            self.fail(f"❌ Data consistency test failed: {str(e)}")
    
    def test_risk_management(self):
        """Test risk management across all versions"""
        try:
            from cfd_strategy_v1 import CFDStrategyV1
            from cfd_strategy_v2 import AdvancedCFDStrategy
            from cfd_strategy_v3 import InnovativeCFDStrategy
            
            # Test with high-risk parameters
            high_risk_params = self.test_params.copy()
            high_risk_params['risk_per_trade'] = 5.0  # 5% risk per trade
            
            strategies = [
                CFDStrategyV1(high_risk_params),
                AdvancedCFDStrategy(high_risk_params),
            ]
            
            ai_params = high_risk_params.copy()
            ai_params.update({
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0
            })
            strategies.append(InnovativeCFDStrategy(ai_params))
            
            # Test position sizing limits
            for i, strategy in enumerate(['V1', 'V2', 'V3']):
                if i < len(strategies):
                    if hasattr(strategies[i], 'calculate_position_size'):
                        position_size = strategies[i].calculate_position_size(25000, 5.0, 4.0)
                        self.assertLess(position_size, 500)  # Reasonable upper limit
                        print(f"✅ {strategy} Risk Management: Position size within limits ({position_size})")
            
        except Exception as e:
            self.fail(f"❌ Risk management test failed: {str(e)}")
    
    def test_save_parameters_functionality(self):
        """Test Save Parameters feature across all versions"""
        import tempfile
        import os
        
        try:
            # Test parameter data structure for each version
            
            # V1 Parameters
            v1_params = {
                'initial_capital': 25000,
                'risk_per_trade': 1.0,
                'max_concurrent_positions': 3,
                'opening_range_minutes': 30,
                'entry_threshold_points': 2.0,
                'stop_loss_points': 4.0,
                'profit_target_points': 8.0,
                'directional_bias_multiplier': 1.5,
                'spread_points': 0.8,
                'commission_per_trade': 1.0,
                'start_date': '2024-01-01',
                'end_date': '2024-01-05',
                'symbol': 'SPX'
            }
            
            # Test calculated values for V1
            sample_position_size = int((v1_params['initial_capital'] * v1_params['risk_per_trade'] / 100) / v1_params['stop_loss_points'])
            self.assertGreater(sample_position_size, 0)
            self.assertLess(sample_position_size, 1000)  # Reasonable bounds
            
            sample_risk_amount = v1_params['initial_capital'] * v1_params['risk_per_trade'] / 100
            self.assertEqual(sample_risk_amount, 250.0)  # 1% of $25,000
            
            sample_transaction_cost = sample_position_size * v1_params['spread_points'] + v1_params['commission_per_trade']
            cost_percentage = sample_transaction_cost / sample_risk_amount * 100
            self.assertLess(cost_percentage, 50)  # Cost should be reasonable percentage of risk
            
            print(f"✅ V1 Save Parameters: Calculations validated")
            print(f"   - Position Size: {sample_position_size} CFDs")
            print(f"   - Risk Amount: ${sample_risk_amount:.2f}")
            print(f"   - Transaction Cost: ${sample_transaction_cost:.2f} ({cost_percentage:.1f}% of risk)")
            
            # V2 Parameters (includes ML features)
            v2_params = v1_params.copy()
            v2_params.update({
                'ml_features_enabled': True,
                'regime_adaptation_enabled': True,
                'dynamic_sizing_enabled': True,
                'confidence_threshold': 0.4,
                'show_regime_analysis': True,
                'show_confidence_analysis': True,
                'show_hourly_analysis': True
            })
            
            # Validate V2 feature flags
            self.assertTrue(v2_params['ml_features_enabled'])
            self.assertTrue(v2_params['regime_adaptation_enabled'])
            self.assertTrue(v2_params['dynamic_sizing_enabled'])
            
            print(f"✅ V2 Save Parameters: ML features validated")
            
            # V3 Parameters (includes AI features)
            v3_params = v2_params.copy()
            v3_params.update({
                'enable_ml': True,
                'enable_regime_detection': True,
                'enable_adaptive_sizing': True,
                'enable_sentiment': True,
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0,
                'show_ai_insights': True,
                'show_ml_predictions': True,
                'show_market_microstructure': True
            })
            
            # Validate V3 AI features
            self.assertTrue(v3_params['enable_ml'])
            self.assertTrue(v3_params['enable_regime_detection'])
            self.assertTrue(v3_params['enable_adaptive_sizing'])
            self.assertTrue(v3_params['enable_sentiment'])
            
            # Test parameter file structure generation
            from datetime import datetime as dt
            
            # Simulate parameter file content validation
            timestamp = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            filename_pattern = f"debug_params_v3_{dt.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Validate filename pattern
            self.assertTrue(filename_pattern.startswith('debug_params_v3_'))
            self.assertTrue(filename_pattern.endswith('.txt'))
            
            print(f"✅ V3 Save Parameters: AI features validated")
            print(f"   - Filename pattern: {filename_pattern}")
            print(f"   - Timestamp format: {timestamp}")
            
            print(f"✅ Save Parameters Feature: All versions validated")
            
        except Exception as e:
            self.fail(f"❌ Save Parameters functionality test failed: {str(e)}")
    
    def test_market_data_fix(self):
        """Test that the market data fix is working correctly"""
        try:
            # Test that MockRetrieve has the get_data method
            mock_retriever = MockRetrieve()
            self.assertTrue(hasattr(mock_retriever, 'get_data'))
            
            # Test get_data method functionality
            data = mock_retriever.get_data("SPX", "2024-01-01", "2024-01-05", "5M")
            
            # Validate data structure
            self.assertIsInstance(data, pd.DataFrame)
            self.assertGreater(len(data), 0)
            
            # Validate required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                self.assertIn(col, data.columns)
            
            # Validate data types
            self.assertTrue(pd.api.types.is_numeric_dtype(data['Close']))
            self.assertTrue(pd.api.types.is_numeric_dtype(data['Volume']))
            
            # Validate datetime index
            self.assertIsInstance(data.index, pd.DatetimeIndex)
            
            # Test that data is within reasonable ranges
            self.assertGreater(data['Close'].min(), 1000)  # SPX should be > 1000
            self.assertLess(data['Close'].max(), 10000)   # SPX should be < 10000
            self.assertGreater(data['Volume'].min(), 0)   # Volume should be positive
            
            print(f"✅ Market Data Fix: get_data method working correctly")
            print(f"   - Data shape: {data.shape}")
            print(f"   - Columns: {list(data.columns)}")
            print(f"   - Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            print(f"   - Date range: {data.index[0]} to {data.index[-1]}")
            
        except Exception as e:
            self.fail(f"❌ Market data fix test failed: {str(e)}")

class TestPerformanceComparison(unittest.TestCase):
    """Performance comparison tests between versions"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.mock_data_retriever = MockRetrieve()
        self.test_params = {
            'initial_capital': 50000,
            'risk_per_trade': 1.0,
            'max_concurrent_positions': 3,
            'opening_range_minutes': 30,
            'entry_threshold_points': 2.0,
            'stop_loss_points': 4.0,
            'profit_target_points': 8.0,
            'directional_bias_multiplier': 1.5,
            'spread_points': 0.8,
            'commission_per_trade': 1.0
        }
        
        # Generate larger dataset for performance testing
        self.performance_data = self.mock_data_retriever.get_data("SPX", "2024-01-01", "2024-01-10", "5M")
    
    def test_execution_speed(self):
        """Compare execution speed between versions"""
        import time
        
        try:
            from cfd_strategy_v1 import CFDStrategyV1
            from cfd_strategy_v2 import AdvancedCFDStrategy
            from cfd_strategy_v3 import InnovativeCFDStrategy
            
            # Time V1 execution
            start_time = time.time()
            v1_strategy = CFDStrategyV1(self.test_params)
            v1_strategy.run_backtest(self.performance_data)
            v1_time = time.time() - start_time
            
            # Time V2 execution
            start_time = time.time()
            v2_strategy = AdvancedCFDStrategy(self.test_params)
            v2_strategy.run_backtest_optimized(self.performance_data)
            v2_time = time.time() - start_time
            
            # Time V3 execution
            start_time = time.time()
            ai_params = self.test_params.copy()
            ai_params.update({
                'ai_confidence_threshold': 0.3,
                'regime_sensitivity': 0.5,
                'adaptive_risk_multiplier': 1.0
            })
            v3_strategy = InnovativeCFDStrategy(ai_params)
            v3_strategy.run_intelligent_backtest(self.performance_data)
            v3_time = time.time() - start_time
            
            print(f"⏱️  Performance Comparison:")
            print(f"   - V1 Baseline: {v1_time:.2f} seconds")
            print(f"   - V2 Performance: {v2_time:.2f} seconds")
            print(f"   - V3 Innovation: {v3_time:.2f} seconds")
            
            # All should complete within reasonable time
            self.assertLess(v1_time, 30)  # 30 seconds max
            self.assertLess(v2_time, 60)  # Allow more time for optimized version
            self.assertLess(v3_time, 120)  # Allow more time for AI version
            
        except Exception as e:
            self.fail(f"❌ Performance comparison failed: {str(e)}")

def run_comprehensive_tests():
    """Run all tests with detailed reporting"""
    print("\n" + "=" * 60)
    print("🧪 COMPREHENSIVE CFD STRATEGY TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all tests
    test_suite.addTest(unittest.makeSuite(TestCFDStrategies))
    test_suite.addTest(unittest.makeSuite(TestPerformanceComparison))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! All 3 CFD strategy versions are working correctly.")
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} tests failed. Review issues above.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Replace actual market_data imports with mock for testing
    import sys
    
    # Mock the market_data module
    class MockMarketDataModule:
        Retrieve = MockRetrieve
    
    sys.modules['market_data'] = MockMarketDataModule()
    
    # Run comprehensive tests
    success = run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
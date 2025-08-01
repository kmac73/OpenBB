#!/usr/bin/env python3
"""
Comprehensive Parameter Testing for SP500 CFD Strategy V1
Tests every parameter individually to ensure full functionality
"""

import sys
import os
sys.path.append('/mnt/c/Users/kevin/git/OpenBB/app/SP500_CFD_v1')

from cfd_strategy_v1 import CFDStrategyV1
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_data():
    """Create synthetic test data for parameter testing"""
    dates = pd.date_range('2024-01-01 09:30:00', '2024-01-03 16:00:00', freq='5min')
    np.random.seed(42)
    base_price = 4500
    prices = []
    
    for i in range(len(dates)):
        # Create some volatility with trend
        price_change = np.random.normal(0, 2)
        if i > 0:
            # Add some momentum
            prev_change = prices[i-1] - (prices[i-2] if i > 1 else base_price)
            price_change += prev_change * 0.1
        
        price = base_price + price_change
        prices.append(price)
        base_price = price

    test_data = pd.DataFrame({
        'Open': prices,
        'High': [p + abs(np.random.normal(0, 1)) for p in prices],
        'Low': [p - abs(np.random.normal(0, 1)) for p in prices],
        'Close': prices,
        'Volume': [int(np.random.lognormal(10, 0.5)) for _ in prices]
    }, index=dates)
    
    return test_data

def get_base_params():
    """Get base parameters for testing"""
    return {
        'initial_capital': 25000,
        'risk_per_trade': 1.0,
        'max_concurrent_positions': 1,
        'opening_range_minutes': 30,
        'entry_threshold_points': 2.0,
        'stop_loss_points': 4.0,
        'profit_target_points': 8.0,
        'directional_bias_multiplier': 1.5,
        'spread_points': 1.0,
        'commission_per_trade': 1.0
    }

def test_parameter(param_name, test_values, test_data):
    """Test a specific parameter with different values"""
    print(f"\n🧪 Testing parameter: {param_name}")
    print("-" * 50)
    
    base_params = get_base_params()
    results = []
    
    for value in test_values:
        try:
            # Update parameter
            test_params = base_params.copy()
            test_params[param_name] = value
            
            # Run strategy
            strategy = CFDStrategyV1(test_params)
            final_equity = strategy.run_backtest(test_data)
            analytics = strategy.generate_analytics()
            
            # CRITICAL: Validate that trades were actually executed
            total_trades = analytics['total_trades']
            if total_trades == 0:
                raise ValueError(f"Strategy with {param_name}={value} executed 0 trades - strategy is not functional")
            
            result = {
                'value': value,
                'final_equity': final_equity,
                'total_trades': analytics['total_trades'],
                'total_return': analytics['total_return'],
                'win_rate': analytics['win_rate'],
                'status': 'SUCCESS'
            }
            
            print(f"  ✅ {param_name}={value}: "
                  f"Equity=${final_equity:.2f}, "
                  f"Trades={analytics['total_trades']}, "
                  f"Return={analytics['total_return']:.2f}%")
            
        except Exception as e:
            result = {
                'value': value,
                'final_equity': None,
                'total_trades': None,
                'total_return': None,
                'win_rate': None,
                'status': f'ERROR: {str(e)}'
            }
            print(f"  ❌ {param_name}={value}: ERROR - {str(e)}")
        
        results.append(result)
    
    return results

def run_comprehensive_parameter_tests():
    """Run comprehensive tests for all parameters"""
    print("🚀 SP500 CFD Strategy V1 - Comprehensive Parameter Testing")
    print("=" * 60)
    
    # Create test data
    print("\n📊 Creating test data...")
    test_data = create_test_data()
    print(f"✅ Created {len(test_data)} data points from {test_data.index[0]} to {test_data.index[-1]}")
    
    # Define parameter test cases
    parameter_tests = {
        'initial_capital': [10000, 25000, 50000, 100000],
        'risk_per_trade': [0.5, 1.0, 1.5, 2.0, 3.0],
        'max_concurrent_positions': [1, 2, 3, 4, 5],
        'opening_range_minutes': [15, 30, 45, 60],
        'entry_threshold_points': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
        'stop_loss_points': [2.0, 3.0, 4.0, 5.0, 6.0],
        'profit_target_points': [4.0, 6.0, 8.0, 10.0, 12.0],
        'directional_bias_multiplier': [1.0, 1.2, 1.5, 1.8, 2.0],
        'spread_points': [0.5, 0.8, 1.0, 1.2, 1.5],
        'commission_per_trade': [0.5, 1.0, 1.5, 2.0]
    }
    
    all_results = {}
    
    # Test each parameter
    for param_name, test_values in parameter_tests.items():
        results = test_parameter(param_name, test_values, test_data)
        all_results[param_name] = results
    
    # Summary report
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = 0
    successful_tests = 0
    failed_tests = 0
    
    for param_name, results in all_results.items():
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        error_count = len(results) - success_count
        
        total_tests += len(results)
        successful_tests += success_count
        failed_tests += error_count
        
        status = "✅ PASS" if error_count == 0 else "⚠️ PARTIAL" if success_count > 0 else "❌ FAIL"
        print(f"{status} {param_name}: {success_count}/{len(results)} values successful")
        
        if error_count > 0:
            print(f"      Errors: {[r['value'] for r in results if r['status'] != 'SUCCESS']}")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    if failed_tests == 0:
        print("\n🎉 ALL PARAMETER TESTS PASSED!")
        print("✅ Strategy is fully functional with all parameter combinations")
    else:
        print(f"\n⚠️ {failed_tests} tests failed - review errors above")
    
    # Performance insights
    print(f"\n💡 PERFORMANCE INSIGHTS:")
    
    # Find best performing parameter values
    for param_name, results in all_results.items():
        successful_results = [r for r in results if r['status'] == 'SUCCESS' and r['total_return'] is not None]
        if successful_results:
            best_result = max(successful_results, key=lambda x: x['total_return'])
            worst_result = min(successful_results, key=lambda x: x['total_return'])
            
            print(f"   {param_name}:")
            print(f"     Best: {best_result['value']} (Return: {best_result['total_return']:.2f}%)")
            print(f"     Worst: {worst_result['value']} (Return: {worst_result['total_return']:.2f}%)")
    
    return all_results

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print(f"\n🔬 TESTING EDGE CASES")
    print("-" * 30)
    
    test_data = create_test_data()
    
    edge_cases = [
        # Extreme risk levels
        {'risk_per_trade': 0.1, 'description': 'Very low risk (0.1%)'},
        {'risk_per_trade': 5.0, 'description': 'Very high risk (5.0%)'},
        
        # Extreme position sizes
        {'stop_loss_points': 1.0, 'description': 'Very tight stops'},
        {'stop_loss_points': 10.0, 'description': 'Very wide stops'},
        
        # Extreme thresholds
        {'entry_threshold_points': 0.1, 'description': 'Very sensitive entries'},
        {'entry_threshold_points': 5.0, 'description': 'Very conservative entries'},
        
        # Risk-reward extremes
        {'profit_target_points': 2.0, 'stop_loss_points': 4.0, 'description': '1:2 risk-reward (negative)'},
        {'profit_target_points': 20.0, 'stop_loss_points': 2.0, 'description': '10:1 risk-reward'},
        
        # No bias
        {'directional_bias_multiplier': 1.0, 'description': 'No directional bias'},
        
        # High transaction costs
        {'spread_points': 2.0, 'commission_per_trade': 5.0, 'description': 'High transaction costs'},
    ]
    
    base_params = get_base_params()
    
    for i, edge_case in enumerate(edge_cases):
        description = edge_case.pop('description')
        test_params = base_params.copy()
        test_params.update(edge_case)
        
        try:
            strategy = CFDStrategyV1(test_params)
            final_equity = strategy.run_backtest(test_data)
            analytics = strategy.generate_analytics()
            
            # CRITICAL: Validate that trades were actually executed
            total_trades = analytics['total_trades']
            if total_trades == 0:
                raise ValueError(f"Edge case '{description}' executed 0 trades - strategy is not functional")
            
            print(f"  ✅ Edge case {i+1}: {description}")
            print(f"      Result: ${final_equity:.2f}, "
                  f"Trades: {analytics['total_trades']}, "
                  f"Return: {analytics['total_return']:.2f}%")
            
        except Exception as e:
            print(f"  ❌ Edge case {i+1}: {description}")
            print(f"      ERROR: {str(e)}")

if __name__ == "__main__":
    # Run comprehensive parameter tests
    results = run_comprehensive_parameter_tests()
    
    # Test edge cases
    test_edge_cases()
    
    print(f"\n" + "=" * 60)
    print("🏁 PARAMETER TESTING COMPLETE")
    print("=" * 60)
    print("All parameter combinations have been tested.")
    print("Review the results above to ensure strategy functionality.")
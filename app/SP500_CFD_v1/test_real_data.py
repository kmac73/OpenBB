#!/usr/bin/env python3
"""
REAL DATA TESTING - SP500 CFD Strategy V1
Tests with actual market data files - NO SYNTHETIC DATA
STRINGENT PASS/FAIL: Must execute trades or test FAILS
"""

import sys
import os
sys.path.append('/mnt/c/Users/kevin/git/OpenBB/app/SP500_CFD_v1')

from cfd_strategy_v1 import CFDStrategyV1
from market_data import Retrieve
import pandas as pd

def test_with_real_data():
    """Test strategy with real market data - MUST produce trades or FAIL"""
    print("🔥 REAL DATA TEST - STRINGENT PASS/FAIL REQUIREMENTS")
    print("=" * 60)
    
    # Use real market data retriever
    data_retriever = Retrieve()
    
    # Test parameters - these should work with real data
    test_params = {
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
    
    try:
        print("📊 Loading REAL market data...")
        # Use actual real data that exists
        real_data = data_retriever.get_data("SPX", "2024-07-01", "2024-07-03", "5M")
        print(f"✅ Loaded {len(real_data)} real data records")
        print(f"   Date range: {real_data.index[0]} to {real_data.index[-1]}")
        print(f"   Columns: {list(real_data.columns)}")
        print(f"   Price range: ${real_data['Close'].min():.2f} - ${real_data['Close'].max():.2f}")
        
        print("\n🚀 Running strategy with real data...")
        strategy = CFDStrategyV1(test_params)
        final_equity = strategy.run_backtest(real_data)
        analytics = strategy.generate_analytics()
        
        print(f"\n📊 STRATEGY RESULTS:")
        print(f"   Final Equity: ${final_equity:,.2f}")
        print(f"   Total Trades: {analytics['total_trades']}")
        print(f"   Win Rate: {analytics['win_rate']:.1f}%")
        print(f"   Total Return: {analytics['total_return']:.2f}%")
        
        # STRINGENT REQUIREMENT: Must execute trades
        if analytics['total_trades'] == 0:
            print("\n❌ CRITICAL FAILURE: Strategy executed 0 trades with real data")
            print("   This indicates the strategy logic is broken")
            return False
        else:
            print(f"\n✅ SUCCESS: Strategy executed {analytics['total_trades']} trades")
            return True
            
    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE: Real data test failed with error: {str(e)}")
        return False

def test_parameter_with_real_data(param_name, test_values):
    """Test specific parameter with real data - STRINGENT per parameter requirements"""
    print(f"\n🧪 REAL DATA PARAMETER TEST: {param_name}")
    print("-" * 50)
    
    data_retriever = Retrieve()
    
    base_params = {
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
    
    # Load real data once
    try:
        real_data = data_retriever.get_data("SPX", "2024-07-01", "2024-07-03", "5M")
        print(f"📊 Using {len(real_data)} real data records")
    except Exception as e:
        print(f"❌ FAILED TO LOAD REAL DATA: {str(e)}")
        return []
    
    results = []
    
    for value in test_values:
        try:
            # Update parameter
            test_params = base_params.copy()
            test_params[param_name] = value
            
            # Run strategy with real data
            strategy = CFDStrategyV1(test_params)
            final_equity = strategy.run_backtest(real_data)
            analytics = strategy.generate_analytics()
            
            # STRINGENT REQUIREMENT: Must execute trades for each parameter value
            if analytics['total_trades'] == 0:
                print(f"  ❌ {param_name}={value}: FAILED - 0 trades executed")
                result = {
                    'value': value,
                    'status': 'FAILED - NO TRADES',
                    'trades': 0,
                    'equity': final_equity,
                    'return': 0.0
                }
            else:
                print(f"  ✅ {param_name}={value}: SUCCESS - {analytics['total_trades']} trades, "
                      f"${final_equity:.2f}, {analytics['total_return']:.2f}%")
                result = {
                    'value': value,
                    'status': 'SUCCESS',
                    'trades': analytics['total_trades'],
                    'equity': final_equity,
                    'return': analytics['total_return']
                }
            
        except Exception as e:
            print(f"  ❌ {param_name}={value}: ERROR - {str(e)}")
            result = {
                'value': value,
                'status': f'ERROR: {str(e)}',
                'trades': 0,
                'equity': 0,
                'return': 0.0
            }
        
        results.append(result)
    
    return results

def run_comprehensive_real_data_tests():
    """Run comprehensive tests with real data - STRINGENT requirements"""
    print("🔥 COMPREHENSIVE REAL DATA TESTING")
    print("STRINGENT PASS/FAIL: Every parameter must produce trades or FAIL")
    print("=" * 70)
    
    # First test basic functionality
    print("\n1️⃣ BASIC FUNCTIONALITY TEST")
    basic_success = test_with_real_data()
    
    if not basic_success:
        print("\n❌ BASIC FUNCTIONALITY FAILED - STOPPING ALL TESTS")
        print("Fix the strategy before testing parameters")
        return False
    
    # Test individual parameters with real data
    print("\n2️⃣ PARAMETER-LEVEL TESTING WITH REAL DATA")
    
    parameter_tests = {
        'risk_per_trade': [0.5, 1.0, 1.5, 2.0],
        'opening_range_minutes': [15, 30, 45, 60],
        'entry_threshold_points': [1.0, 1.5, 2.0, 2.5],
        'stop_loss_points': [3.0, 4.0, 5.0, 6.0],
        'profit_target_points': [6.0, 8.0, 10.0, 12.0],
        'directional_bias_multiplier': [1.0, 1.2, 1.5, 1.8]
    }
    
    all_results = {}
    total_parameter_tests = 0
    successful_parameter_tests = 0
    
    for param_name, test_values in parameter_tests.items():
        results = test_parameter_with_real_data(param_name, test_values)
        all_results[param_name] = results
        
        # Count successes/failures per parameter
        for result in results:
            total_parameter_tests += 1
            if result['status'] == 'SUCCESS':
                successful_parameter_tests += 1
    
    # STRINGENT REPORTING
    print("\n" + "=" * 70)
    print("📊 STRINGENT REAL DATA TEST RESULTS")
    print("=" * 70)
    
    for param_name, results in all_results.items():
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        total_count = len(results)
        
        if success_count == 0:
            status = "❌ COMPLETE FAILURE"
        elif success_count == total_count:
            status = "✅ ALL PASSED"
        else:
            status = "⚠️ PARTIAL SUCCESS"
        
        print(f"{status} {param_name}: {success_count}/{total_count} values successful")
        
        # Show failed values
        failed_values = [r['value'] for r in results if r['status'] != 'SUCCESS']
        if failed_values:
            print(f"      Failed values: {failed_values}")
    
    print(f"\n📊 OVERALL STRINGENT RESULTS:")
    print(f"   Total parameter tests: {total_parameter_tests}")
    print(f"   Successful: {successful_parameter_tests} ({successful_parameter_tests/total_parameter_tests*100:.1f}%)")
    print(f"   Failed: {total_parameter_tests - successful_parameter_tests}")
    
    if successful_parameter_tests == 0:
        print("\n❌ COMPLETE STRATEGY FAILURE")
        print("   Strategy produces 0 trades with ALL parameter combinations")
        print("   Strategy logic is fundamentally broken")
        return False
    elif successful_parameter_tests == total_parameter_tests:
        print("\n🎉 ALL TESTS PASSED WITH REAL DATA")
        print("   Strategy executes trades with all parameter combinations")
        return True
    else:
        print(f"\n⚠️ PARTIAL SUCCESS")
        print(f"   {total_parameter_tests - successful_parameter_tests} parameter combinations produce 0 trades")
        print("   Strategy has issues with certain parameter combinations")
        return False

if __name__ == "__main__":
    print("🚨 REAL DATA TESTING - NO SYNTHETIC DATA ALLOWED")
    print("🚨 STRINGENT REQUIREMENTS - MUST EXECUTE TRADES OR FAIL")
    print("\n" + "=" * 70)
    
    success = run_comprehensive_real_data_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 STRATEGY VALIDATION: PASSED WITH REAL DATA")
    else:
        print("❌ STRATEGY VALIDATION: FAILED WITH REAL DATA")
        print("   Strategy does not execute trades with real market data")
        print("   Fix the strategy logic before proceeding")
    print("=" * 70)
    
    exit(0 if success else 1)
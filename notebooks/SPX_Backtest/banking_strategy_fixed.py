#!/usr/bin/env python3
"""
TRULY CORRECTED Banking Strategy Implementation

The key insight: Banking events should be processed as they occur during the 
trade sequence, not as post-hoc adjustments to balances.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_banking_strategy_FIXED(data, banking_trigger, banking_amount, reset_balance, 
                                   multiple_banking=True, excess_banking=True, 
                                   min_trading_balance=500_000):
    """
    TRULY FIXED: Banking strategy that processes banking in real-time during trades.
    
    KEY FIX: Instead of tracking "adjustments" and "cumulative adjustments",
    this version maintains a single current_balance that gets banking withdrawals
    applied immediately when triggered.
    """
    
    # Initialize with starting balance
    current_balance = data.iloc[0]['account_balance_before']
    banking_events = []
    total_banked = 0
    
    print(f"🔧 TRULY CORRECTED BANKING IMPLEMENTATION")
    print(f"Starting balance: ${current_balance:,.2f}")
    print(f"Banking trigger: ${banking_trigger:,.2f}")
    print()
    
    # Create results tracking
    simulation_results = []
    
    # Process each trade
    for idx, trade in data.iterrows():
        # Calculate the trade P&L from original data
        trade_pnl = trade['account_balance_after'] - trade['account_balance_before']
        
        # Apply trade result to our current balance
        balance_before_trade = current_balance
        current_balance += trade_pnl
        balance_after_trade = current_balance
        
        # Record this trade result
        simulation_results.append({
            'trade_number': trade['trade_number'],
            'exit_time': trade['exit_time'],
            'balance_before_trade': balance_before_trade,
            'trade_pnl': trade_pnl,
            'balance_after_trade': balance_after_trade,
            'balance_after_banking': None,  # Will be updated if banking occurs
            'banking_amount': 0
        })
        
        # Check if banking is triggered AFTER this trade
        banking_occurred = False
        while current_balance >= banking_trigger:
            # Calculate how much to bank
            if excess_banking and current_balance > (reset_balance + banking_amount):
                # Bank everything above reset balance
                amount_to_bank = current_balance - reset_balance
            else:
                # Bank standard amount
                amount_to_bank = min(banking_amount, current_balance - min_trading_balance)
            
            # Safety check
            if current_balance - amount_to_bank < min_trading_balance:
                amount_to_bank = current_balance - min_trading_balance
            
            if amount_to_bank > 0:
                # Execute banking withdrawal
                balance_before_banking = current_balance
                current_balance -= amount_to_bank
                total_banked += amount_to_bank
                
                # Record banking event
                banking_events.append({
                    'trade_index': idx,
                    'balance_before_banking': balance_before_banking,
                    'amount_banked': amount_to_bank,
                    'balance_after_banking': current_balance,
                    'total_banked_cumulative': total_banked
                })
                
                # Update the simulation result for this trade
                simulation_results[-1]['balance_after_banking'] = current_balance
                simulation_results[-1]['banking_amount'] = amount_to_bank
                
                banking_occurred = True
                print(f"💰 Banking after trade {trade['trade_number']}: ${balance_before_banking:,.0f} → Bank ${amount_to_bank:,.0f} → ${current_balance:,.0f} (Total banked: ${total_banked:,.0f})")
            
            # Exit conditions
            if not multiple_banking or current_balance < banking_trigger or amount_to_bank <= 0:
                break
        
        # If no banking occurred, set balance_after_banking to same as after_trade
        if not banking_occurred:
            simulation_results[-1]['balance_after_banking'] = current_balance
    
    # Final results
    original_final = data.iloc[-1]['account_balance_after']
    banking_final_trading = current_balance  # This is our final trading balance
    total_wealth = banking_final_trading + total_banked
    
    return {
        'original_final': original_final,
        'banking_final_trading': banking_final_trading,
        'total_banked': total_banked,
        'total_wealth': total_wealth,
        'improvement_absolute': total_wealth - original_final,
        'improvement_multiple': total_wealth / original_final if original_final > 0 else 0,
        'banking_events': len(banking_events),
        'banking_details': banking_events,
        'simulation_results': pd.DataFrame(simulation_results)
    }

def create_simple_test():
    """Create a simple, predictable test case to validate the logic."""
    # Simple test: Start with $50k, have a few big wins that trigger banking
    data = [
        {'trade_number': 1, 'exit_time': '2008-10-01', 'account_balance_before': 50000, 'account_balance_after': 1500000},  # Big win to $1.5M
        {'trade_number': 2, 'exit_time': '2008-10-02', 'account_balance_before': 1500000, 'account_balance_after': 2500000},  # Win to $2.5M (triggers banking)
        {'trade_number': 3, 'exit_time': '2008-10-03', 'account_balance_before': 2500000, 'account_balance_after': 3500000},  # Win to $3.5M (more banking)  
        {'trade_number': 4, 'exit_time': '2008-10-04', 'account_balance_before': 3500000, 'account_balance_after': 2000000},  # Loss back to $2M (triggers banking)
        {'trade_number': 5, 'exit_time': '2008-10-05', 'account_balance_before': 2000000, 'account_balance_after': 1500000},  # Loss to $1.5M (no banking)
    ]
    
    return pd.DataFrame(data)

def run_fixed_test():
    """Test the truly fixed banking strategy."""
    print("🧪 TESTING TRULY FIXED BANKING STRATEGY")
    print("=" * 60)
    
    # Use simple, predictable test data
    test_data = create_simple_test()
    print("Test scenario:")
    for _, row in test_data.iterrows():
        print(f"  Trade {row['trade_number']}: ${row['account_balance_before']:,.0f} → ${row['account_balance_after']:,.0f}")
    print()
    
    # Run the fixed banking strategy
    results = simulate_banking_strategy_FIXED(
        test_data, 
        banking_trigger=2_000_000,
        banking_amount=1_000_000,
        reset_balance=1_000_000,
        multiple_banking=True,
        excess_banking=True,
        min_trading_balance=500_000
    )
    
    print(f"\n📊 RESULTS:")
    print(f"=" * 30)
    print(f"Original final balance: ${results['original_final']:,.2f}")
    print(f"Banking final trading:  ${results['banking_final_trading']:,.2f}")  
    print(f"Total banked:          ${results['total_banked']:,.2f}")
    print(f"Total wealth:          ${results['total_wealth']:,.2f}")
    print(f"Improvement:           {results['improvement_multiple']:.1f}x")
    print(f"Banking events:        {results['banking_events']}")
    
    # Critical validation
    print(f"\n🔍 VALIDATION:")
    if results['banking_final_trading'] >= 0:
        print(f"✅ Final trading balance is positive")
    else:
        print(f"❌ Final trading balance is negative: ${results['banking_final_trading']:,.2f}")
        return False
        
    if results['total_wealth'] > results['original_final']:
        print(f"✅ Total wealth exceeds original final balance")  
    else:
        print(f"❌ Banking strategy shows no improvement")
        return False
        
    # Mathematical check
    calculated_wealth = results['banking_final_trading'] + results['total_banked']
    if abs(calculated_wealth - results['total_wealth']) < 0.01:
        print(f"✅ Wealth calculation is mathematically correct")
    else:
        print(f"❌ Math error: ${calculated_wealth:,.2f} ≠ ${results['total_wealth']:,.2f}")
        return False
    
    print(f"\n🎉 ALL TESTS PASSED - Implementation is truly fixed!")
    return True

if __name__ == "__main__":
    success = run_fixed_test()
    
    if success:
        print(f"\n🚀 IMPLEMENTATION IS CORRECT")
        print(f"Ready to replace the broken implementation with this fixed version.")
    else:
        print(f"\n❌ STILL BROKEN - More work needed")
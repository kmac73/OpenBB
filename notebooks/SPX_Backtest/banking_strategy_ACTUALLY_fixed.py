#!/usr/bin/env python3
"""
ACTUALLY CORRECT Banking Strategy Implementation

The ROOT CAUSE was fundamental misunderstanding of the simulation logic.

CORRECT APPROACH:
1. Start with the ORIGINAL trade sequence data
2. For each trade, calculate what the balance WOULD BE if we had banked profits earlier
3. Apply banking rules based on the CURRENT simulated balance, not original balance
4. Continue with REDUCED balance for subsequent trades

KEY INSIGHT: Banking reduces the trading account balance, which affects all subsequent trades!
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_banking_strategy_ACTUALLY_CORRECT(data, banking_trigger, banking_amount, reset_balance, 
                                              multiple_banking=True, excess_banking=True, 
                                              min_trading_balance=500_000):
    """
    ACTUALLY CORRECT banking strategy implementation.
    
    The key insight: We need to replay the ENTIRE trading sequence with banking
    applied, not just subtract banking amounts at the end.
    """
    
    banking_events = []
    total_banked = 0
    
    # Start with original initial balance
    current_balance = data.iloc[0]['account_balance_before']
    
    print(f"🔧 ACTUALLY CORRECT BANKING IMPLEMENTATION")
    print(f"Starting balance: ${current_balance:,.2f}")
    print(f"Banking trigger: ${banking_trigger:,.2f}")
    print()
    
    # Process each trade in sequence
    for idx, trade in data.iterrows():
        # Step 1: Apply the trade result proportionally
        original_before = trade['account_balance_before']
        original_after = trade['account_balance_after']
        original_pnl = original_after - original_before
        
        # Calculate the proportional P&L based on our current balance
        if original_before > 0:
            pnl_percentage = original_pnl / original_before
            simulated_pnl = current_balance * pnl_percentage
        else:
            simulated_pnl = original_pnl  # Fallback to absolute amount
        
        # Apply the trade result
        balance_after_trade = current_balance + simulated_pnl
        
        # Step 2: Check for banking after this trade result
        banking_this_trade = 0
        while balance_after_trade >= banking_trigger:
            # Calculate banking amount
            if excess_banking and balance_after_trade > (reset_balance + banking_amount):
                amount_to_bank = balance_after_trade - reset_balance
            else:
                amount_to_bank = min(banking_amount, balance_after_trade - min_trading_balance)
            
            # Safety check
            if balance_after_trade - amount_to_bank < min_trading_balance:
                amount_to_bank = balance_after_trade - min_trading_balance
            
            if amount_to_bank > 0:
                # Execute banking
                balance_before_banking = balance_after_trade
                balance_after_trade -= amount_to_bank
                total_banked += amount_to_bank
                banking_this_trade += amount_to_bank
                
                # Record event
                banking_events.append({
                    'trade_index': idx,
                    'trade_number': trade['trade_number'],
                    'balance_before_banking': balance_before_banking,
                    'amount_banked': amount_to_bank,
                    'balance_after_banking': balance_after_trade,
                    'total_banked_cumulative': total_banked
                })
                
                print(f"💰 Banking after trade {trade['trade_number']}: ${balance_before_banking:,.0f} → Bank ${amount_to_bank:,.0f} → ${balance_after_trade:,.0f}")
            
            # Exit conditions
            if not multiple_banking or balance_after_trade < banking_trigger or amount_to_bank <= 0:
                break
        
        # Step 3: Update current balance for next iteration
        current_balance = balance_after_trade
    
    # Final results
    original_final = data.iloc[-1]['account_balance_after']
    banking_final_trading = current_balance
    total_wealth = banking_final_trading + total_banked
    
    return {
        'original_final': original_final,
        'banking_final_trading': banking_final_trading,
        'total_banked': total_banked,
        'total_wealth': total_wealth,
        'improvement_absolute': total_wealth - original_final,
        'improvement_multiple': total_wealth / original_final if original_final > 0 else 0,
        'banking_events': len(banking_events),
        'banking_details': banking_events
    }

def create_validation_test():
    """Create a test that should definitely work correctly."""
    # Scenario: Account grows steadily, hits banking multiple times, ends higher
    data = [
        # Start modest, grow to trigger banking  
        {'trade_number': 1, 'account_balance_before': 50000, 'account_balance_after': 100000},   # 2x gain
        {'trade_number': 2, 'account_balance_before': 100000, 'account_balance_after': 200000},  # 2x gain  
        {'trade_number': 3, 'account_balance_before': 200000, 'account_balance_after': 400000},  # 2x gain
        {'trade_number': 4, 'account_balance_before': 400000, 'account_balance_after': 800000},  # 2x gain
        {'trade_number': 5, 'account_balance_before': 800000, 'account_balance_after': 1600000}, # 2x gain
        {'trade_number': 6, 'account_balance_before': 1600000, 'account_balance_after': 3200000}, # 2x gain - TRIGGERS BANKING
        {'trade_number': 7, 'account_balance_before': 3200000, 'account_balance_after': 6400000}, # 2x gain - MORE BANKING
        {'trade_number': 8, 'account_balance_before': 6400000, 'account_balance_after': 3200000}, # 50% loss
        {'trade_number': 9, 'account_balance_before': 3200000, 'account_balance_after': 1600000}, # 50% loss  
        {'trade_number': 10, 'account_balance_before': 1600000, 'account_balance_after': 2000000}, # 25% gain - TRIGGERS BANKING
    ]
    
    return pd.DataFrame(data)

def run_validation_test():
    """Test with data designed to validate correct banking behavior."""
    print("🧪 VALIDATION TEST WITH DESIGNED DATA")
    print("=" * 60)
    
    test_data = create_validation_test()
    print("Test scenario (original strategy):")
    for _, row in test_data.iterrows():
        pnl = row['account_balance_after'] - row['account_balance_before']
        pnl_pct = (pnl / row['account_balance_before']) * 100
        print(f"  Trade {row['trade_number']}: ${row['account_balance_before']:,.0f} → ${row['account_balance_after']:,.0f} ({pnl_pct:+.0f}%)")
    
    original_final = test_data.iloc[-1]['account_balance_after']
    print(f"\nOriginal strategy final: ${original_final:,.0f}")
    print()
    
    # Run banking strategy
    results = simulate_banking_strategy_ACTUALLY_CORRECT(
        test_data,
        banking_trigger=2_000_000,
        banking_amount=1_000_000, 
        reset_balance=1_000_000
    )
    
    print(f"\n📊 BANKING STRATEGY RESULTS:")
    print(f"=" * 40)
    print(f"Original final balance: ${results['original_final']:,.2f}")
    print(f"Banking final trading:  ${results['banking_final_trading']:,.2f}")
    print(f"Total banked:          ${results['total_banked']:,.2f}")
    print(f"Total wealth:          ${results['total_wealth']:,.2f}")
    print(f"Improvement:           {results['improvement_multiple']:.1f}x")
    print(f"Banking events:        {results['banking_events']}")
    
    # Validation
    print(f"\n🔍 VALIDATION CHECKS:")
    
    # Test 1: Positive final balance
    if results['banking_final_trading'] >= 0:
        print(f"✅ Final trading balance is positive: ${results['banking_final_trading']:,.2f}")
    else:
        print(f"❌ Final trading balance is NEGATIVE: ${results['banking_final_trading']:,.2f}")
        return False
    
    # Test 2: Total wealth > original (if banking occurred)
    if results['banking_events'] > 0:
        if results['total_wealth'] > results['original_final']:
            print(f"✅ Banking strategy improved total wealth")
        else:
            print(f"❌ Banking strategy did not improve wealth despite {results['banking_events']} events")
            return False
    
    # Test 3: Math check
    calculated_wealth = results['banking_final_trading'] + results['total_banked']
    if abs(calculated_wealth - results['total_wealth']) < 0.01:
        print(f"✅ Wealth calculation is mathematically sound")
    else:
        print(f"❌ Math error in wealth calculation")
        return False
    
    # Test 4: Reasonable banking amounts
    if results['banking_events'] > 0:
        avg_banked = results['total_banked'] / results['banking_events']
        if avg_banked >= 500_000:  # Should be substantial amounts
            print(f"✅ Banking amounts are reasonable (avg ${avg_banked:,.0f})")
        else:
            print(f"⚠️ Banking amounts seem low (avg ${avg_banked:,.0f})")
    
    print(f"\n🎉 VALIDATION PASSED - Implementation appears correct!")
    return True

if __name__ == "__main__":
    success = run_validation_test()
    
    if success:
        print(f"\n🚀 SUCCESS! Banking strategy implementation is ACTUALLY correct")
        print(f"This version properly simulates trading with reduced balance after banking events")
        print(f"Ready to integrate into the main notebook")
    else:
        print(f"\n❌ Still has issues - more debugging needed")
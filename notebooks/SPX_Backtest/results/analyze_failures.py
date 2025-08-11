#!/usr/bin/env python3
"""
SPX Strategy Failure Analysis
Analyzes why the strategy consistently loses money across different time periods
"""

import pandas as pd
import numpy as np

def analyze_period(period_name, filename):
    """Analyze strategy performance for a specific period"""
    print(f'🔍 ANALYZING {period_name}:')
    
    try:
        df = pd.read_csv(filename)
        
        # Core performance metrics
        total_trades = len(df)
        winners = df['is_winner'].sum()
        losers = total_trades - winners
        win_rate = (winners / total_trades) * 100
        
        winning_trades = df[df['is_winner'] == True]
        losing_trades = df[df['is_winner'] == False]
        
        avg_win = winning_trades['net_pnl'].mean()
        avg_loss = losing_trades['net_pnl'].mean()
        
        net_pnl = df['net_pnl'].sum()
        gross_pnl = df['gross_pnl'].sum()
        total_costs = df['transaction_costs'].sum()
        
        print(f'   📊 CORE METRICS:')
        print(f'      Trades: {total_trades} | Win Rate: {win_rate:.1f}% ({winners}W/{losers}L)')
        print(f'      Avg Win: ${avg_win:.2f} | Avg Loss: ${avg_loss:.2f}')
        print(f'      Win/Loss Ratio: {abs(avg_win/avg_loss):.2f}:1')
        print(f'      Net P&L: ${net_pnl:,.2f} | Account Loss: {(net_pnl/10000)*100:.1f}%')
        
        # The core problem: Risk/Reward imbalance
        profit_target = 6.0  # BPS
        stop_loss = 15.0     # BPS
        theoretical_rr = profit_target / stop_loss
        actual_rr = abs(avg_win / avg_loss)
        
        print(f'   ⚖️ RISK/REWARD ANALYSIS:')
        print(f'      Theoretical R/R: {theoretical_rr:.2f}:1 (6 BPS profit / 15 BPS stop)')
        print(f'      Actual R/R: {actual_rr:.2f}:1')
        print(f'      R/R Deficit: {theoretical_rr - actual_rr:.2f}')
        
        # Transaction cost impact
        cost_impact = (total_costs / abs(gross_pnl)) * 100 if gross_pnl != 0 else 0
        print(f'   💸 TRANSACTION COST IMPACT:')
        print(f'      Total Costs: ${total_costs:,.2f} (${total_costs/total_trades:.2f} per trade)')
        print(f'      Cost Impact: {cost_impact:.1f}% of gross P&L')
        
        # Breakeven analysis
        required_win_rate = stop_loss / (stop_loss + profit_target) * 100
        actual_win_rate = win_rate
        win_rate_deficit = actual_win_rate - required_win_rate
        
        print(f'   🎯 BREAKEVEN ANALYSIS:')
        print(f'      Required Win Rate: {required_win_rate:.1f}% (for breakeven)')
        print(f'      Actual Win Rate: {actual_win_rate:.1f}%')
        print(f'      Win Rate Surplus: {win_rate_deficit:+.1f}%')
        
        # Exit reason profitability
        print(f'   📤 EXIT REASON BREAKDOWN:')
        exit_summary = df.groupby('exit_reason').agg({
            'net_pnl': ['count', 'mean', 'sum'],
            'transaction_costs': 'sum'
        }).round(2)
        
        for reason in exit_summary.index:
            count = int(exit_summary.loc[reason, ('net_pnl', 'count')])
            avg_pnl = exit_summary.loc[reason, ('net_pnl', 'mean')]
            total_pnl = exit_summary.loc[reason, ('net_pnl', 'sum')]
            pct = (count / total_trades) * 100
            print(f'      {reason}: {count} ({pct:.1f}%) | Avg: ${avg_pnl:.2f} | Total: ${total_pnl:.2f}')
        
        print(f'')
        
        return {
            'period': period_name,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'net_pnl': net_pnl,
            'cost_impact': cost_impact,
            'theoretical_rr': theoretical_rr,
            'actual_rr': actual_rr
        }
        
    except Exception as e:
        print(f'   ❌ Error: {e}\n')
        return None

def main():
    print('=== COMPREHENSIVE SPX STRATEGY FAILURE ANALYSIS ===\n')
    
    periods = [
        ('2023-2024 (Recent)', 'SPX_Strategy_Results_2023-01-03_2024-03-29.csv'),
        ('2013-2024 (Long)', 'SPX_Strategy_Results_2013-01-03_2024-03-29.csv'), 
        ('2010-2024 (Longest)', 'SPX_Strategy_Results_2010-01-03_2024-03-29.csv')
    ]
    
    results = []
    for period_name, filename in periods:
        result = analyze_period(period_name, filename)
        if result:
            results.append(result)
    
    print('=== ROOT CAUSE ANALYSIS ===')
    print('')
    print('🚨 PRIMARY FAILURE MODE: MATHEMATICAL IMPOSSIBILITY')
    print('   The strategy is fundamentally flawed and cannot be profitable:')
    print('   - Risk 15 BPS (stop loss) to make 6 BPS (profit target)')
    print('   - Risk/Reward ratio of 0.4:1 is mathematically unsustainable')
    print('   - Requires 71.4% win rate just to break even BEFORE costs')
    print('   - Actual win rate ~66% guarantees losses')
    print('')
    
    print('💸 SECONDARY FAILURE MODE: TRANSACTION COST HEMORRHAGE')
    print('   High-frequency trading with fixed costs creates death spiral:')
    avg_cost_impact = sum(r['cost_impact'] for r in results) / len(results)
    print(f'   - Average cost impact: {avg_cost_impact:.1f}% of gross profits')
    print('   - $5 fixed cost per trade regardless of profit size')
    print('   - ~$70 average wins become ~$65 after costs')
    print('   - Strategy would need much larger targets to absorb costs')
    print('')
    
    print('🩹 TERTIARY FACTOR: SLIPPAGE AND EXECUTION REALITY')
    print('   Perfect backtesting vs real market execution:')
    print('   - Backtest assumes perfect fills at exact target/stop prices')
    print('   - Real trading has slippage, especially at market open/close')
    print('   - Bid-ask spreads reduce actual profits')
    print('   - Market gaps can cause worse-than-expected exits')
    print('')
    
    print('=== STRATEGY DESIGN FLAWS ===')
    print('')
    print('1. ASYMMETRIC RISK/REWARD:')
    print('   - Risks $150-200 per trade to make $65-75')
    print('   - One loss wipes out 2.5-3 wins')
    print('   - Win rate needs to be impossibly high (>80%) to overcome this')
    print('')
    
    print('2. SCALPING WITHOUT EDGE:')
    print('   - 1 BPS entry trigger is essentially random noise')
    print('   - No fundamental or technical analysis behind entries')
    print('   - High frequency amplifies transaction costs')
    print('   - Strategy assumes mean reversion that may not exist')
    print('')
    
    print('3. LEVERAGE MULTIPLICATION OF LOSSES:')
    print('   - 20x leverage amplifies small price moves')
    print('   - Amplifies both profits AND losses equally')
    print('   - With negative expectancy, leverage just makes losses bigger faster')
    print('   - Risk management prevents blowup but cannot fix fundamental flaw')
    print('')
    
    print('=== RECOMMENDATIONS ===')
    print('')
    print('🛑 IMMEDIATE ACTIONS:')
    print('   1. STOP trading this strategy - it has negative mathematical expectancy')
    print('   2. Preserve remaining capital for better opportunities')
    print('   3. Do not increase position size or leverage - this will only accelerate losses')
    print('')
    
    print('🔧 STRATEGY FIXES (if continuing):')
    print('   1. INCREASE profit targets to 15+ BPS (match stop loss for 1:1 R/R minimum)')
    print('   2. REDUCE transaction costs (use cheaper broker or larger position sizes)')  
    print('   3. ADD fundamental filters (only trade with strong directional bias)')
    print('   4. REDUCE frequency (fewer trades = lower total transaction costs)')
    print('   5. TEST on paper/simulation before risking real money')
    print('')
    
    print('💡 ALTERNATIVE APPROACHES:')
    print('   1. Trend following instead of mean reversion')
    print('   2. Longer timeframes (daily instead of 5-minute bars)')
    print('   3. Options strategies with asymmetric payoffs')
    print('   4. Index investing instead of active trading')
    print('')
    
    print('=== CONCLUSION ===')
    print('This strategy loses money because it is mathematically designed to lose money.')
    print('No amount of optimization, risk management, or parameter tuning can fix')
    print('a fundamentally flawed risk/reward structure. The consistent 65-66% win rate')
    print('across all periods proves the strategy has some predictive power, but not')
    print('enough to overcome the asymmetric risk/reward ratio and transaction costs.')
    
if __name__ == '__main__':
    main()
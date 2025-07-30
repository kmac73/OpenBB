#!/usr/bin/env python3
"""
Debug PDF generation by testing each section
"""
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

def test_pdf_sections():
    """Test each section of PDF generation individually"""
    
    # Test data
    trades_df = pd.DataFrame({
        'net_pnl': [100, -50, 200, -30, 150],
        'gross_pnl': [110, -40, 210, -20, 160],
        'transaction_cost': [0.445] * 5,
        'type': ['LONG', 'SHORT', 'LONG', 'SHORT', 'LONG'],
        'exit_reason': ['profit_target', 'stop_loss', 'profit_target', 'stop_loss', 'market_close'],
        'entry_price': [4500, 4520, 4480, 4510, 4495],
        'exit_price': [4510, 4510, 4500, 4500, 4505],
        'date': [datetime.now()] * 5
    })

    summary = {
        'total_trades': 5, 'long_trades': 3, 'short_trades': 2,
        'winning_trades': 3, 'losing_trades': 2, 'win_rate': 60.0,
        'total_pnl': 370, 'gross_pnl': 420, 'total_transaction_costs': 2.225,
        'avg_pnl_per_trade': 74, 'avg_winning_trade': 150, 'avg_losing_trade': -40,
        'profit_factor': 1.5, 'sharpe_ratio': 0.8, 'profitable_days': 4,
        'profitable_days_pct': 80, 'total_days': 5, 'max_daily_gain': 200,
        'max_daily_loss': -50, 'avg_daily_pnl': 74, 'daily_volatility': 95, 'var_95': 156.275
    }

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        print("1. Basic PDF setup: OK")
        
        # Title
        story.append(Paragraph("Test Report", styles['Title']))
        story.append(Spacer(1, 20))
        print("2. Title added: OK")
        
        # Simple table
        param_data = [
            ['Parameter', 'Value'],
            ['Test', 'Value']
        ]
        
        param_table = Table(param_data, colWidths=[3*inch, 3*inch])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(param_table)
        print("3. Parameter table: OK")
        
        # Test statistical calculations
        print("4. Testing statistical calculations...")
        pnl_data = trades_df['net_pnl'].values
        n = len(pnl_data)
        mean_pnl = np.mean(pnl_data)
        std_pnl = np.std(pnl_data, ddof=1)
        se_pnl = std_pnl / np.sqrt(n)
        t_stat = mean_pnl / se_pnl if se_pnl != 0 else 0
        df = n - 1
        
        print(f"   Basic stats: mean={mean_pnl:.2f}, std={std_pnl:.2f}, t_stat={t_stat:.2f}")
        
        # Import scipy - this might be the issue
        print("5. Testing scipy import...")
        from scipy import stats as scipy_stats
        print("   Scipy imported successfully")
        
        # Test t-distribution calculations
        print("6. Testing scipy t-distribution...")
        if abs(t_stat) > 8:
            p_value_str = "< 1e-15"
        else:
            p_value = 2 * (1 - scipy_stats.t.cdf(abs(t_stat), df))
            p_value_str = f"{p_value:.6f}"
        
        print(f"   P-value calculation: {p_value_str}")
        
        alpha = 0.05
        t_critical = scipy_stats.t.ppf(1 - alpha/2, df)
        ci_lower = mean_pnl - t_critical * se_pnl
        ci_upper = mean_pnl + t_critical * se_pnl
        
        print(f"   Confidence interval: [{ci_lower:.2f}, {ci_upper:.2f}]")
        print("7. Statistical calculations: OK")
        
        # Add statistical table
        statistical_data = [
            ['Statistical Test', 'Value'],
            ['Sample Size (n)', f"{n:,}"],
            ['Mean P&L per Trade', f"${mean_pnl:.2f}"],
            ['P-Value (two-tailed)', p_value_str],
            ['95% Confidence Interval', f"${ci_lower:.2f} to ${ci_upper:.2f}"]
        ]
        
        statistical_table = Table(statistical_data, colWidths=[3*inch, 3*inch])
        statistical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(statistical_table)
        print("8. Statistical table added: OK")
        
        # Build PDF
        print("9. Building PDF...")
        doc.build(story)
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        
        print(f"10. PDF generation complete: {len(pdf_bytes)} bytes")
        print(f"    PDF header: {pdf_bytes[:20]}")
        
        return pdf_bytes
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_pdf_sections()
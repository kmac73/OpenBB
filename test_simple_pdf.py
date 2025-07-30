#!/usr/bin/env python3
"""
Simple PDF generation test
"""
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

def test_simple_pdf():
    """Test basic PDF generation"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        story.append(Paragraph("Test PDF Report", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Add simple table
        data = [
            ['Parameter', 'Value'],
            ['Test 1', 'Value 1'],
            ['Test 2', 'Value 2']
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        
        # Build PDF
        print("Building PDF...")
        doc.build(story)
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        
        print(f"PDF created: {len(pdf_bytes)} bytes")
        print(f"First 20 bytes: {pdf_bytes[:20]}")
        
        # Save to file
        with open('/tmp/simple_test.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print("PDF saved successfully")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_pdf()
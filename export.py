import io
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def export_to_csv(df: pd.DataFrame) -> bytes:
    """Exports a DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode('utf-8')

def export_to_excel(df: pd.DataFrame) -> bytes:
    """Exports a DataFrame to an Excel (.xlsx) file bytes using openpyxl."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Query Results')
    return output.getvalue()

def export_to_pdf(question: str, sql: str, df: pd.DataFrame, fig: go.Figure | None = None) -> bytes:
    """
    Generates a clean one-page PDF report combining the question, SQL, 
    result table, and an optional Plotly chart image.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4b5563')
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        textColor=colors.HexColor('#1e3a8a'),
        backColor=colors.HexColor('#f3f4f6'),
        borderColor=colors.HexColor('#e5e7eb'),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8
    )

    # 1. Title / Question
    story.append(Paragraph("AI SQL Analytics Report", title_style))
    story.append(Paragraph(f"<b>Question:</b> {question}", body_style))
    story.append(Spacer(1, 8))

    # 2. SQL Query Block
    story.append(Paragraph("Generated SQL:", section_style))
    story.append(Paragraph(sql.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    # 3. Chart Image (if available)
    if fig is not None:
        try:
            # Convert Plotly figure to static image bytes (requires kaleido)
            img_bytes = fig.to_image(format="png", width=500, height=220, scale=2)
            img_io = io.BytesIO(img_bytes)
            story.append(Spacer(1, 4))
            story.append(Image(img_io, width=450, height=198))
            story.append(Spacer(1, 8))
        except Exception:
            # Fallback gracefully if kaleido isn't installed or image conversion fails
            pass

    # 4. Result Table (capped at top 15 rows for clean PDF layout)
    story.append(Paragraph("Result Data Preview:", section_style))
    if df is not None and not df.empty:
        preview_df = df.head(15)
        table_data = [list(preview_df.columns)]
        for _, row in preview_df.iterrows():
            table_data.append([str(val) for val in row])
            
        t = Table(table_data, colWidths=None)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#111827')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No data returned.", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    print("--- Export Test ---")
    df_test = pd.DataFrame({
        "CustomerID": [1001, 1002],
        "CustomerName": ["Rajesh Kumar", "Priya Sharma"],
        "City": ["Hyderabad", "Bangalore"]
    })
    
    csv_bytes = export_to_csv(df_test)
    excel_bytes = export_to_excel(df_test)
    
    print(f"CSV Export: PASSED ({len(csv_bytes)} bytes)")
    print(f"Excel Export: PASSED ({len(excel_bytes)} bytes)")
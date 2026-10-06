import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFReportGenerator:
    @staticmethod
    def generate_pdf(question: str, sql_query: str, df: pd.DataFrame, insights: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        story = []

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1E293B'), spaceAfter=10)
        h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0369A1'), spaceBefore=10, spaceAfter=5)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#334155'))
        code_style = ParagraphStyle('CodeStyle', parent=styles['Code'], fontSize=8, leading=10, textColor=colors.HexColor('#0F172A'), backColor=colors.HexColor('#F1F5F9'))

        story.append(Paragraph("E-Commerce Analytics Executive Report", title_style))
        story.append(Paragraph(f"<b>User Question:</b> {question}", body_style))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Executed PostgreSQL Query", h2_style))
        story.append(Paragraph(sql_query.replace('\n', '<br/>'), code_style))
        story.append(Spacer(1, 10))

        if insights:
            story.append(Paragraph("Executive Business Insights", h2_style))
            story.append(Paragraph(insights.replace('\n', '<br/>'), body_style))
            story.append(Spacer(1, 10))

        story.append(Paragraph(f"Results Summary (Top {min(len(df), 15)} Rows)", h2_style))
        
        if not df.empty:
            sample_df = df.head(15)
            table_data = [[Paragraph(str(col), body_style) for col in sample_df.columns]]
            
            for _, row in sample_df.iterrows():
                row_cells = [Paragraph(str(val), body_style) for val in row.values]
                table_data.append(row_cells)

            col_width = (doc.width) / max(len(df.columns), 1)
            pdf_table = Table(table_data, colWidths=[col_width] * len(df.columns))
            pdf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ]))
            story.append(pdf_table)

        doc.build(story)
        return buffer.getvalue()

pdf_generator = PDFReportGenerator()
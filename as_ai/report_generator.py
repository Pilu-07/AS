import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import json

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

import logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
logging.basicConfig(
    filename=os.path.join(log_dir, "analysis_logs.txt"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def generate_pdf_report(dataset_id: str, report_data: dict) -> str:
    """
    Generates a professional PDF report containing the autonomous analysis insights,
    anomaly detection strings, and visualizations.
    """
    filename = f"{dataset_id}_analysis_report_{int(time.time())}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    
    title_style = styles['Heading1']
    h2_style = styles['Heading2']
    normal_style = styles['Normal']
    code_style = styles['Code']

    # Title
    Story.append(Paragraph(f"Autonomous AI Analysis Report: {dataset_id}", title_style))
    Story.append(Spacer(1, 0.2 * inch))

    # 1. Dataset Profile
    Story.append(Paragraph("1. Dataset Profile", h2_style))
    profile = report_data.get('dataset_profile', {})
    Story.append(Paragraph(f"Rows: {profile.get('rows')} | Columns: {profile.get('columns')}", normal_style))
    Story.append(Spacer(1, 0.1 * inch))

    # 2. Anomalies
    Story.append(Paragraph("2. Anomaly Detection", h2_style))
    anomalies = report_data.get('anomalies', {})
    if anomalies:
        for col, count in anomalies.items():
            Story.append(Paragraph(f"<b>{col}</b>: {count} anomalous outlier(s) detected.", normal_style))
    else:
        Story.append(Paragraph("No significant anomalies detected by Z-Score or IsolationForest.", normal_style))
    Story.append(Spacer(1, 0.1 * inch))
    
    # 3. AI Insights
    Story.append(Paragraph("3. AI Strategic Insights", h2_style))
    insights = report_data.get('insights', {})
    Story.append(Paragraph("<b>Key Trends:</b> " + str(insights.get('key_trends', 'N/A')), normal_style))
    Story.append(Spacer(1, 0.05 * inch))
    Story.append(Paragraph("<b>Business Context:</b> " + str(insights.get('business_insights', 'N/A')), normal_style))
    Story.append(Spacer(1, 0.2 * inch))
    
    # 4. Visualizations
    Story.append(Paragraph("4. Key Visualizations", h2_style))
    visualizations = report_data.get('visualizations', [])
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for viz_url in visualizations:
        # Resolve absolute path from HTTP path
        abs_img_path = os.path.join(root_dir, viz_url.lstrip('/'))
        if os.path.exists(abs_img_path):
            try:
                # Add image scaling
                img = Image(abs_img_path, width=4*inch, height=2.5*inch)
                Story.append(img)
                Story.append(Spacer(1, 0.1 * inch))
            except Exception as e:
                pass
                
    doc.build(Story)
    
    logging.info(f"Generated PDF Report: {filename} for dataset {dataset_id}")
    
    return f"/reports/{filename}"

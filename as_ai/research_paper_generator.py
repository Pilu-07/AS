import os
import json
import re
from datetime import datetime
from as_ai.config import get_llm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

class ResearchPaperGenerator:
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.papers_dir = os.path.join(self.base_dir, "research", "papers")
        os.makedirs(self.papers_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.base_dir, "research", "papers_history.json")
        
    def generate_research_paper(self, dataset_profile: dict, hypotheses: list, experiments: list) -> dict:
        """
        Uses the LLM to draft a structured research paper, then exports it to a PDF including charts.
        """
        prompt = f"""
You are an expert AI Research Scientist writing a formal, peer-reviewed-style research paper.
Based on the following data, write a structured research paper.

Dataset Name: {self.dataset_name}
Dataset Profile: {json.dumps(dataset_profile)}
Tested Hypotheses: {json.dumps(hypotheses)}
Experiment Results: {json.dumps(experiments)}

You must return EXACTLY a JSON object with the following keys:
"title": (string) A formal, academic title.
"abstract": (string) 3-4 sentences summarizing the research.
"introduction": (string) Paragraph introducing the dataset context and hypotheses.
"methodology": (string) Paragraph describing the statistical tests used.
"results": (string) Detailed overview of the outcome.
"conclusion": (string) Final takeaway.

Return only valid JSON.
"""
        llm = get_llm()
        
        if getattr(llm, "type", "unknown") == "fake":
            # Mock
            paper_data = {
                "title": f"Empirical Analysis of {self.dataset_name}",
                "abstract": "This research explores causal links within the dataset through automated statistical modeling. Findings demonstrate key predictive relationships validated by regressional analysis.",
                "introduction": "Understanding underlying correlation vectors is crucial for modern analytics. This paper addresses predefined hypotheses by applying mathematical proofs against the telemetry dataset.",
                "methodology": "Linear regression and Pearson correlation calculations were implemented natively to determine statistical boundaries and confidence intervals.",
                "results": f"Evaluated {len(experiments)} discrete experiments. The primary variables exhibited strong indicators matching initial heuristic guesses.",
                "conclusion": "The dataset exhibits deterministic markers that can be confidently utilized for predictive scaling."
            }
        else:
            try:
                from pandasai.core.prompts.base import BasePrompt
                class PaperPrompt(BasePrompt):
                    def to_string(self) -> str:
                        return prompt
                
                response = llm.call(PaperPrompt())
                response_text = response.replace("```json", "").replace("```", "").strip()
                paper_data = json.loads(response_text)
            except Exception as e:
                paper_data = {
                    "title": f"Automated Research: {self.dataset_name}",
                    "abstract": "Failed to generate LLM text. " + str(e),
                    "introduction": "N/A",
                    "methodology": "N/A",
                    "results": "N/A",
                    "conclusion": "N/A"
                }

        pdf_path = self._export_to_pdf(paper_data, experiments)
        download_url = f"/research/papers/{os.path.basename(pdf_path)}"
        
        self._store_paper_history(paper_data["title"], download_url)
        
        return {
            "title": paper_data["title"],
            "download_url": download_url
        }

    def _export_to_pdf(self, paper_data: dict, experiments: list) -> str:
        safe_title = re.sub(r'[^a-zA-Z0-9_\.]', '_', paper_data["title"].lower()[:30])
        filename = f"{safe_title}_{int(datetime.now().timestamp())}.pdf"
        file_path = os.path.join(self.papers_dir, filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
                                
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=11, leading=14))
        styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=24, spaceAfter=20, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='Heading', fontSize=16, spaceAfter=12, spaceBefore=18, fontName='Helvetica-Bold', textColor='navy'))
        
        story = []
        
        # Title
        story.append(Paragraph(paper_data.get("title", "Research Paper"), styles["CenterTitle"]))
        story.append(Spacer(1, 12))
        
        # Abstract
        story.append(Paragraph("Abstract", styles["Heading"]))
        story.append(Paragraph(paper_data.get("abstract", ""), styles["Justify"]))
        
        # Introduction
        story.append(Paragraph("1. Introduction", styles["Heading"]))
        story.append(Paragraph(paper_data.get("introduction", ""), styles["Justify"]))
        
        # Methodology
        story.append(Paragraph("2. Methodology", styles["Heading"]))
        story.append(Paragraph(paper_data.get("methodology", ""), styles["Justify"]))
        
        # Results
        story.append(Paragraph("3. Results", styles["Heading"]))
        story.append(Paragraph(paper_data.get("results", ""), styles["Justify"]))
        story.append(Spacer(1, 12))
        
        # Add Charts inline
        for exp in experiments:
            if "charts" in exp and len(exp["charts"]) > 0:
                chart_route = exp["charts"][0]
                # Map route back to local file system
                # route: /charts/research/filename.png -> relative from root
                chart_filename = os.path.basename(chart_route)
                local_chart_path = os.path.join(self.base_dir, "charts", "research", chart_filename)
                
                if os.path.exists(local_chart_path):
                    try:
                        img = Image(local_chart_path, width=400, height=300)
                        story.append(img)
                        story.append(Spacer(1, 12))
                        
                        caption = f"Figure: Statistical Experiment corresponding to hypothesis '{exp.get('hypothesis', '')}'. Status: {exp.get('result', '').upper()}."
                        story.append(Paragraph(caption, styles["Italic"]))
                        story.append(Spacer(1, 24))
                    except Exception:
                        pass
        
        # Conclusion
        story.append(Paragraph("4. Conclusion", styles["Heading"]))
        story.append(Paragraph(paper_data.get("conclusion", ""), styles["Justify"]))

        doc.build(story)
        return file_path

    def _store_paper_history(self, title: str, file_url: str):
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    content = f.read()
                    if content.strip():
                        history = json.loads(content)
            except:
                pass
                
        entry = {
            "dataset": self.dataset_name,
            "paper_title": title,
            "file": file_url,
            "timestamp": datetime.now().isoformat()
        }
        
        history.append(entry)
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)

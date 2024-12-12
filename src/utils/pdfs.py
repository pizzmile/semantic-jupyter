from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import re

# Define a custom function to highlight keywords using HTML-like formatting
def highlight_keywords(text, keywords):
    if not text:
        return ""
    for kw in keywords:
        text = re.sub(rf"(?i)\b({re.escape(kw)})\b", r"<b><font color='red'>\1</font></b>", text)
    return text

# Function to convert all fields in a paper to strings
def convert_paper_to_string(paper):
    stringified_paper = {}
    print(paper)
    for key, value in paper.items():
        if isinstance(value, dict):
            # Convert dict values to a string representation
            stringified_paper[key] = str(value)
        elif isinstance(value, list):
            # Convert list of authors or other items to a comma-separated string
            stringified_paper[key] = ", ".join([str(item) for item in value])
        else:
            # Convert all other types to string
            stringified_paper[key] = str(value)
    return stringified_paper

# Create the PDF using Platypus (Page Layout and Typography Using Scripts)
def export_pdf(filename, papers, keywords):
    # Convert all papers to strings before generating the PDF
    papers = [convert_paper_to_string(paper) for paper in papers]

    # Create a document template
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()

    # Create a list to hold the document's flowables (paragraphs, spacers, etc.)
    flowables = []

    # Add each paper's content
    for paper in papers:
        # Paper ID Title
        flowables.append(Paragraph(f"<strong>Paper ID:</strong> {paper['paperId']}", styles['Heading2']))
        flowables.append(Spacer(1, 12))

        # Paper Title
        highlighted_title = highlight_keywords(paper.get('title', "N/A"), keywords)
        flowables.append(Paragraph(f"<strong>Title:</strong> {highlighted_title}", styles['BodyText']))
        flowables.append(Spacer(1, 12))

        # Authors
        highlighted_authors = highlight_keywords(paper.get('authors', "N/A"), keywords)
        flowables.append(Paragraph(f"<strong>Authors:</strong> {highlighted_authors}", styles['BodyText']))
        flowables.append(Spacer(1, 12))

        # TL;DR
        highlighted_tldr = highlight_keywords(paper.get('tldr', "N/A"), keywords)
        flowables.append(Paragraph(f"<strong>TL;DR:</strong> {highlighted_tldr}", styles['BodyText']))
        flowables.append(Spacer(1, 12))

        # Abstract
        highlighted_abstract = highlight_keywords(paper.get('abstract', "N/A"), keywords)
        flowables.append(Paragraph(f"<strong>Abstract:</strong> {highlighted_abstract}", styles['BodyText']))
        flowables.append(Spacer(1, 24))

    # Build the document with the defined flowables
    doc.build(flowables)
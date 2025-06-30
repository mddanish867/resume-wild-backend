# from fpdf import FPDF
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# def save_text_as_pdf(text, output_path):
#     """Save text to a PDF file, handling Unicode characters."""
#     try:
#         # Replace problematic Unicode characters with Latin-1 compatible alternatives
#         text = text.replace('\u2013', '-')  # Replace en dash with hyphen
#         text = text.replace('\u2014', '-')  # Replace em dash with hyphen
#         text = text.replace('\u2018', "'")  # Replace left single quote
#         text = text.replace('\u2019', "'")  # Replace right single quote
#         text = text.replace('\u2026', '...')  # Replace ellipsis
#         # Add more replacements as needed for other common Unicode characters

#         # Alternatively, remove all non-Latin-1 characters
#         text = text.encode('latin-1', errors='ignore').decode('latin-1')

#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Arial", size=12)
#         for line in text.split('\n'):
#             pdf.multi_cell(0, 10, line)
#         pdf.output(output_path)
#         logger.info(f"PDF saved successfully at {output_path}")
#     except Exception as e:
#         logger.error(f"Error saving PDF to {output_path}: {e}")
#         raise

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_text_as_pdf(text, output_path):
    """Save text to a PDF file using ReportLab."""
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        text_object = c.beginText()
        text_object.setTextOrigin(inch, letter[1] - inch)  # Start 1 inch from top-left
        text_object.setLeading(14)  # Line spacing

        for line in text.split('\n'):
            text_object.textLine(line)
        
        c.drawText(text_object)
        c.showPage()
        c.save()
        logger.info(f"PDF saved successfully at {output_path}")
    except Exception as e:
        logger.error(f"Error saving PDF to {output_path}: {e}")
        raise
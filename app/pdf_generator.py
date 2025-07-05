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

import os
import uuid
import logging
from docx import Document
from docx2pdf import convert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_text_as_pdf(text, pdf_path):
    """
    Save optimized text to a .docx file, then convert to .pdf.
    Preserves formatting better than direct text-to-pdf.
    """

    try:
        # 1. Generate a unique temporary .docx path
        temp_docx_path = pdf_path.replace(".pdf", f"_{uuid.uuid4().hex}.docx")

        # 2. Write the optimized text to the .docx file
        doc = Document()
        for line in text.split("\n"):
            if line.strip().startswith("--- ") and line.strip().endswith(" ---"):
                # Format section titles (e.g., --- OVERVIEW ---)
                section_title = line.strip().replace("---", "").strip()
                p = doc.add_paragraph()
                run = p.add_run(section_title)
                run.bold = True
                run.underline = True
            else:
                doc.add_paragraph(line.strip())
        
        doc.save(temp_docx_path)
        logger.info(f"Temporary DOCX saved at: {temp_docx_path}")

        # 3. Convert .docx to .pdf
        convert(temp_docx_path, pdf_path)
        logger.info(f"PDF successfully saved at: {pdf_path}")

        # 4. Cleanup the temporary .docx file
        os.remove(temp_docx_path)
        logger.info(f"Temporary DOCX deleted: {temp_docx_path}")

    except Exception as e:
        logger.error(f"Error saving PDF: {e}")
        raise

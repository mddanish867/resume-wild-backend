import os
import docx
import logging

logger = logging.getLogger(__name__)

def extract_text_from_docx(path):
    """Extract plain text from a .docx file."""
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File not found: {path}")

    try:
        doc = docx.Document(path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not text:
            logger.warning(f"No text content extracted from: {path}")
        return text
    except Exception as e:
        logger.error(f"Error reading .docx file '{path}': {e}")
        raise

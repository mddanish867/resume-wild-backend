import os
import logging
import platform
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_docx_to_pdf(docx_path, pdf_path):
    """
    Converts a .docx file to .pdf using the best available method for the platform.
    Tries multiple conversion methods in order of preference.
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Input DOCX file not found: {docx_path}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    # Try different conversion methods
    conversion_methods = []
    
    # Method 1: docx2pdf (Windows preferred, works on Linux with LibreOffice)
    try:
        from docx2pdf import convert as docx2pdf_convert
        conversion_methods.append(("docx2pdf", docx2pdf_convert))
    except ImportError:
        logger.warning("docx2pdf not available")
    
    # Method 2: python-docx2txt + reportlab (cross-platform fallback)
    conversion_methods.append(("reportlab", convert_with_reportlab))
    
    # Method 3: LibreOffice command line (Linux/Mac)
    if platform.system() in ['Linux', 'Darwin']:
        conversion_methods.append(("libreoffice", convert_with_libreoffice))
    
    # Try each method
    for method_name, method_func in conversion_methods:
        try:
            logger.info(f"Attempting PDF conversion using {method_name}")
            
            if method_name == "docx2pdf":
                method_func(docx_path, pdf_path)
            else:
                method_func(docx_path, pdf_path)
            
            # Verify the PDF was created
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                logger.info(f"Successfully converted DOCX to PDF using {method_name}: {pdf_path}")
                return
            else:
                logger.warning(f"{method_name} method did not produce a valid PDF")
                
        except Exception as e:
            logger.warning(f"PDF conversion failed with {method_name}: {e}")
            continue
    
    # If all methods failed, raise an exception
    raise Exception("All PDF conversion methods failed. Please ensure you have the required dependencies installed.")

def convert_with_reportlab(docx_path, pdf_path):
    """
    Convert DOCX to PDF using python-docx + reportlab.
    This is a fallback method that extracts text and creates a basic PDF.
    """
    try:
        from docx import Document
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
    except ImportError:
        raise ImportError("Required packages not installed. Run: pip install python-docx reportlab")
    
    # Read the DOCX file
    doc = Document(docx_path)
    
    # Create PDF
    pdf_doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                               rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Build content
    story = []
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            story.append(Spacer(1, 6))
            continue
        
        # Determine style based on content
        if i == 0 or len(text.split()) <= 3:
            # Likely a title or heading
            if any(keyword in text.lower() for keyword in ['summary', 'experience', 'skills', 'education', 'projects']):
                story.append(Paragraph(text, heading_style))
            else:
                story.append(Paragraph(text, title_style))
        else:
            # Regular paragraph
            # Escape special characters for reportlab
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(text, normal_style))
    
    # Build PDF
    pdf_doc.build(story)
    logger.info("PDF created using reportlab method")

def convert_with_libreoffice(docx_path, pdf_path):
    """
    Convert DOCX to PDF using LibreOffice command line.
    This method requires LibreOffice to be installed on the system.
    """
    import subprocess
    
    # Check if LibreOffice is available
    libreoffice_commands = ['libreoffice', 'soffice']
    libreoffice_cmd = None
    
    for cmd in libreoffice_commands:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            libreoffice_cmd = cmd
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not libreoffice_cmd:
        raise Exception("LibreOffice not found. Please install LibreOffice for PDF conversion.")
    
    # Get absolute paths
    docx_path = os.path.abspath(docx_path)
    output_dir = os.path.dirname(os.path.abspath(pdf_path))
    
    # Run LibreOffice conversion
    cmd = [
        libreoffice_cmd,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        docx_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"LibreOffice conversion failed: {result.stderr}")
    
    # LibreOffice creates PDF with same name as DOCX
    docx_name = os.path.splitext(os.path.basename(docx_path))[0]
    generated_pdf = os.path.join(output_dir, f"{docx_name}.pdf")
    
    # Rename to desired output name if different
    if generated_pdf != pdf_path:
        if os.path.exists(generated_pdf):
            os.rename(generated_pdf, pdf_path)
    
    logger.info("PDF created using LibreOffice method")

def install_docx2pdf_dependencies():
    """
    Install docx2pdf dependencies based on platform.
    This is a helper function to guide users on installation.
    """
    system = platform.system()
    
    instructions = {
        'Windows': [
            "pip install docx2pdf",
            "Note: docx2pdf uses Microsoft Word COM interface on Windows"
        ],
        'Linux': [
            "sudo apt-get install libreoffice",  # For Ubuntu/Debian
            "pip install docx2pdf",
            "Note: docx2pdf uses LibreOffice on Linux"
        ],
        'Darwin': [  # macOS
            "brew install libreoffice",  # If using Homebrew
            "pip install docx2pdf",
            "Note: docx2pdf uses LibreOffice on macOS"
        ]
    }
    
    if system in instructions:
        logger.info(f"To install PDF conversion dependencies on {system}:")
        for instruction in instructions[system]:
            logger.info(f"  {instruction}")
    else:
        logger.info("PDF conversion setup instructions not available for this platform")

# Test function
def test_conversion(docx_path, pdf_path):
    """Test PDF conversion with error handling"""
    try:
        convert_docx_to_pdf(docx_path, pdf_path)
        print(f"✅ Conversion successful: {pdf_path}")
        return True
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        print("\n📋 Installation help:")
        install_docx2pdf_dependencies()
        return False

if __name__ == "__main__":
    # Test the conversion
    test_docx = "test_resume.docx"
    test_pdf = "test_resume.pdf"
    
    if os.path.exists(test_docx):
        test_conversion(test_docx, test_pdf)
    else:
        print(f"Test file {test_docx} not found")
        print("Create a test DOCX file to test the conversion")
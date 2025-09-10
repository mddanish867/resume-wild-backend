from flask import Blueprint, request, jsonify, send_file
from .models import db, Resume
from .resume_optimizer import optimize_resume_docx
import os
import uuid
import logging
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

resume_bp = Blueprint("resume", __name__)

ALLOWED_EXTENSIONS = {'.docx', '.doc', '.pdf'}

def validate_file(file):
    """Validate uploaded file"""
    if not file or not file.filename:
        return False, "No file provided"
    
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size (max 5MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        return False, "File size too large (max 5MB)"
    
    if file_size < 1024:  # 1KB minimum
        return False, "File too small to be a valid resume"
    
    return True, "Valid file"


def ensure_directory_exists(path):
    """Ensure directory exists, create if not"""
    directory = os.path.dirname(path) if os.path.dirname(path) else path
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

@resume_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Resume optimizer service is running",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@resume_bp.route("/upload/", methods=["POST"])
def upload_resume():
    try:
        user_id = request.form.get("user_id")
        file = request.files.get("file")

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Validate user_id format
        try:
            uuid.UUID(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id format"}), 400

        # Validate file
        is_valid, message = validate_file(file)
        if not is_valid:
            return jsonify({"error": message}), 400

        # Generate unique resume ID
        resume_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        
        # Ensure uploads directory exists
        uploads_dir = "uploads"
        ensure_directory_exists(uploads_dir)
        
        # Save file with unique name
        file_path = os.path.join(uploads_dir, f"{resume_id}_{original_filename}")
        file.save(file_path)
        
        logger.info(f"File saved to: {file_path}")

        # Create database record
        new_resume = Resume(
            id=resume_id,
            user_id=user_id,
            original_path=file_path,
            original_filename=original_filename,
            optimization_status='uploaded'
        )
        
        db.session.add(new_resume)
        db.session.commit()
        
        logger.info(f"Resume record created with ID: {resume_id}")

        return jsonify({
            "resume_id": resume_id, 
            "message": "Resume uploaded successfully",
            "filename": original_filename,
            "status": "uploaded"
        }), 201

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@resume_bp.route("/optimize-resume/<resume_id>", methods=["POST"])
def optimize(resume_id):
    try:
        # Validate resume_id format
        try:
            uuid.UUID(resume_id)
        except ValueError:
            return jsonify({"error": "Invalid resume_id format"}), 400
            
        # Validate input
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.json
        user_id = data.get("user_id")
        job_desc = data.get("job_description")

        if not all([resume_id, user_id, job_desc]):
            return jsonify({"error": "Missing required data: resume_id, user_id, or job_description"}), 400

        # Validate job description length
        if len(job_desc.strip()) < 50:
            return jsonify({"error": "Job description too short (minimum 50 characters)"}), 400

        # Find resume in database
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({"error": f"Resume with ID {resume_id} not found"}), 404
        
        if resume.user_id != user_id:
            return jsonify({"error": "Unauthorized access to resume"}), 403

        # Update status to processing
        resume.update_status('processing')
        db.session.commit()

        # Check if original file exists
        if not os.path.exists(resume.original_path):
            logger.error(f"Original resume file not found: {resume.original_path}")
            resume.update_status('failed')
            db.session.commit()
            return jsonify({"error": "Original resume file not found"}), 404

        # Prepare output paths
        optimized_dir = "optimized"
        ensure_directory_exists(optimized_dir)
        
        optimized_docx_path = os.path.join(optimized_dir, f"{resume_id}_optimized.docx")
        optimized_pdf_path = os.path.join(optimized_dir, f"{resume_id}_optimized.pdf")

        logger.info(f"Starting optimization for resume {resume_id}")
        logger.info(f"Original path: {resume.original_path}")
        logger.info(f"Output DOCX path: {optimized_docx_path}")

        # Optimize the resume
        try:
            keywords_count = optimize_resume_docx(resume.original_path, job_desc, optimized_docx_path)
            logger.info("Resume optimization completed successfully")
        except Exception as opt_error:
            logger.error(f"Resume optimization failed: {str(opt_error)}")
            resume.update_status('failed')
            db.session.commit()
            return jsonify({"error": f"Resume optimization failed: {str(opt_error)}"}), 500

        # Convert to PDF
        final_output_path = optimized_docx_path  # Default to DOCX
        try:
            from .pdf_generator import convert_docx_to_pdf
            convert_docx_to_pdf(optimized_docx_path, optimized_pdf_path)
            final_output_path = optimized_pdf_path
            logger.info("PDF conversion completed successfully")
        except Exception as pdf_error:
            logger.warning(f"PDF conversion failed, using DOCX: {str(pdf_error)}")
            # Continue with DOCX file if PDF conversion fails

        # Verify output file exists
        if not os.path.exists(final_output_path):
            resume.update_status('failed')
            db.session.commit()
            return jsonify({"error": "Failed to create optimized resume"}), 500

        # Update database record
        resume.optimized_path = final_output_path
        resume.job_description = job_desc
        resume.update_status('completed', keywords_count if isinstance(keywords_count, int) else 0)
        db.session.commit()

        return jsonify({
            "message": "Resume optimized successfully",
            "resume_id": resume_id,
            "optimized_resume_path": final_output_path,
            "download_url": f"/download-resume/{resume_id}",
            "keywords_added": resume.keywords_added,
            "status": "completed"
        }), 200

    except Exception as e:
        logger.error(f"Optimization process failed: {str(e)}")
        # Update status to failed if resume exists
        try:
            resume = Resume.query.get(resume_id)
            if resume:
                resume.update_status('failed')
                db.session.commit()
        except:
            pass
        return jsonify({"error": f"Optimization process failed: {str(e)}"}), 500

@resume_bp.route("/download-resume/<resume_id>", methods=["GET"])
def download_resume(resume_id):
    try:
        logger.info(f"Download requested for resume ID: {resume_id}")
        
        # Validate resume_id format
        try:
            uuid.UUID(resume_id)
        except ValueError:
            return jsonify({"error": "Invalid resume ID format"}), 400
        
        # Fetch resume from database
        resume = Resume.query.get(resume_id)
        if not resume:
            logger.error(f"Resume with ID {resume_id} not found in database")
            return jsonify({"error": f"Resume with ID {resume_id} not found"}), 404
        
        # Check if optimized resume exists
        if not resume.optimized_path:
            logger.error(f"No optimized resume available for ID {resume_id}")
            return jsonify({"error": "Optimized resume not available. Please optimize first."}), 404
        
        # Resolve file path
        optimized_path = resume.optimized_path
        if not os.path.isabs(optimized_path):
            optimized_path = os.path.abspath(optimized_path)
        
        logger.info(f"Looking for file at: {optimized_path}")
        
        # Check if file exists
        if not os.path.exists(optimized_path):
            logger.error(f"Optimized resume file not found at: {optimized_path}")
            return jsonify({"error": "Optimized resume file not found"}), 404
        
        # Determine file extension and download name
        file_ext = os.path.splitext(optimized_path)[1]
        download_name = f"optimized_resume_{resume_id}{file_ext}"
        
        # Determine MIME type
        mimetype = 'application/pdf' if file_ext.lower() == '.pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        logger.info(f"Serving file: {optimized_path}")
        
        return send_file(
            optimized_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"Download failed for resume {resume_id}: {str(e)}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@resume_bp.route("/resume-status/<resume_id>", methods=["GET"])
def get_resume_status(resume_id):
    """Get status of a resume (uploaded, optimized, etc.)"""
    try:
        # Validate resume_id format
        try:
            uuid.UUID(resume_id)
        except ValueError:
            return jsonify({"error": "Invalid resume ID format"}), 400
            
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({"error": "Resume not found"}), 404
        
        status = {
            "resume_id": resume.id,
            "user_id": resume.user_id,
            "uploaded_at": resume.created_at.isoformat() if resume.created_at else None,
            "updated_at": resume.updated_at.isoformat() if resume.updated_at else None,
            "has_original": os.path.exists(resume.original_path) if resume.original_path else False,
            "has_optimized": os.path.exists(resume.optimized_path) if resume.optimized_path else False,
            "has_job_description": bool(resume.job_description),
            "optimization_status": resume.optimization_status,
            "keywords_added": resume.keywords_added,
            "original_filename": resume.original_filename
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Status check failed for resume {resume_id}: {str(e)}")
        return jsonify({"error": f"Status check failed: {str(e)}"}), 500

@resume_bp.route("/user-resumes/<user_id>", methods=["GET"])
def get_user_resumes(user_id):
    """Get all resumes for a specific user"""
    try:
        # Validate user_id format
        try:
            uuid.UUID(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user ID format"}), 400
            
        resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
        
        resume_list = []
        for resume in resumes:
            resume_data = resume.to_dict()
            # Add file existence status
            resume_data['has_original'] = os.path.exists(resume.original_path) if resume.original_path else False
            resume_data['has_optimized'] = os.path.exists(resume.optimized_path) if resume.optimized_path else False
            resume_list.append(resume_data)
        
        return jsonify({
            "user_id": user_id,
            "total_resumes": len(resume_list),
            "resumes": resume_list
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to fetch resumes for user {user_id}: {str(e)}")
        return jsonify({"error": f"Failed to fetch resumes: {str(e)}"}), 500
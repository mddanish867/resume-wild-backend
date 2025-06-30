from flask import Blueprint, request, jsonify, send_file
from .models import db, Resume
from .resume_optimizer import extract_text_from_docx, optimize_resume
from .pdf_generator import save_text_as_pdf
import os
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

resume_bp = Blueprint("resume", __name__)

@resume_bp.route("/upload/", methods=["POST"])
def upload_resume():
    user_id = request.form.get("user_id")
    file = request.files.get("file")

    if not file or not user_id:
        return jsonify({"error": "Missing file or user_id"}), 400

    resume_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["docx"]:
        return jsonify({"error": "Only .docx files allowed"}), 400

    path = os.path.join("uploads", f"{resume_id}.docx")
    file.save(path)

    new_resume = Resume(
        id=resume_id,
        user_id=user_id,
        original_path=path
    )
    db.session.add(new_resume)
    db.session.commit()

    return jsonify({"resume_id": resume_id, "message": "Uploaded successfully."})


@resume_bp.route("/optimize-resume/<resume_id>", methods=["POST"])
def optimize(resume_id):
    data = request.json
    user_id = data.get("user_id")
    job_desc = data.get("job_description")

    if not all([resume_id, user_id, job_desc]):
        return jsonify({"error": "Missing data"}), 400

    resume = Resume.query.get(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    text = extract_text_from_docx(resume.original_path)
    optimized_text = optimize_resume(text, job_desc)

    optimized_path = os.path.join("optimized", f"{resume_id}.pdf")
    save_text_as_pdf(optimized_text, optimized_path)

    resume.optimized_path = optimized_path
    resume.job_description = job_desc
    db.session.commit()

    return jsonify({"message": "Resume optimized", "resume_id": resume_id})

@resume_bp.route("/download-resume/<resume_id>", methods=["GET"])
def download_resume(resume_id):
    logger.info(f"Attempting to download resume with ID: '{resume_id}' (type: {type(resume_id)})")
    
    # Normalize resume_id
    resume_id = str(resume_id).strip().lower()  # Ensure string, remove whitespace, normalize case
    
    # Fetch the resume from the database
    try:
        resume = Resume.query.get(resume_id)
        if not resume:
            # Log all available resume IDs for debugging
            all_resume_ids = [r.id for r in Resume.query.all()]
            logger.error(f"Resume with ID '{resume_id}' not found in database. Available IDs: {all_resume_ids}")
            return jsonify({
                "error": f"Resume with ID '{resume_id}' not found",
                "available_ids": all_resume_ids
            }), 404
    except Exception as e:
        logger.error(f"Database query failed for resume_id '{resume_id}': {e}")
        return jsonify({"error": "Database error while fetching resume"}), 500
    
    # Check optimized_path
    if not resume.optimized_path:
        logger.error(f"No optimized path found for resume ID '{resume_id}'")
        return jsonify({"error": "Optimized resume not available"}), 404
    
    # Ensure the path is absolute
    optimized_path = resume.optimized_path
    logger.info(f"Raw optimized_path from database: '{optimized_path}'")
    if not os.path.isabs(optimized_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'optimized'))
        optimized_path = os.path.join(base_dir, os.path.basename(optimized_path))
    
    # Log the resolved path
    logger.info(f"Resolved path for file check: '{optimized_path}'")
    
    # Check if the file exists
    if not os.path.exists(optimized_path):
        logger.error(f"Optimized resume file not found at '{optimized_path}'")
        return jsonify({"error": f"Optimized resume file not found at '{optimized_path}'"}), 404
    
    try:
        logger.info(f"Serving optimized resume file: '{optimized_path}'")
        return send_file(
            optimized_path,
            as_attachment=True,
            download_name=f"optimized_resume_{resume_id}.pdf"
        )
    except Exception as e:
        logger.error(f"Error serving file '{optimized_path}': {e}")
        return jsonify({"error": "Failed to download resume"}), 500
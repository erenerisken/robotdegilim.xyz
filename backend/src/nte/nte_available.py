import logging

from backend.src.errors import AbortNteAvailableError
from src.config import app_constants
from src.nte.io import load_data, load_departments, load_nte_list, write_nte_available
from src.utils.s3 import upload_to_s3
from src.nte.parse import build_available_index, build_course_output

logger = logging.getLogger(app_constants.log_nte_available)

def run_nte():
    """Main NTE processing function."""
    try:
        logger.info("Starting NTE processing.")
        courses_data = load_data()
        departments_data = load_departments()
        nte_data = load_nte_list()
        
        # Build available courses index
        logger.info("Building available courses index.")
        available_index = build_available_index(courses_data, departments_data)
        
        matched = 0
        missed = 0
        output = []
                
        # Handle both dict and list formats for NTE data
        if isinstance(nte_data, dict):
            iterable = (course for course_list in nte_data.values() for course in course_list)
        else:
            iterable = iter(nte_data)
        
        for course in iterable:
            raw_code = (course.get("code") or course.get("Code") or "").strip()
            credits = course.get("credits") or course.get("Credits") or ""
            
            # Normalize code (remove spaces)
            normalized_code = raw_code.replace(" ", "")
            
            # Check if course is available
            course_info = available_index.get(normalized_code)
            if not course_info:
                missed += 1
                continue
            
            # Build course output
            course_output = build_course_output(
                course_info["numeric"],
                normalized_code,
                course_info["name"],
                credits,
                courses_data
            )
            
            output.append(course_output)
            matched += 1
        
        output_path = write_nte_available(output)
        
        # Upload to S3
        upload_to_s3(str(output_path), app_constants.nte_available_json)
        
        logger.info(f"NTE processing completed successfully. Matched: {matched}, Missed: {missed}")
        
    except Exception as e:
        raise AbortNteAvailableError(f"NTE processing failed, error: {str(e)}") from e
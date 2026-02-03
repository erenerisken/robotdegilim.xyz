"""NTE available pipeline orchestrator for building and publishing nteAvailable.json."""

import logging

from app.core.constants import (
    LOGGER_ERROR,
    LOGGER_NTE_AVAILABLE,
    NTE_AVAILABLE_FILE,
)
from app.core.errors import AppError
from app.core.logging import log_item
from app.core.paths import published_path, staged_path
from app.nte.parse import build_available_index, extract_nte_courses, build_course_output
from app.nte.io import load_dependencies
from app.storage.local import move_file, write_json
from app.storage.s3 import upload_file

def run_nte_available():
    try:
        log_item(LOGGER_NTE_AVAILABLE, logging.INFO, "NTE available process started.")

        deps=load_dependencies()
        departments_data=deps["departments"]
        nte_list=deps["nte_list"]
        nte_courses=[]
        extract_nte_courses(nte_list, nte_courses)
        courses_data=deps["data"]
        available_index= build_available_index(courses_data, departments_data)

        if not available_index:
            raise AppError("No available courses found in dependencies data.", "NTE_AVAILABLE_NO_COURSES")
        
        output: list[dict[str, object]] = []
        for course in nte_courses:
            code = course.get("code", "").strip().upper().replace(" ", "")
            if not code:
                continue
            course_info= available_index.get(code, None)
            if not course_info:
                continue
            credits=course.get("credits", "").strip()
            output.append(build_course_output(
                course_info["numeric"],
                prefixed_code=code,
                course_name=course_info["name"],
                credits=credits,
                courses_data=courses_data
            ))
        
        output.sort(key=lambda item: item.get("code", {}).get("departmental", ""))

        if not output:
            raise AppError("No matching NTE courses could be produced from the input data.", "NTE_AVAILABLE_NO_NTE_COURSES")
        
        output_path = staged_path(NTE_AVAILABLE_FILE)
        output_published_path = published_path(NTE_AVAILABLE_FILE)

        write_json(output_path, output)
        upload_file(output_path, NTE_AVAILABLE_FILE)
        move_file(output_path, output_published_path)

        log_item(LOGGER_NTE_AVAILABLE, logging.INFO, "NTE available process completed successfully and files uploaded to S3.")
        return str(output_published_path)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "NTE available processing failed.",
            "NTE_AVAILABLE_PROCESSING_FAILED",
            cause=e,
        )
        log_item(LOGGER_ERROR, logging.ERROR, err)
        raise err

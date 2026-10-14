"""
Application storage and backend validation service.
Handles applicant data persistence, rigorous backend input validation,
backend-level duplicate prevention, and transactional integrity guarantees.
"""

import os
import re
import uuid
import threading
from typing import Dict, Any, List, Optional, Tuple

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ApplicationStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._applications: Dict[str, Dict[str, Any]] = {}
        # Composite unique index: (job_id, normalized_email) -> ref_id
        self._unique_submissions: Dict[Tuple[str, str], str] = {}

    def clear(self) -> None:
        """Reset storage for clean test isolation."""
        with self._lock:
            self._applications.clear()
            self._unique_submissions.clear()

    def get_count(self) -> int:
        with self._lock:
            return len(self._applications)

    def get_all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._applications.values())

    def get_by_ref(self, ref_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._applications.get(ref_id)

    def validate_inputs(
        self,
        full_name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        job_id: Optional[str],
        experience_level: Optional[str],
        cover_letter: Optional[str],
        filename: Optional[str],
        file_size: int = 0
    ) -> List[str]:
        """
        Comprehensive validation rules for candidate submissions.
        Returns a list of human-readable error messages if any check fails.
        """
        errors: List[str] = []

        # 1. Job ID validation
        if not job_id or not job_id.strip():
            errors.append("Job ID is required.")

        # 2. Full Name validation (Required, Whitespace check, Length boundary)
        if full_name is None:
            errors.append("Full Name is required.")
        else:
            stripped_name = full_name.strip()
            if not stripped_name:
                errors.append("Full Name cannot be empty or contain only whitespace.")
            elif len(stripped_name) < 2:
                errors.append("Full Name must be at least 2 characters long.")
            elif len(stripped_name) > 100:
                errors.append("Full Name cannot exceed 100 characters.")

        # 3. Email validation (Required, Whitespace check, Length & Format)
        if email is None:
            errors.append("Email Address is required.")
        else:
            stripped_email = email.strip()
            if not stripped_email:
                errors.append("Email Address cannot be empty or contain only whitespace.")
            elif len(stripped_email) > 120:
                errors.append("Email Address cannot exceed 120 characters.")
            elif not EMAIL_REGEX.match(stripped_email):
                errors.append("Please enter a valid email address (e.g., candidate@example.com).")

        # 4. Phone validation (Required, Whitespace check, Digits boundary)
        if phone is None:
            errors.append("Phone Number is required.")
        else:
            stripped_phone = phone.strip()
            if not stripped_phone:
                errors.append("Phone Number cannot be empty or contain only whitespace.")
            else:
                digits_only = re.sub(r"\D", "", stripped_phone)
                if len(digits_only) < 7:
                    errors.append("Phone Number must contain at least 7 digits.")
                elif len(digits_only) > 20:
                    errors.append("Phone Number cannot exceed 20 digits.")

        # 5. Experience level validation
        valid_experience = {"Entry", "Mid", "Senior", "Lead"}
        if not experience_level or experience_level.strip() not in valid_experience:
            errors.append("Please select a valid experience level.")

        # 6. Cover letter length boundary (Optional)
        if cover_letter and len(cover_letter) > 2000:
            errors.append("Cover Letter cannot exceed 2000 characters.")

        # 7. Resume file validation (Required, File extension, File size)
        if not filename or not filename.strip():
            errors.append("Resume file is required. Please upload a PDF or DOCX file.")
        else:
            _, ext = os.path.splitext(filename.strip().lower())
            if ext not in ALLOWED_EXTENSIONS:
                errors.append(f"Invalid file type '{ext}'. Allowed file types are: .pdf, .doc, .docx")
            elif file_size > MAX_FILE_SIZE_BYTES:
                errors.append("File size exceeds maximum limit of 5MB.")

        return errors

    def submit_application(
        self,
        job_id: str,
        job_title: str,
        full_name: str,
        email: str,
        phone: str,
        experience_level: str,
        resume_filename: str,
        resume_size: int,
        cover_letter: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Thread-safe application submission.
        Guarantees backend-level duplicate prevention and atomicity.
        Returns: (success: bool, ref_id_or_none, error_message_or_none)
        """
        # Run validations
        errors = self.validate_inputs(
            full_name=full_name,
            email=email,
            phone=phone,
            job_id=job_id,
            experience_level=experience_level,
            cover_letter=cover_letter,
            filename=resume_filename,
            file_size=resume_size
        )
        if errors:
            return False, None, errors[0]

        normalized_email = email.strip().lower()
        clean_name = full_name.strip()
        clean_phone = phone.strip()
        clean_cover = (cover_letter or "").strip()

        with self._lock:
            # Check duplicate submission at the backend level
            dedup_key = (job_id, normalized_email)
            if dedup_key in self._unique_submissions:
                existing_ref = self._unique_submissions[dedup_key]
                return (
                    False,
                    None,
                    f"Duplicate application: An application for this job has already been submitted under {normalized_email} (Ref: {existing_ref})."
                )

            # Generate reference number
            ref_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
            record = {
                "ref_id": ref_id,
                "job_id": job_id,
                "job_title": job_title,
                "full_name": clean_name,
                "email": normalized_email,
                "phone": clean_phone,
                "experience_level": experience_level,
                "resume_filename": resume_filename,
                "cover_letter": clean_cover,
                "status": "Submitted"
            }

            self._applications[ref_id] = record
            self._unique_submissions[dedup_key] = ref_id

            return True, ref_id, None


# Global singleton store
store = ApplicationStore()

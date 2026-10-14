"""
Flask Web Application for Job Application Portal.
Implements job listings, keyword search, job details, multi-field application submission,
safe failure simulation (server errors & latency), and test inspection endpoints.
"""

import os
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from portal.jobs import get_all_jobs, get_job_by_id, search_jobs
from portal.storage import store

app = Flask(__name__)
app.config["SECRET_KEY"] = "qa-assessment-secure-token-2026"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB request payload limit


@app.route("/", methods=["GET"])
def index():
    """Job listings homepage with keyword search and department filtering."""
    query = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()

    filtered_jobs = search_jobs(keyword=query, department=department)

    # Collect unique departments for filter dropdown
    all_departments = sorted(list(set(j["department"] for j in get_all_jobs())))

    return render_template(
        "jobs.html",
        jobs=filtered_jobs,
        query=query,
        department=department,
        departments=all_departments,
        total_count=len(filtered_jobs)
    )


@app.route("/jobs/<job_id>", methods=["GET"])
def job_detail(job_id):
    """Job details view showing comprehensive requirements and responsibilities."""
    job = get_job_by_id(job_id)
    if not job:
        abort(404)
    return render_template("job_detail.html", job=job)


@app.route("/jobs/<job_id>/apply", methods=["GET"])
def apply_page(job_id):
    """Candidate job application form."""
    job = get_job_by_id(job_id)
    if not job:
        abort(404)
    return render_template("apply.html", job=job, form_data={}, error=None)


@app.route("/jobs/<job_id>/apply", methods=["POST"])
def submit_application(job_id):
    """
    Handle application submissions.
    Supports failure simulations (?simulate_error=500, ?simulate_delay=N) for safe QA testing.
    """
    job = get_job_by_id(job_id)
    if not job:
        abort(404)

    # 1. Latency simulation
    simulate_delay = request.args.get("simulate_delay") or request.form.get("simulate_delay")
    if simulate_delay:
        try:
            delay_sec = float(simulate_delay)
            time.sleep(min(delay_sec, 5.0))
        except ValueError:
            pass

    # 2. Server error simulation (safe failure testing)
    simulate_error = request.args.get("simulate_error") or request.form.get("simulate_error")
    if simulate_error == "500":
        # Crucial: verify that failing request DOES NOT create record
        return render_template(
            "error.html",
            error_code=500,
            message="Internal Server Error (Simulated): Database transaction failed before persistence."
        ), 500

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    experience_level = request.form.get("experience_level")
    cover_letter = request.form.get("cover_letter")

    resume_file = request.files.get("resume")
    filename = resume_file.filename if resume_file else ""
    file_bytes = 0
    if resume_file:
        resume_file.seek(0, os.SEEK_END)
        file_bytes = resume_file.tell()
        resume_file.seek(0)

    form_data = {
        "full_name": full_name or "",
        "email": email or "",
        "phone": phone or "",
        "experience_level": experience_level or "",
        "cover_letter": cover_letter or ""
    }

    # Submit to storage service with validation and duplicate checking
    success, ref_id, err_msg = store.submit_application(
        job_id=job_id,
        job_title=job["title"],
        full_name=full_name,
        email=email,
        phone=phone,
        experience_level=experience_level,
        resume_filename=filename,
        resume_size=file_bytes,
        cover_letter=cover_letter
    )

    if not success:
        return render_template(
            "apply.html",
            job=job,
            form_data=form_data,
            error=err_msg
        ), 400

    return redirect(url_for("application_success", ref_id=ref_id))


@app.route("/success/<ref_id>", methods=["GET"])
def application_success(ref_id):
    """Submission confirmation page with reference ID."""
    application = store.get_by_ref(ref_id)
    if not application:
        return render_template(
            "error.html",
            error_code=404,
            message="Application record not found."
        ), 404
    return render_template("success.html", application=application)


# --- API / Health / QA Fixture Endpoints ---

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "job-portal"}), 200


@app.route("/api/applications", methods=["GET"])
def api_applications():
    """Inspect stored applications for automated assertions."""
    return jsonify({
        "count": store.get_count(),
        "applications": store.get_all()
    }), 200


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset application storage for pristine test state."""
    store.clear()
    return jsonify({"status": "cleared"}), 200


@app.errorhandler(404)
def handle_404(e):
    return render_template("error.html", error_code=404, message="Page or Resource Not Found"), 404


@app.errorhandler(500)
def handle_500(e):
    return render_template("error.html", error_code=500, message="An internal server error occurred."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5555, debug=False)

"""
Automated tests for valid job application submissions, duplicate prevention, and concurrency.
"""

from playwright.sync_api import Page, expect
from tests.conftest import get_app_count, get_stored_applications


def test_successful_complete_application_submission(page: Page, base_url: str, test_files: dict):
    """Verify that a complete, valid job application is accepted and returns a Reference ID."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Devon Avery")
    page.locator("#email").fill("devon.avery@example.com")
    page.locator("#phone").fill("+1 (555) 987-6543")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["pdf"])
    page.locator("#cover_letter").fill("I have extensive experience building scalable test frameworks.")

    page.locator("#submit-btn").click()

    # Verify confirmation page
    expect(page.locator("#success-confirmation-card")).to_be_visible()
    expect(page.locator("#confirmed-applicant-name")).to_have_text("Devon Avery")
    expect(page.locator("#confirmed-job-title")).to_have_text("Senior QA Automation Engineer")

    ref_locator = page.locator("#confirmation-ref")
    expect(ref_locator).to_be_visible()
    ref_id = ref_locator.inner_text().strip()
    assert ref_id.startswith("APP-"), f"Unexpected reference ID format: {ref_id}"

    # Verify directly in backend storage
    assert get_app_count(base_url) == 1
    stored_apps = get_stored_applications(base_url)
    assert len(stored_apps) == 1
    assert stored_apps[0]["email"] == "devon.avery@example.com"
    assert stored_apps[0]["job_id"] == "qa-eng-101"


def test_duplicate_submission_prevented_at_backend_level(page: Page, base_url: str, test_files: dict):
    """
    Verify duplicate prevention at the backend persistence layer.
    A candidate attempting to re-apply for the same job with the same email must be rejected.
    """
    candidate_email = "alex.duplicate@example.com"

    # Step 1: First valid submission
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")
    page.locator("#full_name").fill("Alex Duplicate")
    page.locator("#email").fill(candidate_email)
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["pdf"])
    page.locator("#submit-btn").click()

    # First submission should succeed
    expect(page.locator("#success-confirmation-card")).to_be_visible()
    assert get_app_count(base_url) == 1

    # Step 2: Second submission attempt for same job and same email
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")
    page.locator("#full_name").fill("Alex Duplicate")
    page.locator("#email").fill(candidate_email)
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["pdf"])
    page.locator("#submit-btn").click()

    # Second submission must be rejected
    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Duplicate application: An application for this job has already been submitted")

    # Backend store MUST remain strictly at 1 record
    assert get_app_count(base_url) == 1


def test_duplicate_submission_case_insensitive_prevention(page: Page, base_url: str, test_files: dict):
    """Verify backend duplicate prevention is case-insensitive on email addresses."""
    # First submission with lowercase
    page.goto(f"{base_url}/jobs/devops-eng-103/apply")
    page.locator("#full_name").fill("Chris Case")
    page.locator("#email").fill("chris.case@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["pdf"])
    page.locator("#submit-btn").click()
    expect(page.locator("#success-confirmation-card")).to_be_visible()

    # Second submission with UPPERCASE email
    page.goto(f"{base_url}/jobs/devops-eng-103/apply")
    page.locator("#full_name").fill("Chris Case")
    page.locator("#email").fill("CHRIS.CASE@EXAMPLE.COM")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["pdf"])
    page.locator("#submit-btn").click()

    expect(page.locator("#form-error-alert")).to_be_visible()
    expect(page.locator("#form-error-alert")).to_contain_text("Duplicate application")
    assert get_app_count(base_url) == 1


def test_repeated_rapid_clicks_handled(page: Page, base_url: str, test_files: dict):
    """Verify that rapid repeated clicks on submit do not create duplicate records."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")
    page.locator("#full_name").fill("Rapid Clicker")
    page.locator("#email").fill("rapid.click@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Lead")
    page.locator("#resume").set_input_files(test_files["pdf"])

    submit_btn = page.locator("#submit-btn")
    # Simulate rapid double click
    submit_btn.dblclick()

    expect(page.locator("#success-confirmation-card")).to_be_visible()
    # Confirm that exactly 1 record was persisted in backend store
    assert get_app_count(base_url) == 1


def test_page_refresh_resilience(page: Page, base_url: str):
    """Verify that page refresh on application form reloads cleanly without broken state."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")
    page.locator("#full_name").fill("Draft Name")

    page.reload()

    expect(page.locator("#application-form")).to_be_visible()
    expect(page.locator("#submit-btn")).to_be_enabled()

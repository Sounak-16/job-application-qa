"""
Automated tests for input validations, whitespace handling, and field boundary constraints.
"""

from playwright.sync_api import Page, expect


def test_empty_form_submission_rejected(page: Page, base_url: str):
    """Verify that submitting an empty form is rejected with a validation error."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#submit-btn").click()

    # Form error alert should be displayed
    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("cannot be empty or contain only whitespace")


def test_whitespace_only_name_rejected(page: Page, base_url: str, test_files: dict):
    """Verify that entering whitespace-only in Full Name is rejected."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("     ")
    page.locator("#email").fill("valid.email@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Full Name cannot be empty or contain only whitespace.")


def test_whitespace_only_email_rejected(page: Page, base_url: str, test_files: dict):
    """Verify that entering whitespace-only in Email is rejected."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Jordan Smith")
    page.locator("#email").fill("   \t  ")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Email Address cannot be empty or contain only whitespace.")


def test_invalid_email_format_rejected(page: Page, base_url: str, test_files: dict):
    """Verify that malformed email addresses (missing @ or domain) are rejected."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Jordan Smith")
    page.locator("#email").fill("invalid-email-format-without-domain")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Please enter a valid email address")


def test_phone_number_digit_boundary_rejected(page: Page, base_url: str, test_files: dict):
    """Verify that phone numbers with fewer than 7 digits are rejected."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Jordan Smith")
    page.locator("#email").fill("jordan.smith@example.com")
    page.locator("#phone").fill("12345")  # Only 5 digits
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Phone Number must contain at least 7 digits.")


def test_name_exceeding_max_boundary_rejected(page: Page, base_url: str, test_files: dict):
    """Verify that entering a full name exceeding 100 characters triggers boundary validation."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    oversized_name = "Alexander" * 12  # 108 characters
    page.locator("#full_name").fill(oversized_name)
    page.locator("#email").fill("alexander@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Lead")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Full Name cannot exceed 100 characters.")


def test_prohibited_file_extension_rejected(page: Page, base_url: str, test_files: dict):
    """Verify that dangerous or invalid resume file types (.exe, .png) are rejected."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Security Tester")
    page.locator("#email").fill("sec.test@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["exe"])

    page.locator("#submit-btn").click()

    alert = page.locator("#form-error-alert")
    expect(alert).to_be_visible()
    expect(alert).to_contain_text("Invalid file type '.exe'")


def test_valid_docx_extension_accepted(page: Page, base_url: str, test_files: dict):
    """Verify that legitimate DOCX resume files are accepted."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Morgan Docx")
    page.locator("#email").fill("morgan.docx@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["docx"])

    page.locator("#submit-btn").click()

    # Should land on success confirmation
    expect(page.locator("#success-confirmation-card")).to_be_visible()
    expect(page.locator("#confirmed-resume")).to_have_text("valid_resume.docx")

"""
Automated tests for portal navigation flows, breadcrumbs, and detail routing.
"""

from playwright.sync_api import Page, expect


def test_navigate_from_listing_to_details(page: Page, base_url: str):
    """Verify navigation from homepage to specific job detail view."""
    page.goto(base_url)

    # Click view details on QA role
    page.locator("#view-job-qa-eng-101").click()

    expect(page).to_have_url(f"{base_url}/jobs/qa-eng-101")
    expect(page.locator("#detail-job-title")).to_have_text("Senior QA Automation Engineer")
    expect(page.locator("#detail-department")).to_have_text("Engineering")
    expect(page.locator("#detail-salary")).to_contain_text("$125,000 - $155,000 / year")
    expect(page.locator("#detail-responsibilities li")).to_have_count(5)
    expect(page.locator("#detail-requirements li")).to_have_count(5)


def test_navigate_back_to_listings_via_breadcrumb(page: Page, base_url: str):
    """Verify breadcrumb link returns candidate to open roles catalog."""
    page.goto(f"{base_url}/jobs/fullstack-eng-102")

    page.locator("#back-to-jobs").click()

    expect(page).to_have_url(f"{base_url}/")
    expect(page.locator(".job-card")).to_have_count(5)


def test_navigate_from_details_to_apply_form(page: Page, base_url: str):
    """Verify 'Apply for this Position' button transitions to application form."""
    page.goto(f"{base_url}/jobs/qa-eng-101")

    page.locator("#apply-for-job-btn").click()

    expect(page).to_have_url(f"{base_url}/jobs/qa-eng-101/apply")
    expect(page.locator("h1")).to_have_text("Submit Application")
    expect(page.locator("#application-form")).to_be_visible()


def test_cancel_application_returns_to_job(page: Page, base_url: str):
    """Verify 'Cancel' button on application form navigates back to job details."""
    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#cancel-btn").click()

    expect(page).to_have_url(f"{base_url}/jobs/qa-eng-101")

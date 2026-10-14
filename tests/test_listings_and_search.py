"""
Automated tests for Job Listings Discovery and Keyword Search functionality.
"""

from playwright.sync_api import Page, expect


def test_all_job_listings_rendered(page: Page, base_url: str):
    """Verify that all default active job postings render with accurate titles and compensation."""
    page.goto(base_url)

    # Verify brand header and main heading
    expect(page.locator("#brand-logo")).to_be_visible()
    expect(page.locator("h1")).to_contain_text("Find Your Next High-Impact Role")

    # Verify counter shows 5 opportunities
    counter = page.locator("#results-counter")
    expect(counter).to_contain_text("Showing 5 opportunities")

    # Verify 5 job cards exist
    job_cards = page.locator(".job-card")
    expect(job_cards).to_have_count(5)

    # Check key job roles exist
    expect(page.locator("#job-title-qa-eng-101")).to_have_text("Senior QA Automation Engineer")
    expect(page.locator("#job-title-fullstack-eng-102")).to_have_text("Full Stack Software Engineer")
    expect(page.locator("#job-title-devops-eng-103")).to_have_text("Cloud DevOps & Site Reliability Engineer")


def test_keyword_search_matches_skills(page: Page, base_url: str):
    """Verify keyword search filters listings by technical skills (e.g. Playwright)."""
    page.goto(base_url)

    search_input = page.locator("#search-input")
    search_input.fill("Playwright")
    page.locator("#search-submit").click()

    # Counter should update to 1 opportunity
    expect(page.locator("#results-counter")).to_contain_text("Showing 1 opportunity for \"Playwright\"")

    # Only QA Automation role should be displayed
    job_cards = page.locator(".job-card")
    expect(job_cards).to_have_count(1)
    expect(page.locator("#job-title-qa-eng-101")).to_be_visible()


def test_keyword_search_case_insensitive(page: Page, base_url: str):
    """Verify keyword search is case-insensitive (e.g. 'react')."""
    page.goto(base_url)

    page.locator("#search-input").fill("react")
    page.locator("#search-submit").click()

    job_cards = page.locator(".job-card")
    expect(job_cards).to_have_count(1)
    expect(page.locator("#job-title-fullstack-eng-102")).to_be_visible()


def test_keyword_search_zero_results_and_reset(page: Page, base_url: str):
    """Verify that searching for a non-existent keyword displays empty state and allows reset."""
    page.goto(base_url)

    page.locator("#search-input").fill("NonExistentTermXYZ99")
    page.locator("#search-submit").click()

    # Counter should show 0
    expect(page.locator("#results-counter")).to_contain_text("Showing 0 opportunities")

    # Empty state message
    empty_state = page.locator("#empty-state-notice")
    expect(empty_state).to_be_visible()
    expect(empty_state).to_contain_text("No matching positions found")

    # Click reset button
    page.locator("#reset-filter-btn").click()

    # Should restore full listing
    expect(page.locator(".job-card")).to_have_count(5)


def test_filter_by_department(page: Page, base_url: str):
    """Verify filtering job postings by Department dropdown."""
    page.goto(base_url)

    page.locator("#dept-filter").select_option("Infrastructure")
    page.locator("#search-submit").click()

    job_cards = page.locator(".job-card")
    expect(job_cards).to_have_count(1)
    expect(page.locator("#job-title-devops-eng-103")).to_be_visible()

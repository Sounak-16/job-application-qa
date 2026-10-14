"""
Automated tests for safe failure simulation, latency handling, network drops,
and verification that failed requests NEVER create unintended backend records.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.conftest import get_app_count


def test_simulated_500_server_error_creates_zero_records(page: Page, base_url: str, test_files: dict):
    """
    Verify that an internal server error (HTTP 500) renders an error page safely
    and STRICTLY DOES NOT create an unintended application record in storage.
    """
    assert get_app_count(base_url) == 0

    # Submit application with simulate_error=500 trigger
    page.goto(f"{base_url}/jobs/qa-eng-101/apply?simulate_error=500")

    page.locator("#full_name").fill("Morgan CrashTest")
    page.locator("#email").fill("morgan.crash@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    # Verify error page rendered safely
    expect(page.locator("#error-status-code")).to_have_text("500")
    expect(page.locator("#error-message-text")).to_contain_text("Internal Server Error (Simulated)")

    # CRITICAL QA REQUIREMENT: Confirm zero records were created
    assert get_app_count(base_url) == 0, "Security/Integrity failure: A failed 500 request created an unintended application record!"


def test_simulated_slow_response_handles_latency(page: Page, base_url: str, test_files: dict):
    """Verify that slow network responses (simulated latency) are handled cleanly without crashing."""
    assert get_app_count(base_url) == 0

    page.goto(f"{base_url}/jobs/qa-eng-101/apply?simulate_delay=1.0")

    page.locator("#full_name").fill("Slowpoke Candidate")
    page.locator("#email").fill("slowpoke@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Mid")
    page.locator("#resume").set_input_files(test_files["pdf"])

    page.locator("#submit-btn").click()

    # Verify eventual success
    expect(page.locator("#success-confirmation-card")).to_be_visible(timeout=10000)
    expect(page.locator("#confirmed-applicant-name")).to_have_text("Slowpoke Candidate")
    assert get_app_count(base_url) == 1


def test_network_route_failure_simulation(page: Page, base_url: str, test_files: dict):
    """
    Verify browser and backend behavior when network route is dropped or aborted.
    Guarantees no records are created if request fails to reach backend completion.
    """
    assert get_app_count(base_url) == 0

    page.goto(f"{base_url}/jobs/qa-eng-101/apply")

    page.locator("#full_name").fill("Network Drop")
    page.locator("#email").fill("net.drop@example.com")
    page.locator("#phone").fill("555-019-2834")
    page.locator("#experience_level").select_option("Senior")
    page.locator("#resume").set_input_files(test_files["pdf"])

    # Simulate network failure by aborting the POST request
    page.route("**/jobs/**/apply*", lambda route: route.abort("failed"))

    # When form submits and route is aborted, navigation raises an error
    with pytest.raises(Exception):
        with page.expect_navigation():
            page.locator("#submit-btn").click()

    # Verify no record created in backend store
    assert get_app_count(base_url) == 0


def test_validation_failure_creates_zero_records(page: Page, base_url: str):
    """Verify that rejected form validation attempts never persist partial or orphan records."""
    assert get_app_count(base_url) == 0

    page.goto(f"{base_url}/jobs/qa-eng-101/apply")
    page.locator("#submit-btn").click()

    expect(page.locator("#form-error-alert")).to_be_visible()
    assert get_app_count(base_url) == 0

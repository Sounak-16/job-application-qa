# Test Plan: Job Application Workflow Quality Assurance

---

## 1. Executive Summary & Objectives

The primary goal of this QA assessment is to evaluate the end-to-end user workflow of the Job Application Portal. The assessment verifies that candidates can discover open positions through search and filtering, review detailed role specifications, and successfully submit complete, valid job applications without data loss, UI distortion, or system crashes.

### Key Quality Objectives:
1. **Functional Integrity**: Verify that job browsing, keyword search, detailed job specifications, and multi-field application submissions operate smoothly.
2. **Input Validation & Boundary Robustness**: Enforce strict client-side and backend-level validations against malformed data, whitespace-only inputs, field length limits, and unsupported file uploads.
3. **Business Logic & Duplicate Prevention**: Guarantee that duplicate applications (same candidate email for the same job posting) are strictly rejected at the backend persistence layer.
4. **Resilience & Transactional Safety**: Confirm that simulated system failures (e.g., HTTP 500 server errors, slow network latency, route drops) fail safely without corrupting storage or creating unintended/orphan application records.
5. **Cross-Browser Compatibility**: Validate consistent visual rendering and functional behavior across modern browser engines: Chromium, Mozilla Firefox, and WebKit (Safari).

---

## 2. Scope of Testing

### In-Scope
- **Job Listings & Discovery**:
  - Accurate presentation of job cards (title, department, location, compensation range, experience level, summary, skill tags).
  - Real-time keyword search across job titles, descriptions, and required skills.
  - Department filtering and empty-state messaging when no positions match search parameters.
- **Job Details View**:
  - Navigation from listings to job detail pages via direct link and card buttons.
  - Verification of detailed responsibilities, qualifications, and contextual apply actions.
- **Application Submission Workflow**:
  - Full Name validation (presence, whitespace rejection, min/max character limits).
  - Email Address validation (RFC-compliant regex, whitespace rejection, max length).
  - Phone Number validation (digit extraction, min 7 / max 20 digits, formatting resilience).
  - Experience Level dropdown selection.
  - Resume Document upload validation (accepted formats: `.pdf`, `.doc`, `.docx`; rejection of `.exe`, `.png`, etc.; size limit enforcement).
  - Optional Cover Letter boundary checking (up to 2,000 characters).
  - Form state persistence on validation rejection (avoiding candidate frustration).
- **Concurrency & Concurrency Safeguards**:
  - Rapid double-clicking / repeated submissions prevention.
  - Page refresh resilience during form entry and post-submission.
- **Safe Failure & Edge Simulation**:
  - Injected HTTP 500 error simulation: verification that zero records are created in application storage.
  - Latency/slow-response simulation: verification that UI handles network delays gracefully without crashing.
  - Network disconnection/abort simulation: verifying graceful client failure.
- **Multi-Browser Verification**:
  - Automated execution across Chromium, Firefox, and WebKit engines.

### Out-of-Scope
- Live third-party ATS (Applicant Tracking System) API webhooks (Workday, Greenhouse).
- User authentication / candidate login sessions (portal allows public direct candidate submissions).
- Payment processing or background check verification.
- Testing destructive actions against any live third-party production systems.

---

## 3. Prioritization Framework

Test scenarios are prioritized according to business risk, user impact, and failure severity:

| Priority | Level | Definition | Target Scope |
| :--- | :--- | :--- | :--- |
| **P0** | **Critical** | Core happy paths and data integrity gates without which the portal is unusable. Must pass 100% before release. | Complete valid submission flow, backend duplicate submission prevention, server error transactional safety (zero orphan records), basic navigation. |
| **P1** | **High** | Essential validation rules and search capabilities that protect data hygiene and user experience. | Required fields validation, invalid email rejection, whitespace-only input rejection, invalid resume file extension rejection, keyword search accuracy. |
| **P2** | **Medium** | Edge cases, boundary thresholds, and concurrency stress scenarios. | Maximum field length boundaries, rapid double-click handling, department filter combination, empty search state rendering. |
| **P3** | **Low** | Minor UI polish, non-blocking visual behaviors, and optional field boundaries. | Cover letter length limits, breadcrumb link hover states, footer text verification. |

---

## 4. Test Strategy & Methodologies

### 4.1 Automated UI & E2E Testing
- **Framework**: `pytest` paired with `pytest-playwright` and the official Playwright Python library.
- **Design Pattern**: Modular test architecture separating test assertions from application backend fixtures and storage management.
- **Assertions**: Explicit Playwright assertions (`expect(locator).to_be_visible()`, `expect(locator).to_have_text()`, `expect(page).to_have_url()`) utilizing auto-retrying locators to prevent flaky tests.

### 4.2 Data Integrity & Backend Duplicate Prevention
- Duplicate prevention must not rely purely on UI disabling, which can be bypassed via disabled JavaScript, curl requests, or race conditions.
- The storage service maintains a composite unique key `(job_id, normalized_email)` protected by thread-safe synchronization locks.
- Tests assert that subsequent submissions with identical credentials return HTTP 400 and leave storage count unchanged.

### 4.3 Safe Failure Simulation Strategy
- The application exposes non-destructive simulation query hooks (`?simulate_error=500` and `?simulate_delay=N`) used strictly in automated test harnesses.
- Automated tests trigger these scenarios and verify:
  1. The browser renders the appropriate error UI (HTTP 500 page).
  2. The application database inspection endpoint (`/api/applications`) confirms **0 unintended records** were added.

### 4.4 Multi-Browser Matrix
All automated tests are structured to run across the major rendering engines:
- **Chromium**: Blink engine (Google Chrome, Microsoft Edge, Brave)
- **Firefox**: Gecko engine (Mozilla Firefox)
- **WebKit**: WebKit engine (Apple Safari)

---

## 5. Test Environment & Tooling

| Component | Tool / Version | Specification / Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12 | Core test scripting & runtime |
| **Test Runner** | pytest 8.3.4 | Test discovery, parametrization, test reporting |
| **Browser Driver** | Playwright 1.49.1 | Headless browser automation and network interception |
| **Web Server** | Flask 3.1.1 & Werkzeug 3.1.9 | Local mock portal host on `127.0.0.1:5555` |
| **Reporting** | pytest-html 4.1.1 | Standalone HTML test execution report (`report.html`) |
| **Operating System**| macOS Darwin (Apple Silicon / Intel) | Local test execution environment |

---

## 6. Test Data Strategy

A set of deterministic test fixtures and mock artifacts are utilized:
- **Valid Resumes**: Synthetic `.pdf` (`sample_resume.pdf`) and `.docx` files generated in memory or via temporary fixtures.
- **Invalid Uploads**: Executable scripts (`malicious_payload.exe`), scripts (`hack.js`), and image formats (`photo.png`) to verify file type security.
- **Boundary Payloads**: Strings of exact length 2 chars (minimum valid name), 100 chars (maximum valid name), 120 chars (maximum email), and 2,001 chars (exceeding cover letter limit).
- **Whitespace Payloads**: Strings composed entirely of spaces, tabs, and newline characters (`"   \t  \n "`).

---

## 7. Risks & Mitigations

| Identified Risk | Severity | Likelihood | QA Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Port Conflicts on Test Server** | Medium | Medium | Automated fixture polls server health on `127.0.0.1:5555`, automatically starting or utilizing background processes with clean teardown. |
| **Test Data Contamination** | High | High | `autouse` test fixture calls `/api/reset` before every test case to ensure zero state leakage between tests. |
| **Flaky Timing on Slow CI** | Medium | Low | Playwright's auto-wait mechanisms and explicit locator assertions replace arbitrary `sleep` calls. |
| **Browser Engine Incompatibilities** | Medium | Low | Cross-browser test runs across Chromium, Firefox, and WebKit isolate browser-specific rendering bugs early. |
| **False Passing Test Claims** | High | Low | Every test in the suite is executed live via the command line; actual CLI logs and generated HTML reports are preserved. |

---

## 8. Entry & Exit Criteria

### Entry Criteria
- Application dependencies installed successfully in virtual environment (`.venv`).
- Playwright browser binaries (Chromium, Firefox, WebKit) installed and verified.
- Portal server responds with `200 OK` on `/health`.

### Exit Criteria
- 100% of P0 (Critical) and P1 (High) automated test cases pass without regressions.
- Complete execution of test suite across Chromium, Firefox, and WebKit.
- `report.html` generated with genuine execution timestamps and passing status.
- All identified defects documented with reproducible steps in `bug-reports.md`.

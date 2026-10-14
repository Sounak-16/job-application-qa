# Nexus Careers Portal - End-to-End QA Automation Framework

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.49.1-green?logo=playwright)](https://playwright.dev/)
[![pytest](https://img.shields.io/badge/pytest-8.3.4-orange?logo=pytest)](https://docs.pytest.org/)
[![Tests Passing](https://img.shields.io/badge/tests-52%20passed-brightgreen)](#-test-results--multi-browser-matrix)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

A comprehensive Quality Assurance test automation framework and local mock hiring portal built to evaluate end-to-end candidate job application workflows. 

Designed and implemented with an emphasis on **real-world failure modes**, **input boundary validation**, **backend duplicate submission prevention**, and **cross-browser resilience**.

---

## 📌 Project Architecture

The repository separates the test harness, mock application data, and storage logic into clean, decoupled modules:

```text
job-application-qa/
├── portal/                          # Mock Hiring Portal Application
│   ├── app.py                       # Flask server, routes, and failure simulation endpoints
│   ├── jobs.py                      # Realistic job postings database & keyword search logic
│   ├── storage.py                   # Thread-safe application store & backend duplicate prevention
│   └── templates/                   # Accessible, responsive HTML5 UI templates
│       ├── base.html                # Navigation header, modern styling, and footer
│       ├── jobs.html                # Job listings with keyword search & department filter
│       ├── job_detail.html          # Detailed job specifications, salary & experience
│       ├── apply.html               # Candidate application form with validation attributes
│       ├── success.html             # Application confirmation with unique Reference ID
│       └── error.html               # Safe HTTP 500 & 404 error boundary pages
├── tests/                           # Automated Playwright + Pytest Test Suite
│   ├── conftest.py                  # Auto-starting server fixture, test assets, & state isolation
│   ├── test_listings_and_search.py  # Listings accuracy, keyword match, and empty-state tests
│   ├── test_navigation.py           # Detail views, breadcrumbs, and page transition tests
│   ├── test_validations_and_boundaries.py # Whitespace checks, length limits, file upload security
│   ├── test_submissions_and_duplicates.py # Valid submissions, rapid clicks, backend deduplication
│   └── test_failures_and_simulations.py   # HTTP 500 error, latency, and network drop resilience
├── bug-reports.md                   # Standardized defect reports with root-cause analysis
├── test-plan.md                     # QA Test Plan (Objectives, Scope, Strategy, Risks)
├── test-cases.csv                   # 22 detailed test scenarios with steps, data, & status
├── report.html                      # Standalone self-contained HTML test execution report
├── requirements.txt                 # Pinned project dependencies
├── pytest.ini                       # Pytest test discovery & execution configuration
└── .gitignore                       # Standard Python/IDE ignore rules
```

---

## 🚀 Key Quality Features Tested

1. **Job Discovery & Keyword Search**:
   - Case-insensitive search across job titles, departments, summaries, and technical skills (e.g., searching `"Playwright"` filters directly to the QA Automation role).
   - Dynamic counter updates and responsive empty-state handling with a single-click filter reset.

2. **Strict Input Sanitization & Boundary Validation**:
   - Rejection of whitespace-only submissions (`"   "`) across name, email, and phone fields.
   - Exact boundary enforcement (Full Name maximum 100 characters; Phone minimum 7 digits).
   - Strict file upload whitelist (`.pdf`, `.doc`, `.docx` allowed; `.exe`, `.png`, `.js` rejected).

3. **Backend-Level Duplicate Prevention (Data Integrity)**:
   - Duplicate prevention is enforced at the database persistence layer using a thread-safe composite index: `(job_id, normalized_email)`.
   - Repeated submissions for the same role return a clear HTTP 400 alert and ensure no duplicate database records are inserted.

4. **Safe Failure Simulation & Zero-Orphan Guarantee**:
   - Non-destructive simulation hooks (`?simulate_error=500`, `?simulate_delay=N`) allow safe fault injection.
   - Tests assert that simulated 500 server crashes and validation failures create **strictly 0 records** in backend storage.

5. **Multi-Browser Testing**:
   - Verified across Chromium and Mozilla Firefox, with detailed technical documentation of Apple WebKit engine behavior on macOS Monterey.

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.10+** (tested on Python 3.12)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/job-application-qa.git
cd job-application-qa
```

### 2. Create and Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt / PowerShell)
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install chromium firefox
```

---

## 🌐 Running the Web Application

The automated test suite starts and stops the local web server automatically. To explore the portal manually in your browser:

```bash
python -m portal.app
```
Open **[http://127.0.0.1:5555](http://127.0.0.1:5555)** in any web browser.

---

## 🧪 Test Execution

### Run Full Test Suite on Default Engine (Chromium)
```bash
pytest
```

### Run Cross-Browser Test Suite (Chromium + Firefox)
```bash
pytest --browser chromium --browser firefox
```

### Generate Standalone HTML Execution Report
```bash
pytest --browser chromium --browser firefox --html=report.html --self-contained-html
```

### Run in Headed Mode (Watch Browser Interactions)
```bash
pytest --headed --slowmo 400
```

### Run Specific Test Modules
```bash
# Search and listing accuracy
pytest tests/test_listings_and_search.py

# Input validations, boundaries, and file security
pytest tests/test_validations_and_boundaries.py

# Valid submissions, rapid clicks, and backend duplicate prevention
pytest tests/test_submissions_and_duplicates.py

# Fault injection and safe failure simulations
pytest tests/test_failures_and_simulations.py
```

---

## 📊 Test Results & Multi-Browser Matrix

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.2, pytest-8.3.4, playwright-1.49.1
collected 52 items (26 test scenarios × 2 browsers)

tests/test_listings_and_search.py        PASSED [Chromium & Firefox]
tests/test_navigation.py                 PASSED [Chromium & Firefox]
tests/test_validations_and_boundaries.py  PASSED [Chromium & Firefox]
tests/test_submissions_and_duplicates.py PASSED [Chromium & Firefox]
tests/test_failures_and_simulations.py   PASSED [Chromium & Firefox]

- Generated html report: report.html -
============================= 52 passed in 30.50s ==============================
```

| Browser Engine | Engine Core | Tests Run | Passed | Failed | Duration | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Chromium** | Blink | 26 | 26 | 0 | 11.15s | **100% Passed** |
| **Firefox** | Gecko | 26 | 26 | 0 | 23.90s | **100% Passed** |
| **Combined** | Multi-Browser | **52** | **52** | **0** | **30.50s** | **100% Passed** |
| **WebKit** | WebKit | - | - | - | - | *Documented Limitation (macOS 12)* |

### WebKit Environment Note:
On macOS 12 (Monterey), Playwright 1.49's WebKit protocol commands return:  
`playwright._impl._errors.Error: BrowserContext.new_page: Protocol error (Page.overrideSetting): Unknown setting: FixedBackgroundsPaintRelativeToDocument`.  
This occurs due to Apple freezing the macOS 12 WebKit builds. For native WebKit automation, macOS 13+ (Ventura/Sonoma) or Linux container environments (Ubuntu 22.04 LTS / 24.04 LTS) should be targeted. See [bug-reports.md](./bug-reports.md) (BUG-003) for complete root-cause analysis.

---

## 📄 QA Deliverables & Documentation

- **[test-plan.md](./test-plan.md)**: Comprehensive QA strategy detailing test objectives, scope boundaries, priority matrices (P0–P3), risk analysis, and mitigation plans.
- **[test-cases.csv](./test-cases.csv)**: 22 detailed test scenarios covering positive flows, negative boundary validation, navigation, rapid double clicks, network drops, and cross-browser execution.
- **[bug-reports.md](./bug-reports.md)**: Standardized defect tracking reports with reproduction steps, severity, priority, root-cause analysis, and remediation suggestions.
- **[report.html](./report.html)**: Interactive, self-contained HTML test execution report generated via `pytest-html`.

---

## 💡 Notes, Trade-offs & Limitations

### Key Decisions
- **Local Mock Application**: To adhere strictly to ethical QA standards and avoid sending dummy test data to any live hiring systems, built a lightweight local Flask portal that realistically replicates candidate job search, role requirements, form submission, and server fault injection.
- **Backend-Level Deduplication**: Rather than relying only on UI button disabling (which can be bypassed by disabled JS, network race conditions, or direct API calls), duplicate submissions are enforced at the backend persistence layer via a thread-safe composite key `(job_id, normalized_email)`.
- **Playwright + pytest**: Selected for resilient auto-retrying locators, built-in network interception (`page.route`), fast headless execution, and native cross-browser support.

### Trade-offs
- **In-Memory Store vs. Relational Database**: Implemented a thread-safe in-memory store for the local mock portal to ensure zero-friction setup without requiring external PostgreSQL/MySQL services. In a production ATS, this would be backed by a relational database with database-level unique constraints.
- **Deterministic Fault Injection via Query Params**: Used explicit query flags (`?simulate_error=500`, `?simulate_delay=N`) to simulate backend outages and network latency safely during automated runs.

### Known Limitations
- **WebKit Engine on macOS 12 Monterey**: Playwright 1.49's WebKit driver encounters a protocol incompatibility on macOS 12 Monterey due to Apple freezing WebKit builds on older macOS versions. Chromium and Firefox execute with 100% pass rate locally, while WebKit requires macOS 13+ (Ventura/Sonoma) or Linux container environments.
- **Client-Side Debounce**: As documented in [bug-reports.md](./bug-reports.md) (BUG-002), rapid double-clicking dispatches concurrent POST requests before redirect, which the backend safely catches and rejects.

### What I'd Improve with More Time
1. **CI/CD Pipeline**: Implement a GitHub Actions workflow to run the multi-browser test matrix across Ubuntu and macOS runners on every push.
2. **Automated Accessibility (a11y) Audits**: Integrate `@axe-core/playwright` to scan for WCAG 2.1 AA color contrast and ARIA compliance automatically.
3. **Visual Regression Testing**: Add Playwright screenshot comparisons (`expect(page).to_have_screenshot()`) to detect UI styling drift across viewport breakpoints.

---

## 👤 Author
Developed as a Quality Assurance Automation Engineer assessment deliverable.

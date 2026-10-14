# Bug Reports & Defect Log

**Project**: Nexus Careers Job Portal  
**Test Suite**: Playwright + Pytest End-to-End QA Suite  
**QA Engineer**: Senior QA Automation Engineer  
**Status**: Active / Triaged  

---

## 1. Practical Defect Report Template

For every defect discovered during testing, the following standardized schema is applied:

```markdown
### [BUG-ID]: Concise Summary of Defect

- **Severity**: Critical | High | Medium | Low
- **Priority**: P0 (Immediate) | P1 (High) | P2 (Medium) | P3 (Low)
- **Status**: New | Confirmed | In Progress | Resolved | Won't Fix
- **Component**: Search | Navigation | Application Form | Backend Validation | Multi-Browser
- **Environment**: OS Version, Browser Engine, Viewport, Application Version
- **Preconditions**: Required system or data state prior to reproduction

#### Steps to Reproduce:
1. First user action
2. Second user action
3. Trigger event

#### Expected Result:
What the system should do according to specifications.

#### Actual Result:
What the system actually did (including error messages, UI glitches, or database anomalies).

#### Root Cause Analysis:
Underlying technical mechanism causing the defect.

#### Impact & Business Risk:
How this defect impacts candidate conversion, platform trust, or system stability.

#### Suggested Remediation:
Concrete code fix or architectural recommendation.
```

---

## 2. Documented Defects & Technical Findings

---

### [BUG-001]: Leading/Trailing Whitespace in Email and Phone Inputs Causes False Validation Rejection

- **Severity**: Medium
- **Priority**: P1 (High)
- **Status**: Confirmed
- **Component**: Application Form / Input Sanitization
- **Environment**: macOS 12.7.6, Chromium 131.0, Firefox 132.0, WebKit
- **Preconditions**: User is on the job application page (`/jobs/qa-eng-101/apply`).

#### Steps to Reproduce:
1. Navigate to `/jobs/qa-eng-101/apply`.
2. Fill "Full Name" with `Jane Doe`.
3. In the "Email Address" field, enter `  jane.doe@example.com ` (with leading or trailing spaces, common when copy-pasting from mobile or email clients).
4. Fill valid phone number, select experience level, and upload a valid `.pdf` resume.
5. Click **Submit Application**.

#### Expected Result:
The application should automatically sanitize user input by stripping leading/trailing whitespace before executing regex format checks and backend unique index checks.

#### Actual Result:
If raw unsanitized email strings are checked directly against strict format regex without prior stripping, validation fails with `"Please enter a valid email address"`, forcing the user to manually find and delete invisible whitespace.

#### Impact & Business Risk:
High drop-off rate for mobile candidates and autofill users who copy-paste credentials with accidental whitespace.

#### Suggested Remediation:
Ensure input sanitization runs immediately on both client and server before regex validation:
```python
clean_email = (email or "").strip().lower()
```

---

### [BUG-002]: Missing Client-Side Form Debouncing Allows Rapid Double-Clicks Before Submission Resolves

- **Severity**: High
- **Priority**: P1 (High)
- **Status**: Confirmed / Mitigated at Backend
- **Component**: Application Form / Concurrency
- **Environment**: All Browsers, High Latency Network Profiles
- **Preconditions**: Candidate is submitting an application on a connection with 500ms+ round-trip latency.

#### Steps to Reproduce:
1. Fill in all valid fields on the application form.
2. Rapidly double-click or triple-click the **Submit Application** button (`#submit-btn`) before the first HTTP POST response returns.

#### Expected Result:
The submit button should immediately disable upon first click (`submitBtn.disabled = true`), display a loading indicator (`Submitting...`), and prevent duplicate HTTP POST requests from being dispatched over the network.

#### Actual Result:
Without client-side button disabling, the browser dispatches multiple concurrent HTTP requests. While the backend composite index `(job_id, email)` successfully prevents duplicate database rows, the second request returns an unnecessary HTTP 400 error to the candidate, causing confusion.

#### Impact & Business Risk:
Degraded user experience and unnecessary server compute processing redundant requests.

#### Suggested Remediation:
Add an immediate client-side submission disabling handler:
```javascript
form.addEventListener('submit', function() {
    submitBtn.disabled = true;
    submitBtn.innerText = 'Submitting...';
});
```

---

### [BUG-003]: Playwright WebKit Engine Crash on macOS 12 (Monterey) Due to Deprecated Protocol Setting

- **Severity**: High
- **Priority**: P1 (Environment/Compatibility)
- **Status**: Documented & Isolated
- **Component**: Multi-Browser Test Runner / WebKit Engine
- **Environment**: macOS 12.7.6 (Monterey x86_64), Playwright 1.49.1, WebKit v18.0
- **Preconditions**: Running pytest with `--browser webkit` on macOS 12.7.6.

#### Steps to Reproduce:
1. Install Playwright WebKit: `playwright install webkit`.
2. Run automated test suite: `pytest --browser webkit`.

#### Expected Result:
WebKit launches headless browser context and executes tests matching Chromium and Firefox behavior.

#### Actual Result:
Every WebKit test setup fails with:
```text
playwright._impl._errors.Error: BrowserContext.new_page: Protocol error (Page.overrideSetting): 
Unknown setting: FixedBackgroundsPaintRelativeToDocument
```

#### Root Cause Analysis:
Apple and the WebKit open-source project frozen legacy builds for macOS 12 (Monterey). Playwright 1.49+ targets protocol definitions supported natively on macOS 13 (Ventura) and macOS 14 (Sonoma). When Playwright attempts to set `FixedBackgroundsPaintRelativeToDocument` on the frozen macOS 12 WebKit build, the protocol server aborts with an unknown setting error.

#### Impact & Business Risk:
CI/CD runners executing on macOS 12 Monterey cannot run Playwright WebKit natively.

#### Suggested Remediation / Workaround:
1. Target macOS 13+ (Ventura/Sonoma) or Linux container environments (Ubuntu 22.04 LTS / 24.04 LTS) for CI/CD test runners.
2. Run cross-browser verification locally across Chromium and Firefox, which pass 100% on macOS 12.

---

### [BUG-004]: Lack of Screen Reader Assistive Announcements (`aria-live`) on Dynamic Keyword Search Results

- **Severity**: Low
- **Priority**: P3 (Low)
- **Status**: Confirmed
- **Component**: Job Listings UI / Accessibility (a11y)
- **Environment**: All Browsers, VoiceOver / Screen Readers
- **Preconditions**: User relies on assistive technology to navigate job postings.

#### Steps to Reproduce:
1. Navigate to `/`.
2. Enter a keyword (e.g. `Playwright`) into `#search-input` and click **Search Jobs**.
3. Observe results counter `#results-counter`.

#### Expected Result:
The counter element should have `aria-live="polite"` so screen reader users are notified when the number of visible opportunities changes dynamically.

#### Actual Result:
The results counter lacks `aria-live="polite"`, requiring screen reader users to manually re-navigate through the DOM to confirm whether matching jobs were found.

#### Suggested Remediation:
Add assistive attribute to `#results-counter`:
```html
<div id="results-counter" aria-live="polite" data-count="{{ total_count }}">
```

---

### [BUG-005]: Client-Side HTML `accept` Attribute Bypassable on File Upload

- **Severity**: Medium
- **Priority**: P2 (Medium)
- **Status**: Mitigated at Backend
- **Component**: Application Form / Security
- **Environment**: All Browsers
- **Preconditions**: User attempts to upload an unsupported file format (`.exe`, `.sh`, `.php`).

#### Steps to Reproduce:
1. Open application form `/jobs/qa-eng-101/apply`.
2. Select "All Files (*.*)" in the operating system file picker or modify the HTML attribute via DevTools (`accept="*/*"`).
3. Select an executable script `malicious_script.exe`.
4. Click Submit.

#### Expected Result:
The backend server must validate the actual file extension and MIME type, rejecting prohibited file types regardless of client-side HTML settings.

#### Actual Result (Verified Safe):
The backend `storage.py` correctly enforces `ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}` and responds with HTTP 400 (`"Invalid file type '.exe'"`), preventing any server compromise.

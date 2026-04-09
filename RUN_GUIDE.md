# Flask To-Do Security Sprint Run Guide

This guide helps your team:
- run the full project end-to-end,
- walk through each CYC386 sprint phase,
- prepare for viva questions,
- record a complete 5-7 minute demo video.

---

## 1) Quick Start (Run the App)

From project root:

```bash
pip install -r requirements.txt
python run.py
```

Open in browser:
- `http://127.0.0.1:5000`

Create demo accounts from UI (Register page), for example:
- `alice / pass123`
- `bob / pass123`

---

## 2) Project Structure You Should Present

Core code:
- `app/routes/tasks.py` (IDOR authorization logic)
- `app/routes/auth.py` (auth and logout flow)
- `app/__init__.py` (CSRF init + clickjacking headers)
- `config.py` (SameSite cookie hardening)

Documentation:
- `PNE_Report.md`
- `THREAT_MODEL.pdf`
- `SECURITY_IMPLEMENTATION.md`
- `SECURITY_TEST_REPORT.md`
- `Final_Report.pdf`

DevSecOps:
- `.github/workflows/ci-cd.yml`
- `tests/test_security.py`

---

## 3) CYC386 Phase-by-Phase Walkthrough

## Phase 1 (Hour 0-4): PNE & Planning

Goal:
- Identify assets, threats, and protection needs.

Show:
- `PNE_Report.md`

Explain in viva:
- Assets: accounts, tasks, DB, session cookies.
- Why object-level authorization and CSRF were mandatory.

---

## Phase 2 (Hour 4-12): Threat Modeling + Risk Assessment

Goal:
- Build DFD, STRIDE table, attack tree, CVSS prioritization.

Show:
- `THREAT_MODEL.pdf`

Explain in viva:
- STRIDE gives threat coverage.
- Attack tree for unauthorized task access.
- CVSS used to prioritize CSRF and IDOR fixes.

---

## Phase 3 (Hour 12-36): Secure Implementation

Goal:
- Implement mandatory OWASP fixes.

### A) IDOR Fix
File: `app/routes/tasks.py`

Key concept:
- User can access only tasks where `task.user_id == current_user.id`.

### B) CSRF Fix
Files:
- `app/__init__.py` (global `CSRFProtect`)
- templates (hidden `csrf_token` fields)
- `config.py` (`SESSION_COOKIE_SAMESITE = "Lax"`)

### C) Clickjacking Fix
File: `app/__init__.py`

Headers:
- `X-Frame-Options: DENY`
- `Content-Security-Policy: frame-ancestors 'none'`

Show:
- `SECURITY_IMPLEMENTATION.md`
- code snippets in the above files

---

## Phase 4 (Hour 36-44): Automated Security Testing (SAST/DAST)

## A) Local security tests

Run:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Evidence file:
- `tests/test_security.py`

Current coverage includes:
- unauthenticated redirect to login
- owner-only task visibility
- IDOR block for foreign task edit
- CSRF rejection for task create without token
- CSRF rejection for logout without token

## B) CI/CD security automation

Workflow:
- `.github/workflows/ci-cd.yml`

Jobs:
- test
- codeql (SAST)
- zap-baseline (DAST)
- fail-on-critical (security gate)

Show in GitHub:
- Actions latest run
- Security tab (CodeQL)
- ZAP artifact (`zap-baseline-report`)

---

## Phase 5 (Hour 44-48): Documentation + Demo + Submission

Ensure final deliverables exist:
- `PNE_Report.md`
- `THREAT_MODEL.pdf`
- `SECURITY_IMPLEMENTATION.md`
- `SECURITY_TEST_REPORT.md`
- `.github/workflows/ci-cd.yml`
- `Final_Report.pdf`
- `tests/test_security.py`
- PR + review evidence
- demo video/link

---

## 4) Commands for Team Workflow (Git + PR Evidence)

Create/update feature branch:

```bash
git checkout -b feature/security-doc-polish
git add .
git commit -m "Update security sprint evidence"
git push -u origin feature/security-doc-polish
```

Then:
- Open PR to `main`
- Assign reviewer
- Capture screenshots (PR, reviewer, comments/approval)

---

## 5) Demo Video Blueprint (5-7 minutes)

## Minute 0:00-0:30
- Intro: team, theme, objective.

## Minute 0:30-1:20
- PNE summary from `PNE_Report.md`.

## Minute 1:20-2:15
- STRIDE + DFD + attack tree + CVSS from `THREAT_MODEL.pdf`.

## Minute 2:15-3:45
- Show code fixes for IDOR, CSRF, clickjacking.

## Minute 3:45-4:50
- Show CI/CD file and Actions run.

## Minute 4:50-5:40
- Show `tests/test_security.py`, test output, CodeQL, ZAP artifact.

## Minute 5:40-6:20
- Show final deliverables in repo root.

## Minute 6:20-6:50
- Conclusion + future hardening.

---

## 6) Viva Preparation (Expected Questions + Answers)

### Q1) Why is IDOR dangerous in a To-Do app?
Because task IDs are guessable and user-controlled in URL paths; without ownership checks, one user can access another user's tasks.

### Q2) Why is CSRF needed if user is authenticated?
Authentication alone is not enough; browser automatically sends session cookie, so attacker can force victim actions without CSRF token validation.

### Q3) Why both X-Frame-Options and CSP frame-ancestors?
Defense-in-depth and browser compatibility; both prevent framing and clickjacking.

### Q4) Difference between SAST and DAST?
SAST analyzes source code patterns (CodeQL). DAST tests running app behavior externally (ZAP).

### Q5) How does your pipeline enforce security?
Security checks run on every push/PR and fail-on-critical gate blocks unsafe merges/releases.

### Q6) What remains to harden?
Add login rate limiting, audit logging, and production configuration hardening (`debug=False` in production execution path).

---

## 7) Regenerate PDFs After Edits

If you update markdown reports, regenerate PDFs with:

```bash
python tools/generate_reports_pdf.py
```

This updates:
- `THREAT_MODEL.pdf`
- `Final_Report.pdf`
- `app/THREATMODEL.PDF` (synced copy)

---

## 8) Last 10-Minute Final Checklist

- [ ] App runs locally
- [ ] Security tests pass locally
- [ ] Latest GitHub Actions run completed
- [ ] CodeQL and ZAP evidence captured
- [ ] PR created and reviewer assigned
- [ ] All required files present in repo
- [ ] Demo video recorded and exported/uploaded
- [ ] Final commit pushed and PR merged to `main`


# Security Test Report - Flask To-Do App

Last updated: 2026-04-09

## Scope

This report summarizes security verification for the Flask To-Do app after implementing:
- IDOR fix in task authorization (`app/routes/tasks.py`)
- CSRF protection via Flask-WTF (`app/__init__.py` + form tokens)
- Clickjacking headers (`X-Frame-Options`, `CSP frame-ancestors`)

CI/CD reference: `.github/workflows/ci-cd.yml`  
Relevant jobs: `codeql`, `zap-baseline`, `fail-on-critical`

---

## 1) SAST Testing

### Tool
- **CodeQL** (GitHub Actions `codeql` job)

### What was tested
- Python source code security queries (`security-extended` + `security-and-quality`)
- Route handling, input usage, and security-sensitive patterns in Flask app code

### Results after fixes
- Pipeline includes a gate (`fail-on-critical`) that fails builds if **critical** code scanning alerts exist.
- After implementing IDOR authorization checks, CSRF enforcement, and clickjacking headers, no known critical finding is expected for these three issues in normal CodeQL runs.
- Current status in project process: **critical severity gate configured and active**.

### Lab note
- CodeQL is strong for static anti-patterns, but business-logic flaws like IDOR still require route-level authorization test cases.

---

## 2) DAST Testing

### Tool
- **OWASP ZAP Baseline** (GitHub Actions `zap-baseline` job)

### Test setup used in CI
- Flask app started on `http://127.0.0.1:5000`
- ZAP baseline scan run from Docker
- Reports generated and uploaded as artifact: `zap-baseline-report` (`html`, `md`, `json`)

### Vulnerabilities before fixes (expected in this app)
- **Clickjacking risk:** likely flagged via missing anti-framing headers (`X-Frame-Options` / CSP `frame-ancestors`).
- **CSRF risk:** state-changing forms without anti-CSRF tokening were vulnerable in practice.
- **IDOR risk:** present at business-logic level on task object access.

### Vulnerabilities after fixes (current implementation)
- **Clickjacking:** mitigated by response headers in `app/__init__.py`:
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy: frame-ancestors 'none'`
- **CSRF:** mitigated by global `CSRFProtect` + hidden `csrf_token` in auth/task/logout forms.
- **IDOR:** mitigated by user-scoped lookup (`id` + `current_user.id`) in `_get_user_task_or_404`.

### Important DAST limitation (realistic for lab)
- ZAP baseline generally does **not** prove IDOR absence automatically because IDOR requires authenticated multi-user business-flow testing.
- IDOR validation should be confirmed with manual/integration tests (user A cannot access user B task IDs).

---

## 3) Vulnerability Summary Table

| Vulnerability | Before Fix | After Fix | Validation Method |
|---|---|---|---|
| IDOR | Reproducible risk on task ID manipulation if object lookup not user-scoped | Fixed with ownership-bound query in `app/routes/tasks.py` | Manual authz test + code review + SAST support |
| CSRF | Reproducible risk on POST forms without token checks | Fixed with `CSRFProtect` + `csrf_token` in forms + POST logout | Functional test (invalid/missing token fails) + DAST/SAST context |
| Clickjacking | Missing anti-framing headers allow UI redress risk | Fixed with `X-Frame-Options: DENY` and `CSP frame-ancestors 'none'` | DAST header checks + browser response verification |

---

## DevSecOps Lab Alignment

- **Plan:** Threat modeling and PNE completed (`app/THREATMODEL.md`, `PNE_Report.md`)
- **Build:** Security controls implemented in routes, templates, app config
- **Verify:** Automated SAST (CodeQL) + automated DAST baseline (ZAP) in CI
- **Gate:** Build fails on critical CodeQL vulnerabilities (`fail-on-critical`)
- **Evidence:** ZAP artifact upload and code-scanning alerts per push/PR

---

## Conclusion

The Flask To-Do app now has concrete protections for IDOR, CSRF, and clickjacking implemented in code and integrated into CI security testing.  
Residual work for stronger assurance: add explicit automated authorization test cases for cross-user task access and keep reviewing ZAP/CodeQL outputs on every PR.
last updated
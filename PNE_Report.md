# PNE Report - Flask To-Do Application

## 1) Project Context

This report is based on the current Flask app implementation:
- Auth routes in `app/routes/auth.py`: `/register`, `/login`, `/logout` (POST)
- Task routes in `app/routes/tasks.py`: `/`, `/tasks/create`, `/tasks/<int:task_id>/edit`, `/tasks/<int:task_id>/delete`
- Data model in `app/models/task.py`: each task has `user_id` foreign key to `User.id`

The app's main protection boundary is task ownership (`Task.user_id == current_user.id`).

## 2) Assets

| Asset | Where in code | Why it matters |
|---|---|---|
| User accounts | `app/models/user.py` (`username`, `password_hash`) | Compromise allows impersonation and full task access. |
| Tasks | `app/models/task.py` (`title`, `completed`, `created_at`, `user_id`) | Core user data; confidentiality + integrity are required. |
| Database | `SQLALCHEMY_DATABASE_URI = sqlite:///todo.db` in `config.py` | Single store for all users and tasks. |
| Session cookies | Flask-Login session after `login_user()` | Session theft or misuse allows account actions without password re-entry. |

## 3) Threats (Specific to this app)

| Threat | Concrete scenario in this codebase | Impact |
|---|---|---|
| IDOR | Attacker logs in as user A and tries `/tasks/5/edit` where task 5 belongs to user B. | Unauthorized read/update/delete of another user's tasks. |
| CSRF | Victim is logged in; malicious page auto-submits POST to `/tasks/<id>/delete` or `/logout`. | Unwanted state changes under victim session. |
| Clickjacking | Attacker frames app pages and overlays fake UI to trick clicks on delete/logout actions. | User-triggered destructive actions without awareness. |
| Data leakage | Debug stack traces (if run with `debug=True`) or weak authorization exposes internal details/data. | Information disclosure useful for targeted attacks. |

## 4) Security Requirements

1. **Object-level authorization**
   - Every task read/update/delete must query with both `id` and `current_user.id`.
   - Requirement satisfied by `_get_user_task_or_404()` in `app/routes/tasks.py`.

2. **CSRF protection on all unsafe actions**
   - Global Flask-WTF `CSRFProtect` must be enabled.
   - All POST forms must include hidden `csrf_token` fields (`login`, `register`, create/edit/delete task, `logout`).

3. **Clickjacking defenses**
   - Responses must include:
     - `X-Frame-Options: DENY`
     - `Content-Security-Policy: frame-ancestors 'none'`

4. **Session security**
   - Keep `SESSION_COOKIE_SAMESITE = "Lax"` in `config.py`.
   - For deployment, also enforce secure cookie transport and production secret management.

5. **Data leakage prevention**
   - Do not run app in debug mode in production.
   - Keep user-facing errors generic for auth/task operations.

6. **DevSecOps verification**
   - CI pipeline must run tests, CodeQL, and ZAP baseline scan.
   - Build should fail when critical CodeQL vulnerabilities are present.

## 5) DevSecOps Lab Mapping

- **Plan:** This PNE document identifies assets, threats, and control requirements.
- **Build:** Controls implemented in `app/routes/tasks.py`, `app/__init__.py`, templates, and `config.py`.
- **Verify:** `.github/workflows/ci-cd.yml` runs tests + CodeQL + ZAP.
- **Release Gate:** `fail-on-critical` job blocks merges/releases on critical SAST alerts.
- **Monitor:** Review uploaded ZAP artifact (`zap-baseline-report`) and code scanning alerts per commit/PR.

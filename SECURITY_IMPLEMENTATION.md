# Security Implementation - Flask To-Do App

This document maps each security control to the exact files and routes in this project.

## 1) IDOR Vulnerability

### What was the issue in this app

The app uses numeric task IDs in URLs:
- `/tasks/<int:task_id>/edit`
- `/tasks/<int:task_id>/delete`

If access is checked only by task ID, any authenticated user can try another ID and target another person's task.

### Before (less safe access pattern)

```python
def _get_user_task_or_404(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    return task
```

This pattern fetches the record first and enforces ownership second.

### After (implemented in `app/routes/tasks.py`)

```python
def _get_user_task_or_404(task_id):
    return Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
```

### Practical behavior now

- A user can update/delete only rows where `Task.user_id` matches their `current_user.id`.
- Trying another user's `task_id` no longer exposes that object and returns `404`.
- This helper is used by both `edit_task()` and `delete_task()`.

---

## 2) CSRF Protection

### What changed in backend

`app/__init__.py` now initializes global CSRF checking:

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
...
csrf.init_app(app)
```

### What changed in routes/templates

All state-changing forms include:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

Implemented in:
- `app/templates/auth/login.html`
- `app/templates/auth/register.html`
- `app/templates/tasks/index.html` (create + delete forms)
- `app/templates/tasks/edit_task.html`
- `app/templates/base.html` (logout form)

`/logout` in `app/routes/auth.py` was also changed to:

```python
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
```

### Before vs after

- **Before:** cross-site pages could submit POSTs to app actions using victim cookies.
- **After:** missing/invalid token causes request rejection by Flask-WTF.

### Practical behavior now

- CSRF attacks on task create/edit/delete and logout are blocked unless a valid token from this app is present.
- `SESSION_COOKIE_SAMESITE = "Lax"` in `config.py` adds extra browser-side CSRF resistance.

---

## 3) Clickjacking Protection

### What changed

`app/__init__.py` adds response headers for every request:

```python
@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    return response
```

### Before vs after

- **Before:** pages could be embedded inside attacker-controlled iframes.
- **After:** modern and legacy browsers block framing of the app.

### Practical behavior now

- UI redress attacks (hidden frame + fake clicks) are blocked for task and auth pages.

---

## Quick Verification (What to test)

1. Log in as user A and try editing/deleting user B's task ID directly -> should return `404`.
2. Remove `csrf_token` from a POST request (e.g., delete form) -> request should fail.
3. Check response headers in browser/network tab -> must include:
   - `X-Frame-Options: DENY`
   - `Content-Security-Policy: frame-ancestors 'none'`

## Remaining hardening items

- Disable debug mode in production launch path (`run.py` currently has `debug=True`).
- Add login rate limiting for `/login`.
- Add audit logs for task CRUD and auth events.

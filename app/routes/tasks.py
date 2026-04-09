from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Task

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/", methods=["GET"])
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template("tasks/index.html", tasks=tasks)


@tasks_bp.route("/tasks/create", methods=["POST"])
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("tasks.index"))

    task = Task(title=title, owner=current_user)
    db.session.add(task)
    db.session.commit()
    flash("Task created.", "success")
    return redirect(url_for("tasks.index"))


def _get_user_task_or_404(task_id):
    # Security fix (IDOR): scope task lookup to the logged-in user so one user
    # cannot access another user's task by changing the task id in the URL.
    return Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()


@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = _get_user_task_or_404(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        completed = request.form.get("completed") == "on"

        if not title:
            flash("Task title is required.", "error")
            return render_template("tasks/edit_task.html", task=task)

        task.title = title
        task.completed = completed
        db.session.commit()
        flash("Task updated.", "success")
        return redirect(url_for("tasks.index"))

    return render_template("tasks/edit_task.html", task=task)


@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = _get_user_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("tasks.index"))

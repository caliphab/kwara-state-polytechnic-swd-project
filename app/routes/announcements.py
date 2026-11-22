from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from app.forms import AnnouncementForm
from app.models import Announcement, UserRole


announcements_bp = Blueprint("announcements", __name__)

ALLOWED_POSTERS = {UserRole.ADMIN, UserRole.CLASSREP}


@announcements_bp.route("/publish-announcement", methods=["POST"])
@login_required
def create_announcements():
    form = AnnouncementForm()

    if form.validate_on_submit():
        if current_user.role not in ALLOWED_POSTERS:
            flash("Only Class Reps and Administrators can post announcements.", "danger")

            return redirect(url_for("page.announcements"))

        new_notice = Announcement(
            title=form.title.data.strip(),
            category=form.category.data,
            body=form.body.data.strip(),
            is_pinned=form.is_pinned.data,
            author_id=current_user.id,
        )

        db.session.add(new_notice)
        db.session.commit()

        flash("Announcement published successfully!", "success")

        return redirect(url_for("page.announcements"))
    
    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "danger")

    return redirect(url_for("page.announcements"))




@announcements_bp.route("/delete/<int:notice_id>", methods=["POST"])
@login_required
def delete_announcement(notice_id):
    notice = db.session.get(Announcement, notice_id)

    if not notice:
        flash("Announcement not found.", "danger")

        return redirect(url_for("page.announcements"))

    is_admin = current_user.role == UserRole.ADMIN
    is_owner = notice.author_id == current_user.id and current_user.role == UserRole.CLASSREP

    if not (is_admin or is_owner):
        flash("You do not have permission to delete this announcement.", "danger")

        return redirect(url_for("page.announcements"))

    db.session.delete(notice)
    db.session.commit()

    flash("Announcement deleted.", "info")

    return redirect(url_for("page.announcements"))

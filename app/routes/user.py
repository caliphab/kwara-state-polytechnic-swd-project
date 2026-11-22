from flask import Blueprint, current_app, flash, redirect, url_for, request
from flask_login import current_user, login_required
from extensions import db
from app.forms import EditProfileForm
from app.models import UserRole, User
from werkzeug.utils import secure_filename
import secrets, os


user_bp = Blueprint("user", __name__)

VALID_LEVELS = {"ND I", "ND II", "HND I", "HND II"}


def save_profile_photo(form_photo):
    """Generates a unique filename and saves the uploaded image to static/assets."""
    random_hex = secrets.token_hex(8)
    safe_name = secure_filename(form_photo.filename)
    _, file_ext = os.path.splitext(safe_name)
    new_filename = f"{random_hex}{file_ext.lower()}"

    upload_folder = os.path.join(current_app.root_path, "static", "assets")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, new_filename)

    form_photo.save(file_path)
    return new_filename


@user_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        if form.photo.data:
            old_photo = current_user.photo
            new_photo = save_profile_photo(form.photo.data)

            current_user.photo = new_photo

            if old_photo and old_photo != "photo.png":
                old_photo_path = os.path.join(current_app.root_path, "static", "assets", old_photo)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

        current_user.email = form.email.data.strip().lower()
        current_user.mobile = form.mobile.data.strip() if form.mobile.data else None

        db.session.commit()

        flash("Your profile has been updated successfully!", "success")

        return redirect(url_for("page.dashboard"))

    return redirect(url_for("page.profile"))

@user_bp.route("/update/role/<int:user_id>", methods=["POST"])
@login_required
def update_user_role(user_id):
    user = db.session.get(User, user_id)

    if not user:
        flash("User account not found.", "danger")
        return redirect(url_for("page.dashboard"))

    if user.id == current_user.id:
        flash("You cannot modify your own administrator role.", "warning")

        return redirect(url_for("page.dashboard"))

    new_role = request.form.get("role", "").strip().lower()
    valid_roles = {role.value for role in UserRole}

    if new_role not in valid_roles:
        flash("Invalid role selected.", "danger")

        return redirect(url_for("page.dashboard"))

    if user.role.value == new_role:
        flash(f"{user.surname} ({user.matric}) is already assigned as {new_role.capitalize()}.", "info")

        return redirect(url_for("page.dashboard"))

    user.role = UserRole(new_role)
    db.session.commit()

    flash(f"Updated {user.surname} ({user.matric}) to {new_role.capitalize()}.", "success")

    return redirect(url_for("page.dashboard"))

VALID_LEVELS = {"ND I", "ND II", "HND I", "HND II"}


@user_bp.route("/update/level/<int:user_id>", methods=["POST"])
@login_required
def update_user_level(user_id):
    user = db.session.get(User, user_id)

    if not user:
        flash("User account not found.", "danger")

        return redirect(url_for("page.dashboard"))

    new_level = request.form.get("level", "").strip().upper()

    if new_level not in VALID_LEVELS:
        flash("Invalid academic level selected.", "danger")

        return redirect(url_for("page.dashboard"))

    if user.level == new_level:
        flash(f"{user.surname} ({user.matric}) is already in {new_level}.", "info")

        return redirect(url_for("page.dashboard"))

    user.level = new_level
    db.session.commit()

    flash(f"Updated {user.surname} ({user.matric}) level to {new_level}.", "success")
    
    return redirect(url_for("page.dashboard"))

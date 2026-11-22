from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from extensions import db
from app.forms import SigninForm, SignupForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("page_bp.index"))

    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        matric = form.matric.data.strip().upper()

        existing_user = User.query.filter(
            (User.email == email) | (User.matric == matric)
        ).first()

        if existing_user:
            flash("An account with this Email or Matric Number already exists.", "danger")
            return render_template("index.html", signup_form=form, signin_form=SigninForm())

        new_user = User(
            email=email,
            matric=matric,
            level=form.level.data,
            surname=form.surname.data.strip().title(),
            middlename=form.middlename.data.strip().title() if form.middlename.data else None,
            lastname=form.lastname.data.strip().title(),
            mobile=form.mobile.data.strip() if form.mobile.data else None,
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please sign in with your Matric Number.", "success")

    if request.method == "POST":
        flash("Please correct the highlighted errors in the registration form.", "danger")

    return redirect(url_for("page.home"))


@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("page.dashboard"))

    form = SigninForm()

    if form.validate_on_submit():
        matric = form.matric.data.strip().upper()
        user = User.query.filter_by(matric=matric).first()

        if user and user.check_password(form.password.data):
            user.status = True
            db.session.commit()

            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.matric}", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("page.dashboard"))

        flash("Invalid Matric Number or Password. Please try again.", "danger")

    return redirect(url_for("page.home"))


@auth_bp.route("/logout")
@login_required
def signout():
    current_user.status = False
    db.session.commit()

    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("page.home"))

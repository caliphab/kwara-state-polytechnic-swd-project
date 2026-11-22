from flask import Blueprint, render_template, redirect, url_for, request
from app.forms import SignupForm, SigninForm, EditProfileForm, AnnouncementForm, CourseForm
from app.models import UserRole, User, Announcement, Course, CourseRegistration
from flask_login import login_required, current_user


page_bp = Blueprint("page", __name__)


@page_bp.app_context_processor
def inject_auth_forms():
    return {
        "signup_form": SignupForm(),
        "signin_form": SigninForm()
    }


@page_bp.route('/')
def home():
    return render_template("index.html")


@page_bp.route("/about")
def about():
    return render_template("about.html")


@page_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == UserRole.ADMIN:
        role_filter = request.args.get("role", "all").lower()
        search_query = request.args.get("q", "").strip()

        query = User.query

        if role_filter in {"student", "classrep", "admin"}:
            query = query.filter_by(role=UserRole(role_filter))

        if search_query:
            pattern = f"%{search_query}%"
            query = query.filter(
                (User.matric.ilike(pattern))
                | (User.surname.ilike(pattern))
                | (User.lastname.ilike(pattern))
                | (User.email.ilike(pattern))
            )

        users = query.order_by(User.id.desc()).all()

        stats = {
            "total_users": User.query.count(),
            "students": User.query.filter_by(role=UserRole.STUDENT).count(),
            "classreps": User.query.filter_by(role=UserRole.CLASSREP).count(),
            "online_now": User.query.filter_by(status=True).count(),
        }

        return render_template(
            "admin-dashboard.html",
            users=users,
            stats=stats,
            role_filter=role_filter,
            search_query=search_query,
            roles=UserRole,
        )

    user_registrations = CourseRegistration.query.filter_by(
        user_id=current_user.id,
        session="2026/2027",
    ).all()

    registered_courses = [reg.course for reg in user_registrations]
    total_units = sum(course.units for course in registered_courses)

    latest_announcements = (
        Announcement.query.order_by(
            Announcement.is_pinned.desc(),
            Announcement.created_at.desc(),
        )
        .limit(5)
        .all()
    )

    return render_template(
        "student-dashboard.html",
        registered_courses=registered_courses,
        total_units=total_units,
        announcements=latest_announcements,
    )

@page_bp.route('/profile')
@login_required
def profile():
    form = EditProfileForm()

    form.email.data = current_user.email
    form.mobile.data = current_user.mobile

    return render_template("profile.html", form=form)

@page_bp.route('/announcements')
@login_required
def announcements():
    form = AnnouncementForm()

    category_filter = request.args.get("category", "All")

    query = Announcement.query
        
    if category_filter != "All":
        query = query.filter_by(category=category_filter)

    all_notices = query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()

    can_post = current_user.role in {UserRole.ADMIN, UserRole.CLASSREP}

    return render_template("announcements.html", announcements=all_notices, form=form, can_post=can_post, category_filter=category_filter)

@page_bp.route("/courses")
@login_required
def courses():
    form = CourseForm()

    semester_filter = request.args.get("semester", "First")
    is_admin = current_user.role == UserRole.ADMIN

    query = Course.query.filter_by(is_active=True, semester=semester_filter)

    if is_admin:
        level_filter = request.args.get("level", "All")

        if level_filter != "All":
            query = query.filter_by(level=level_filter)
    else:
        level_filter = current_user.level
        query = query.filter_by(level=current_user.level)

    available_courses = query.order_by(Course.code.asc()).all()

    user_registrations = (
        CourseRegistration.query.filter_by(user_id=current_user.id, session="2026/2027")
        .join(Course)
        .filter(Course.semester == semester_filter)
        .all()
    )

    registered_course_ids = {reg.course_id for reg in user_registrations}
    total_units = sum(reg.course.units for reg in user_registrations)

    return render_template("courses.html", form=form, available_courses=available_courses, user_registrations=user_registrations, registered_course_ids=registered_course_ids, total_units=total_units, max_units=24, level_filter=level_filter, semester_filter=semester_filter, can_manage=is_admin,)


from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required
from extensions import db
from app.forms import CourseForm
from app.models import Course, CourseRegistration, UserRole

courses_bp = Blueprint("courses", __name__)

ALLOWED_MANAGERS = {UserRole.ADMIN}
MAX_SEMESTER_UNITS = 24
CURRENT_SESSION = "2026/2027"


@courses_bp.route("/create", methods=["POST"])
@login_required
def create_course():

    if current_user.role not in ALLOWED_MANAGERS:
        flash("Only Administrators can add courses.", "danger")

        return redirect(url_for("page.courses"))

    form = CourseForm()

    if form.validate_on_submit():

        new_course = Course(
            code=form.code.data.strip().upper(),
            title=form.title.data.strip().title(),
            units=form.units.data,
            semester=form.semester.data,
            level=form.level.data,
            lecturer=form.lecturer.data.strip().title() if form.lecturer.data else None,
        )

        db.session.add(new_course)
        db.session.commit()

        flash(f"{new_course.code} added to the course catalog.", "success")

    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "danger")

    return redirect(url_for("page.courses"))


@courses_bp.route("/register/<int:course_id>", methods=["POST"])
@login_required
def register_course(course_id):
    course = db.session.get(Course, course_id)

    if not course or not course.is_active:
        flash("Selected course is not available.", "danger")

        return redirect(url_for("page.courses"))

    if current_user.role != UserRole.ADMIN and course.level != current_user.level:
        flash(f"You can only register courses designated for {current_user.level}.", "danger")
        
        return redirect(url_for("page.courses", semester=course.semester))

    existing = CourseRegistration.query.filter_by(
        user_id=current_user.id,
        course_id=course.id,
        session=CURRENT_SESSION,
    ).first()

    if existing:
        flash(f"You have already registered {course.code}.", "warning")

        return redirect(url_for("page.courses", semester=course.semester))

    current_regs = (
        CourseRegistration.query.filter_by(user_id=current_user.id, session=CURRENT_SESSION)
        .join(Course)
        .filter(Course.semester == course.semester)
        .all()
    )

    current_units = sum(r.course.units for r in current_regs)

    if current_units + course.units > MAX_SEMESTER_UNITS:
        flash(
            f"Cannot register {course.code} ({course.units} units). "
            f"Maximum limit of {MAX_SEMESTER_UNITS} units per semester exceeded.",
            "danger",
        )

        return redirect(url_for("page.courses", semester=course.semester))

    registration = CourseRegistration(
        user_id=current_user.id,
        course_id=course.id,
        session=CURRENT_SESSION,
        status="Approved",
    )

    db.session.add(registration)
    db.session.commit()

    flash(f"Successfully registered {course.code} - {course.title}.", "success")

    return redirect(url_for("page.courses", semester=course.semester))


@courses_bp.route("/drop/registrations/<int:reg_id>", methods=["POST"])
@login_required
def drop_course(reg_id):
    reg = db.session.get(CourseRegistration, reg_id)

    if not reg or reg.user_id != current_user.id:
        flash("Course registration record not found.", "danger")

        return redirect(url_for("page.courses"))

    semester = reg.course.semester
    code = reg.course.code

    db.session.delete(reg)
    db.session.commit()

    flash(f"Dropped {code} from your registered courses.", "info")

    return redirect(url_for("page.courses", semester=semester))


@courses_bp.route("/delete/<int:course_id>", methods=["POST"])
@login_required
def delete_course(course_id):

    if current_user.role not in ALLOWED_MANAGERS:
        flash("You do not have permission to delete courses.", "danger")

        return redirect(url_for("page.courses"))

    course = db.session.get(Course, course_id)

    if course:
        code = course.code

        db.session.delete(course)
        db.session.commit()

        flash(f"Course {code} removed from catalog.", "info")

    return redirect(url_for("page.courses"))

from extensions import db, user_mixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from datetime import datetime, timezone


class UserRole(str, Enum):
    STUDENT = 'student'
    CLASSREP = 'classrep'
    ADMIN = 'admin'

class User(user_mixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    matric = db.Column(db.String(55), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    middlename = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(255), nullable=True, default="photo.png")
    mobile = db.Column(db.String(25))
    status = db.Column(db.Boolean, default=False)
    role = db.Column(db.Enum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.STUDENT)
    level = db.Column(db.String(20), nullable=False, default="ND I")

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.id}>"

class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="General")
    body = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", backref=db.backref("announcements", lazy=True))

    def __repr__(self):
        return f"<Announcement {self.id}: {self.title}>"

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    units = db.Column(db.Integer, nullable=False, default=2)
    semester = db.Column(db.String(20), nullable=False, default="First")
    level = db.Column(db.String(20), nullable=False, default="ND I")
    lecturer = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    registrations = db.relationship("CourseRegistration", back_populates="course", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Course {self.code}: {self.title}>"

class CourseRegistration(db.Model):
    __tablename__ = "course_registrations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    session = db.Column(db.String(20), nullable=False, default="2026/2027")
    status = db.Column(db.String(20), nullable=False, default="Approved")
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint("user_id", "course_id", "session", name="uq_user_course_session"),)

    student = db.relationship("User", backref=db.backref("course_registrations", lazy=True))
    course = db.relationship("Course", back_populates="registrations")

    def __repr__(self):
        return f"<Registration User={self.user_id} Course={self.course_id}>"


class AcademicCalendarEvent(db.Model):
    __tablename__ = "academic_calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(60), nullable=False, default="Academic")
    session = db.Column(db.String(20), nullable=False, index=True)
    semester = db.Column(db.String(20), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    author = db.relationship("User", backref="calendar_events")

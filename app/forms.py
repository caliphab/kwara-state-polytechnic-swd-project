from extensions import flask_form
from wtforms import StringField, TelField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, NumberRange
from flask_wtf.file import FileAllowed, FileField


class SignupForm(flask_form):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(max=255),
        ],
    )
    
    mobile = TelField(
        "Mobile Number",
        validators=[
            Optional(),
            Length(max=25),
        ],
    )

    matric = StringField(
        "Matric No.",
        validators=[
            DataRequired(message="Matric number is required."),
            Length(max=55),
        ],
    )

    level = SelectField(
        "Academic Level", 
        choices=[
            ("ND I", "ND I"), 
            ("ND II", "ND II"), 
            ("HND I", "HND I"), 
            ("HND II", "HND II")
        ], 
        validators=[
            DataRequired()
        ]
    )

    surname = StringField(
        "Surname",
        validators=[
            DataRequired(message="Surname is required."),
            Length(max=50),
        ],
    )

    middlename = StringField(
        "Middle Name",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    lastname = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Last name is required."),
            Length(max=50),
        ],
    )

    password = PasswordField(
        "Create Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be between 8 and 128 characters."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords do not match."),
        ],
    )

    submit = SubmitField("Create Account")

class SigninForm(flask_form):
    matric = StringField(
        "Matric Number",
        validators=[
            DataRequired(message="Matric number is required."),
            Length(max=55),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
        ],
    )

    remember = BooleanField("Remember Me")

    submit = SubmitField("Sign In")

class EditProfileForm(flask_form):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(max=255),
        ],
    )
    mobile = TelField(
        "Mobile Number",
        validators=[
            Optional(),
            Length(max=25),
        ],
    )
    photo = FileField(
        "Profile Photo",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Only JPG, PNG, and WEBP images are allowed."),
        ],
    )
    submit = SubmitField("Save Changes")

class AnnouncementForm(flask_form):
    title = StringField(
        "Announcement Title",
        validators=[
            DataRequired(message="Title is required."),
            Length(max=150, message="Title cannot exceed 150 characters."),
        ],
    )
    category = SelectField(
        "Category",
        choices=[
            ("General", "General Notice"),
            ("Lecture", "Lecture Update"),
            ("Timetable", "Timetable Adjustment"),
            ("Exam", "Examination Notice"),
            ("Registration", "Course Registration"),
        ],
        validators=[DataRequired()],
    )
    body = TextAreaField(
        "Announcement Details",
        validators=[
            DataRequired(message="Please enter the announcement content."),
            Length(min=10, message="Announcement must be at least 10 characters."),
        ],
    )
    is_pinned = BooleanField("Pin to top of announcements")
    submit = SubmitField("Publish Now")

class CourseForm(flask_form):
    code = StringField(
        "Course Code",
        validators=[
            DataRequired(message="Course code is required."),
            Length(max=20),
        ],
    )
    title = StringField(
        "Course Title",
        validators=[
            DataRequired(message="Course title is required."),
            Length(max=150),
        ],
    )
    units = IntegerField(
        "Credit Units",
        validators=[
            DataRequired(message="Credit units are required."),
            NumberRange(min=1, max=6, message="Units must be between 1 and 6."),
        ],
    )
    semester = SelectField(
        "Semester",
        choices=[("First", "First Semester"), ("Second", "Second Semester")],
        validators=[DataRequired()],
    )
    level = SelectField(
        "Level",
        choices=[
            ("ND I", "ND I"),
            ("ND II", "ND II"),
            ("HND I", "HND I"),
            ("HND II", "HND II"),
        ],
        validators=[DataRequired()],
    )
    lecturer = StringField(
        "Course Lecturer",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )
    submit = SubmitField("Add Course")

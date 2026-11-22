from flask import Flask, redirect, url_for
from config import config_env
from extensions import db, migrate, login_manager, csrf



def create_app(env):
    app = Flask(__name__)
    app.config.from_object(config_env[env.lower()])

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.signin"
    login_manager.login_message = "Please signin to access this page."
    login_manager.login_message_category = "warning"

    from app.routes.page import page_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.announcements import announcements_bp
    from app.routes.courses import courses_bp
    from app.routes.calendar import calendar_bp

    app.register_blueprint(page_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/my-account")
    app.register_blueprint(announcements_bp, url_prefix="/announcements")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(calendar_bp)

    @app.route('/')
    def index():
        return redirect(url_for("page.home"))

    from app.models import User

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
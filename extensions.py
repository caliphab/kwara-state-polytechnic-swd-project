from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_login import UserMixin, LoginManager
from flask_wtf.csrf import CSRFProtect


flask_form = FlaskForm
user_mixin = UserMixin
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
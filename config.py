import os


app_env = os.getenv("APP_ENV", "development")


class Configurations:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///devlopment_database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

class Development(Configurations):
    DEBUG = True

class Production(Configurations):
    DEBUG = False


config_env = {
    "development": Development(),
    "production": Production()
}
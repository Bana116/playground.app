import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-later")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///creativeplay.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # EMAIL SETTINGS
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
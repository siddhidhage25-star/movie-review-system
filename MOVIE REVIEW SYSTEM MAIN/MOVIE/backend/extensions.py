"""
Flask extensions initialization module.
This module creates the db and login_manager instances to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions (but don't bind to app yet)
db = SQLAlchemy()
login_manager = LoginManager()

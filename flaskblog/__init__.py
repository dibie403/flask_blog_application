import os
import json
from flask import Flask
from config import Config, initialize_firebase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# Initialize Flask app with static and template folders explicitly specified
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# Load configurations
app.config.from_object(Config)

# Initialize Firebase
initialize_firebase()

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configure email server
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("DB_USER")  # Email username from env
app.config['MAIL_PASSWORD'] = os.environ.get("DBPASSWORD")  # Email password from env
mail = Mail(app)

# Import routes
from flaskblog import routes


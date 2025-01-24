import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, storage

class Config:
    # Load environment variables
    load_dotenv()

    # Application secret key
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def initialize_firebase():
    """Initializes Firebase only if it hasn't been initialized yet."""
    if not firebase_admin._apps:  # Check if Firebase is already initialized
        firebase_credentials = os.getenv("Firebase_Credentials")
        if firebase_credentials:
            cred = credentials.Certificate(json.loads(firebase_credentials))
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'face-check-attendance.appspot.com'  # Replace with your actual bucket name
            })
        else:
            raise ValueError("FIREBASE_CREDENTIALS environment variable is not set.")




		



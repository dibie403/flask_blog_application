import os
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

    # Firebase setup
    firebase_credentials_path = os.getenv("Firebase_Credentials")

    if firebase_credentials_path:
        try:
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'face-check-attendance.appspot.com'  # Replace with your bucket name
            })
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")
    else:
        print("Firebase credentials path is missing.")


		



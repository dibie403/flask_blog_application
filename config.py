import os 
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, storage

class Config:

		SECRET_KEY=(os.environ.get('SECRET_KEY'))
		#SQLALCHEMY_DATABASE_URI =(os.environ.get('SQLALCHEMY_DATABASE_URI'))
		SQLALCHEMY_DATABASE_URI =(os.environ.get('SQLALCHEMY_DATABASE_URI'))
		SQLALCHEMY_TRACK_MODIFICATIONS = False
		load_dotenv()
		firebase_credentials_path = os.getenv("Firebase_Credentials")

		if firebase_credentials_path:
		    # Initialize Firebase Admin SDK
		    cred = credentials.Certificate(firebase_credentials_path)
		    firebase_admin.initialize_app(cred, {
		        'storageBucket': 'face-check-attendance.appspot.com'  # Your Firebase Storage bucket name
		    })
		else:
		    print("Firebase credentials path is missing.")

		



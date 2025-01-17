import os 


class Config:

		SECRET_KEY=(os.environ.get('SECRET_KEY'))
		#SECRET_KEY='90d29299e6c6ffddeba3ac23230e125c'
		SQLALCHEMY_DATABASE_URI = (os.environ.get('SQLALCHEMY_DATABASE_URI'))
		SQLALCHEMY_TRACK_MODIFICATIONS = False

import os 


class Config:

		STATIC_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
        TEMPLATES_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

		SECRET_KEY=(os.environ.get('SECRET_KEY'))
		#SECRET_KEY='90d29299e6c6ffddeba3ac23230e125c'
		SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
		SQLALCHEMY_TRACK_MODIFICATIONS = False
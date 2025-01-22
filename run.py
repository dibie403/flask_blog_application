from flaskblog import app
import os



if __name__ == '__main__':
    app.run(debug=True)


  


SQLALCHEMY_DATABASE_URI = (os.environ.get('SQLALCHEMY_DATABASE_URI'))
print(SQLALCHEMY_DATABASE_URI)













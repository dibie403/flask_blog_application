from flaskblog import app
import os



if __name__ == '__main__':
    app.run(debug=True)







SECRET_KEY=(os.environ.get('SECRET_KEY'))
print(SECRET_KEY)
from flaskblog import app
import os



if __name__ == '__main__':
    app.run(debug=True)


print(os.environ.get("DB_"))
print(os.environ.get("DB_PASSWORD"))

from flaskblog.models import Post

with app.app_context():
    users=Post.query.all()
    print(users)


    
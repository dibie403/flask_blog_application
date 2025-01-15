from flaskblog import app
import os



if __name__ == '__main__':
    app.run(debug=True)


print(os.environ.get("DB_"))
print(os.environ.get("DB_PASSWORD"))

from flaskblog import app,db,bcrypt,mail
from flaskblog.models import Feedback

with app.app_context():
    users=Feedback.query.all()
    print(users)



    
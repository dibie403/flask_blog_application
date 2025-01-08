from flaskblog import app
import os



if __name__ == '__main__':
    app.run(debug=True)


print(os.environ.get("DB_"))
print(os.environ.get("DB_PASSWORD"))

from flaskblog.models import Notification

with app.app_context():
    users=Notification.query.all()
    print(users)


    
from datetime import datetime
from flaskblog import db,login_manager,app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Love(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    # Define relationships
    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    post = db.relationship('Post', backref=db.backref('likes', lazy=True))

    def __repr__(self):
        return f"Like('{self.user_id}', '{self.post_id}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    image_file = db.Column(db.String(255), nullable=False, default='https://firebasestorage.googleapis.com/v0/b/face-check-attendance.appspot.com/o/profile_pix%2Fdefault.jpg?alt=media&token=e4bdbe08-92f1-4fc7-8e60-086e98e63a66')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False,default=False)
    Biography= db.Column(db.Text, nullable=False,default='Add A Brief Description About Yourself')
    

    
    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            # Pass the expiration time in seconds (e.g., 1800 for 30 minutes)
            data = s.loads(token, max_age=1800)
            user_id = data['user_id']
        except SignatureExpired:
            # Handle expired token
            return None
        except BadSignature:
            # Handle invalid token
            return None

        # Assuming User.query.get retrieves a user by their ID
        return User.query.get(user_id)

    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}','{self.is_admin}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False,default=False)
    image = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    

    def __repr__(self):
        return f"Post('{self.title}', '{self.image}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))

    def __repr__(self):
        return f"Comment('{self.content}', '{self.user_id}', '{self.post_id}')"


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    # Foreign keys
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    comment = db.relationship('Comment', backref=db.backref('replies', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('replies', lazy=True))

    def __repr__(self):
        return f"Reply('{self.content[:20]}', '{self.created_at}')"


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    initiator= db.Column(db.Integer, nullable=False,default=None)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)



    # Define relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    post = db.relationship('Post', backref=db.backref('notifications', lazy=True))
    comment = db.relationship('Comment', backref=db.backref('notifications', lazy=True))


    def __repr__(self):
         return f"Notification('{self.content}','{self.user_id}')"

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref=db.backref('feedbacks', lazy=True))


    def __repr__(self):
         return f"Feedback('{self.content}', '{self.user_id}')"

    
    
    

    


   

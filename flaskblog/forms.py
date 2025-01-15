from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flaskblog.models import User



class RegistrationForm(FlaskForm):
	username=StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
	email=StringField('Email',validators=[DataRequired(),Email()])
	password=PasswordField('Password', validators=[DataRequired()])
	confirm_password=PasswordField('Comfirm Password',validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField('Sign up')

	#function to handle wether the user alredy exist in the database.
	def validate_username(self,username):
		user=User.query.filter_by(username=username.data).first()

		if user:
			raise ValidationError('Username already taken,Please pick a unique username')

	def validate_email(self,email):
		user=User.query.filter_by(email=email.data).first()

		if user:
			raise ValidationError('Email already Exist,Please use a unique Email')

class LoginForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	password=PasswordField('Password', validators=[DataRequired()])
	remember=BooleanField('Remember me')
	submit=SubmitField('Log in')



class AccountUpdateForm(FlaskForm):
	username=StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
	email=StringField('Email',validators=[DataRequired(),Email()])
	Biography=TextAreaField('Biography',validators=[DataRequired()])
	picture=FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
	
	submit=SubmitField('Update')

	#function to ensure that there is a change to be updated.
	def validate_username(self,username):
		if username.data != current_user.username:
			user=User.query.filter_by(username=username.data).first()

			if user:
				raise ValidationError('Username already taken,Please pick a unique username')

	def validate_email(self,email):
		if email.data != current_user.email:
			user=User.query.filter_by(email=email.data).first()

			if user:
				raise ValidationError('Email already Exist,Please use a unique Email')


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    Content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Add Post Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Post')

	


class UpdatePostForm(FlaskForm):
	title=StringField('Title', validators=[DataRequired()])
	Content=TextAreaField('Content',validators=[DataRequired()])
	
	submit=SubmitField('Update')

class RequestResetTokenForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	submit=SubmitField('Request Reset')

class ResetPasswordForm(FlaskForm):
	password=PasswordField('Password', validators=[DataRequired()])
	confirm_password=PasswordField('Comfirm Password',validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField('Reset')

class FeedbackForm(FlaskForm):
    Content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')



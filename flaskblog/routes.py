import secrets
import os
import tempfile
import re
import random
from flask import jsonify
from flask import send_file,abort
from sqlalchemy import func
from PIL import Image
from flask import render_template,url_for, flash, redirect,request
from flaskblog import app,db,bcrypt,mail
from flaskblog.forms import RegistrationForm,LoginForm,AccountUpdateForm,CreatePostForm,UpdatePostForm,RequestResetTokenForm,ResetPasswordForm,FeedbackForm
from flaskblog.models import User,Post,Comment,Reply,Love,Notification,Feedback
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
from dotenv import load_dotenv
from io import BytesIO
import mimetypes
from firebase_admin import storage



# Load environment variables from .env file
#load_dotenv()

# Fetch the Firebase credentials path from the environment variable



@app.route("/")
@app.route("/home")
def home():

    pages=request.args.get('page',1,type=int)
    post = Post.query.order_by(Post.date.desc()).paginate(per_page=10)
    user=User.query.all()
    add_admin()

    limit = 10  # Number of users to display
    random_users = random.sample(user, min(len(user), limit))  # Randomly pick users, ensuring no more than `limit`
    image_file = None
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
   
    return render_template('home.html', post=post, title='Home',image_file=image_file,user=random_users)



@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/just",methods=['POST','GET'])
def just():
    form=RegistrationForm()
    if form.validate_on_submit():
        flash(f"You have been register successfully {form.username.data}!", 'success')
        return redirect(url_for('home'))
    return render_template('just.html',title='register',form=form)
    


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f"You have been registered successfully {form.username.data}! Please proceed to login 😊", 'success')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Error during registration: {e}")
            flash("An error occurred while processing your registration. Please try again.", "danger")
    return render_template('register.html', title='register', form=form)


@app.route("/congratulation",methods=['POST','GET'])
def congratulation():
    return render_template('congratulations.html',title='congratulation')

@app.route("/login",methods=['POST','GET'])
def login():
    form=LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
            #flash(f"Welcome {form.email.data}!, Check what's New on the Site😊", 'success')
        else:
            flash(f"Unsuccessful login,Incorrect credentials", 'danger')

    return render_template('login.html',title='login',form=form)    

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


from flask import request

@app.route("/Account")
@login_required
def Account():
    # Get the profile image file path
    print(f"Image URL: {current_user.image_file}")

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    # Fetch the page number from the query parameters (default is 1)
    page = request.args.get('page', 1, type=int)
    
    # Query the posts related to the current user, ordered by date descending
    post = Post.query.filter_by(user_id=current_user.id).order_by(Post.date.desc()).paginate(page=page, per_page=10)
    
    return render_template('Account.html', title='Account', post=post, image_file=image_file)

def save_picture_for_local_profile_pix(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.split(form_picture.filename)
    picture_fn=random_hex +f_ext
    picture_path=os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size=(250,250)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture_for_local_post_pix(form_picture):
    # Generate a random filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # Get the file extension
    picture_fn = random_hex + f_ext  # Generate a new filename with a random hex string and original extension

    # Define the path where the image will be saved (static/post_images)
    picture_path = os.path.join(app.root_path, 'static/post_images', picture_fn)

    # Ensure the directory exists
    os.makedirs(os.path.join(app.root_path, 'static/post_images'), exist_ok=True)

    # Resize and save the picture
    output_size = (250, 250)  # Resize the image to a thumbnail size (adjust as needed)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)  # Save the image to the path

    # Return the filename (so you can store this in the database)
    return picture_fn



from firebase_admin import storage
import os
import secrets
from PIL import Image
from io import BytesIO

def save_picture(form_picture):
    # Generate a random filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # Open the image and resize to a thumbnail (optional)
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # If the image is in RGBA (transparency), we need to convert it to RGB for JPEG
    if i.mode == 'RGBA':
        # Convert RGBA to RGB
        i = i.convert('RGB')

    # Save the image to a BytesIO object
    img_byte_arr = BytesIO()

    # If it's a PNG, save it as PNG, otherwise save it as JPEG
    if f_ext.lower() == '.png':
        i.save(img_byte_arr, format='PNG')
    else:
        i.save(img_byte_arr, format='JPEG')

    # Reset the stream to the beginning
    img_byte_arr.seek(0)

    # Upload the image to Firebase Storage
    bucket = storage.bucket()  # This gets the default Firebase Storage bucket
    blob = bucket.blob('profile_pix/' + picture_fn)  # Save the image under 'profile_pix' folder

    # Upload the image from the BytesIO object
    blob.upload_from_file(img_byte_arr, content_type=f'image/{f_ext[1:]}')

    # Optionally, make the image public by adding metadata
    blob.make_public()

    # Return the public URL of the uploaded image
    return blob.public_url


def save_picture1(form_picture):
    try:
        # Generate a random filename
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext

        # Open the image and resize to a thumbnail (optional)
        output_size = (250, 250)
        i = Image.open(form_picture)
        i.thumbnail(output_size)

        # If the image is in RGBA (transparency), convert to RGB for JPEG
        if i.mode == 'RGBA':
            i = i.convert('RGB')

        # Save the image to a BytesIO object
        img_byte_arr = BytesIO()

        # Determine the correct MIME type
        mime_type, _ = mimetypes.guess_type(form_picture.filename)
        if mime_type is None:
            mime_type = 'image/jpeg'  # Default fallback to JPEG

        # Save image in appropriate format
        if f_ext.lower() == '.png':
            i.save(img_byte_arr, format='PNG')
        else:
            i.save(img_byte_arr, format='JPEG')

        # Reset the stream to the beginning
        img_byte_arr.seek(0)

        # Upload the image to Firebase Storage
        bucket = storage.bucket()  # This gets the default Firebase Storage bucket
        blob = bucket.blob(f'images/{picture_fn}')  # Save the image under 'images' folder

        # Upload the image from the BytesIO object
        blob.upload_from_file(img_byte_arr, content_type=mime_type)

        # Optionally, make the image public by adding metadata
        blob.make_public()

        # Return the public URL of the uploaded image
        return blob.public_url

    except Exception as e:
        print(f"Error in save_picture1: {e}")
        raise ValueError("An error occurred while saving the picture.")


@app.route("/Account/edit", methods=['POST', 'GET'])
@login_required
def edit():
    # Set the default image URL
    image_file = current_user.image_file  # This should hold the Firebase URL now

    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            # Save the image to Firebase Storage and get the public URL
            picture_file = save_picture(form.picture.data)  # Firebase URL returned here
            current_user.image_file = picture_file  # Save the Firebase URL to the database

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.Biography = form.Biography.data
        db.session.commit()
        flash("Profile updated successfully", 'success')
        return redirect(url_for('Account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.Biography.data = current_user.Biography

    return render_template('edit.html', title='Edit', image_file=image_file, form=form)


@app.route("/Account1/edit1", methods=['POST', 'GET'])
@login_required
def edit1():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)

            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.Biography = form.Biography.data
        db.session.commit()
        flash("Profile updated successfully", 'success')
        return redirect(url_for('Account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.Biography.data= current_user.Biography
    return render_template('edit.html', title='Edit', image_file=image_file, form=form)





def generate_slug(title):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    return slug



@app.route("/Account/post1/new1", methods=['POST', 'GET'])
@login_required
def new_post1():
    form = CreatePostForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    image = None  # Set image to None initially
    
    if form.validate_on_submit():
        # Handle invalid file types
        if form.picture.errors:
            for error in form.picture.errors:
                flash(f"File upload error: {error}", "danger")
            return redirect(url_for('new_post'))
        
        # Save the image if provided
        if form.picture.data:
            try:
                # Save image temporarily or upload to cloud storage
                picture_file = save_picture1(form.picture.data)  # Saves image locally to static/post_images
                image = picture_file  # Update image reference to the saved image
                print(f"Image saved: {image}")  # Debug log
            except Exception as e:
                print(f"Error saving image: {e}")
                flash("Error saving the image. Please try again.", 'danger')
                return redirect(url_for('new_post'))
        
        # Generate the slug based on the title
        slug = generate_slug(form.title.data)
        
        # Create and add the new post
        post = Post(
            title=form.title.data.upper(),
            slug=slug,
            content=form.Content.data,
            author=current_user,
            image=image  # Save image file reference (path or cloud URL)
        )
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for('home'))
    
    return render_template('create_new.html', title='New Post', form=form, image_file=image_file)


@app.route('/image/<filename>')
def serve_image(filename):
    # Path to the static folder where images are stored
    image_path = os.path.join(app.root_path, 'static', 'post_images', filename)
    
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        abort(404) 

@app.route("/Account/post/new", methods=['POST', 'GET'])
@login_required
def new_post():
    form = CreatePostForm()
    
    # Remove the image_file for profile pictures if not needed here
    image = None  # Set image to None initially

    if form.validate_on_submit():
        # Handle invalid file types
        if form.picture.errors:
            for error in form.picture.errors:
                flash(f"File upload error: {error}", "danger")
            return redirect(url_for('new_post'))

        # Save the image if provided
        if form.picture.data:
            try:
                # Save the image to Firebase Storage and get the public URL
                image = save_picture1(form.picture.data)  # Now it returns the public URL
                print(f"Image saved: {image}")  # Debug log
            except Exception as e:
                print(e)
                flash(f"{e}", 'danger')
                return redirect(url_for('new_post'))

        # Generate the slug based on the title
        slug = generate_slug(form.title.data)

        # Create and add the new post
        post = Post(
            title=form.title.data.upper(),
            slug=slug,
            content=form.Content.data,
            author=current_user,
            image=image  # Store the public URL of the image
        )
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for('home'))

    return render_template('create_new.html', title='New Post', form=form)

       
       


@app.route("/show", methods=['POST', 'GET'])
@login_required
def show_img():
    #image_file= url_for( current_user.image_file)
    #picture = url_for('static', filename='profile_pics/' + user.image_file)

    return render_template('show_image.html')

global picture
@app.route("/home/search_person/<username>")
@login_required
def look(username):
    with app.app_context():

        user = User.query.filter_by(username=username).first_or_404()  # Fetch the user by username
        if user.username == current_user.username:
            return redirect(url_for('Account'))
        else:
            page = request.args.get('page', 1, type=int)
    
            # Query the posts related to the current user, ordered by date descending
            posts= Post.query.filter_by(user_id=user.id).order_by(Post.date.desc()).paginate(page=page, per_page=10)
            #posts = user.posts  # Get all posts by the user
            name = user.username
            email = user.email
            print(user.id)
            #picture = url_for('static', filename='profile_pics/' + user.image_file)
            #image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
            #print(picture)
            

    return render_template('search_person.html', name=name, email=email, posts=posts, user=user)


@app.route("/search_person/show2", methods=['POST', 'GET'])
@login_required
def show_img2():
    picture = request.args.get('picture')  # Get the 'picture' parameter from the URL query string

    # Debugging step: print the picture URL
    print(f"Picture URL received: {picture}")

    if not picture:
        return redirect(url_for('home'))  # If no picture is passed, redirect to home
    
    return render_template('show_image2.html', picture=picture)

@app.route("/post/<slug>", methods=['POST', 'GET'])
@login_required
def post_detail(slug):
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    post = Post.query.filter_by(slug=slug).first_or_404()  # Query by slug instead of title
    comments = Comment.query.filter_by(post_id=post.id).all()
    
    # Check for an edit_comment_id query parameter
    edit_comment_id = request.args.get("edit_comment_id", type=int)
    edit_comment = Comment.query.get(edit_comment_id) if edit_comment_id else None
    
    # Render the post detail template with the edit_comment context
    return render_template('post_detail.html', post=post, image_file=image_file, comments=comments, edit_comment=edit_comment)




@app.route("/post/detail/update/<int:post_id>", methods=['POST', 'GET'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)
    #post = Post.query.filter_by(id=post_id).first
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
   
    print(post.id)
    print(post.author.username)
    print(post.user_id)

    form = UpdatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.Content.data
        db.session.commit()
        flash("blog updated successfully", 'success')
        return redirect(url_for('post_detail',slug=post.slug))
    elif request.method == 'GET':
        form.title.data = post.title
        form.Content.data = post.content
    return render_template('edit_post.html',form=form,post=post,image_file=image_file)

# Route to Delete Post
@app.route('/post/detail/delete/<int:post_id>', methods=['POST', 'GET'])
@login_required
def delete(post_id):

    # Get the post or raise 404 if it doesn't exist
    post = Post.query.get_or_404(post_id)
    
    # Delete associated comments, replies, and likes
    for comment in post.comments:
        for reply in comment.replies:
            db.session.delete(reply)
        db.session.delete(comment)
    
    for like in post.likes:
        db.session.delete(like)

    for notification in post.notifications:
        db.session.delete(notification)

    # Delete the post itself
    db.session.delete(post)
    db.session.commit()

    flash("Post and all its associated data deleted successfully.", "success")
    return redirect(url_for('home'))


@app.route("/post/detail/<int:post_id>/comment", methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author.id == current_user.id:
        pass
    else:
        notification=Notification(user_id=post.author.id,content=f'{current_user.username} commented on your post',initiator=current_user.id,post_id=post.id)
        print(notification)
        db.session.add(notification)
        db.session.commit
        print(f'notification of comment added {current_user.username}')


    content = request.form['content']
    comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post.id,slug=post.slug))

@app.route("/post/detail/comment/delete/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)  # Fetch the comment by its ID
    post_id=comment.post.id
    print(comment.post.title)
    print(comment.post.id)
   
    try:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the comment.", "danger")
        print(e)
    return redirect(url_for('post_detail',slug=comment.post.slug, post_id=comment.post.id))
    

@app.route("/post/detail/comment/edit/<int:comment_id>", methods=["POST"])
@login_required
def edit_comment(comment_id):
    # Fetch the comment to be edited
    comment = Comment.query.get_or_404(comment_id)
    
    # Ensure the user is authorized to edit the comment
    if comment.user != current_user:
        abort(403)
    
    # Update comment content
    form_content = request.form.get("content", "").strip()  # Ensure no leading/trailing spaces
    if not form_content:
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for('post_detail', slug=comment.post.slug, edit_comment_id=comment_id))
    
    comment.content = form_content
    db.session.commit()
    flash("Comment updated successfully!", "success")
    
    # Redirect back to the post detail page
    return redirect(url_for('post_detail', slug=comment.post.slug))


@app.route("/comment/reply1/<int:comment_id>", methods=["POST","GET"])
@login_required
def reply1_comment(comment_id):
    # Fetch the comment to be edited
    comment = Comment.query.get_or_404(comment_id)
    content=request.form['content']
    reply = Reply(content=content, comment_id=comment.id, user_id=current_user.id)
    db.session.add(reply)
    db.session.commit()
    flash("reply updated successfully!", "success")

    image_file= url_for('static', filename='profile_pics/' + current_user.image_file)



    return render_template('reply.html', comment=comment,content=content,image_file=image_file)



@app.route("/comment/reply/<int:comment_id>", methods=["POST", "GET"])
@login_required
def reply_comment(comment_id):
    # Fetch the comment to be replied to
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id == current_user.id:
        pass
    else:
        print(comment_id,comment.post)
        notification=Notification(user_id=comment.user.id,content=f'{current_user.username} replied to your comment',initiator=current_user.id,comment_id=comment_id,post_id=comment.post_id)
        print(notification)
        db.session.add(notification)
        db.session.commit
        print(f'notification of reply added {current_user.username}')
    


    if request.method == "POST":
        # Get reply content from the form
        content = request.form.get("content")
        
        if not content.strip():
            flash("Reply cannot be empty!", "danger")
            return render_template('reply.html', comment=comment, content="", image_file=url_for('static', filename='profile_pics/' + current_user.image_file))
        
        # Create a new Reply object
        reply = Reply(content=content, comment_id=comment.id, user_id=current_user.id)
        db.session.add(reply)
        db.session.commit()
        print(reply.comment_id)
        print(reply.user_id)
        flash("Reply added successfully!", "success")
        return redirect(url_for('reply_comment',comment_id=comment.id))

    reply=comment.replies
    # Check for an edit_comment_id query parameter
    edit_reply_id = request.args.get("edit_reply_id", type=int)
    edit_reply = Reply.query.get(edit_reply_id) if edit_reply_id else None

    # If GET request, render reply form with existing content
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    return render_template('reply.html', comment=comment, image_file=image_file,edit_reply=edit_reply)

@app.route("/comment/reply/delete/<int:reply_id>", methods=["POST"])
@login_required
def delete_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)  # Fetch the comment by its ID
    comment_id=reply.comment.id
    print(reply)
    print(reply.comment.id)
    print(reply.user.id)
    print(reply.user_id)
    db.session.delete(reply)
    db.session.commit()
    flash("reply deleted successfully!", "success")
    
    return redirect(url_for('reply_comment',comment_id=reply.comment_id))

@app.route("/comment/reply/edit/<int:reply_id>", methods=["POST", "GET"])
@login_required
def edit_reply(reply_id):
    # Fetch the reply to be edited
    reply = Reply.query.get_or_404(reply_id)

    # Ensure the user is authorized to edit the reply
    if reply.user != current_user:
        abort(403)

    # Handle GET request to prepopulate the form
    if request.method == "GET":
        comment = reply.comment
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('reply.html', comment=comment, image_file=image_file, edit_reply=reply)

    # Handle POST request to update the reply
    form_content = request.form.get("content", "").strip()
    if not form_content:
        flash("Reply cannot be empty.", "danger")
        return redirect(url_for('reply_comment', comment_id=reply.comment_id, edit_reply_id=reply.id))

    reply.content = form_content
    db.session.commit()
    flash("Reply updated successfully!", "success")
    return redirect(url_for('reply_comment', comment_id=reply.comment_id))


#@app.route("/like/<int:post_id>", methods=["POST"])
#@login_required
#def like_post(post_id):
   # post = Post.query.get_or_404(post_id)
    
    # Check if the current user has already liked the post
    #existing_like = Love.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    #if not existing_like:
        # If the like doesn't exist, create a new like
        #like = Love(user_id=current_user.id, post_id=post.id)
        #db.session.add(like)
        #db.session.commit()
        #flash("You liked this post.", "info")
    #else:
        #flash("You have already liked this post.", "info")

    #return redirect(request.referrer)  # Redirect back to the previous page




#@app.route("/unlike_post/<int:post_id>", methods=["POST"])
#@login_required
#def unlike_post(post_id):
    #post = Post.query.get_or_404(post_id)

    # Find the like and remove it
    #existing_like = Love.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    #if existing_like:
        #db.session.delete(existing_like)
        #db.session.commit()
        #flash("You unliked this post.", "info")
    #else:
        #like_post(post_id)
    
    #return redirect(request.referrer)

@app.route("/post_detail/pin_post", methods=["POST","GET"])
def pin_post():
  flash("You pinned this post.", "info")

  return redirect(request.referrer)





@app.route("/unlike_like_post/<int:post_id>", methods=["POST", "GET"])
@login_required
def unlike_like_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Find the like
    existing_like = Love.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if existing_like:
        # If the like exists, delete it (unlike the post)
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"status": "success", "action": "unliked", "post_id": post_id})
    else:
        #send notifications
        if post.author.id == current_user.id:
            pass
        else:
            notification=Notification(user_id=post.author.id,content=f'{current_user.username} liked your post',initiator=current_user.id,post_id=post.id)
            db.session.add(notification)
            db.session.commit
            print(f'notification added {current_user.username}')
        # If the like doesn't exist, create it (like the post)
        like = Love(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({"status": "success", "action": "liked", "post_id": post_id})
        



    
        



# Admin Page Route
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    posts = Post.query.all()  # Fetch all posts
    users = User.query.all()  # Fetch all users
    comments=Comment.query.all()
    if current_user.email != 'dibieemmanuel403@gmail.com':  # Ensure the user is an admin
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('home'))  # Redirect unauthorized users to home

    return render_template('admin.html', users=users, posts=posts,comments=comments)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.email != 'dibieemmanuel403@gmail.com':
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('admin_page'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_page'))

# Route to Delete Post
@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    if current_user.email != 'dibieemmanuel403@gmail.com':
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('admin_page'))

    # Get the post or raise 404 if it doesn't exist
    post = Post.query.get_or_404(post_id)
    
    # Delete associated comments, replies, and likes
    for comment in post.comments:
        for reply in comment.replies:
            db.session.delete(reply)
        db.session.delete(comment)
    
    for like in post.likes:
        db.session.delete(like)

    # Delete the post itself
    db.session.delete(post)
    db.session.commit()

    flash("Post and all its associated data deleted successfully.", "success")
    return redirect(url_for('admin_page'))


@app.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment_admin(comment_id):
    # Check if the user is an admin
    if current_user.email != 'dibieemmanuel403@gmail.com':
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('admin_page'))

    # Fetch the comment or raise a 404 if it doesn't exist
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        # Delete the comment
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the comment: {e}", "danger")

    return redirect(url_for('admin_page'))



@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Check if the current user has admin privileges
    if current_user.email != 'dibieemmanuel403@gmail.com':
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('admin_page'))

    # Load user and current image file
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update user details from the form
        user.username = request.form['username']
        user.email = request.form['email']
        
        # Handle the 'is_admin' status from the form and convert it to a boolean
        is_admin_value = request.form.get('is_admin', 'false').lower()  # Default to 'false'
        user.is_admin = is_admin_value == 'true'

        # Commit the updates to the database
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('admin_page'))

    return render_template('Admin_edit_user.html', user=user, image_file=image_file)


# Route to Edit Post
@app.route('/admin/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if current_user.email != 'dibieemmanuel403@gmail.com':
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('admin_page'))

    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for('admin_page'))

    return render_template('Admin_edit_post.html', post=post)


def add_admin():
    admin_user = User.query.filter_by(email="dibieemmanuel403@gmail.com").first()
    print(admin_user)

    if admin_user:
        admin_user.is_adminn = True
        db.session.commit()
        print(f"User {admin_user.username} is now an admin!")
    else:
        print("User not found.")

def send_reset_email(user):
    # Generate a reset token
    token = user.get_reset_token()
    
    # Create the email message
    msg = Message(
        'Password Reset Request',
        sender='noreply@demo.com',
        recipients=[user.email]
    )
    
    # Email body
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not request this password reset, please ignore this email and no changes will be made.
'''

    # Send the email
    mail.send(msg)

@app.route('/request_token', methods=['GET', 'POST'])
def request_reset_token():
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetTokenForm()
    if form.validate_on_submit():
       user=User.query.filter_by(email=form.email.data).first()   
       #send_reset_email(user)
       flash("An email has been sent to you with instruction to folow",'info')
       return redirect(url_for('login'))
    return render_template('request_reset_token.html',title='Reset_password',form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_password(token)
    if user is None:
        flash('this is an invalid or incorrect token','warning')
        return_redirect(url_for('request_reset_token'))

    form=ResetPasswordForm() 
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        user.password=hashed_password
        db.session.commit()
        flash(f"You password has been update!, please procceed to login😊", 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html',title='Reset_password',form=form)


@app.route('/notification', methods=['GET', 'POST'])
def notification():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date.desc()).limit(10).all()
    enriched_notifications = []

    for notification in notifications:
        initiator = User.query.get(notification.initiator)  # Fetch the initiator
        enriched_notifications.append({
            'notification': notification,
            'initiator': initiator,
        })

        print(enriched_notifications)

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('Notification.html',title='Notification',notifications=enriched_notifications,image_file=image_file)

@app.route('/search_post', methods=['GET', 'POST'])
def search_post():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    content = ''
    if request.method == 'POST':
        content = request.form['content']  # Get content from the form

    page = request.args.get('page', 1, type=int)
    # Apply pagination directly on the query object
    post = Post.query.filter(Post.content.contains(content)).paginate(page=page, per_page=5)

    return render_template('search.html', post=post,image_file=image_file)  # Render the results

@app.route("/test-upload", methods=['POST', 'GET'])
def test_upload():
    notifications = Notification.query.all()
    print(notifications)

    for notification in notifications:
        db.session.delete(notification)
        db.session.commit()
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            print(f"File received: {file.filename}")
            return "File uploaded!"
        return "No file received!"
    return '''
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>
    '''

@app.route("/feedback", methods=['POST', 'GET'])
@login_required
def feedback():
    form = FeedbackForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    if form.validate_on_submit():
        
        # Create and add the new feedback
        feedback = Feedback(content=form.Content.data, user_id=current_user.id)
        db.session.add(feedback)
        db.session.commit()
        flash("feedback sent successfully!", "success")
        return redirect(url_for('home'))
    
    return render_template('feedback.html', title='feedback', form=form, image_file=image_file)


@app.route("/feedback_view")
def feedback_view():
    # Get the page number from the request arguments (default is 1)
    page = request.args.get('page', 1, type=int)
    
    # Use .paginate() on the SQLAlchemy query object
    post = Feedback.query.paginate(page=page, per_page=10)
    
    # Construct the URL for the user's profile image
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
   
    # Render the template with the paginated posts and other data
    return render_template('show_feedback.html', post=post, title='Feedback', image_file=image_file)





    
    











    

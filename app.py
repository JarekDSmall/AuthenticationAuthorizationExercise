from flask import Flask, render_template, redirect, url_for, flash, abort
from forms import RegistrationForm, LoginForm, FeedbackForm
from models import User, Feedback
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login view

# Initialize the database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Process the form data and add a new user to the database
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process the login form and authenticate the user
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('user_info', username=user.username))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def user_info(username):
    # Retrieve user information from the database
    user = User.query.filter_by(username=username).first()
    feedback = Feedback.query.filter_by(username=username).all()
    return render_template('user_info.html', user=user, feedback=feedback)

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
@login_required
def add_feedback(username):
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(title=form.title.data, content=form.content.data, username=username)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback added successfully!', 'success')
        return redirect(url_for('user_info', username=username))
    return render_template('feedback_form.html', form=form, form_title='Add Feedback')

@app.route('/users/<username>/feedback/<int:feedback_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_feedback(username, feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username != username:
        abort(403)  # Only allow the owner to edit their feedback
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash('Feedback updated successfully!', 'success')
        return redirect(url_for('user_info', username=username))
    return render_template('feedback_form.html', form=form, form_title='Edit Feedback')

@app.route('/users/<username>/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
def delete_feedback(username, feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username != username:
        abort(403)  # Only allow the owner to delete their feedback
    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted successfully!', 'success')
    return redirect(url_for('user_info', username=username))

@app.route('/secret')
@login_required
def secret():
    return "You made it!"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)




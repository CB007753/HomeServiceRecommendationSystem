from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        fullname = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(fullname) < 3:
            flash('Full name must be greater than 2 characters.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            # Add user to the database
            flash('Successfully signed up.', category='success')

    return render_template("sign_up.html")


@auth.route('/logout')
def logout():
    return "<p>Logged Out</p>"

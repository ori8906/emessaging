import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskapp.db import get_db
from flaskapp.services.emailservice import EmailService

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method != 'POST':
        return render_template('auth/register.html')

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error is not None:
        flash(error)
        return render_template('auth/register.html')

    try:
        db.execute(
            "INSERT INTO user (username, password_hash, email, activated) VALUES (?, ?, ?, 0)",
            (username, generate_password_hash(password), email),
        )
        db.commit()
    except db.IntegrityError:
        flash(f"User {username} is already registered.")
        return render_template('auth/register.html')

    activationLink = url_for("auth.activate", _external=True) + "?account=" + email
    emailservice = EmailService()
    emailservice.send_email(email, "eMessaging Account Activation",
        f"Activate your account by following this link: { activationLink }")
    return redirect(url_for("auth.login"))

@bp.route("/activate", methods=("GET",))
def activate():
    emailToActivate = request.args["account"]
    if emailToActivate is None:
        flash("Incorrect activation link.")
        return redirect(url_for("auth.login"))
    
    db = get_db()
    try:
        db.execute(
            "UPDATE user SET activated = 1 WHERE email = ?",
            (emailToActivate,)
        )
        db.commit()
    except db.IntegrityError:
        flash("No such user to activate.")
        return redirect(url_for("auth.login"))
    
    return redirect(url_for("auth.login"))

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ? AND activated = 1',
            (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
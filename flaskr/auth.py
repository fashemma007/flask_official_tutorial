import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# creates a Blueprint named 'auth'.
# the blueprint needs to know where it’s defined,
# so __name__ is passed as the second argument.
# The `url_prefix` will be prepended to all the URLs
# associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route associates the URL /register with the 
# register() view function; a visit to /auth/register
# will call this function
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # If the user submitted the form, request.method will be 'POST'
    if request.method == 'POST':
        # request.form is a special type of dict 
        # for mapping submitted form keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

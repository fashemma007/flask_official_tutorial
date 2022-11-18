import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flaskr.db import get_db

# creates a Blueprint named 'auth'.
# the blueprint needs to know where it’s defined,
# so __name__ is passed as the second argument.
# The `url_prefix` will be prepended to all the URLs
# associated with the blueprint.
bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):  # creating a decorator for other views
    # when this is called on a view function, it wraps it
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # if g.user is None, it redirects to login page, else it
        if g.user is None:
            return redirect(url_for("auth.login"))
        # continues with the user's request
        return view(**kwargs)

    return wrapped_view

# @bp.route associates the URL /register with the
# register() view function; a visit to /auth/register
# will call this function
@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    # If the user submitted the form, request.method will be 'POST'
    if request.method == "POST":
        # request.form is a special type of dict
        # for mapping submitted form keys and values
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

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

    return render_template("auth/register.html")


# @bp.route associates the URL /login with the
# login() view function; a visit to /auth/login
# will call this function
@bp.route("/login", methods=("GET", "POST"))
def login():
    # if form is submitted, request.method will be 'POST'
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        # db is queried using the given username to search
        # if the user exists in the database
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        # if no result was gotten i.e. user doesn't exist
        if user is None:
            error = "Incorrect username."

        # check_password_hash() hashes the provided password
        # and compares it against the password hash in the database
        # ==========================================================
        # if user exists but password is wrong
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        # if there was no error, save session in cookie
        # ====================================================
        # session is a dict that stores data across requests
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")

# registers a function that runs before the view function,
# no matter what URL is requested.
# ==================================================================
# load_logged_in_user() checks if a user id is stored in the session
# and gets that user’s data from the database, storing it on g.user,
@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


# to logout a user, we need to delete the userid from session
@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))



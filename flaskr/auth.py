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
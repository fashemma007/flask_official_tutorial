import os

from flask import Flask

# application factory function
def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    # creates the Flask instance
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from . import db

    db.init_app(app)

    # importing & registring auth & blog blueprints
    from . import auth
    from . import blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)


    # app.add_url_rule() works similarly to app.route()
    # it creates an alternate route to the blog page of our app
    # with this, both '/' and '/index' would direct to blogs page
    app.add_url_rule("/", endpoint="index")

    return app

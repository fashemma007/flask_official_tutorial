import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    # tempfile.mkstemp() creates and opens a temporary file,
    # returning the file descriptor and the path to it
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,  # tells Flask that the app is in test mode
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
# Tests will use the client to make requests to
# the application without running the server.
    return app.test_client()

# client. app.test_cli_runner() creates a runner that can
# call the Click commands registered with the application.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

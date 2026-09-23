import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.api import app as flask_app
from app.models import init_db


@pytest.fixture()
def client(request):
    """Flask test client, backed by a freshly seeded SQLite DB.

    Pass -m "bad_data" marker or use seed_bad_data param via indirect
    parametrization if a test needs the intentionally broken dataset.
    """
    seed_bad_data = getattr(request, "param", False)
    init_db(seed_bad_data=seed_bad_data)
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c

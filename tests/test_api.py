"""
API-level tests: validate HTTP status codes, response shape, and basic
business rules for the Employee Transactions API.
"""
import pytest


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_list_employees_returns_all(client):
    resp = client.get("/employees")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 3
    assert {"id", "name", "department", "balance"} <= data[0].keys()


def test_get_single_employee(client):
    resp = client.get("/employees/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Asha Rao"
    assert data["department"] == "Engineering"


def test_get_nonexistent_employee_returns_404(client):
    resp = client.get("/employees/999")
    assert resp.status_code == 404


def test_get_employee_transactions(client):
    resp = client.get("/employees/1/transactions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    types = {t["type"] for t in data}
    assert types == {"credit", "debit"}


@pytest.mark.parametrize("employee_id", [1, 2, 3])
def test_every_seeded_employee_is_reachable(client, employee_id):
    resp = client.get(f"/employees/{employee_id}")
    assert resp.status_code == 200

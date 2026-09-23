"""
Data validation / reconciliation tests.

These go straight at the database with SQL and cross-check it against
itself (and against the API) - this is the "data validation and
reconciliation using complex SQL queries" skill called out in the JD.

Each test is run twice via indirect parametrization:
  - clean dataset  -> should pass
  - "dirty" dataset (seed_bad_data=True) -> should catch the injected defects

This mirrors real QA work: you write one reconciliation check, then prove
it actually catches bad data, not just that it passes on good data.
"""
import pytest
from app.models import get_connection


def orphaned_transactions():
    """Transactions whose employee_id has no matching employee row."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id, t.employee_id
        FROM transactions t
        LEFT JOIN employees e ON t.employee_id = e.id
        WHERE e.id IS NULL
    """).fetchall()
    conn.close()
    return rows


def balance_mismatches():
    """Employees whose stored balance doesn't match sum(credits) - sum(debits)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            e.id,
            e.name,
            e.balance AS stored_balance,
            COALESCE(SUM(CASE WHEN t.type = 'credit' THEN t.amount
                               WHEN t.type = 'debit' THEN -t.amount
                               ELSE 0 END), 0) AS computed_balance
        FROM employees e
        LEFT JOIN transactions t ON t.employee_id = e.id
        GROUP BY e.id
        HAVING stored_balance != computed_balance
    """).fetchall()
    conn.close()
    return rows


@pytest.mark.parametrize("client", [False], indirect=True)
def test_no_orphaned_transactions_on_clean_data(client):
    assert orphaned_transactions() == []


@pytest.mark.parametrize("client", [True], indirect=True)
def test_orphaned_transaction_is_detected_on_dirty_data(client):
    orphans = orphaned_transactions()
    assert len(orphans) == 1
    assert orphans[0]["employee_id"] == 99


@pytest.mark.parametrize("client", [False], indirect=True)
def test_no_balance_mismatch_on_clean_data(client):
    assert balance_mismatches() == []


@pytest.mark.parametrize("client", [True], indirect=True)
def test_balance_mismatch_is_detected_on_dirty_data(client):
    mismatches = balance_mismatches()
    assert len(mismatches) == 1
    assert mismatches[0]["name"] == "Vikram Shah"

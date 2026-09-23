# Backend Test Automation Framework

A small, self-contained project built to demonstrate **backend test automation
skills**: API testing, SQL-based data validation/reconciliation, and
Shell-based test orchestration — the core skills for a backend/automation QA role.

## What this demonstrates

| JD requirement | Where it's shown |
|---|---|
| Python automation development | `tests/test_api.py`, `tests/test_reconciliation.py` — pytest-based framework, fixtures, parametrization |
| SQL query development, data validation & reconciliation | `tests/test_reconciliation.py` — raw SQL joins/aggregates that cross-check the database against itself |
| Testing APIs and backend services | `app/api.py` (Flask API) + full API test coverage |
| Shell scripting / Unix-Linux | `scripts/run_tests.sh` — environment setup, test execution, reporting |
| CI/CD awareness | `.github/workflows/ci.yml` — runs the suite automatically on every push |
| Defect lifecycle thinking | Tests are run against both a "clean" dataset and a deliberately "dirty" dataset to prove the checks actually catch real defects, not just pass by default |

## Project structure

```
backend-test-automation/
├── app/
│   ├── api.py              # Flask API (system under test)
│   └── models.py           # SQLite schema + seed data (clean & "dirty" modes)
├── tests/
│   ├── test_api.py             # API-level tests (status codes, response shape)
│   └── test_reconciliation.py  # SQL reconciliation checks (orphaned rows, balance mismatches)
├── scripts/
│   └── run_tests.sh        # setup, seed, run, report — one command
├── .github/workflows/ci.yml
├── requirements.txt
└── README.md
```

## What the "system under test" is

A tiny Employee/Transactions API:
- `GET /employees` — list employees
- `GET /employees/<id>` — single employee
- `GET /employees/<id>/transactions` — transactions for an employee

The database has two seed modes:
- **Clean data** — everything reconciles correctly.
- **Dirty data** (`seed_bad_data=True`) — deliberately injects two realistic
  defects: an orphaned transaction (references a non-existent employee) and
  a balance mismatch (stored balance doesn't match the sum of transactions).

Each reconciliation test is run against **both** datasets, so the suite
proves the check passes on good data *and* actually catches the bad data —
not just "asserts True."

## How to run it

```bash
git clone <your-repo-url>
cd backend-test-automation
./scripts/run_tests.sh
```

This will:
1. Create a virtual environment (first run only)
2. Install dependencies
3. Run the full pytest suite
4. Generate `reports/report.html` and `reports/junit.xml`
5. Print a pass/fail summary

Or run tests directly:
```bash
pip install -r requirements.txt
pytest -v tests/
```

## Example: a reconciliation query

```sql
SELECT
    e.id, e.name, e.balance AS stored_balance,
    COALESCE(SUM(CASE WHEN t.type = 'credit' THEN t.amount
                       WHEN t.type = 'debit' THEN -t.amount
                       ELSE 0 END), 0) AS computed_balance
FROM employees e
LEFT JOIN transactions t ON t.employee_id = e.id
GROUP BY e.id
HAVING stored_balance != computed_balance
```

This is the kind of query used to catch real data integrity issues in
production systems — exactly the "data validation and reconciliation using
complex SQL queries across large-scale databases" skill this project is
meant to demonstrate.

## Tech stack

Python 3.11+, Flask, SQLite, pytest, pytest-html, Shell scripting, GitHub Actions.

## Notes / possible extensions

- Swap SQLite for Postgres to demonstrate a "large-scale database" more realistically.
- Add Jira/Zephyr-style defect logging as a mock integration.
- Add a Jenkinsfile alongside the GitHub Actions workflow.

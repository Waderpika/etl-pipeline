"""
Small Flask API used as the system-under-test.

Endpoints:
    GET /employees            -> list all employees
    GET /employees/<id>       -> single employee
    GET /employees/<id>/transactions -> transactions for an employee
    GET /health               -> liveness check
"""
from flask import Flask, jsonify, abort
from app.models import get_connection

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/employees")
def list_employees():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/employees/<int:employee_id>")
def get_employee(employee_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    if row is None:
        abort(404, description="Employee not found")
    return jsonify(dict(row))


@app.get("/employees/<int:employee_id>/transactions")
def get_employee_transactions(employee_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE employee_id = ?", (employee_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=True, port=5000)

import os
import pymysql
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-chupa-melox")

AUTH_URL = os.getenv("AUTH_URL", "http://auth_service:5000/validate")

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_DB = os.getenv("MYSQL_DB", "projectdb")
MYSQL_USER = os.getenv("MYSQL_USER", "project-user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "project-passwd")

# rules/constraints for inputting data into the metrics
METRIC_RULES = {
    "grade": {"min": 0, "max": 100},
    "temperature": {"min": -50, "max": 50},
    "humidity": {"min": 0, "max": 100},
    "pressure": {"min": 0, "max": 2000}
}


def validate_user(username, password):
    try:
        request = requests.post(AUTH_URL, json={"username": username, "password": password}, timeout=3)
        request.raise_for_status()
        return bool(request.json().get("ok"))
    except Exception:
        return False


def insert_reading(username, metric, value):
    connector = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
    )
    try:
        with connector.cursor() as cursor:
            cursor.execute(
                "INSERT INTO readings(username, metric, value) VALUES (%s, %s, %s)",
                (username, metric, value),
            )
    finally:
        connector.close()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/submit")
def submit():
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    metric = (request.form.get("metric") or "").strip().lower()
    value_raw = (request.form.get("value") or "").strip()

    # basic validation
    try:
        value = float(value_raw)
    except ValueError:
        flash("Invalid value. Must be numeric.", "danger")
        return redirect(url_for("index"))
    
    # Per-metric validation
    rules = METRIC_RULES.get(metric)
    if rules:
        if value < rules["min"] or value > rules["max"]:
            flash(f"Value out of range for {metric}. Allowed: {rules['min']} to {rules['max']}.",
                "danger",)
            return redirect(url_for("index"))

    # Auth check
    if not validate_user(username, password):
        flash("Auth failed. Invalid credentials.", "danger")
        return redirect(url_for("index"))

    # Insert into MySQL
    try:
        insert_reading(username, metric, value)
    except Exception as e:
        flash(f"DB insert failed: {e}", "danger")
        return redirect(url_for("index"))

    flash("Saved to MySQL!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
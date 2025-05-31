from flask import Flask, jsonify, render_template_string
import psycopg2
import time
import os
from psycopg2 import pool

app = Flask(__name__)

# Database configuration with connection pooling
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'votes')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

# Connection pool
connection_pool = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Voting Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin-top: 40px; text-align: center; }
        table { margin: 0 auto; border-collapse: collapse; font-size: 18px; }
        th, td { padding: 10px 20px; border: 1px solid #ccc; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Live Voting Results</h1>
    {% if results %}
    <table>
        <tr>
            <th>Candidate</th>
            <th>Votes</th>
        </tr>
        {% for candidate, votes in results.items() %}
        <tr>
            <td>{{ candidate }}</td>
            <td>{{ votes }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p>No votes recorded yet.</p>
    {% endif %}
</body>
</html>
"""

def initialize_db_connection_pool():
    global connection_pool
    max_retries = 5
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                port=DB_PORT
            )
            print("Database connection pool initialized successfully")
            return
        except psycopg2.OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Database connection failed (attempt {attempt + 1}), retrying...")
            time.sleep(retry_delay)

def get_db_connection():
    return connection_pool.getconn()

def release_db_connection(conn):
    connection_pool.putconn(conn)

@app.route('/')
def home():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
        rows = cur.fetchall()
        results = {candidate: count for candidate, count in rows}
        return render_template_string(HTML_TEMPLATE, results=results)
    except Exception as e:
        app.logger.error(f"Error rendering results page: {str(e)}")
        return "<h2>Internal Server Error</h2>", 500
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/favicon.ico')
def favicon():
    return '', 404

@app.route('/results')
def results():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
        rows = cur.fetchall()
        results = {candidate: count for candidate, count in rows}
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Error fetching results: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == '__main__':
    print("Initializing database connection pool...")
    initialize_db_connection_pool()

    # Schema initialization is skipped here intentionally to avoid conflict
    print("Starting result app...")
    app.run(host='0.0.0.0', port=5001, debug=False)

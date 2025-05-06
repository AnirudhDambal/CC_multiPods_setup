from flask import Flask, jsonify
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

def initialize_db_schema():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                candidate VARCHAR(255) NOT NULL,
                voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Database schema initialized successfully")
    except Exception as e:
        print(f"Error initializing database schema: {str(e)}")
        raise
    finally:
        if conn:
            release_db_connection(conn)

@app.route('/')
def home():
    return "Result App Service - GET results from /results"

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
    
    print("Initializing database schema...")
    initialize_db_schema()
    
    print("Starting result app...")
    app.run(host='0.0.0.0', port=5001, debug=False)  # debug=False in production
from flask import Flask, request, jsonify
import psycopg2
import time

app = Flask(__name__)

# Database configuration
DB_HOST = "postgres"  # Changed from "db"
DB_NAME = "votes"
DB_USER = "postgres"
DB_PASS = "postgres"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def initialize_db():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
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
            cur.close()
            conn.close()
            print("Database initialized successfully")
            return
        except psycopg2.OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Database connection failed (attempt {attempt + 1}), retrying...")
            time.sleep(retry_delay)

@app.route('/')
def home():
    return "Voting App Service - POST votes to /vote"

@app.route('/favicon.ico')
def favicon():
    return '', 404

@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    if not data or 'candidate' not in data:
        return jsonify({"error": "Candidate name required"}), 400
    
    candidate = data['candidate']
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO votes (candidate) VALUES (%s)", (candidate,))
        conn.commit()
        return jsonify({"status": "success", "candidate": candidate})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("Initializing database...")
    initialize_db()
    print("Starting voting app...")
    app.run(host='0.0.0.0', port=5000)
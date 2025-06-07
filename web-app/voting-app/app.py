from flask import Flask, request, jsonify, render_template_string
import psycopg2
import time

app = Flask(__name__)

# Database configuration
DB_HOST = "postgres"
DB_NAME = "votes"
DB_USER = "postgres"
DB_PASS = "postgres"

# Simple HTML template for frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vote for a Candidate</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        form { display: inline-block; margin-top: 20px; }
        input, button { padding: 10px; font-size: 16px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Vote for a Candidate</h1>
    <form method="POST" action="/vote">
        <input type="text" name="candidate" placeholder="Enter candidate name" required />
        <button type="submit">Submit Vote</button>
    </form>
    {% if message %}
        <p><strong>{{ message }}</strong></p>
    {% endif %}
</body>
</html>
"""

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

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

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('candidate') or (request.get_json() or {}).get('candidate')
    if not candidate:
        return jsonify({"error": "Candidate name required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO votes (candidate) VALUES (%s)", (candidate,))
        conn.commit()
        cur.close()
        conn.close()
        if request.is_json:
            return jsonify({"status": "success", "candidate": candidate})
        else:
            return render_template_string(HTML_TEMPLATE, message=f"Vote submitted for {candidate}!")
    except Exception as e:
        if request.is_json:
            return jsonify({"error": str(e)}), 500
        return render_template_string(HTML_TEMPLATE, message=f"Error: {str(e)}")

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == '__main__':
    print("Initializing database...")
    initialize_db()
    print("Starting voting app...")
    app.run(host='0.0.0.0', port=5000)

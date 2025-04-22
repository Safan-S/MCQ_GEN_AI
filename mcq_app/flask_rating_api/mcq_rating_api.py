from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import logging

app = Flask(__name__)
CORS(app)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database URL from environment ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    try:
        data = request.json
        logger.info(f"Received rating data: {data}")

        # Required fields
        required_fields = [
            'model_id', 'model_name', 'subject_id', 'subject_name',
            'grammatical_fluency', 'answerability', 'complexity',
            'relevance', 'repetability', 'repetability_in_answers'
        ]

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing field: {field}")
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Convert all values to strings for compatibility
        values = [str(data[field]) for field in required_fields]

        # Insert into mcq_ratings table
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO mcq_ratings (
                model_id, model_name, subject_id, subject_name,
                grammatical_fluency, answerability, complexity,
                relevance, repetability, repetability_in_answers,
                submitted_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ''', values)

        conn.commit()
        cur.close()
        conn.close()

        logger.info("Rating submitted successfully.")
        return jsonify({"message": "Rating submitted successfully"}), 201

    except Exception as e:
        logger.exception("Error while submitting rating")
        return jsonify({"error": str(e)}), 500

# --- Run the app ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

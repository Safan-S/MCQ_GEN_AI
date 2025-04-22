from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO ratings (model_id, model_name, subject_id, subject_name, grammatical_fluency, answerability, complexity, relevance, repetability, repetability_in_answers)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        data['model_id'],
        data['model_name'],
        data['subject_id'],
        data['subject_name'],
        data['grammatical_fluency'],
        data['answerability'],
        data['complexity'],
        data['relevance'],
        data['repetability'],
        data['repetability_in_answers']
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Rating submitted successfully"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
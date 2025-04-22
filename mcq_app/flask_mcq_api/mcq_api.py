from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/mcqs', methods=['GET'])
def get_mcqs():
    subject = request.args.get('subject')
    model = request.args.get('model')

    conn = get_connection()
    cur = conn.cursor()
    query = '''
        SELECT q.question_id, q.question_text, a.correct_option, 
               json_agg(json_build_object('option_label', o.option_label, 'option_text', o.option_text)) AS options
        FROM questions q
        JOIN options o ON q.question_id = o.question_id
        JOIN answers a ON q.question_id = a.question_id  -- Join with answers table to get correct_option
        JOIN subjects s ON q.subject_id = s.subject_id
        JOIN models m ON q.model_id = m.model_id
        WHERE s.subject_name = %s AND m.model_name = %s
        GROUP BY q.question_id, a.correct_option
    '''
    cur.execute(query, (subject, model))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    mcqs = []
    for row in rows:
        mcqs.append({
            "question_id": row[0],
            "question_text": row[1],
            "correct_option": row[2],
            "options": row[3]
        })

    return jsonify(mcqs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

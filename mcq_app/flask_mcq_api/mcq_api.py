from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os


class MCQAPI:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)

        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        self.setup_routes()

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    def setup_routes(self):
        @self.app.route('/mcqs', methods=['GET'])
        def get_mcqs():
            return self.fetch_mcqs()

    def fetch_mcqs(self):
        subject = request.args.get('subject')
        model = request.args.get('model')

        if not subject or not model:
            return jsonify({"error": "Both subject and model are required"}), 400

        conn = self.get_connection()
        cur = conn.cursor()

        query = '''
            SELECT q.question_id, q.question_text, a.correct_option, 
                   json_agg(json_build_object('option_label', o.option_label, 'option_text', o.option_text)) AS options
            FROM questions q
            JOIN options o ON q.question_id = o.question_id
            JOIN answers a ON q.question_id = a.question_id
            JOIN subjects s ON q.subject_id = s.subject_id
            JOIN models m ON q.model_id = m.model_id
            WHERE s.subject_name = %s AND m.model_name = %s
            GROUP BY q.question_id, a.correct_option
        '''

        cur.execute(query, (subject, model))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        mcqs = [{
            "question_id": row[0],
            "question_text": row[1],
            "correct_option": row[2],
            "options": row[3]
        } for row in rows]

        return jsonify(mcqs)

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)


# --- Run the API ---
if __name__ == '__main__':
    api = MCQAPI()
    api.run()

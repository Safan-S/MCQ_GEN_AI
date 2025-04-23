from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import logging


class RatingAPI:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)

        self.setup_logging()
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        self.setup_routes()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    def setup_routes(self):
        @self.app.route('/submit_rating', methods=['POST'])
        def submit_rating():
            return self.handle_rating_submission()

    def handle_rating_submission(self):
        try:
            data = request.json
            self.logger.info(f"Received rating data: {data}")

            required_fields = [
                'model_id', 'model_name', 'subject_id', 'subject_name',
                'grammatical_fluency', 'answerability', 'complexity',
                'relevance', 'repetability', 'repetability_in_answers'
            ]

            for field in required_fields:
                if field not in data:
                    self.logger.error(f"Missing field: {field}")
                    return jsonify({"error": f"Missing field: {field}"}), 400

            values = [str(data[field]) for field in required_fields]

            conn = self.get_connection()
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

            self.logger.info("Rating submitted successfully.")
            return jsonify({"message": "Rating submitted successfully"}), 201

        except Exception as e:
            self.logger.exception("Error while submitting rating")
            return jsonify({"error": str(e)}), 500

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)


# --- Start the API ---
if __name__ == '__main__':
    api = RatingAPI()
    api.run()

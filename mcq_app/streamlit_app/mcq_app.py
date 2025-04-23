import streamlit as st
import requests

MCQ_API_URL = "https://mcq-gen-ai.onrender.com"
RATING_API_URL = "https://mcq-gen-ai-ratings.onrender.com"


class MCQApp:
    def __init__(self):
        self.subjects = [
            "Artificial Intelligence", "Data Structure", "Computer Networks", "Operating System",
            "Software Engineering", "DBMS", "Algorithms", "Web Programming", "C++", "Machine Learning"
        ]
        self.models = [
            "Google/gemini-2.0-flash",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "deepseek/deepseek-r1",
            "deepseek/deepseek-r1-zero",
            "Cohere/command-r-plus",
            "meta-llama/llama-4-maverick"
        ]
        self.subject = None
        self.model = None

    def setup_page(self):
        st.set_page_config(page_title="MCQ Practice App", layout="wide")
        st.title("MCQ Practice App")

    def select_inputs(self):
        self.subject = st.selectbox("Choose Subject", self.subjects)
        self.model = st.selectbox("Choose Model", self.models)

    def fetch_mcqs(self):
        response = requests.get(f"{MCQ_API_URL}/mcqs", params={
            "subject": self.subject,
            "model": self.model
        })
        return response

    def load_questions_button(self):
        if st.button("Load Questions"):
            response = self.fetch_mcqs()
            if response.status_code == 200:
                st.session_state.mcqs = response.json()
                st.session_state.score = 0
                st.session_state.answered = {}
                st.session_state.rated = False
            else:
                st.error("Failed to fetch questions. Check backend.")

    def render_question(self, idx, q):
        st.markdown(f"**{idx + 1}. {q['question_text']}**")
        sorted_options = sorted(q['options'], key=lambda x: x['option_label'])
        options_dict = {opt['option_label']: opt['option_text'] for opt in sorted_options}

        selected = st.radio(
            "Choose an answer:",
            [f"{label}) {text}" for label, text in options_dict.items()],
            key=f"q_{q['question_id']}",
            index=None
        )

        if selected:
            selected_label = selected.split(')')[0]
            correct_label = q["correct_option"]
            correct_text = options_dict[correct_label]

            st.session_state.answered[q['question_id']] = selected_label

            if selected_label == correct_label:
                st.success(" Correct!")
                return 1
            else:
                st.error(f" Incorrect. Correct answer: {correct_label}) {correct_text}")
        return 0

    def display_questions(self):
        if "mcqs" not in st.session_state:
            return

        mcqs = st.session_state.mcqs
        score = 0
        st.subheader(f"Total Questions: {len(mcqs)}")

        for idx, q in enumerate(mcqs):
            score += self.render_question(idx, q)
            st.markdown("---")

        st.markdown(f"### Final Score: {score} / {len(mcqs)}")

    def show_rating_form(self):
        if "mcqs" not in st.session_state or len(st.session_state.answered) != len(st.session_state.mcqs):
            return

        if st.session_state.get("rated", False):
            st.info(" You’ve already submitted a rating. Reload questions to rate again.")
            return

        st.subheader(" Rate the quality of these MCQs (1 = low, 5 = high)")

        ratings = {
            "grammatical_fluency": st.slider("Grammatical Fluency", 1, 5, 3),
            "answerability": st.slider("Answerability", 1, 5, 3),
            "complexity": st.slider("Complexity", 1, 5, 3),
            "relevance": st.slider("Relevance", 1, 5, 3),
            "repetability": st.slider("Repetability in Questions", 1, 5, 3),
            "repetability_in_answers": st.slider("Repetability in Answers", 1, 5, 3)
        }

        if st.button("Submit Ratings"):
            self.submit_rating(ratings)

    def submit_rating(self, ratings):
        payload = {
            "model_name": self.model,
            "subject_name": self.subject,
            "model_id": 1,
            "subject_id": 1,
            **ratings
        }
        response = requests.post(f"{RATING_API_URL}/submit_rating", json=payload)

        if response.status_code == 201:
            st.success(" Thanks for your feedback!")
            st.session_state.rated = True
            st.experimental_rerun()
        else:
            st.error(" Failed to submit rating. Try again.")

    def run(self):
        self.setup_page()
        self.select_inputs()
        self.load_questions_button()
        self.display_questions()
        self.show_rating_form()


def main():
    app = MCQApp()
    app.run()


main()

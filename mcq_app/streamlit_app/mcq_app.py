import streamlit as st
import requests

MCQ_API_URL = "https://mcq-api.onrender.com"
RATING_API_URL = "https://mcq-rating-api.onrender.com"

class MCQApp:
    def __init__(self):
        st.set_page_config(page_title="MCQ Practice App", layout="wide")

        self.subjects = ["Artificial Intelligence", "Data Structure", "Computer Networks", "Operating System", "Software Engineering",
                         "DBMS", "Algorithms", "Web Programing", "C++", "Machine Lerning"]
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

    def select_inputs(self):
        st.title("MCQ Practice App")
        self.subject = st.selectbox("Choose Subject", self.subjects)
        self.model = st.selectbox("Choose Model", self.models)

    def load_questions(self):
        if st.button("Load Questions"):
            response = requests.get(f"{MCQ_API_URL}/mcqs", params={
                "subject": self.subject,
                "model": self.model
            })
            if response.status_code == 200:
                st.session_state.mcqs = response.json()
                st.session_state.score = 0
                st.session_state.answered = {}
            else:
                st.error("Failed to fetch questions. Check backend.")

    def display_questions(self):
        if "mcqs" in st.session_state:
            mcqs = st.session_state.mcqs
            score = 0
            st.subheader(f"Total Questions: {len(mcqs)}")

            for idx, q in enumerate(mcqs):
                st.markdown(f"**{idx+1}. {q['question_text']}**")
                options_dict = {opt['option_label']: opt['option_text'] for opt in q['options']}

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
                        score += 1
                    else:
                        st.error(f" Incorrect. Correct answer: {correct_label}) {correct_text}")

                st.markdown("---")

            st.markdown(f"### Final Score: {score} / {len(mcqs)}")

    def show_rating_form(self):
        if "mcqs" in st.session_state and len(st.session_state.answered) == len(st.session_state.mcqs):
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
                payload = {
                    "model_name": self.model,
                    "subject_name": self.subject,
                    "model_id": 1,
                    "subject_id": 1,
                    **ratings
                }
                res = requests.post(f"{RATING_API_URL}/submit_rating", json=payload)
                if res.status_code == 201:
                    st.success(" Thanks for your feedback!")
                else:
                    st.error(" Failed to submit rating. Try again.")

    def run(self):
        self.select_inputs()
        self.load_questions()
        self.display_questions()
        self.show_rating_form()

def main():
    app = MCQApp()
    app.run()

main()

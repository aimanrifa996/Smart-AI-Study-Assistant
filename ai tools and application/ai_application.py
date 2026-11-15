
import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Updated Gemini model
MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(
    page_title="Smart AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)


# ==========================================
# 2. GEMINI API CONNECTION
# ==========================================

@st.cache_resource
def get_client():
    if not API_KEY:
        return None

    return genai.Client(api_key=API_KEY)


client = get_client()


def ask_gemini(prompt):

    if client is None:
        return "ERROR: API key not found. Check your .env file."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response.text:
            return response.text

        return "The AI returned an empty response."

    except Exception as error:
        return f"ERROR: {str(error)}"


# ==========================================
# 3. APPLICATION HEADER
# ==========================================

st.title("🎓 Smart AI Study Assistant")

st.write(
    "Your AI-powered learning companion for studying, "
    "understanding concepts, coding and exam preparation."
)

st.divider()


# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("📚 Navigation")

page = st.sidebar.radio(
    "Choose a feature",
    [
        "Dashboard",
        "AI Chat Assistant",
        "Explain Concepts",
        "Notes Summarizer",
        "Quiz Generator",
        "Coding Assistant"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Powered by Google Gemini AI")


# ==========================================
# 5. DASHBOARD
# ==========================================

if page == "Dashboard":

    st.header("Welcome to your AI Study Assistant!")

    st.write(
        "Learn smarter with AI-powered tools designed "
        "to make studying easier and more productive."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "💬 **AI Chat Assistant**\n\n"
            "Ask questions and get AI-generated answers."
        )

        st.info(
            "📖 **Explain Concepts**\n\n"
            "Understand difficult topics in simple language."
        )

        st.info(
            "📝 **Notes Summarizer**\n\n"
            "Convert lengthy notes into concise summaries."
        )

    with col2:
        st.info(
            "❓ **Quiz Generator**\n\n"
            "Generate practice questions for your subjects."
        )

        st.info(
            "💻 **Coding Assistant**\n\n"
            "Understand code and identify programming errors."
        )

    if client:
        st.success("Gemini API client initialized.")
    else:
        st.error("Gemini API key is missing. Check your .env file.")


# ==========================================
# 6. AI CHAT ASSISTANT
# ==========================================

elif page == "AI Chat Assistant":

    st.header("💬 AI Chat Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask your study question...")

    if user_input:

        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        conversation = "\n".join(
            f'{m["role"]}: {m["content"]}'
            for m in st.session_state.chat_history
        )

        prompt = f"""
        You are a helpful AI study assistant.

        Answer questions accurately and clearly.
        Use simple language and examples where appropriate.

        Conversation:
        {conversation}
        """

        with st.chat_message("assistant"):

            with st.spinner("Gemini is thinking..."):
                answer = ask_gemini(prompt)

            st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )


# ==========================================
# 7. EXPLAIN CONCEPTS
# ==========================================

elif page == "Explain Concepts":

    st.header("📖 Explain Concepts")

    topic = st.text_input(
        "Enter a topic you want to understand"
    )

    level = st.selectbox(
        "Choose explanation level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button("Explain Topic"):

        if not topic.strip():
            st.warning("Please enter a topic.")

        else:

            prompt = f"""
            Explain the following topic: {topic}

            Explanation level: {level}

            Include:
            1. Simple definition
            2. Detailed explanation
            3. Real-life example
            4. Important points
            5. Short conclusion

            Make the explanation accurate and easy to understand.
            """

            with st.spinner("Generating explanation..."):
                answer = ask_gemini(prompt)

            st.markdown(answer)


# ==========================================
# 8. NOTES SUMMARIZER
# ==========================================

elif page == "Notes Summarizer":

    st.header("📝 Notes Summarizer")

    notes = st.text_area(
        "Paste your study notes here",
        height=250,
        placeholder="Paste your notes here..."
    )

    if st.button("Summarize Notes"):

        if not notes.strip():
            st.warning("Please enter your notes.")

        else:

            prompt = f"""
            Summarize these study notes.

            Organize the result into:

            1. Main topic
            2. Short summary
            3. Important points
            4. Key terms and definitions
            5. Final revision points

            Notes:
            {notes}
            """

            with st.spinner("Summarizing your notes..."):
                answer = ask_gemini(prompt)

            st.markdown(answer)


# ==========================================
# 9. QUIZ GENERATOR
# ==========================================

elif page == "Quiz Generator":

    st.header("❓ Quiz Generator")

    topic = st.text_input("Enter a quiz topic")

    number = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("Generate Quiz"):

        if not topic.strip():
            st.warning("Please enter a topic.")

        else:

            prompt = f"""
            Generate exactly {number} multiple-choice questions
            about {topic}.

            Return ONLY valid JSON in this format:

            {{
                "questions": [
                    {{
                        "question": "Question text",
                        "options": [
                            "Option A",
                            "Option B",
                            "Option C",
                            "Option D"
                        ],
                        "answer": "Option A",
                        "explanation": "Explanation of the answer"
                    }}
                ]
            }}

            The answer must exactly match one of the four options.
            """

            with st.spinner("Creating your quiz..."):
                result = ask_gemini(prompt)

            try:

                if result.startswith("ERROR:"):
                    raise ValueError(result)

                cleaned = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    result.strip(),
                    flags=re.IGNORECASE
                )

                quiz = json.loads(cleaned)

                questions = quiz["questions"]

                if len(questions) != number:
                    raise ValueError("Incorrect number of questions.")

                for question in questions:

                    if (
                        len(question["options"]) != 4
                        or question["answer"] not in question["options"]
                    ):
                        raise ValueError("Invalid question format.")

                st.session_state.quiz = quiz
                st.session_state.quiz_submitted = False

            except Exception as error:
                st.error(f"Could not create a valid quiz: {error}")

    if "quiz" in st.session_state:

        st.divider()
        st.subheader("Your Practice Quiz")

        if not st.session_state.get("quiz_submitted", False):

            with st.form("quiz_form"):

                answers = []

                for i, question in enumerate(
                    st.session_state.quiz["questions"]
                ):

                    st.markdown(
                        f"**Question {i + 1}: {question['question']}**"
                    )

                    answer = st.radio(
                        "Choose your answer:",
                        question["options"],
                        key=f"quiz_answer_{i}"
                    )

                    answers.append(answer)

                submitted = st.form_submit_button("Submit Quiz")

            if submitted:

                score = 0

                for i, question in enumerate(
                    st.session_state.quiz["questions"]
                ):

                    if answers[i] == question["answer"]:
                        score += 1

                st.session_state.quiz_score = score
                st.session_state.quiz_answers = answers
                st.session_state.quiz_submitted = True

                st.rerun()

        else:

            questions = st.session_state.quiz["questions"]
            score = st.session_state.quiz_score

            st.success(
                f"Your Score: {score} / {len(questions)}"
            )

            for i, question in enumerate(questions):

                st.markdown(
                    f"**Question {i + 1}: {question['question']}**"
                )

                st.write(
                    "Your answer:",
                    st.session_state.quiz_answers[i]
                )

                st.write(
                    "Correct answer:",
                    question["answer"]
                )

                st.caption(question["explanation"])
                st.divider()

            if st.button("Generate Another Quiz"):

                del st.session_state.quiz
                st.session_state.quiz_submitted = False

                st.rerun()


# ==========================================
# 10. CODING ASSISTANT
# ==========================================

elif page == "Coding Assistant":

    st.header("💻 Coding Assistant")

    language = st.selectbox(
        "Select programming language",
        [
            "Python",
            "Java",
            "C",
            "HTML",
            "CSS",
            "JavaScript"
        ]
    )

    task = st.selectbox(
        "What do you need help with?",
        [
            "Explain Code",
            "Find and Fix Errors",
            "Write Code",
            "Improve Code"
        ]
    )

    code = st.text_area(
        "Enter your code or programming question",
        height=250
    )

    if st.button("Get Coding Help"):

        if not code.strip():
            st.warning("Please enter code or a question.")

        else:

            prompt = f"""
            You are an experienced programming assistant.

            Programming language: {language}
            User request: {task}

            Help the user with the following:

            {code}

            Explain your solution clearly.

            If correcting code:
            1. Identify the problem.
            2. Provide corrected code.
            3. Explain the changes.

            Do not claim to execute code that you have not executed.
            """

            with st.spinner("Analyzing your code..."):
                answer = ask_gemini(prompt)

            st.markdown(answer)


# ==========================================
# 11. FOOTER
# ==========================================

st.divider()

st.caption(
    "Smart AI Study Assistant | "
    "Built with Python, Streamlit and Google Gemini AI"
)

import streamlit as st
from pypdf import PdfReader
import random
import re
from datetime import datetime
import pandas as pd


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="StudyMeta AI",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "score_history" not in st.session_state:
    st.session_state.score_history = []

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""


# =========================================================
# HEADER
# =========================================================

st.title("📚 StudyMeta AI")

st.write(
    "Your smart study companion for PDF learning, "
    "question answering and quizzes."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Study Settings")

    difficulty = st.selectbox(
        "Choose difficulty",
        ["Easy", "Medium", "Hard"]
    )

    question_count = st.slider(
        "Quiz questions",
        3,
        10,
        5
    )

    st.divider()

    st.header("📊 Quiz History")

    if st.session_state.score_history:

        for i, result in enumerate(
            reversed(st.session_state.score_history),
            1
        ):

            st.write(
                f"Attempt {i}: "
                f"{result['score']}/{result['total']} "
                f"({result['percentage']:.0f}%)"
            )

    else:

        st.info("No quiz attempts yet.")


# =========================================================
# PDF UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📄 Upload your study PDF",
    type=["pdf"]
)


if uploaded_file is None:

    st.info("👆 Upload a PDF to start studying.")

    st.subheader("✨ What can StudyMeta AI do?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("📄 **PDF Reader**")
        st.write("Read and search your study material.")

    with col2:
        st.write("🤖 **Ask Questions**")
        st.write("Ask questions based on your PDF.")

    with col3:
        st.write("🎯 **Quiz**")
        st.write("Practice and track your score.")

    st.stop()


# =========================================================
# READ PDF
# =========================================================

try:

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

except Exception as e:

    st.error(f"Could not read PDF: {e}")
    st.stop()


if not text.strip():

    st.error("⚠️ No readable text found in this PDF.")
    st.stop()


st.session_state.pdf_text = text


# =========================================================
# PDF INFORMATION
# =========================================================

page_count = len(reader.pages)
word_count = len(text.split())


col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📄 Pages", page_count)

with col2:
    st.metric("📝 Words", word_count)

with col3:
    st.metric("🎚️ Level", difficulty)


st.divider()


# =========================================================
# PREPARE TEXT
# =========================================================

clean_text = text.replace("\n", " ")

paragraphs = [
    p.strip()
    for p in re.split(r"\n\s*\n", text)
    if len(p.split()) >= 5
]

sentences = re.split(
    r"(?<=[.!?])\s+",
    clean_text
)

sentences = [
    s.strip()
    for s in sentences
    if len(s.split()) >= 7
]


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📖 PDF Reader",
        "🤖 Ask StudyMeta",
        "📚 Summary",
        "❓ Questions",
        "🎯 Quiz",
        "📊 History"
    ]
)


# =========================================================
# TAB 1 - PDF READER
# =========================================================

with tab1:

    st.header("📖 PDF Reader")

    search = st.text_input(
        "🔎 Search something in your PDF"
    )

    if search:

        pattern = re.compile(
            re.escape(search),
            re.IGNORECASE
        )

        matches = list(
            pattern.finditer(text)
        )

        st.write(
            f"Found **{len(matches)}** occurrence(s)."
        )

        if matches:

            start = max(
                0,
                matches[0].start() - 500
            )

            end = min(
                len(text),
                matches[0].end() + 1000
            )

            st.info(
                text[start:end]
            )

        else:

            st.warning(
                "This word/topic was not found in the PDF."
            )

    else:

        st.text_area(
            "PDF Text",
            text[:20000],
            height=450
        )


# =========================================================
# TAB 2 - ASK STUDYMETА
# =========================================================

with tab2:

    st.header("🤖 Ask StudyMeta AI")

    st.write(
        "Ask a question about your uploaded PDF."
    )

    st.caption(
        "Example: What is process scheduling? "
        "Explain it in detail."
    )

    user_question = st.text_input(
        "💬 Your question"
    )

    if st.button("🔍 Find Answer"):

        if not user_question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            # -----------------------------------------
            # Extract important keywords
            # -----------------------------------------

            stop_words = {
                "what", "is", "are", "the", "a", "an",
                "of", "in", "on", "to", "for", "and",
                "or", "how", "why", "explain", "define",
                "tell", "me", "about", "with", "from"
            }

            question_words = re.findall(
                r"\b[a-zA-Z]{3,}\b",
                user_question.lower()
            )

            keywords = [
                word
                for word in question_words
                if word not in stop_words
            ]

            # -----------------------------------------
            # Find relevant sentences
            # -----------------------------------------

            scored_sentences = []

            for sentence in sentences:

                sentence_lower = sentence.lower()

                score = sum(
                    sentence_lower.count(keyword)
                    for keyword in keywords
                )

                if score > 0:

                    scored_sentences.append(
                        (score, sentence)
                    )

            scored_sentences.sort(
                reverse=True
            )

            relevant = [
                sentence
                for score, sentence
                in scored_sentences[:5]
            ]

            # -----------------------------------------
            # ANSWER
            # -----------------------------------------

            if relevant:

                st.success(
                    f"Found relevant information for: "
                    f"**{user_question}**"
                )

                st.subheader("📖 Detailed Answer")

                st.write(
                    "Based on the information available "
                    "in your uploaded PDF:"
                )

                for sentence in relevant:

                    st.write(
                        "• " + sentence
                    )

                # -------------------------------------
                # KEY POINTS
                # -------------------------------------

                st.subheader("💡 Key Points")

                for sentence in relevant[:3]:

                    st.markdown(
                        f"- {sentence}"
                    )

                # -------------------------------------
                # EXAM ANSWER
                # -------------------------------------

                st.subheader(
                    "📝 Exam-Oriented Answer"
                )

                exam_answer = (
                    f"**Definition:** "
                    f"The topic asked is related to "
                    f"{', '.join(keywords[:5])}.\n\n"
                )

                exam_answer += (
                    "**Explanation:** "
                    + " ".join(relevant[:3])
                )

                st.markdown(
                    exam_answer
                )

                # -------------------------------------
                # SOURCE
                # -------------------------------------

                st.subheader(
                    "📌 Source from PDF"
                )

                for sentence in relevant:

                    st.info(sentence)

            else:

                st.warning(
                    "I couldn't find a matching topic "
                    "in this PDF."
                )

                st.write(
                    "Try using important keywords from "
                    "your study material."
                )


# =========================================================
# TAB 3 - SUMMARY
# =========================================================

with tab3:

    st.header("📚 Study Summary")

    words = text.split()

    summary = " ".join(
        words[:300]
    )

    if len(words) > 300:

        summary += "..."

    st.write(summary)

    st.divider()

    st.download_button(
        "⬇️ Download Summary",
        data=summary,
        file_name="StudyMeta_Summary.txt",
        mime="text/plain"
    )


# =========================================================
# TAB 4 - PRACTICE QUESTIONS
# =========================================================

with tab4:

    st.header("❓ Practice Questions")

    if not sentences:

        st.warning(
            "Not enough text to create questions."
        )

    else:

        for i, sentence in enumerate(
            sentences[:10],
            1
        ):

            st.write(
                f"### Q{i}. Explain this:"
            )

            st.info(sentence)


# =========================================================
# QUIZ FUNCTION
# =========================================================

def create_quiz(sentence_list, count):

    selected = random.sample(
        sentence_list,
        min(count, len(sentence_list))
    )

    quiz = {}

    for i, correct in enumerate(selected):

        wrong = [
            "This information is unrelated to the topic.",
            "This statement is not mentioned in the study material.",
            "This describes a completely different concept."
        ]

        options = [correct] + wrong

        random.shuffle(options)

        quiz[i] = {
            "question": correct,
            "correct": correct,
            "options": options
        }

    return quiz


# =========================================================
# TAB 5 - QUIZ
# =========================================================

with tab5:

    st.header("🎯 Quiz Mode")

    st.write(
        f"Difficulty: **{difficulty}**"
    )

    if len(sentences) < 3:

        st.warning(
            "Upload a PDF with enough readable text."
        )

    else:

        if st.button("🔄 Generate New Quiz"):

            st.session_state.quiz_data = create_quiz(
                sentences,
                question_count
            )

            st.session_state.quiz_submitted = False

            st.rerun()


        if st.session_state.quiz_data is None:

            st.session_state.quiz_data = create_quiz(
                sentences,
                question_count
            )


        quiz_data = st.session_state.quiz_data

        answers = {}

        for i, data in quiz_data.items():

            st.write(
                f"### Question {i + 1}"
            )

            st.write(
                "Which statement is taken from your PDF?"
            )

            answers[i] = st.radio(
                "Choose:",
                data["options"],
                key=f"quiz_{i}"
            )

            st.divider()


        if st.button("🚀 Submit Quiz"):

            score = 0

            for i, data in quiz_data.items():

                if answers[i] == data["correct"]:

                    score += 1

            total = len(quiz_data)

            percentage = (
                score / total
            ) * 100

            result = {
                "date": datetime.now().strftime(
                    "%d-%m-%Y %H:%M"
                ),
                "score": score,
                "total": total,
                "percentage": percentage,
                "difficulty": difficulty
            }

            st.session_state.score_history.append(
                result
            )

            st.session_state.last_score = score
            st.session_state.last_total = total
            st.session_state.last_answers = answers

            st.session_state.quiz_submitted = True

            st.rerun()


        if st.session_state.quiz_submitted:

            score = st.session_state.last_score
            total = st.session_state.last_total

            percentage = (
                score / total
            ) * 100

            st.divider()

            st.subheader("📊 Your Result")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Score",
                    f"{score}/{total}"
                )

            with c2:
                st.metric(
                    "Percentage",
                    f"{percentage:.0f}%"
                )

            with c3:
                st.metric(
                    "Level",
                    difficulty
                )


            if percentage == 100:

                st.success(
                    "🎉 Perfect Score!"
                )

            elif percentage >= 60:

                st.info(
                    "👍 Good job! Keep practicing."
                )

            else:

                st.warning(
                    "📖 Review your PDF and try again."
                )


            st.subheader(
                "✅ Answer Review"
            )

            for i, data in quiz_data.items():

                user_answer = (
                    st.session_state.last_answers[i]
                )

                if user_answer == data["correct"]:

                    st.success(
                        f"Q{i + 1}: Correct ✅"
                    )

                else:

                    st.error(
                        f"Q{i + 1}: Incorrect ❌"
                    )

                    st.write(
                        "Correct answer:",
                        data["correct"]
                    )


# =========================================================
# TAB 6 - HISTORY
# =========================================================

with tab6:

    st.header("📊 Quiz History")

    if not st.session_state.score_history:

        st.info(
            "No quiz attempts yet."
        )

    else:

        history_df = pd.DataFrame(
            st.session_state.score_history
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

        average = history_df[
            "percentage"
        ].mean()

        st.metric(
            "📈 Average Score",
            f"{average:.1f}%"
        )

        csv = history_df.to_csv(
            index=False
        )

        st.download_button(
            "⬇️ Download History",
            csv,
            file_name="StudyMeta_Quiz_History.csv",
            mime="text/csv"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📚 StudyMeta AI | Python + Streamlit + PyPDF + Pandas"
)
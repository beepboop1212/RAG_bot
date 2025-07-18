# quiz.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import os
from typing import List, Optional, Dict, Any

# Pydantic Model for Structured Output
from pydantic import BaseModel, Field, field_validator

# ... (QuizItem class definition remains the same as before) ...
class QuizItem(BaseModel):
    question: str = Field(description="The quiz question.")
    options: List[str] = Field(description="A list of 4 multiple choice options, or an empty list if no new question can be generated.")
    answer: int = Field(description="The 0-indexed integer of the correct option in the 'options' list, or 0 if no new question can be generated.")
    explanation: str = Field(
        description="A brief, factual explanation of why the correct answer is correct, directly derived from the provided text. Avoid meta-references to the text itself (e.g., 'the document states', 'according to the text'). If no new question, this explains why."
    )

    @field_validator('options')
    @classmethod
    def check_options_length(cls, v: List[str], values) -> List[str]:
        question_data = values.data.get('question')
        if not isinstance(v, list):
            raise ValueError("Options must be a list.")
        if question_data == "NO_NEW_QUESTION":
            if v:
                raise ValueError("Options list must be empty when question is 'NO_NEW_QUESTION'.")
            return v
        if len(v) != 4:
            raise ValueError("Options list must contain exactly 4 items for a regular question.")
        if not all(isinstance(opt, str) for opt in v):
            raise ValueError("All options must be strings.")
        return v

    @field_validator('answer')
    @classmethod
    def check_answer_index(cls, v: int, values) -> int:
        options_data = values.data.get('options')
        question_data = values.data.get('question')
        if question_data == "NO_NEW_QUESTION":
            if not options_data and v == 0:
                return v
            else:
                raise ValueError("For 'NO_NEW_QUESTION', answer must be 0 and options empty.")
        if options_data:
            num_options = len(options_data)
            if not (0 <= v < num_options):
                raise ValueError(f"Answer index must be between 0 and {num_options - 1}.")
        else:
             raise ValueError("Options are missing for a regular question, cannot validate answer index.")
        return v

# Load environment variables
load_dotenv()

# --- Caching ---
# ... (get_llm and fetch_website_content functions remain the same) ...
@st.cache_resource
def get_llm():
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("GOOGLE_API_KEY not found. Please set it in your .env file or environment.")
        return None
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
        return llm
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_website_content(_url: str):
    st.info(f"Fetching content from: {_url}")
    try:
        headers = {"User-Agent": "QuizrApp/1.0 (StreamlitQuizBot/contact@example.com)"}
        loader = WebBaseLoader(_url, requests_kwargs={"headers": headers})
        docs = loader.load()
        if not docs:
            st.warning("Could not fetch any content from the URL.")
            return None
        full_text = "\n\n".join([doc.page_content for doc in docs])
        max_chars_for_quiz = 100000
        if len(full_text) > max_chars_for_quiz:
            st.info(f"Content is long ({len(full_text):,} chars). Using the first {max_chars_for_quiz:,} characters for quiz generation.")
            return full_text[:max_chars_for_quiz]
        return full_text
    except Exception as e:
        st.error(f"Error fetching website content: {e}")
        return None

# --- Quiz Generation Logic ---
# ... (generate_quiz_from_text function remains the same) ...
def generate_quiz_from_text(text_content: str, llm, asked_questions_texts: List[str]):
    if not llm: return None
    parser = PydanticOutputParser(pydantic_object=QuizItem)
    asked_questions_list_str = "\n".join([f"- {q}" for q in asked_questions_texts]) if asked_questions_texts else "N/A (this is the first question)"
    prompt_template_str = """
    You are an expert quiz generator. Based on the following text, generate ONE new multiple-choice quiz question.
    The question must be answerable SOLELY from the provided text.
    The question should have exactly 4 options.
    Indicate the correct answer (as a 0-indexed integer).
    Provide a brief, factual explanation for why the correct answer is correct, directly derived from the text.
    The explanation must NOT include phrases like 'the text states', 'according to the document', 'as mentioned in the passage', etc. Just state the facts supporting the answer.

    IMPORTANT: DO NOT generate any of the following questions, as they have already been asked:
    --- PREVIOUSLY ASKED QUESTIONS ---
    {asked_questions_list_str}
    --- END PREVIOUSLY ASKED QUESTIONS ---

    If you ABSOLUTELY CANNOT generate a new, unique question (different from the list above) based on the provided text,
    then and only then, respond with the following exact JSON structure:
    {{"question": "NO_NEW_QUESTION", "options": [], "answer": 0, "explanation": "Could not generate a new unique question from the remaining text or based on the provided constraints."}}

    {format_instructions}

    Here is the text to base the quiz on:
    --- TEXT ---
    {text_content}
    --- END TEXT ---

    Your response must be a single JSON object matching the Pydantic schema.
    """
    prompt = PromptTemplate(
        template=prompt_template_str,
        input_variables=["text_content", "asked_questions_list_str"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm | parser
    try:
        with st.spinner("Generating new quiz question..."):
            quiz_item_result = chain.invoke({
                "text_content": text_content,
                "asked_questions_list_str": asked_questions_list_str
            })
        if quiz_item_result.question == "NO_NEW_QUESTION":
            st.warning("Could not generate a new unique question. The content might be exhausted, or all relevant questions have been asked.")
            return None
        return quiz_item_result
    except Exception as e:
        st.error(f"Error generating or parsing quiz: {e}")
        try:
            raw_output_chain = prompt | llm
            raw_output = raw_output_chain.invoke({
                "text_content": text_content,
                "asked_questions_list_str": asked_questions_list_str
            })
            st.warning("LLM raw output (if parsing failed):")
            st.code(raw_output.content if hasattr(raw_output, 'content') else str(raw_output), language="json")
        except Exception as raw_e:
            st.error(f"Could not get raw output: {raw_e}")
        return None

# --- Streamlit App UI & State Management ---
st.set_page_config(page_title="Website Quizzer Deluxe", layout="wide")
st.title("📚 Website Link Quizzer Deluxe")
st.markdown("Enter a website link to start a quiz. Answer questions, see your history, and stop when you're done!")

llm = get_llm()
if not llm:
    st.warning("LLM could not be initialized. Please check your API key and console for errors, then refresh.")
    st.stop()

if 'current_url' not in st.session_state: st.session_state.current_url = ""
if 'web_content' not in st.session_state: st.session_state.web_content = None
if 'quiz_item' not in st.session_state: st.session_state.quiz_item = None
if 'user_answer_index' not in st.session_state: st.session_state.user_answer_index = None
if 'submitted_answer' not in st.session_state: st.session_state.submitted_answer = False
if 'quiz_history' not in st.session_state: st.session_state.quiz_history = []
if 'asked_questions_texts' not in st.session_state: st.session_state.asked_questions_texts = []
if 'quiz_active' not in st.session_state: st.session_state.quiz_active = False
if 'form_key_suffix' not in st.session_state: st.session_state.form_key_suffix = 0

# --- HELPER FUNCTIONS (Define display_history HERE) ---
def display_history():
    """Helper to display the quiz history."""
    for i, record in enumerate(reversed(st.session_state.quiz_history)): # Show newest first
        container = st.container(border=True)
        container.markdown(f"**{len(st.session_state.quiz_history) - i}. {record['question']}**")
        container.markdown(f"Your Answer: _{record['user_answer_text']}_")
        if record['is_correct']:
            container.success(f"Result: Correct (Correct Answer: *{record['correct_answer_text']}*)")
        else:
            container.error(f"Result: Incorrect (Correct Answer: *{record['correct_answer_text']}*)")
        container.caption(f"Explanation: {record['explanation']}")

def reset_quiz_session():
    st.session_state.web_content = None
    st.session_state.quiz_item = None
    st.session_state.user_answer_index = None
    st.session_state.submitted_answer = False
    st.session_state.quiz_history = []
    st.session_state.asked_questions_texts = []
    st.session_state.quiz_active = False
    st.session_state.form_key_suffix += 1

def add_to_history(quiz_item: QuizItem, user_idx: int, is_correct: bool):
    history_entry = {
        "question": quiz_item.question,
        "options": quiz_item.options,
        "user_answer_text": quiz_item.options[user_idx] if user_idx is not None and 0 <= user_idx < len(quiz_item.options) else "N/A",
        "correct_answer_text": quiz_item.options[quiz_item.answer],
        "correct_answer_index": quiz_item.answer,
        "is_correct": is_correct,
        "explanation": quiz_item.explanation
    }
    st.session_state.quiz_history.append(history_entry)
    if quiz_item.question not in st.session_state.asked_questions_texts and quiz_item.question != "NO_NEW_QUESTION":
        st.session_state.asked_questions_texts.append(quiz_item.question)

def load_new_question():
    if st.session_state.web_content and llm:
        st.session_state.quiz_item = generate_quiz_from_text(
            st.session_state.web_content,
            llm,
            st.session_state.asked_questions_texts
        )
        st.session_state.user_answer_index = None
        st.session_state.submitted_answer = False
        st.session_state.form_key_suffix += 1
        if st.session_state.quiz_item is None:
            st.session_state.quiz_active = False
            st.warning("No more unique questions could be generated for this content. Quiz ended.")
    else:
        st.session_state.quiz_active = False # Ensure quiz is not active if content is missing

# --- UI FOR URL INPUT AND STARTING QUIZ ---
# ... (This part remains the same) ...
url_input_col, start_button_col = st.columns([3,1])
with url_input_col:
    url = st.text_input(
        "Enter Website URL:",
        value=st.session_state.current_url,
        key=f"url_input_{st.session_state.form_key_suffix}"
    )
with start_button_col:
    if st.button("Start/New Quiz from URL", key="start_quiz_btn", use_container_width=True, type="primary"):
        if url:
            if url != st.session_state.current_url or not st.session_state.quiz_active:
                reset_quiz_session()
                st.session_state.current_url = url
                st.session_state.web_content = fetch_website_content(url)
                if st.session_state.web_content:
                    st.session_state.quiz_active = True
                    load_new_question()
                    st.rerun() # Rerun to show the first question immediately
                else:
                    st.error("Failed to fetch content. Cannot start quiz.")
        else:
            st.warning("Please enter a URL.")

st.markdown("---")

# --- UI FOR ACTIVE QUIZ (QUESTION, OPTIONS, SUBMIT) ---
# ... (This part remains the same) ...
if st.session_state.quiz_active and st.session_state.quiz_item:
    quiz = st.session_state.quiz_item
    st.subheader("🧠 Quiz Time!")
    st.markdown(f"**Question {len(st.session_state.quiz_history) + 1}:** {quiz.question}")

    form_key = f"quiz_form_{st.session_state.form_key_suffix}"
    with st.form(key=form_key):
        options_with_indices = [f"{i+1}. {opt}" for i, opt in enumerate(quiz.options)]
        user_choice_display = st.radio(
            "Choose your answer:",
            options=options_with_indices,
            index=st.session_state.user_answer_index,
            key=f"radio_{form_key}"
        )
        submit_button = st.form_submit_button("Submit Answer", use_container_width=True)

    if submit_button:
        if user_choice_display:
            st.session_state.user_answer_index = options_with_indices.index(user_choice_display)
            st.session_state.submitted_answer = True
            st.rerun() # Rerun to show results immediately
        else:
            st.warning("Please select an answer before submitting.")
            st.session_state.submitted_answer = False

# --- UI FOR DISPLAYING RESULT OF SUBMITTED ANSWER ---
# ... (This part remains the same) ...
if st.session_state.submitted_answer and st.session_state.quiz_item:
    quiz = st.session_state.quiz_item
    user_idx = st.session_state.user_answer_index
    is_correct = (user_idx == quiz.answer)

    last_history_q = st.session_state.quiz_history[-1]["question"] if st.session_state.quiz_history else None
    if quiz.question != last_history_q: # Add to history only if it's a new submission for this question
         add_to_history(quiz, user_idx, is_correct)

    if is_correct:
        st.success(f"🎉 Correct! Your answer: **{quiz.options[user_idx]}**")
    else:
        st.error(f"😢 Incorrect. Your answer: **{quiz.options[user_idx]}**. Correct answer was: **{quiz.options[quiz.answer]}**")
    st.info(f"**Explanation:** {quiz.explanation}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Question", key="next_q_btn", use_container_width=True, type="primary",
                      disabled=not st.session_state.quiz_active):
            st.session_state.submitted_answer = False
            load_new_question()
            st.rerun()
    with col2:
        if st.button("Stop Quiz", key="stop_quiz_after_answer", use_container_width=True):
            st.session_state.quiz_active = False
            st.session_state.submitted_answer = False
            st.info("Quiz stopped.")
            st.rerun()

# --- UI FOR "STOP QUIZ" BUTTON (if quiz is active but no answer submitted yet) ---
# ... (This part remains the same) ...
elif st.session_state.quiz_active and not st.session_state.submitted_answer and st.session_state.quiz_item:
    if st.button("Stop Quiz", key="stop_quiz_main", use_container_width=True):
        st.session_state.quiz_active = False
        st.info("Quiz stopped.")
        st.rerun()

# --- UI FOR QUIZ SUMMARY (when quiz is not active but history exists) ---
# ... (This part remains the same) ...
if not st.session_state.quiz_active and st.session_state.quiz_history:
    st.subheader("🏁 Quiz Summary & History")
    correct_answers = sum(1 for item in st.session_state.quiz_history if item["is_correct"])
    total_questions = len(st.session_state.quiz_history)
    if total_questions > 0:
        score_percent = (correct_answers / total_questions) * 100
        st.metric(label="Your Score", value=f"{correct_answers}/{total_questions}", delta=f"{score_percent:.1f}%")
        
        # --- ADDED CODE: Display history here ---
        st.markdown("---") # Optional separator
        st.subheader("📜 Detailed Quiz History") # Or just keep the existing header from display_history
        display_history()
    else:
        st.info("No questions were answered in this session.")

# --- UI FOR DISPLAYING QUIZ HISTORY (Calls the now-defined display_history) ---
if st.session_state.quiz_history:
    if st.session_state.quiz_active :
         with st.expander("📜 View Quiz History", expanded=False):
            display_history() # CALLING THE FUNCTION
    elif not st.session_state.quiz_item and not st.session_state.quiz_active : # Show only if quiz fully stopped & no active q
        st.subheader("📜 Final Quiz History")
        display_history() # CALLING THE FUNCTION

# # --- Footer ---
# # ... (This part remains the same) ...
# st.markdown("---")
# st.markdown("Powered by Langchain & Google Gemini Flash. Features: Non-repeating questions, history, stop quiz.")
# frontend/app.py
import streamlit as st
from api_client import (
    login_user,
    get_user_sessions,
    create_new_session,
    get_session_details,
    get_session_messages_from_api, # New import
    send_message_to_backend      # New import
)
from datetime import datetime

# --- Page Configuration and Session State Initialization (EXISTING CODE) ---
st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "user_sessions" not in st.session_state:
    st.session_state.user_sessions = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "current_session_details" not in st.session_state:
    st.session_state.current_session_details = None
# chat_messages will store dicts like: {"sender_type": "user", "content": "hello"}
# or directly the dicts received from the backend which include "id", "timestamp" etc.
if "chat_messages" not in st.session_state: # For displaying messages in the current chat
    st.session_state.chat_messages = []


# --- Utility to load messages for current session ---
def load_chat_messages_for_session():
    if st.session_state.current_session_id:
        messages = get_session_messages_from_api(st.session_state.current_session_id)
        if messages is not None:
            st.session_state.chat_messages = messages
        else:
            st.session_state.chat_messages = [] # Reset if loading fails
            # Error is displayed by api_client
    else:
        st.session_state.chat_messages = []


# --- Main Application Logic (EXISTING CODE) ---
def main():
    st.title("🤖 Gemini Powered Chatbot")
    if not st.session_state.logged_in:
        render_login_page()
    else:
        if not st.session_state.user_sessions and st.session_state.user_info:
            load_user_sessions() # Load user's sessions if not already loaded
        
        # If a session is selected, load its messages
        # This needs to be smart about when to reload (e.g. on session switch)
        # The session switch logic already handles clearing messages, so this might be redundant here
        # and better placed inside the session selection logic.

        render_main_app_layout()

# --- Login Page (EXISTING CODE) ---
def render_login_page():
    st.subheader("Welcome! Please log in or sign up.")
    with st.form("login_form"):
        name = st.text_input("Your Name", key="login_name_main_v2")
        topic = st.text_input("Topic of Interest", key="login_topic_main_v2")
        submitted = st.form_submit_button("Login / Register")

        if submitted:
            if not name or not topic:
                st.warning("Please enter both your name and topic of interest.")
            else:
                user_data = login_user(name, topic)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_info = user_data
                    st.session_state.user_sessions = []
                    st.session_state.current_session_id = None
                    st.session_state.current_session_details = None
                    st.session_state.chat_messages = []
                    st.success(f"Welcome, {user_data['name']}! You are logged in.")
                    st.rerun()

# --- Load User Sessions (EXISTING CODE) ---
def load_user_sessions():
    if st.session_state.user_info:
        user_id = st.session_state.user_info.get("id")
        if user_id:
            sessions_data = get_user_sessions(user_id)
            if sessions_data is not None:
                st.session_state.user_sessions = sessions_data
            else:
                st.session_state.user_sessions = []

# --- Main App Layout (after login) ---
def render_main_app_layout():
    st.sidebar.header(f"User: {st.session_state.user_info['name']}")
    st.sidebar.caption(f"Topic: {st.session_state.user_info['topic_of_interest']}")
    st.sidebar.markdown("---")

    if st.sidebar.button("Logout", key="logout_button_sidebar_v2"):
        # ... (logout logic - reset session state) ...
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.user_sessions = []
        st.session_state.current_session_id = None
        st.session_state.current_session_details = None
        st.session_state.chat_messages = []
        st.info("You have been logged out.")
        st.rerun()

    st.sidebar.subheader("Chat Sessions")
    new_session_name = st.sidebar.text_input("New session name (optional)", key="new_session_name_input_v2")
    if st.sidebar.button("✨ Create New Session", key="create_session_button_v2"):
        if st.session_state.user_info:
            user_id = st.session_state.user_info["id"]
            new_session = create_new_session(user_id, new_session_name if new_session_name else "New Chat")
            if new_session:
                st.sidebar.success(f"Session '{new_session['session_name']}' created!")
                load_user_sessions() # Reload sessions list
                # Automatically select the new session
                st.session_state.current_session_id = new_session['id']
                st.session_state.current_session_details = new_session
                load_chat_messages_for_session() # Load (empty) messages for the new session
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write("Your Chats:")

    if not st.session_state.user_sessions:
        st.sidebar.info("No chat sessions yet. Create one!")
    else:
        for session in st.session_state.user_sessions:
            session_display_name = session.get('session_name', f"Session {session['id']}")
            try:
                created_at_dt = datetime.fromisoformat(session['created_at'].replace('Z', '+00:00'))
                created_at_str = created_at_dt.strftime("%b %d, %H:%M") # Shorter format
            except:
                created_at_str = session.get('created_at', 'N/A')

            button_label = f"{session_display_name} ({created_at_str})"
            if st.sidebar.button(button_label, key=f"session_btn_{session['id']}_v2"):
                if st.session_state.current_session_id != session['id']:
                    st.session_state.current_session_id = session['id']
                    st.session_state.current_session_details = session
                    load_chat_messages_for_session() # Load messages for the selected session
                    st.rerun()

    # --- Main Chat Area ---
    if st.session_state.current_session_id and st.session_state.current_session_details:
        render_chat_interface(st.session_state.current_session_details)
    else:
        st.info("👈 Select a session from the sidebar or create a new one to start chatting.")


# --- MODIFIED Chat Interface ---
def render_chat_interface(session_details):
    st.header(f"{session_details.get('session_name', 'Chat')}") # Simpler header
    # st.caption(f"Session ID: {session_details['id']} | Created: ...") # Optional: Can be less prominent

    # Display existing chat messages
    # st.session_state.chat_messages now contains dicts from backend
    for msg in st.session_state.chat_messages:
        # Backend 'sender_type' should be 'user' or 'ai'
        # Streamlit chat_message expects 'user' or 'assistant' for role
        role = "user" if msg.get("sender_type") == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.get("content", "*empty message*")) # Use markdown for better formatting
            # Optionally display timestamp
            # if "timestamp" in msg:
            #     ts = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).strftime('%H:%M:%S')
            #     st.caption(f"{ts}")


    # Chat input
    # frontend/app.py
# ... in render_chat_interface ...
    user_input = st.chat_input("Your message...", key=f"chat_input_sid_{session_details['id']}")

    if user_input:
        print(f"[FRONTEND_APP] User input received: '{user_input}' for session_id: {session_details['id']}") # DEBUG

        # ... (optimistic update) ...
        st.session_state.chat_messages.append({
            "sender_type": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        # Consider NOT rerunning here immediately if debugging the backend call.
        # Or, place the rerun after the backend call attempt.
        # st.rerun() # Temporarily comment out or move for clearer debugging print order

        print(f"[FRONTEND_APP] Calling send_message_to_backend for session {session_details['id']}") # DEBUG
        ai_response = send_message_to_backend(session_details['id'], user_input)
        print(f"[FRONTEND_APP] AI response from backend: {ai_response}") # DEBUG

        if ai_response:
            print("[FRONTEND_APP] AI response successful, reloading messages.") # DEBUG
            load_chat_messages_for_session()
        else:
            print("[FRONTEND_APP] AI response failed or None.") # DEBUG
        
        st.rerun() # Rerun to display changes

    # user_input = st.chat_input("Your message...", key=f"chat_input_sid_{session_details['id']}")

    # if user_input:
    #     # Display user's message immediately (optimistic update)
    #     # Use the same structure as messages from backend for consistency
    #     # This temporary message won't have an ID or backend timestamp yet
    #     st.session_state.chat_messages.append({
    #         "sender_type": "user",
    #         "content": user_input,
    #         "timestamp": datetime.now().isoformat() # Approximate timestamp
    #     })
    #     st.rerun() # Rerun to show the user's message quickly

    #     # Send to backend and get AI response
    #     ai_response = send_message_to_backend(session_details['id'], user_input)

    #     if ai_response:
    #         # Remove the temporary optimistic user message if we are about to reload all messages.
    #         # Or, better: fetch all messages again to get the "true" state from DB,
    #         # including the user message with its DB ID and the new AI message.
    #         load_chat_messages_for_session() # Reload all messages from backend
    #     else:
    #         # If sending failed, the error is shown by api_client.
    #         # We might want to remove the optimistic user message or mark it as "failed to send"
    #         # For simplicity now, we'll just rely on the next full load or user action.
    #         # To remove the last (optimistic) message if AI response fails:
    #         # st.session_state.chat_messages.pop() # Removes the last message
    #         pass
    #     st.rerun() # Rerun to display AI's response and updated message list


if __name__ == "__main__":
    main()
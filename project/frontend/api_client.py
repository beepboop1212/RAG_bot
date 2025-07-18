# frontend/api_client.py
import requests
import streamlit as st
from typing import List, Dict, Any, Optional, Generator

BACKEND_URL = "http://localhost:8000/api/v1"

# --- login_user, get_user_sessions, create_new_session, get_session_details (EXISTING CODE) ---
# Ensure these are present and correct from previous steps. I'll put placeholders for brevity.

def login_user(name: str, topic: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.post(
            f"{BACKEND_URL}/users/login",
            json={"name": name, "topic_of_interest": topic}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err}"
        try:
            error_detail = response.json().get('detail', response.text)
            error_message += f" - {error_detail}"
        except ValueError:
            error_message += f" - {response.text}"
        st.error(error_message)
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Error connecting to the backend: {conn_err}")
    except Exception as e:
        st.error(f"An unexpected error occurred during login: {e}")
    return None

def get_user_sessions(user_id: int) -> Optional[List[Dict[str, Any]]]:
    try:
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/sessions")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error fetching sessions: {http_err} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred fetching sessions: {e}")
    return None

def create_new_session(user_id: int, session_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    payload = {}
    if session_name and session_name.strip():
        payload["session_name"] = session_name.strip()
    else:
        payload["session_name"] = "New Chat" # Explicitly send default
    try:
        response = requests.post(
            f"{BACKEND_URL}/users/{user_id}/sessions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error creating session: {http_err} - Detail: {response.text}")
    except Exception as e:
        st.error(f"An error occurred creating session: {e}")
    return None

def get_session_details(session_id: int) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{BACKEND_URL}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error fetching session details: {http_err} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred fetching session details: {e}")
    return None

# --- NEW FUNCTIONS FOR CHAT MESSAGES ---
def get_session_messages_from_api(session_id: int) -> Optional[List[Dict[str, Any]]]:
    """Fetches all messages for a given session ID from the backend."""
    if not session_id:
        return []
    try:
        response = requests.get(f"{BACKEND_URL}/sessions/{session_id}/messages")
        response.raise_for_status()
        return response.json() # List of message dicts
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error fetching messages: {http_err} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred fetching messages: {e}")
    return None


# def send_message_to_backend(session_id: int, message_content: str) -> Optional[Dict[str, Any]]:
#     """Sends a user's message to the backend and gets the AI's response."""
#     if not session_id or not message_content:
#         return None
#     try:
#         payload = {"content": message_content}
#         response = requests.post(
#             f"{BACKEND_URL}/sessions/{session_id}/messages",
#             json=payload
#         )
#         response.raise_for_status()
#         return response.json() # AI's response message dict
#     except requests.exceptions.HTTPError as http_err:
#         st.error(f"HTTP error sending message: {http_err} - Detail: {response.text}")
#     except Exception as e:
#         st.error(f"An error occurred sending message: {e}")
#     return None

# frontend/api_client.py
# ...
def send_message_to_backend(session_id: int, message_content: str) -> Optional[Dict[str, Any]]:
    print(f"[API_CLIENT] send_message_to_backend called with session_id: {session_id}, content: '{message_content}'") # DEBUG
    if not session_id or not message_content:
        print("[API_CLIENT] send_message_to_backend: Invalid session_id or message_content.") # DEBUG
        return None
    try:
        payload = {"content": message_content}
        print(f"[API_CLIENT] Sending POST to: {BACKEND_URL}/sessions/{session_id}/messages with payload: {payload}") # DEBUG
        response = requests.post(
            f"{BACKEND_URL}/sessions/{session_id}/messages",
            json=payload,
            timeout=30 # Add a timeout
        )
        print(f"[API_CLIENT] Response status: {response.status_code}") # DEBUG
        print(f"[API_CLIENT] Response text: {response.text[:200]}") # DEBUG (first 200 chars)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error sending message: {http_err} - Detail: {response.text}")
        print(f"[API_CLIENT] HTTPError: {http_err} - {response.text}") # DEBUG
    except Exception as e:
        st.error(f"An error occurred sending message: {e}")
        print(f"[API_CLIENT] Exception: {e}") # DEBUG
    return None
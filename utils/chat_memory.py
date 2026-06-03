import streamlit as st


def initialize_memory():

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []


def add_user_message(message):

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": message,
        }
    )


def add_assistant_message(message):

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": message,
        }
    )


def get_chat_context():

    history = ""

    for msg in st.session_state.chat_history:

        history += (
            f"{msg['role'].capitalize()}: "
            f"{msg['content']}\n"
        )

    return history


def clear_memory():

    st.session_state.chat_history = []
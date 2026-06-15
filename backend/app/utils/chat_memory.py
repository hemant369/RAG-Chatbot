import streamlit as st

from backend.app.utils.logger import logger


def initialize_memory():

    st.session_state.setdefault("chat_history", [])

    logger.info("Chat memory initialized")


def add_user_message(message):

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    logger.debug(f"User message added to memory: {message}")


def add_assistant_message(message):

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": message,
        }
    )

    logger.debug("Assistant response added to memory")


def get_chat_context():

    if "chat_history" not in st.session_state:
        logger.debug("No chat history available for context")
        return ""

    history = ""

    for msg in st.session_state.chat_history:

        history += f"{msg['role'].capitalize()}: " f"{msg['content']}\n"

    logger.debug("Chat context built from history")
    return history


def clear_memory():

    st.session_state.chat_history = []
    logger.info("Chat memory cleared")

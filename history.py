import streamlit as st
from datetime import datetime

def init_history():
    """Initializes the query history list in Streamlit session state if missing."""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

def add_history_entry(question: str, case: str, sql: str = None, row_count: int = 0, execution_time: float = 0.0):
    """Appends a new query entry to the session history log."""
    init_history()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "case": case,
        "sql": sql,
        "row_count": row_count,
        "execution_time": execution_time
    }
    # Prepend so the newest queries appear at the top
    st.session_state.query_history.insert(0, entry)

def clear_history():
    """Clears all query history from session state."""
    st.session_state.query_history = []

def get_history():
    """Returns the current query history list."""
    init_history()
    return st.session_state.query_history
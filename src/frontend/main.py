import requests
import json
import time
import streamlit as st
import sseclient  # sseclient-py


def backend_call(query: str):
    url = f"http://orchestrator/streamingSearch?query={query}"
    stream_response = requests.get(url, stream=True)
    client = sseclient.SSEClient(stream_response)  # type: ignore

    # Loop forever (while connection "open")
    for event in client.events():
        yield event


def display_chat_messages():
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)


def process_backend_response(prompt):
    full_response = ""
    columns = st.columns(2)
    button_count = 0
    button_placeholders, message_placeholder = [], None
    with st.spinner("Thinking..."):
        for chunk in backend_call(prompt):
            button_count, button_placeholders = display_backend_response(
                chunk, button_count, columns, button_placeholders
            )
            full_response, message_placeholder = process_chunk_event(
                chunk, full_response, message_placeholder
            )

    st.session_state.messages.append({"role": "assistant", "content": full_response})


def display_backend_response(chunk, button_count, columns, button_placeholders):
    if chunk.event == "search":
        for item in json.loads(chunk.data).get("items"):
            button_placeholder = assign_button_placeholder(columns, button_placeholders)
            button_placeholder.button(
                label=item.get("link")[8:42] + "...", key=button_count
            )
            button_count += 1
            button_placeholders.append(button_placeholder)
            time.sleep(0.05)
    return button_count, button_placeholders


def assign_button_placeholder(columns, button_placeholders):
    return (
        columns[0].empty() if len(button_placeholders) % 2 == 0 else columns[1].empty()
    )


def process_chunk_event(chunk, full_response, message_placeholder):
    if chunk.event == "token":
        if not message_placeholder:
            message_placeholder = st.empty()
        full_response += chunk.data
        message_placeholder.markdown(full_response + "▌")
    return full_response, message_placeholder


st.title("InternetWhisper")
# Initialize chat history
st.session_state.messages = st.session_state.get("messages", [])

display_chat_messages()

# Accept user input
if prompt := st.chat_input("Ask me a question..."):
    process_user_input(prompt)
    process_backend_response(prompt)

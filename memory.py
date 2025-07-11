# memory.py
import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

HISTORY_DIR = "chat_histories"

# Ensure the history directory exists
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_chat_sessions():
    """Scans the history directory and returns a list of sessions, sorted by most recent."""
    sessions = []
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(HISTORY_DIR, filename), "r") as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data["id"],
                        "title": data.get("title", "Untitled Chat"),
                        "creation_date": data["creation_date"]
                    })
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: Could not read or parse session file: {filename}")
    
    # Sort sessions by creation date, most recent first
    sessions.sort(key=lambda s: s["creation_date"], reverse=True)
    return sessions

def load_chat_session(session_id: str) -> list:
    """Loads the messages from a specific session file."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return _deserialize_messages(data["messages"])
    except FileNotFoundError:
        return []

def save_chat_session(session_id: str, messages: list, llm):
    """Saves a chat session. If session_id is None, creates a new session."""
    if session_id is None:
        # This is a new chat, create a new session ID and title
        now = datetime.now()
        session_id = now.strftime("%Y%m%d_%H%M%S")
        title = _generate_chat_title(messages, llm)
        creation_date = now.isoformat()
    else:
        # For existing chats, we keep the original title and creation date
        existing_data = load_chat_session(session_id)
        # This is a bit inefficient, but simple. A better way would be to not reload.
        # But for this case, let's keep it simple.
        # We need to find the original title and date.
        filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            title = data.get("title", "Untitled Chat")
            creation_date = data.get("creation_date", datetime.now().isoformat())
        except FileNotFoundError:
             title = _generate_chat_title(messages, llm)
             creation_date = datetime.now().isoformat()

    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    data = {
        "id": session_id,
        "title": title,
        "creation_date": creation_date,
        "messages": _serialize_messages(messages)
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    
    return session_id # Return the ID, especially important for new chats

def delete_chat_session(session_id: str):
    """Deletes a specific chat session file."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)

def _generate_chat_title(messages: list, llm) -> str:
    """Generates a short title for the chat using the LLM."""
    # Find the first user message to use as a prompt for the title
    first_user_message = next((m.content for m in messages if isinstance(m, HumanMessage)), "To-Do List Discussion")
    
    prompt = f"Generate a very short, concise title (4-5 words maximum) for a conversation that starts with this user message: '{first_user_message}'"
    try:
        response = llm.invoke(prompt)
        # Clean up the title from quotes or extra text
        title = response.content.strip().strip('"')
        return title
    except Exception as e:
        print(f"Error generating title: {e}")
        return "Untitled Chat"

# Helper functions to convert messages to/from JSON-compatible format
def _serialize_messages(messages: list) -> list:
    serializable = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            serializable.append({"type": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            serializable.append({"type": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            serializable.append({"type": "ai", "content": msg.content, "tool_calls": msg.tool_calls or []})
    return serializable

def _deserialize_messages(data: list) -> list:
    messages = []
    for item in data:
        if item["type"] == "system":
            messages.append(SystemMessage(content=item["content"]))
        elif item["type"] == "human":
            messages.append(HumanMessage(content=item["content"]))
        elif item["type"] == "ai":
            messages.append(AIMessage(content=item["content"], tool_calls=item.get("tool_calls", [])))
    return messages
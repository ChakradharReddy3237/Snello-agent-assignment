# memory.py
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

MEMORY_FILE = "conversation_history.json"

def save_conversation(history: list):
    """Saves the conversation history to a JSON file."""
    # We need to convert the message objects to a dictionary format that can be saved as JSON
    serializable_history = []
    for message in history:
        if isinstance(message, SystemMessage):
            serializable_history.append({"type": "system", "content": message.content})
        elif isinstance(message, HumanMessage):
            serializable_history.append({"type": "human", "content": message.content})
        elif isinstance(message, AIMessage):
            # We also need to save tool calls if they exist
            tool_calls = message.tool_calls or []
            serializable_history.append({
                "type": "ai", 
                "content": message.content,
                "tool_calls": tool_calls
            })
        # Note: We are not saving ToolMessage for simplicity, as the agent regenerates it.
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(serializable_history, f, indent=4)


def load_conversation() -> list:
    """Loads the conversation history from a JSON file."""
    try:
        with open(MEMORY_FILE, "r") as f:
            serializable_history = json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, start with a fresh history
        return []
    
    # We need to convert the dictionaries back into LangChain message objects
    history = []
    for item in serializable_history:
        if item["type"] == "system":
            history.append(SystemMessage(content=item["content"]))
        elif item["type"] == "human":
            history.append(HumanMessage(content=item["content"]))
        elif item["type"] == "ai":
            # Recreate the AIMessage, including tool calls if they were saved
            message = AIMessage(content=item["content"], tool_calls=item.get("tool_calls", []))
            history.append(message)
            
    return history
# tools.py
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
import database # Import the database module we just created

# Define input schemas for better tool usage by the LLM.
# This helps the AI know exactly what information to provide.
class AddTodoInput(BaseModel):
    item: str = Field(description="The content of the to-do item to add.")

@tool(args_schema=AddTodoInput)
def add_todo(item: str) -> str:
    """Use this tool to add a new item to the user's to-do list."""
    print(f"--- Calling add_todo tool with item: {item} ---")
    database.add_item(item)
    return f"Successfully added '{item}' to the to-do list."

@tool
def list_todos() -> str:
    """Use this tool to list all the items in the user's to-do list."""
    print("--- Calling list_todos tool ---")
    items = database.list_items()
    if not items:
        return "The user's to-do list is currently empty."
    
    # Format the output nicely so the AI can present it well
    formatted_items = [f"ID {item_id}: {item_text}" for item_id, item_text in items]
    return "Here is the user's current to-do list:\n" + "\n".join(formatted_items)

class RemoveTodoInput(BaseModel):
    item_id: int = Field(description="The numerical ID of the to-do item that should be removed.")

@tool(args_schema=RemoveTodoInput)
def remove_todo(item_id: int) -> str:
    """Use this tool to remove a specific item from the to-do list using its ID."""
    print(f"--- Calling remove_todo tool with ID: {item_id} ---")
    
    # Call the updated database function and store the result
    was_deleted = database.remove_item(item_id)
    
    # Provide an intelligent response based on the outcome
    if was_deleted:
        return f"Successfully removed to-do item with ID {item_id}."
    else:
        return f"Error: No to-do item found with ID {item_id}. Please check the ID and try again."

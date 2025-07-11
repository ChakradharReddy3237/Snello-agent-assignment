# tools.py
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
import database

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
    
    # --- THE FINAL, PERFECT FORMATTING LOGIC ---
    # This creates the clean "1. Item" format.
    formatted_list = [f"{item_id}. {item_text}" for item_id, item_text in items]
    
    # Join the items with a newline character.
    final_list_string = "\n".join(formatted_list)
    
    # We explicitly add the header here so the LLM doesn't have to.
    return f"Here is your current to-do list:\n{final_list_string}"

class RemoveTodoInput(BaseModel):
    item_id: int = Field(description="The numerical ID of the to-do item that should be removed.")

@tool(args_schema=RemoveTodoInput)
def remove_todo(item_id: int) -> str:
    """Use this tool to remove a specific item from the to-do list using its ID."""
    print(f"--- Calling remove_todo tool with ID: {item_id} ---")
    
    was_deleted = database.remove_item(item_id)
    
    if was_deleted:
        return f"Successfully removed to-do item with ID {item_id}."
    else:
        return f"Error: No to-do item found with ID {item_id}. Please check the ID and try again."
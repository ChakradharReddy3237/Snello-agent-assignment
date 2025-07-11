# main.py

# Import the tools, not the database functions directly
from tools import add_todo, list_todos, remove_todo
from database import initialize_database

if __name__ == '__main__':
    # Initialize the database once at the start
    initialize_database()
    print("Database initialized.")

    print("\n--- Testing LangChain Tools ---")

    # To use a LangChain tool, you call its .invoke() method with a dictionary
    print("\n1. Adding items via tools:")
    print(add_todo.invoke({"item": "Test the LangChain tools"}))
    print(add_todo.invoke({"item": "Prepare for the agent layer"}))

    print("\n2. Listing items via tool:")
    # The list_todos tool doesn't need any input, so we pass an empty dictionary
    current_list_str = list_todos.invoke({})
    print(current_list_str)

    print("\n3. Removing an item via tool (e.g., item with ID 3):")
    # NOTE: The ID might be different on your machine if you ran the test before.
    # We will just assume we want to remove ID 3 for this test.
    print(remove_todo.invoke({"item_id": 3}))

    print("\n4. Final list via tool:")
    print(list_todos.invoke({}))

    print("\n5. Testing error handling by removing a non-existent item (ID 999):")
    print(remove_todo.invoke({"item_id": 999}))

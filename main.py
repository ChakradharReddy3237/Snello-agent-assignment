
# Import the functions we just moved to database.py
from database import initialize_database, add_item, list_items, remove_item

if __name__ == '__main__':
    # This is our test block to make sure the foundation works
    initialize_database()
    print("Database initialized.")

    print("\n--- Testing To-Do List ---")
    
    # Add some items
    add_item("Finish building the database layer")
    add_item("Start working on the tools layer")

    print("\nCurrent To-Do List:")
    current_list = list_items()
    if not current_list:
        print("The list is empty.")
    else:
        for id, item in current_list:
            print(f"{id}: {item}")

    # Remove an item (e.g., the one with ID 1)
    if current_list:
        print(f"\nRemoving item with ID {current_list[0][0]}...")
        remove_item(current_list[0][0]) 

    print("\nTo-Do List after removal:")
    for id, item in list_items():
        print(f"{id}: {item}")
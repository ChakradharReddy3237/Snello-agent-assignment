# main.py
from agent import create_agent_graph
from database import initialize_database
from langchain_core.messages import SystemMessage, HumanMessage

# Import our new memory functions
from memory import save_conversation, load_conversation

if __name__ == '__main__':
    # Initialize the database once at the start
    initialize_database()
    print("Database initialized. To-do list is ready.")
    print("Snello Todo Agent is ready! Type 'exit' to quit.")

    # Create the agent
    app = create_agent_graph()

    # --- MEMORY LOGIC ---
    # Load previous conversation history or start a new one
    conversation_history = load_conversation()
    
    if not conversation_history:
        # If history is empty, add the initial system message
        print("Starting new conversation.")
        conversation_history.append(
            SystemMessage(content="You are a helpful to-do list assistant named Snello. You can add, remove, and list items. Be friendly and confirm actions. Ask for clarification if a user's request is ambiguous.")
        )
    else:
        print("Loaded previous conversation.")
    # --- END MEMORY LOGIC ---

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            # Save the final history before exiting
            save_conversation(conversation_history)
            print("Conversation saved. Goodbye!")
            break
        
        conversation_history.append(HumanMessage(content=user_input))
        
        inputs = {"messages": conversation_history}
        result = app.invoke(inputs)
        
        ai_response = result['messages'][-1]
        
        conversation_history.append(ai_response)
        
        # Save the history after every turn
        save_conversation(conversation_history)
        
        print(f"Agent: {ai_response.content}")
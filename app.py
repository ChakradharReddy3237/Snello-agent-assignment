# app.py
import streamlit as st
import database
import memory
from agent import create_agent_graph
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Snello AI Agent", page_icon="🚀", layout="wide")

# --- INITIALIZATION ---
if "agent" not in st.session_state:
    database.initialize_database()
    st.session_state.agent = create_agent_graph()
    st.session_state.title_generator_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
    print("Dependencies initialized.")

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
    st.session_state.messages = [SystemMessage(content="You are a helpful AI assistant named Snello. Start by greeting the user and asking how you can help with their to-do list.")]

# --- SIDEBAR ---
with st.sidebar:
    st.header("🚀 Snello AI Agent")
    st.caption("Your AI-powered task manager.")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = None
        st.session_state.messages = [SystemMessage(content="You are a helpful AI assistant named Snello. Greet the user.")]
        st.rerun()

    st.markdown("---")
    st.subheader("🗓️ Chat History")
    chat_sessions = memory.get_chat_sessions()
    for session in chat_sessions:
        if st.button(session['title'], key=f"session_btn_{session['id']}", use_container_width=True):
            st.session_state.current_chat_id = session['id']
            st.session_state.messages = memory.load_chat_session(session['id'])
            st.rerun()

    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    if st.button("🗑️ Clear To-Do List", use_container_width=True, type="secondary"):
        database.clear_all_todos()
        st.success("To-do list cleared!")

    if st.button("🔥 Delete Current Chat", use_container_width=True, type="secondary"):
        if st.session_state.current_chat_id:
            memory.delete_chat_session(st.session_state.current_chat_id)
            st.session_state.current_chat_id = None
            st.session_state.messages = [SystemMessage(content="You are a helpful AI assistant named Snello. Greet the user.")]
            st.success("Chat session deleted.")
            st.rerun()
        else:
            st.warning("No active chat to delete.")

# --- MAIN CHAT INTERFACE ---
st.title("Snello AI Agent")
st.caption("I'm ready to help you manage your tasks. Start a new chat or load a previous one from the sidebar.")

# Display chat messages
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message.content)

# Handle user input
if prompt := st.chat_input("What can I help you with today?"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                inputs = {"messages": st.session_state.messages}
                result = st.session_state.agent.invoke(inputs)
                ai_response = result['messages'][-1]
                st.session_state.messages.append(ai_response)
                
                new_session_id = memory.save_chat_session(
                    st.session_state.current_chat_id, 
                    st.session_state.messages,
                    st.session_state.title_generator_llm
                )
                st.session_state.current_chat_id = new_session_id
            
            except Exception as e:
                # Catch the exception and check for the rate limit error
                if "ResourceExhausted" in str(e) or "429" in str(e):
                    error_message = "I've been working hard and have hit my daily usage limit! Please try again tomorrow. 🙏"
                    st.error(error_message)
                    # We still want to save the user's message to the history
                    st.session_state.messages.append(AIMessage(content=error_message))
                else:
                    # Handle other potential errors
                    st.error("An unexpected error occurred. Please try again.")
                    print(f"An unexpected error occurred: {e}")

    st.rerun()
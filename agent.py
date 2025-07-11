# agent.py
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
# This is the new, better way to handle tools!
from langgraph.prebuilt import ToolNode 
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Import the tools we created
from tools import add_todo, list_todos, remove_todo

# Load environment variables from .env file
load_dotenv()

# Check for Google API key
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Google API Key not found in .env file. Please add it.")

# 1. Define the state for our graph
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], lambda x, y: x + y]

# 2. Set up the tools and the LLM
tools = [add_todo, list_todos, remove_todo]
# The ToolNode will handle executing our tools
tool_node = ToolNode(tools)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

# 3. Define the nodes for our graph

# This node decides whether to call a tool or not
def agent_node(state: AgentState):
    """Invokes the LLM to get the next action."""
    print("---AGENT NODE---")
    model_with_tools = llm.bind_tools(tools)
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 4. Define the edges for our graph
def should_continue(state: AgentState) -> str:
    """Determines the next step for the agent."""
    print("---ROUTING---")
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# 5. Build the graph
def create_agent_graph():
    """Creates and returns the compiled LangGraph agent."""
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    # The ToolNode is added directly to the graph
    graph.add_node("tools", tool_node) 
    
    graph.set_entry_point("agent")
    
    graph.add_conditional_edges(
        "agent",
        should_continue,
    )
    graph.add_edge("tools", "agent")
    
    return graph.compile()
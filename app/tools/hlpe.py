from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from airways import get_airways_route_info
from roadways import get_roadways_route_info
from railways import get_railways_route_info
from seaways import get_seaways_route_info
from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
import os

load_dotenv()

# Define tools
tools = [
    get_airways_route_info,
    get_railways_route_info,
    get_roadways_route_info,
    get_seaways_route_info
]

# Define LLMs
planner_llm = ChatOpenAI(model='gpt-4o-mini')
final_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

planner_llm_with_tools = planner_llm.bind_tools(tools)

# System message for planning step
sys_msg = SystemMessage(content="You are a travel planner that uses tools to gather info, then another assistant will summarize it.")

# Stage 1: Tool calling
def planner_node(state: MessagesState):
    return {"messages": [planner_llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Stage 2: Gemini final summarization
def summarizer_node(state: MessagesState):
    return {"messages": [final_llm.invoke(state["messages"])]}

# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("planner", planner_node)
builder.add_node("tools", ToolNode(tools))
builder.add_node("summarizer", summarizer_node)

# Control flow
builder.add_edge(START, "planner")
builder.add_conditional_edges("planner", tools_condition)
builder.add_edge("tools", "summarizer")

# Compile the graph
graph = builder.compile()

# Input query
messages = [
    HumanMessage(content="Give me 3 best ways to ship cargos from Pune to California, using airways, railways, seaways, or roadways. Consider cost, time, and carbon emission. Don't give direct routes, you may give routes like first go from pune to delhi by train, then delhi to california by flight, or first go from pune to mumbai by road, then mumbai to california by ship or something like that. For each route i want Total time, total cost (INR), total carbon emission railway station of pune if 'pune-jn-pune'.")
]

# Run the graph
final_state = graph.invoke({"messages": messages})

# Print results
for m in final_state["messages"]:
    m.pretty_print()

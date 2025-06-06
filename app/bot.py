from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
import aiosqlite
import json
import os

from app.routers.products import get_products
from app.routers.stock_forecast import stock_forecast
from app.routers.route_optimizer import best_route 
from app.routers.resource_optimizer import resource_optimizer

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

tools = [
    get_products,
    stock_forecast,
    best_route,
    resource_optimizer
]

llm = llm.bind_tools(tools)

class State(MessagesState):
    summary: str

async def get_bot():
    conn = await aiosqlite.connect("chats/test.db", check_same_thread=False)
    memory = AsyncSqliteSaver(conn)

    async def assistant(state: State):
        summary = state.get("summary", "")
        if summary:
            system_message = SystemMessage(content=f"Summary of conversation earlier: {summary}")
            messages = [system_message] + state["messages"]
        else:
            messages = state["messages"]

        response = await llm.ainvoke(messages)
        print(f"LLM Response: {response}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"Tool calls detected: {response.tool_calls}")
            return {"messages": [response]}  # Return the full response with tool calls
        else:
            print("No tool calls detected")
            return {"messages": [response]}

    async def summarize_conversation(state: State):
        summary = state.get("summary", "")
        if summary:
            summary_message = (
                f"This is summary of the conversation to date: {summary}\n\n"
                "Extend the summary by taking into account the new messages above:"
            )
        else:
            summary_message = "Create a summary of the conversation above:"

        messages = state["messages"] + [HumanMessage(content=summary_message)]
        response = await llm.ainvoke(messages)

        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

        try:
            if hasattr(response, 'content'):
                summary_text = response.content
            else:
                summary_text = str(response)
        except Exception as e:
            print(f"Error processing summary: {e}")
            summary_text = "Summary unavailable"

        return {
            "summary": summary_text,
            "messages": delete_messages
        }

    def should_continue(state: State):
        messages = state.get("messages", [])
        if len(messages) > 6:
            return "summarize_conversation"
        return END

    workflow = StateGraph(State)
    workflow.add_node("assistant", assistant)  # Renamed for clarity
    workflow.add_node("summarize_conversation", summarize_conversation)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "assistant")
    
    workflow.add_conditional_edges(
        "assistant", 
        tools_condition,
        {
            "tools": "tools",
            "__end__": "assistant_continue"  # Create a decision node
        }
    )
    
    def assistant_continue(state: State):
        return should_continue(state)
    
    workflow.add_node("assistant_continue", lambda state: {})
    workflow.add_conditional_edges(
        "assistant_continue",
        should_continue,
        {
            "summarize_conversation": "summarize_conversation",
            "__end__": END
        }
    )
    
    workflow.add_edge("tools", "assistant")
    workflow.add_edge("summarize_conversation", END)

    agent = workflow.compile(checkpointer=memory)
    return agent, conn


async def get_bot_simple():
    conn = await aiosqlite.connect("chats/test.db", check_same_thread=False)
    memory = AsyncSqliteSaver(conn)

    async def assistant(state: State):
        summary = state.get("summary", "")
        if summary:
            system_message = SystemMessage(content=f"Summary of conversation earlier: {summary}")
            messages = [system_message] + state["messages"]
        else:
            messages = state["messages"]

        response = await llm.ainvoke(messages)
        print(f"Assistant response: {response}")
        return {"messages": [response]}

    async def summarize_conversation(state: State):
        summary = state.get("summary", "")
        if summary:
            summary_message = f"This is summary of the conversation to date: {summary}\n\nExtend the summary by taking into account the new messages above:"
        else:
            summary_message = "Create a summary of the conversation above:"

        messages = state["messages"] + [HumanMessage(content=summary_message)]
        response = await llm.ainvoke(messages)
        
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        summary_text = response.content if hasattr(response, 'content') else str(response)

        return {
            "summary": summary_text,
            "messages": delete_messages
        }

    def route_after_assistant(state: State):
        """Route after assistant - either to tools, summarize, or end"""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        if len(messages) > 6:
            return "summarize"
            
        return "__end__"

    workflow = StateGraph(State)
    workflow.add_node("assistant", assistant)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("summarize", summarize_conversation)

    workflow.add_edge(START, "assistant")
    workflow.add_conditional_edges(
        "assistant",
        route_after_assistant,
        {
            "tools": "tools",
            "summarize": "summarize", 
            "__end__": END
        }
    )
    workflow.add_edge("tools", "assistant")
    workflow.add_edge("summarize", END)

    agent = workflow.compile(checkpointer=memory)
    return agent, conn
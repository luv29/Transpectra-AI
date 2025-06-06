from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.airways import get_airways_route_info
from app.tools.roadways import get_roadways_route_info
from app.tools.railways import get_railways_route_info
from app.tools.seaways import get_seaways_route_info
# from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import SystemMessage
import os
import json

# load_dotenv()

tools = [
    get_airways_route_info,
    get_railways_route_info,
    get_roadways_route_info,
    get_seaways_route_info
]

planner_llm = ChatOpenAI(model='gpt-4o-mini')
final_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

planner_llm_with_tools = planner_llm.bind_tools(tools)

sys_msg = SystemMessage(content="You are a travel planner that uses tools to gather info, then another assistant will summarize it.")

summarizer_sys_msg = SystemMessage(content="""You are a travel route summarizer.

You must return your response as a valid JSON array containing exactly 3 route options. Each route should be optimized for different priorities (cost, time, carbon emissions).

Format each route as:
[
    {
        "total_cost": <number in INR>,
        "total_time": "<time with units>",
        "total_carbon_emission": "<emission with units>",                           
        "feature": "<explanation of why this route is chosen>",
        "route": [
            {
                "from": "<origin city>",
                "to": "<destination city>",
                "distance": "<distance with units>",
                "by": "<transport mode: train/truck/flight/ship>"
            }
        ]
    }
]

Important:
- Consider multi-modal routes (e.g., Pune→Mumbai by road, then Mumbai→California by ship)
- Return ONLY the JSON array, no additional text

- Railway Station CODES for ixigo, Pass exactly this names else tool call will fail:
    Pune - "PUNE"
    Delhi / New Delhi - "NDLS"
    Mumbai all stations - "LTT"
    Surat - "ST"
    Kolkata -"HWH"
    Chennai - "MAS"
    Vadodra - "BRC"
    Chandigarh - "CDG"
    Ahmedabad - "ADI"
    Bengaluru - "SBC"
""")

# Stage 1: Tool calling
def planner_node(state: MessagesState):
    return {"messages": [planner_llm_with_tools.invoke([sys_msg] + state["messages"])]}

def summarizer_node(state: MessagesState):
    all_messages = [summarizer_sys_msg] + state["messages"]
    
    response = final_llm.invoke(all_messages)
    
    try:
        json_content = response.content.strip()
        
        if json_content.startswith('```json'):
            json_content = json_content.replace('```json', '').replace('```', '').strip()
        elif json_content.startswith('```'):
            json_content = json_content.replace('```', '').strip()
        
        parsed_json = json.loads(json_content)
        
        if not isinstance(parsed_json, list) or len(parsed_json) != 3:
            raise ValueError("Response must be a JSON array with exactly 3 routes")
        
        for i, route in enumerate(parsed_json):
            required_fields = ['total_cost', 'total_time', 'total_carbon_emission', 'route']
            for field in required_fields:
                if field not in route:
                    raise ValueError(f"Route {i+1} missing required field: {field}")
        
        response.content = json.dumps(parsed_json, indent=2)
        
    except (json.JSONDecodeError, ValueError) as e:
        error_response = [{
            "total_cost": 0,
            "total_time": "Error",
            "total_carbon_emission": "Error",
            "route": [{
                "from": "Error",
                "to": "Error", 
                "distance": "Error",
                "by": "Error",
                "feature": f"JSON parsing failed: {str(e)}"
            }]
        }]
        response.content = json.dumps(error_response, indent=2)
    
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("planner", planner_node)
builder.add_node("tools", ToolNode(tools))
builder.add_node("summarizer", summarizer_node)

builder.add_edge(START, "planner")
builder.add_conditional_edges("planner", tools_condition)
builder.add_edge("tools", "summarizer")

graph = builder.compile()

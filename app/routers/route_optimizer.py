from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import APIRouter, HTTPException
from app.schemas import OptimizeRoute
from app.agent import graph
import json

router = APIRouter()

def best_route(source: str, destination: str) -> dict:
    """
    Suggests the 3 best multi-modal shipping routes from a source to a destination.

    Args:
        source: The starting location of the cargo.
        destination: The target location for delivery.

    Returns:
        dict: A dictionary with 3 best route suggestions. Each route includes:
            - Total cost (in INR)
            - Total time
            - Total carbon emission
            - Step-by-step route description using airways, railways, seaways, or roadways

    The function uses an LLM-based planner to consider combinations like:
    - Pune → Delhi by train → California by flight
    - Pune → Mumbai by road → California by ship
    """
    messages = [
        HumanMessage(content=f"Give me 3 best ways to ship cargos from {source} to {destination}, using airways, railways, seaways, or roadways. Consider cost, time, and carbon emission. Don't give direct routes, you may give routes like first go from pune to delhi by train, then delhi to california by flight, or first go from pune to mumbai by road, then mumbai to california by ship or something like that. For each route i want Total time, total cost (INR), total carbon emission.")
    ]

    final_state = graph.invoke({"messages": messages})

    final_message = final_state["messages"][-1]
    
    return json.loads(final_message.content)

@router.post('/route_optimizer')
def route_optimizer(req: OptimizeRoute):
    try:
        return best_route(req.source, req.destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
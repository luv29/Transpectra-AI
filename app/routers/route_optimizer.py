from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import APIRouter, HTTPException
from app.schemas import OptimizeRoute
from app.agent import graph
import json

router = APIRouter()

@router.post('/route_optimizer')
def route_optimizer(req: OptimizeRoute):
    try:
        messages = [
            HumanMessage(content=f"Give me 3 best ways to ship cargos from {req.source} to {req.destination}, using airways, railways, seaways, or roadways. Consider cost, time, and carbon emission. Don't give direct routes, you may give routes like first go from pune to delhi by train, then delhi to california by flight, or first go from pune to mumbai by road, then mumbai to california by ship or something like that. For each route i want Total time, total cost (INR), total carbon emission.")
        ]

        final_state = graph.invoke({"messages": messages})

        final_message = final_state["messages"][-1]
        
        return json.loads(final_message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
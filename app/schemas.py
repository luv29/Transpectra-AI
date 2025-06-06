from pydantic import BaseModel
from typing import List, Dict, Any

# class ProductInput(BaseModel):
#     products: List[Dict[str, Any]]

class ProductInput(BaseModel):
    products: List[str]

class OptimizeRoute(BaseModel):
    source: str
    destination: str

class BotSchema(BaseModel):
    chat_id: str
    prompt: str
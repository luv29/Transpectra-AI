from pydantic import BaseModel
from typing import List, Dict, Any

# class ProductInput(BaseModel):
#     products: List[Dict[str, Any]]

class ProductInput(BaseModel):
    products: List[str]

class OptimizeRoute(BaseModel):
    source: str
    destination: str

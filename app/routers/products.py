from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()

dataset = pd.read_csv('app/models/dataset.csv')

@router.get("/get_products")
def get_products():
    try:
        first_column = dataset.columns[0]
        products = dataset[first_column].dropna().tolist() 
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
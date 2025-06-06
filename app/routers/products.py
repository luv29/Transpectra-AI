from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()

dataset = pd.read_csv('app/models/dataset.csv')

def get_products() -> dict:
    """
    Fetches the list of products from the first column of the dataset.

    Returns:
        dict: A dictionary containing a list of product names under the key 'products'.
              Example: {"products": ["product1", "product2", "product3", ...]}
    
    This function does not take any input parameters. It reads the dataset from a CSV file
    and extracts non-null values from the first column, which is assumed to contain product names.
    """
    first_column = dataset.columns[0]
    products = dataset[first_column].dropna().tolist() 
    return {"products": products}


@router.get("/get_products")
def get_products_route():
    try:
        return get_products()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
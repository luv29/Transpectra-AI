from fastapi import FastAPI
from app.routers import stock_forecast, products

app = FastAPI()

app.include_router(stock_forecast.router)
app.include_router(products.router)

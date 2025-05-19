from fastapi import FastAPI
from app.routers import stock_forecast

app = FastAPI()

app.include_router(stock_forecast.router)

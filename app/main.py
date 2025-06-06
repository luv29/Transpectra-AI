from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.routers import route_optimizer, stock_forecast, products, bot

app = FastAPI()

app.include_router(stock_forecast.router)
app.include_router(products.router)
app.include_router(route_optimizer.router)
app.include_router(bot.router)
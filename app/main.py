from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="Transpectra AI API",
    description="AI endpoints for transpectra",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = ["*"]  # In production, replace with specific origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import route_optimizer, stock_forecast, products, bot, resource_optimizer

app.include_router(stock_forecast.router)
app.include_router(products.router)
app.include_router(route_optimizer.router)
app.include_router(bot.router)
app.include_router(resource_optimizer.router)
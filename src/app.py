import datetime
import logging
import os
from typing import Any, Dict, List, Union

from beanie import Document, init_beanie
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field

from src.cleaning_schedule import HospitableAPI
from src.db_model import ReservationData
from src.models import Reservation, ReservationIncoming

# Load environment variables from .env file
load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)

# Environment variables from .env file
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
HOSPITABLE_API_KEY = os.getenv("HOSPITABLE_API_KEY")

# MongoDB client initialization
mongo_client = None

# FastAPI app initialization
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class UserProfile(Document):
    username: str = Field(...)
    email: str = Field(...)
    age: int = Field(...)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now)

    class Settings:
        name = "user_profiles"

    def __str__(self):
        return f"UserProfile(username={self.username}, email={self.email}, age={self.age}, created_at={self.created_at})"


async def init_db():
    """Initialize database connection and Beanie models."""
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(database=client[DATABASE_NAME], document_models=[UserProfile, Reservation, ReservationIncoming, User])


@app.get("/")
async def root(request: Request):
    """Root endpoint to return the cleaning schedule."""
    cleaning_schedule = [
        {"date": "2024-09-01", "address": "1234 Main St", "guests_count": 4,
            "checkout_date": "2024-09-05", "status": "Confirmed"},
        {"date": "2024-09-02", "address": "5678 Elm St", "guests_count": 2,
            "checkout_date": "2024-09-06", "status": "Pending"},
    ]
    return templates.TemplateResponse("index.html", {"request": request, "schedule": cleaning_schedule})


@app.get("/schedule", response_class=HTMLResponse)
async def kevin():
    """Get Kevin's cleaning data using Hospitable API."""
    api = HospitableAPI(HOSPITABLE_API_KEY)
    content = api.get_complete_cleaning()
    return HTMLResponse(content=content)


def convert_objectid(data):
    """Convert ObjectId to string recursively."""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


@app.post("/json-endpoint/")
async def json_endpoint(request: Request):
    """Endpoint to receive and store JSON data."""
    json_data = await request.json()
    client = AsyncIOMotorClient(MONGO_URL)
    client[DATABASE_NAME]["res"].insert_one(json_data)
    logger.info(f"Received JSON data: {json_data}")
    return {"received": json_data}


@app.get("/upcoming-month/")
async def get_upcoming_month():
    """Get reservations for the upcoming month."""
    client = AsyncIOMotorClient(MONGO_URL)
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    next_month = (datetime.datetime.now(datetime.timezone.utc) +
                  datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    pipeline = [
        {"$match": {"start_date": {"$gte": today, "$lt": next_month}}},
        {"$sort": {"code": 1, "updated_at": -1}},
        {"$group": {"_id": "$code", "latestRecord": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$latestRecord"}},
        {"$project": {"_id": 1, "start_date": 1,
                      "action": 1, "code": 1, "updated_at": 1}},
    ]

    cursor = client[DATABASE_NAME]["res"].aggregate(pipeline)
    reservations = await cursor.to_list(length=None)

    reservations = convert_objectid(reservations)
    return {"reservations": reservations}


@app.post("/beanie-endpoint/")
async def beanie_endpoint(reservation: ReservationData):
    """Insert reservation data using Beanie ORM."""
    await reservation.insert()
    return {"status": "received", "reservation": reservation}


# Add the DB init to the startup event
app.add_event_handler("startup", init_db)

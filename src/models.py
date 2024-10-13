from datetime import datetime
from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field


class ReservationStatusHistory(BaseModel):
    category: Optional[str] = None
    sub_category: Optional[str] = None
    changed_at: Optional[datetime] = None


class ReservationStatus(BaseModel):
    current: Optional[ReservationStatusHistory] = None
    history: List[ReservationStatusHistory] = []


class Guests(BaseModel):
    total: Optional[int] = 0
    adult_count: Optional[int] = 0
    child_count: Optional[int] = 0
    infant_count: Optional[int] = 0
    pet_count: Optional[int] = 0


class StatusHistory(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None
    changed_at: Optional[datetime] = None


class Reservation(Document):
    id: Optional[str] = Field(default=None, alias="_id")
    code: Optional[str] = None
    platform: Optional[str] = None
    platform_id: Optional[str] = None
    booking_date: Optional[datetime] = None
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    reservation_status: Optional[ReservationStatus] = None
    conversation_id: Optional[str] = None
    guests: Optional[Guests] = None
    status: Optional[str] = None
    status_history: List[StatusHistory] = []

    class Settings:
        name = "reservations"


# ------------------------- Webhook -------------------------

class Listing(BaseModel):
    id: Optional[str]
    property_id: Optional[int]
    name: Optional[str]
    nickname: Optional[str]
    address: Optional[str]
    picture_url: Optional[str]
    lat: Optional[float]
    lng: Optional[float]


class Guest(BaseModel):
    id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    picture_url: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    phone_last_4: Optional[str]
    email: Optional[str]


class ReservationModel(BaseModel):
    uuid: Optional[str]
    user_id: Optional[str]
    code: Optional[str]
    channel: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    checkin_time: Optional[str]
    checkout_time: Optional[str]
    nights: Optional[int]
    guests: Optional[int]
    adults: Optional[int]
    children: Optional[int]
    infants: Optional[int]
    pets: Optional[int]
    status: Optional[str]
    listing: Optional[Listing]
    child_reservations: Optional[List[dict]]
    guest: Optional[Guest]
    currency: Optional[str]
    security_price: Optional[float]
    security_price_formatted: Optional[str]
    per_night_price: Optional[float]
    per_night_price_formatted: Optional[str]
    base_price: Optional[float]
    base_price_formatted: Optional[str]
    extras_price: Optional[float]
    extras_price_formatted: Optional[str]
    subtotal: Optional[float]
    subtotal_formatted: Optional[str]
    tax_amount: Optional[float]
    tax_amount_formatted: Optional[str]
    guest_fee: Optional[float]
    guest_fee_formatted: Optional[str]
    total_price: Optional[float]
    total_price_formatted: Optional[str]
    host_service_fee: Optional[float]
    host_service_fee_formatted: Optional[str]
    payout_price: Optional[float]
    payout_price_formatted: Optional[str]
    created_at: Optional[int]
    updated_at: Optional[int]
    sent_at: Optional[int]


class ReservationIncoming(Document, ReservationModel):
    class Settings:
        collection = "reservation_incoming"





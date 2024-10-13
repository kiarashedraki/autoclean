from typing import Optional
from beanie import Document


class Guest(Document):
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture_url: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    phone_last_4: Optional[int] = None
    email: Optional[str] = None


class Listing(Document):
    id: Optional[str] = None
    property_id: Optional[int] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    address: Optional[str] = None
    picture_url: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class ReservationData(Document):
    action: Optional[str] = None
    uuid: Optional[str] = None
    user_id: Optional[str] = None
    code: Optional[str] = None
    channel: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    checkin_time: Optional[str] = None
    checkout_time: Optional[str] = None
    nights: Optional[int] = None
    guests: Optional[int] = None
    adults: Optional[int] = None
    children: Optional[int] = None
    infants: Optional[int] = None
    pets: Optional[int] = None
    status: Optional[str] = None
    listing: Optional[Listing] = None
    guest: Optional[Guest] = None
    per_night_price: Optional[float] = None
    total_price: Optional[float] = None

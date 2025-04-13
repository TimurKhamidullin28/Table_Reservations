from datetime import datetime
from pydantic import BaseModel


class TableIn(BaseModel):
    name: str
    seats: int
    location: str


class TableOut(TableIn):
    id: int

    class Config:
        orm_mode = True


class ReservationIn(BaseModel):
    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: int


class ReservationOut(ReservationIn):
    id: int

    class Config:
        orm_mode = True

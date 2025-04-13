import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import async_get_db
from models import Table, Reservation
import schemas


router_t = APIRouter(prefix='/tables', tags=['tables'])


@router_t.get("", response_model=List[schemas.TableOut])
async def get_tables_list(session: AsyncSession = Depends(async_get_db)):
    """Эндпойнт получения списка всех столиков"""

    tables_all = await session.execute(select(Table))
    tables = tables_all.scalars().all()
    return [schemas.TableOut.from_orm(table) for table in tables]


@router_t.post("", response_model=schemas.TableOut)
async def create_new_table(table: schemas.TableIn,
                           session: AsyncSession = Depends(async_get_db)) -> Table:
    """Эндпойнт создания нового столика"""

    new_table = Table(**table.dict())
    session.add(new_table)
    await session.commit()
    return new_table


@router_t.delete("/{table_id}")
async def delete_table_by_id(table_id: int,
                             session: AsyncSession = Depends(async_get_db)):
    """Эндпойнт удаления столика по его id"""

    match_table = await session.execute(select(Table).filter(Table.id == table_id))
    table = match_table.scalar()
    if table:
        await session.delete(table)
        await session.commit()
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Table not found")


router_r = APIRouter(prefix='/reservations', tags=['reservations'])


@router_r.get("", response_model=List[schemas.ReservationOut])
async def get_reservations_list(session: AsyncSession = Depends(async_get_db)):
    """Эндпойнт получения списка всех броней"""

    reservations_all = await session.execute(select(Reservation))
    reservations = reservations_all.scalars().all()
    return [schemas.ReservationOut.from_orm(res) for res in reservations]


@router_r.post("", response_model=schemas.ReservationOut)
async def create_new_reservation(reservation: schemas.ReservationIn,
                                 session: AsyncSession = Depends(async_get_db)) -> Reservation:
    """Эндпойнт создания новой брони"""

    match_reserves = await session.execute(select(Reservation).filter(Reservation.table_id == reservation.table_id))
    reserves = match_reserves.scalars().all()

    for reserve in reserves:
        start_reserve = reserve.reservation_time
        end_reserve = start_reserve + datetime.timedelta(minutes=reserve.duration_minutes)
        if start_reserve <= reservation.reservation_time <= end_reserve:
            raise HTTPException(status_code=400,
                                detail="Table is already reserved for this period time")
    new_reserve = Reservation(**reservation.dict())
    session.add(new_reserve)
    await session.commit()
    return new_reserve


@router_r.delete("/{res_id}")
async def delete_reservation_by_id(res_id: int, session: AsyncSession = Depends(async_get_db)):
    """Эндпойнт удаления брони по id"""

    match_reserve = await session.execute(select(Reservation).filter(Reservation.id == res_id))
    reservation = match_reserve.scalar()
    if reservation:
        await session.delete(reservation)
        await session.commit()
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Reservation not found")

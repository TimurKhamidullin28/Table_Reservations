from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from routers import router_t, router_r
from database import engine, async_get_db
from models import Base

app = FastAPI()

app.include_router(router_t)
app.include_router(router_r)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown(session: AsyncSession = Depends(async_get_db)):
    await session.close()
    await engine.dispose()

from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.models import Base, Table
from api.database import async_get_db as get_db_session
from api.main import app

DATABASE_URL_TEST = f"postgresql+asyncpg://admin:admin@localhost:5433/test_restaurant_db"


@pytest.fixture()
async def db_session():
    engine = create_async_engine(DATABASE_URL_TEST, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        table_1 = Table(name="Table 1", seats=2, location="Зал у окна")
        table_2 = Table(name="Table 2", seats=4, location="Терраса")
        session.add(table_1)
        session.add(table_2)
        yield session
        await session.close()


@pytest.fixture()
def test_app(db_session: AsyncSession):
    app.dependency_overrides[get_db_session] = lambda: db_session
    return app


@pytest.fixture()
async def async_client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://localhost:8000/",
    ) as client:
        yield client

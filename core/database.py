import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_async_engine(
    DATABASE_URL,
    #echo=True,
    future=True
)

#FastAPI dependency
async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

#prepare for garbage collector
# see tip under https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-core
async def dispose():
    await engine.dispose()


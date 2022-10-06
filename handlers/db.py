from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_create(
        session: AsyncSession, model: Callable, **kwargs) -> Callable:
    """
    Method for looking up an object with the given kwargs.
    Creating one if necessary.
    """
    statement = select(model).filter_by(**kwargs)
    async with session() as session:
        result = await session.execute(statement)
        instance = result.scalars().first()
        if instance:
            return instance
        instance = model(**kwargs)
        session.add(instance)
        await session.commit()
        return instance

from asyncio import sleep
from datetime import timedelta

from sqlalchemy import select

from db_connect.connect import async_session
from models.models import DemoUser, User
from config import DEMO_USER_EXPIRATION, MEDIA_DIR, TEMP_FILES_EXPIRATION
from shared.file_transporter import remove_files_older_than
from shared.time_utils import now_utc


async def clear_demo_users():
    """Removes expired demo accounts"""
    async with async_session() as session:
        query = select(DemoUser.user_id).filter(DemoUser.created_at + timedelta(seconds=DEMO_USER_EXPIRATION) < now_utc())
        find_ids_to_delete = await session.execute(query)
        ids_to_delete = find_ids_to_delete.scalars().all()

        if ids_to_delete:
            query = User.__table__.delete().where(User.id.in_(ids_to_delete))
            await session.execute(query)
            await session.commit()


async def clear_temp_files():
    """Removes expired temporary files"""
    temp_files_path = MEDIA_DIR.joinpath('temp')
    remove_files_older_than(temp_files_path, timedelta(seconds=TEMP_FILES_EXPIRATION))


async def run_background_task():
    """Cyclic launch of background tasks"""
    await clear_demo_users()
    await clear_temp_files()
    await sleep(300)
    await run_background_task()


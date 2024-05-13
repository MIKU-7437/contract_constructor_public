from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from starlette.requests import Request

from auth.key_tools import check_jwt_token
from models.models import Session
from db_connect.connect import get_session
from shared.time_utils import now_utc


async def get_session_data(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """Аутентификация пользователя"""
    jwt = request.headers.get('jwt')
    if not jwt:
        raise HTTPException(status_code=401, detail='Unauthorized request')

    session_data = check_jwt_token(jwt)
    if not session_data:
        raise HTTPException(status_code=401, detail='Unauthorized request')

    query = select(Session).filter_by(id=session_data['session'])
    query = query.options(noload('*'))
    find_session = await session.execute(query)
    current_session = find_session.scalar()

    if not current_session:
        raise HTTPException(status_code=401, detail='Unauthorized request')

    if current_session.expired_at < now_utc():
        raise HTTPException(status_code=401, detail='Unauthorized request')

    return {'user_id': current_session.user_id, 'session_id': session_data['session'], 'async_session': session}

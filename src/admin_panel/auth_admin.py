from datetime import datetime, timedelta

from fastapi import Depends
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.orm import noload
from starlette.requests import Request

from auth.access_checker import get_session_data
from auth.key_tools import check_password, get_jwt_token, check_jwt_token, get_refresh_token
from config import REFRESH_EXPIRATION
from db_connect.connect import async_session
from models.models import SimpleEntry, Session
from shared.time_utils import now_utc


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        async with async_session() as session:
            query = select(SimpleEntry).filter_by(login=username)
            exist_user_login = await session.execute(query)
            existing_entry = exist_user_login.scalar()

            if not existing_entry:
                return False

            if not check_password(password, existing_entry.hashed_password):
                return False

            user = existing_entry.user
            if not user.is_superuser:
                return False

            refresh_expiration = datetime.utcnow() + timedelta(seconds=REFRESH_EXPIRATION)
            new_session = Session(user=user, expired_at=refresh_expiration)
            session.add(new_session)
            await session.commit()

        new_jwt = get_jwt_token({'session': new_session.id.hex})
        new_refresh = str(new_session.refresh)

        request.session.update({'jwt': new_jwt, 'refresh': new_refresh})
        return True

    async def logout(self, request: Request) -> bool:
        jwt = request.session.get("jwt")
        session_data = check_jwt_token(jwt)

        if not session_data:
            request.session.clear()
            return True
        else:
            async with async_session() as session:
                query = select(Session).filter_by(id=session_data['session'])
                query = query.options(noload('*'))
                find_session = await session.execute(query)
                exist_session = find_session.scalar()
                exist_session.expired_at = datetime.utcnow()
                await session.commit()
                request.session.clear()
                return True

    async def __refresh(self, refresh: str) -> dict | None:
        async with async_session() as session:
            query = select(Session).filter_by(refresh=refresh)
            query = query.options(noload('*'))
            find_session = await session.execute(query)
            exist_session = find_session.scalar()

            if not exist_session:
                return

            if exist_session.expired_at < now_utc():
                return

            new_jwt = get_jwt_token({'session': exist_session.id.hex})
            exist_session.refresh = get_refresh_token()
            exist_session.expired_at = datetime.utcnow() + timedelta(seconds=REFRESH_EXPIRATION)
            await session.commit()

            response = {'jwt': new_jwt, 'refresh': exist_session.refresh}
            return response

    async def authenticate(self, request: Request, session_data=Depends(get_session_data)) -> bool:
        """Частично смысл jwt теряется из-за упрощенной аутентификации библиотеки"""
        jwt = request.session.get("token")
        refresh = request.session.get("refresh")

        session_data = check_jwt_token(jwt)
        if not session_data:
            new_keys = await self.__refresh(refresh)
            if not new_keys:
                return False
            else:
                request.session.update({'jwt': new_keys['jwt'], 'refresh': new_keys['refresh']})
                return True
        else:
            async with async_session() as session:
                query = select(Session).filter_by(id=session_data['session'])
                query = query.options(noload('*'))
                find_session = await session.execute(query)
                current_session = find_session.scalar()

                if not current_session:
                    return False

                if current_session.expired_at < now_utc():
                    return False
            return True

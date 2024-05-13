from datetime import timedelta
from uuid import uuid4
from sqlalchemy import select, and_
from sqlalchemy.orm import noload

from config import REFRESH_EXPIRATION
from models.models import User, SimpleEntry, Session, DemoUser
from shared.project_loader import add_project, ProjectLoaderException
from .auth_shemas import RegisterDTO, LoginDTO, RefreshDTO, LogoutDTO, DemoDTO
from shared.base_usecase import BaseUC
from .key_tools import get_hash, check_password, get_jwt_token, get_refresh_token
from shared.time_utils import now_utc


class DemoUC(BaseUC):
    """Create a new demo user with demo project"""
    ReqDTO = DemoDTO

    async def process_request(self, req) -> dict | None:
        new_user = User(name='anonymous', email=uuid4().hex + '@demo.com')
        self.session.add(new_user)

        refresh_expiration = now_utc() + timedelta(seconds=REFRESH_EXPIRATION)
        new_session = Session(user=new_user, expired_at=refresh_expiration)
        self.session.add(new_session)

        new_demo_user = DemoUser(user=new_user)
        self.session.add(new_demo_user)
        await self.session.flush()

        try:
            await add_project(self.session, new_user.id)
        except ProjectLoaderException as exc:
            self.add_error(error_type='system_error', message=exc, http_code=500)
            return

        new_jwt = get_jwt_token({'session': new_session.id.hex, 'demo': True})
        expiration = str(new_demo_user.expiration.total_seconds()).split('.')[0]
        response = {
            'user_id': new_user.id,
            'name': new_user.name,
            'jwt': new_jwt,
            'refresh': new_session.refresh,
            'expiration_delta': int(expiration)
        }
        return response


class RegisterUC(BaseUC):
    """Register a new user"""
    ReqDTO = RegisterDTO

    async def process_request(self, req) -> dict | None:
        query = select(User.email).filter_by(email=req.email).options(noload('*'))
        find_user_email = await self.session.execute(query)
        existing_email = find_user_email.scalar()
        if existing_email:
            self.add_error(error_type='business_error', message='Email is already exist', location='email', http_code=406)
            return

        query = select(SimpleEntry.login).filter_by(login=req.login).options(noload('*'))
        exist_user_login = await self.session.execute(query)
        existing_login = exist_user_login.scalar()
        if existing_login:
            self.add_error(error_type='business_error', message='Login is already exist', location='login', http_code=406)
            return

        hashed_password = get_hash(req.password)
        new_entry = SimpleEntry(login=req.login, hashed_password=hashed_password)
        new_user = User(name=req.name, email=req.email, simple_entry=new_entry)
        self.session.add(new_user)
        await self.session.commit()
        response = {'user_id': new_user.id, 'name': new_user.name, 'email': new_user.email, 'login': new_user.simple_entry.login}
        return response


class LoginUC(BaseUC):
    """Create a new user session, returns refresh token and jwt token"""
    ReqDTO = LoginDTO

    async def process_request(self, req) -> dict | None:
        query = select(SimpleEntry).filter_by(login=req.login).options(noload('*'))
        exist_user_entry = await self.session.execute(query)
        existing_entry = exist_user_entry.scalar()
        if not existing_entry:
            self.add_error(error_type='param_error', message='Incorrect login or password', http_code=401)
            return

        if not check_password(req.password, existing_entry.hashed_password):
            self.add_error(error_type='param_error', message='Incorrect login or password', http_code=401)
            return

        query = select(User).filter_by(id=existing_entry.user_id).options(noload('*'))
        find_user = await self.session.execute(query)
        user = find_user.scalar()

        refresh_expiration = now_utc() + timedelta(seconds=REFRESH_EXPIRATION)
        new_session = Session(user=user, expired_at=refresh_expiration)
        self.session.add(new_session)
        await self.session.commit()
        new_jwt = get_jwt_token({'session': new_session.id.hex})
        new_refresh = new_session.refresh
        response = {'user_id': user.id, 'name': user.name, 'jwt': new_jwt, 'refresh': new_refresh}
        return response


class RefreshUC(BaseUC):
    """Create new refresh token and jwt token"""
    ReqDTO = RefreshDTO

    async def process_request(self, req) -> dict | None:
        query = select(Session).filter_by(refresh=req.refresh).options(noload('*'))
        find_session = await self.session.execute(query)
        exist_session = find_session.scalar()

        if not exist_session:
            self.add_error(error_type='business_error', message='Invalid token', http_code=404)
            return

        if exist_session.expired_at < now_utc():
            self.add_error(error_type='business_error', message='Invalid token', http_code=404)
            return

        query = select(DemoUser.id).filter_by(user_id=exist_session.user_id).options(noload('*'))
        find_demo_user = await self.session.execute(query)
        exist_demo_user = find_demo_user.scalar()

        query = select(User.name).filter_by(id=exist_session.user_id).options(noload('*'))
        find_username = await self.session.execute(query)
        username = find_username.scalar()

        if exist_demo_user:
            new_jwt = get_jwt_token({'session': exist_session.id.hex, 'demo': True})
        else:
            new_jwt = get_jwt_token({'session': exist_session.id.hex})

        exist_session.refresh = get_refresh_token()
        exist_session.expired_at = now_utc() + timedelta(seconds=REFRESH_EXPIRATION)
        await self.session.commit()

        response = {'user_id': exist_session.user_id, 'name': username, 'jwt': new_jwt, 'refresh': exist_session.refresh}
        return response


class LogoutUC(BaseUC):
    """Drop user session"""
    ReqDTO = LogoutDTO

    async def process_request(self, req) -> dict | None:
        query = select(Session).filter_by(id=req.session_id).options(noload('*'))
        find_session = await self.session.execute(query)
        exist_session = find_session.scalar()
        exist_session.expired_at = now_utc()
        await self.session.commit()
        return {}


class LogoutOthersUC(BaseUC):
    """Drop other user sessions"""
    ReqDTO = LogoutDTO

    async def process_request(self, req) -> dict | None:
        query = select(Session).filter(and_(
            Session.user_id == req.user_id,
            Session.id != req.session_id,
            Session.expired_at > now_utc()
        ))
        query = query.options(noload('*'))
        find_all_sessions = await self.session.execute(query)
        current_sessions = find_all_sessions.scalars()

        for user_session in current_sessions:
            user_session.expired_at = now_utc()
        await self.session.commit()
        return {}

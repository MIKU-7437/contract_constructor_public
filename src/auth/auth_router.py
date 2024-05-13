from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from shared.common_schemas import OutputDataDTO
from .access_checker import get_session_data
from .auth_uc import RegisterUC, LoginUC, RefreshUC, LogoutUC, LogoutOthersUC, DemoUC
from db_connect.connect import get_session

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/demo/', response_model=OutputDataDTO)
async def register(session: AsyncSession = Depends(get_session)):
    uc = DemoUC({}, session)
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@auth_router.post('/register/', response_model=OutputDataDTO)
async def register(input_data: dict, session: AsyncSession = Depends(get_session)):
    uc = RegisterUC(input_data, session)
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@auth_router.post('/login/', response_model=OutputDataDTO)
async def login(input_data: dict, session: AsyncSession = Depends(get_session)):
    uc = LoginUC(input_data, session)
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@auth_router.post('/refresh/', response_model=OutputDataDTO)
async def refresh(input_data: dict, session: AsyncSession = Depends(get_session)):
    uc = RefreshUC(input_data, session)
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@auth_router.post('/logout/', response_model=OutputDataDTO)
async def logout(request: Request, session: AsyncSession = Depends(get_session)):
    session_data = await get_session_data(request, session)
    if not session_data:
        return {}
    await LogoutUC(session_data, session).exec()
    return {}


@auth_router.post('/logout-others/', response_model=OutputDataDTO)
async def logout_others(session_data=Depends(get_session_data)):
    uc = LogoutOthersUC(session_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}

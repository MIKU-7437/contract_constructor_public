from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from shared.common_schemas import OutputDataDTO
from auth.access_checker import get_session_data
from usecases.form_uc import GetFormUC, GetUpdatedFormUC


form_router = APIRouter(prefix='/project/form', tags=['Form'])


@form_router.post('/', response_model=OutputDataDTO)
async def get_form(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = GetFormUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@form_router.patch('/', response_model=OutputDataDTO)
async def get_updated_form(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = GetUpdatedFormUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


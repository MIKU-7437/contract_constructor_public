from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, Form
from fastapi.exceptions import HTTPException

from shared.common_schemas import OutputDataDTO
from auth.access_checker import get_session_data
from usecases.template_uc import CreateTemplateUC, UpdateTemplateUC, DeleteTemplateUC, TemplateFromDocxUC

template_router = APIRouter(prefix='/project/template', tags=['Template'])


@template_router.post('/create/', response_model=OutputDataDTO)
async def template_create(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = CreateTemplateUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@template_router.patch('/update/', response_model=OutputDataDTO)
async def template_update(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = UpdateTemplateUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@template_router.delete('/delete/', response_model=OutputDataDTO)
async def template_delete(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DeleteTemplateUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@template_router.post('/from-docx/', response_model=OutputDataDTO)
async def convert_docx(file: UploadFile, project_id: Annotated[int, Form()], session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], 'file': file, 'project_id': project_id}
    uc = TemplateFromDocxUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


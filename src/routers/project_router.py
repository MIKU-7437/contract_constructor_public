from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from shared.common_schemas import OutputDataDTO
from auth.access_checker import get_session_data
from usecases.project_uc import CreateProjectUC, UpdateProjectUC, DeleteProjectUC, ListProjectsUC, DetailProjectsUC


project_router = APIRouter(prefix='', tags=['Project'])


@project_router.get('/projects/', response_model=OutputDataDTO)
async def projects_list(session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id']}
    uc = ListProjectsUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@project_router.post('/project/detail/', response_model=OutputDataDTO)
async def projects_detail(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DetailProjectsUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@project_router.post('/project/create/', response_model=OutputDataDTO)
async def project_create(input_data: dict, session_data=Depends(get_session_data)):

    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = CreateProjectUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@project_router.patch('/project/update/', response_model=OutputDataDTO)
async def project_update(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = UpdateProjectUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@project_router.delete('/project/delete/', response_model=OutputDataDTO)
async def project_delete(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DeleteProjectUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}

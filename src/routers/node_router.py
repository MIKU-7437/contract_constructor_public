from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from shared.common_schemas import OutputDataDTO
from auth.access_checker import get_session_data
from usecases.node_uc import CreateNodeUC, PutNodeUC, DeleteNodeUC


node_router = APIRouter(prefix='/project/node', tags=['Nodes'])


@node_router.post('/create/', response_model=OutputDataDTO)
async def node_create(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = CreateNodeUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@node_router.put('/update/', response_model=OutputDataDTO)
async def node_update(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = PutNodeUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@node_router.delete('/delete/', response_model=OutputDataDTO)
async def node_delete(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DeleteNodeUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}

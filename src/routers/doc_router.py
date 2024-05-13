from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from shared.common_schemas import OutputDataDTO
from auth.access_checker import get_session_data
from usecases.doc_uc import DocxFromTemplateSaveUC, GetDocUC, DeleteDocUC, UpdateDocUC, ListDocsUC, DocxFromTemplateUC


doc_router = APIRouter(prefix='/project', tags=['Document'])


@doc_router.get('/documents/', response_model=OutputDataDTO)
async def docx_from_html_save(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = ListDocsUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@doc_router.post('/document/from-html/', response_model=OutputDataDTO)
async def docx_from_html(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DocxFromTemplateUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return FileResponse(response.data['file_path'], filename=response.data['filename'])


@doc_router.post('/document/from-html/save/', response_model=OutputDataDTO)
async def docx_from_html_save(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DocxFromTemplateSaveUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@doc_router.post('/document/download/', response_model=OutputDataDTO, response_class=FileResponse)
async def get_document(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = GetDocUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return FileResponse(response.data['file_path'], filename=response.data['filename'])


@doc_router.patch('/document/update/', response_model=OutputDataDTO)
async def update_document(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = UpdateDocUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}


@doc_router.delete('/document/delete/', response_model=OutputDataDTO)
async def delete_document(input_data: dict, session_data=Depends(get_session_data)):
    query_data = {'user_id': session_data['user_id'], **input_data}
    uc = DeleteDocUC(query_data, session_data['async_session'])
    response = await uc.exec()
    if not response:
        raise HTTPException(status_code=response.http_error, detail=response.errors)
    else:
        return {'data': response.data}

import traceback
from uuid import uuid4

from sqlalchemy import select, and_
from sqlalchemy.orm import noload

from converter.html_docx_converter import Converter
from schemas.doc_chemas import DocxFromTemplateSaveDTO, GetDocDTO, DeleteDocDTO, UpdateDocDTO, ListDocsDTO, \
    DocxFromTemplateDTO
from models.models import Project, Document
from shared.base_usecase import BaseUC
from config import MEDIA_DIR


class ListDocsUC(BaseUC):
    """Get existing document"""
    ReqDTO = ListDocsDTO

    async def process_request(self, req) -> list | None:
        query = select(Project).filter_by(user_id=req.user_id, id=req.project_id)
        query = query.options(noload(Project.nodes), noload(Project.templates), noload(Project.user))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        documents = []
        for doc in project.documents:
            values = {
                'id': doc.id,
                'name': doc.name,
                'created_at': doc.created_at
            }
            documents.append(values)

        return documents


class DocxFromTemplateUC(BaseUC):
    """Convert html to docx and returns without saving (with temp file)"""
    ReqDTO = DocxFromTemplateDTO

    async def process_request(self, req) -> dict | None:
        filename = req.name + '.docx'
        unique_name = uuid4().hex + '_' + filename
        temp_file_path = MEDIA_DIR.joinpath('temp', unique_name)

        try:
            Converter().html_to_docx(req.html, temp_file_path)
            return {'file_path': temp_file_path, 'filename': filename}
        except Exception:
            traceback.print_exc(limit=10)
            self.add_error(error_type='system_error', message='Error converting html to docx', http_code=500)
            return


class DocxFromTemplateSaveUC(BaseUC):
    """Convert html to docx and save"""
    ReqDTO = DocxFromTemplateSaveDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Document.name).filter_by(project_id=project_id, name=req.name)
        find_duplicate_name = await self.session.execute(query)
        duplicate_name = find_duplicate_name.scalar()
        if duplicate_name:
            self.add_error(error_type='business_error', message='Document name already exist', http_code=406)
            return

        new_doc = Document(name=req.name, project_id=req.project_id)
        self.session.add(new_doc)
        await self.session.flush()

        try:
            Converter().html_to_docx(req.html, new_doc.file_path)
            await self.session.commit()
            return {'project_id': project_id, 'document_id': new_doc.id, 'name': new_doc.name}
        except Exception:
            traceback.print_exc(limit=10)
            self.add_error(error_type='system_error', message='Error converting html to docx', http_code=500)
            return


class UpdateDocUC(BaseUC):
    """Update exist document base html"""
    ReqDTO = UpdateDocDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Document).filter_by(project_id=project_id, id=req.document_id)
        query = query.options(noload('*'))
        find_document = await self.session.execute(query)
        document = find_document.scalar()
        if not document:
            self.add_error(error_type='param_error', message='Document does not exist', http_code=404)
            return

        query = select(Document.name).filter(and_(
            Document.project_id == project_id,
            Document.name == req.name,
            Document.id != req.document_id
        ))
        find_duplicate_name = await self.session.execute(query)
        duplicate_name = find_duplicate_name.scalar()
        if duplicate_name:
            self.add_error(error_type='business_error', message='Document name already exist', http_code=406)
            return

        if req.name:
            document.name = req.name
            await self.session.flush()

        if req.html:
            try:
                Converter().html_to_docx(req.html, document.file_path)
            except Exception:
                self.add_error(error_type='system_error', message='Error converting html to docx', http_code=500)
                return

        await self.session.commit()
        return {'project_id': project_id, 'document_id': document.id, 'name': document.name}


class GetDocUC(BaseUC):
    """Get existing document"""
    ReqDTO = GetDocDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Document).filter_by(project_id=project_id, id=req.document_id)
        query = query.options(noload('*'))
        find_document = await self.session.execute(query)
        document = find_document.scalar()
        if not document:
            self.add_error(error_type='param_error', message='Document does not exist', http_code=404)
            return

        filepath = document.file_path
        filename = document.name + '.docx'

        return {'file_path': filepath, 'filename': filename}


class DeleteDocUC(BaseUC):
    """Delete existing document"""
    ReqDTO = DeleteDocDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Document).filter_by(project_id=project_id, id=req.document_id)
        query = query.options(noload('*'))
        find_document = await self.session.execute(query)
        document = find_document.scalar()
        if not document:
            self.add_error(error_type='param_error', message='Document does not exist', http_code=404)
            return

        await self.session.delete(document)
        await self.session.commit()
        return {'deleted_document': req.document_id}

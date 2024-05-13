from sqlalchemy import select, and_
from sqlalchemy.orm import noload

from converter.html_docx_converter import Converter
from schemas.template_schemas import CreateTemplateDTO, UpdateTemplateDTO, DeleteTemplateDTO, TemplateFromDocxDTO
from models.models import Project, Template
from shared.base_usecase import BaseUC
from shared.file_transporter import save_string_to_file


class CreateTemplateUC(BaseUC):
    """Create a new template"""
    ReqDTO = CreateTemplateDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Template.name).filter_by(project_id=project_id, name=req.name)
        find_duplicate = await self.session.execute(query)
        duplicate = find_duplicate.scalar()
        if duplicate:
            self.add_error(error_type='business_error', message='Template name already exist', http_code=406)
            return

        new_template = Template(name=req.name, project_id=req.project_id)
        self.session.add(new_template)
        await self.session.commit()

        save_string_to_file(new_template.file_path, req.html)
        return {'id': new_template.id, 'name': new_template.name}


class UpdateTemplateUC(BaseUC):
    """Update an exist template"""
    ReqDTO = UpdateTemplateDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Template).filter_by(project_id=project_id, id=req.template_id)
        query = query.options(noload('*'))
        find_template = await self.session.execute(query)
        template = find_template.scalar()
        if not template:
            self.add_error(error_type='param_error', message='Template does not exist', http_code=404)
            return

        query = select(Template.id).filter(and_(
            Template.project_id == project_id,
            Template.name == req.name,
            Template.id != req.template_id
        ))
        find_duplicate_name = await self.session.execute(query)
        duplicate_name = find_duplicate_name.scalar()
        if duplicate_name:
            self.add_error(error_type='business_error', message='Template name already exist', http_code=406)
            return

        if req.name is not None and template.name != req.name:
            template.name = req.name

        if req.html is not None:
            save_string_to_file(template.file_path, req.html)

        await self.session.commit()
        return {'id': template.id, 'name': template.name}


class DeleteTemplateUC(BaseUC):
    """Delete an exist template"""
    ReqDTO = DeleteTemplateDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        query = select(Template).filter_by(project_id=project_id, id=req.template_id)
        query = query.options(noload('*'))
        find_template = await self.session.execute(query)
        template = find_template.scalar()
        if not template:
            self.add_error(error_type='param_error', message='Template does not exist', http_code=404)
            return

        await self.session.delete(template)
        await self.session.commit()
        return {'deleted_template': req.template_id}


class TemplateFromDocxUC(BaseUC):
    """Convert docx to html, and create template object"""
    ReqDTO = TemplateFromDocxDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.id).filter_by(user_id=req.user_id, id=req.project_id)
        find_project_id = await self.session.execute(query)
        project_id = find_project_id.scalar()
        if not project_id:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        raw_filename = req.file.filename.split('.')
        filename = raw_filename[0]

        query = select(Template.id).filter_by(project_id=project_id, name=filename)
        find_duplicate_name = await self.session.execute(query)
        duplicate_name = find_duplicate_name.scalar()
        if duplicate_name:
            self.add_error(error_type='business_error', message='Template name already exist', http_code=406)
            return

        try:
            html_file = Converter().docx_to_html(req.file)

            new_template = Template(name=filename, project_id=req.project_id)
            self.session.add(new_template)
            await self.session.commit()

            save_string_to_file(new_template.file_path, html_file)

            return {'id': new_template.id, 'name': new_template.name, 'html': html_file}

        except Exception:
            self.add_error(error_type='param_error', message='File read error', http_code=406)
            return


from sqlalchemy import select, and_
from sqlalchemy.orm import noload

from graph_processing.graph_encoder import GraphEncoder
from shared.file_transporter import load_string_from_file
from models.models import Project
from schemas.project_schemas import CreateProjectDTO, UpdateProjectDTO, DeleteProjectDTO, ListProjectsDTO, \
    DetailProjectsDTO
from shared.base_usecase import BaseUC


class CreateProjectUC(BaseUC):
    """Create a new project"""
    ReqDTO = CreateProjectDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project.name).filter_by(user_id=req.user_id, name=req.name)
        find_duplicate_name = await self.session.execute(query)
        duplicate_name = find_duplicate_name.scalar()
        if duplicate_name:
            self.add_error(error_type='business_error', message='Project name already exist', http_code=406)
            return

        new_project = Project(name=req.name, user_id=req.user_id)
        self.session.add(new_project)
        await self.session.commit()

        return {'id': new_project.id, 'name': new_project.name}


class UpdateProjectUC(BaseUC):
    """Update existing project"""
    ReqDTO = UpdateProjectDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(user_id=req.user_id, id=req.project_id)
        query = query.options(noload('*'))
        find_project = await self.session.execute(query)
        current_project = find_project.scalar()
        if not current_project:
            self.add_error(error_type='business_error', message='Project does not exist', http_code=404)
            return

        find_duplicate_name = await self.session.execute(select(Project.name).filter(and_(
            Project.user_id == req.user_id,
            Project.name == req.name,
            Project.id != req.project_id
        )))
        duplicate_name = find_duplicate_name.scalar()
        if duplicate_name:
            self.add_error(error_type='business_error', message='Project name already exist', http_code=406)
            return

        if current_project.name != req.name:
            current_project.name = req.name
            await self.session.commit()

        return {'id': current_project.id, 'name': current_project.name}


class DeleteProjectUC(BaseUC):
    """Delete existing project"""
    ReqDTO = DeleteProjectDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(id=req.project_id)
        query = query.options(noload('*'))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='business_error', message='Project does not exist', http_code=404)
            return

        await self.session.delete(project)
        await self.session.commit()
        return {'deleted_project': req.project_id}


class ListProjectsUC(BaseUC):
    """List of user projects"""
    ReqDTO = ListProjectsDTO

    async def process_request(self, req) -> list:
        query = select(Project).filter_by(user_id=req.user_id)
        query = query.options(noload(Project.user), noload(Project.templates))
        find_projects = await self.session.execute(query)
        current_projects = find_projects.scalars()

        def get_documents(user_project: Project) -> list:
            documents = []
            for doc in user_project.documents:
                documents.append({
                    'id': doc.id,
                    'project_id': doc.project_id,
                    'name': doc.name,
                    'created_at': doc.created_at,
                })
            return documents

        projects = []
        for project in current_projects:
            projects.append({
                'id': project.id,
                'name': project.name,
                'created_at': project.created_at,
                'documents': get_documents(project),
                'nodes_count': len(project.nodes)
            })

        return projects


class DetailProjectsUC(BaseUC):
    """Details of one user projects"""
    ReqDTO = DetailProjectsDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(user_id=req.user_id, id=req.project_id)
        query = query.options(noload(Project.user))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='business_error', message='Project does not exist', http_code=404)
            return

        def get_templates(project_templates: list) -> list:
            templates = []
            for temp in project_templates:
                templates.append({
                    'template_id': temp.id,
                    'name': temp.name,
                    'created_at': temp.created_at,
                    'html': load_string_from_file(temp.file_path),
                })
            return templates

        def get_documents(documents: list) -> list:
            docs = []
            for doc in documents:
                docs.append({
                    'id': doc.id,
                    'name': doc.name,
                    'created_at': doc.created_at,
                })
            return docs

        response = {
            'id': project.id,
            'name': project.name,
            'created_at': project.created_at,
            'templates': get_templates(project.templates),
            'documents': get_documents(project.documents),
            'nodes': GraphEncoder().deserialize_nodes(project.nodes)
        }

        return response

from sqlalchemy import select
from sqlalchemy.orm import noload

from graph_processing.graph import Graph
from graph_processing.graph_encoder import GraphEncoder
from schemas.form_schemas import GetFormDTO, GetUpdatedFormDTO
from models.models import Project
from shared.base_usecase import BaseUC
from shared.file_transporter import load_string_from_file


class GetFormUC(BaseUC):
    """Get active nodes and templates from project"""
    ReqDTO = GetFormDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(user_id=req.user_id, id=req.project_id)
        query = query.options(noload(Project.user), noload(Project.documents))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        nodes = GraphEncoder().deserialize_nodes(project.nodes)
        graph = Graph(nodes)
        active_nodes = graph.unload_active
        if nodes and not active_nodes:
            self.add_errors(graph.get_errors, http_code=500)
            return

        templates = []
        for template in project.templates:
            fields = {
                'template_id': template.id,
                'name': template.name,
                'html': load_string_from_file(template.file_path)
            }
            templates.append(fields)

        for node in project.nodes:
            node_id = str(node.id)
            if node_id in active_nodes.keys():
                active_nodes[node_id]['created_at'] = node.created_at
        return {'project_id': project.id, 'project_name': project.name, 'active_nodes': active_nodes, 'templates': templates}


class GetUpdatedFormUC(BaseUC):
    """Get updated active nodes based on new contents"""
    ReqDTO = GetUpdatedFormDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(user_id=req.user_id, id=req.project_id)
        query = query.options(noload(Project.user), noload(Project.documents), noload(Project.templates))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='param_error', message='Project does not exist', http_code=404)
            return

        nodes = GraphEncoder().deserialize_nodes(project.nodes)
        graph = Graph(nodes)
        graph.change_nodes_content(req.contents)
        errors = graph.get_errors
        if errors:
            self.add_errors(errors, http_code=406)
            return
        active_nodes = graph.unload_active

        for node in project.nodes:
            node_id = str(node.id)
            if node_id in active_nodes.keys():
                active_nodes[node_id]['created_at'] = node.created_at

        return {'project_id': project.id, 'project_name': project.name, 'active_nodes': active_nodes}

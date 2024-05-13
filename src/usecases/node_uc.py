from sqlalchemy import select, and_
from sqlalchemy.orm import noload

from models.models import Project, Node
from schemas.node_schemas import CreateNodeDTO, PutNodeDTO, DeleteNodeDTO
from shared.base_usecase import BaseUC
from graph_processing.graph import Graph
from graph_processing.graph_encoder import GraphEncoder


class CreateNodeUC(BaseUC):
    """Create a new node"""
    ReqDTO = CreateNodeDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(id=req.project_id, user_id=req.user_id)
        query = query.options(noload(Project.user), noload(Project.documents), noload(Project.templates))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='business_error', message='Project does not exist', http_code=404)
            return

        try:
            query = select(Node.id).filter(Node.id.in_(req.nodes.keys()))
            find_duplicate_id = await self.session.execute(query)
            duplicate_id = find_duplicate_id.scalars().all()
            if duplicate_id:
                duplicate = []
                for node_id in duplicate:
                    duplicate.append(str(node_id))
                self.add_error(error_type='param_error', message=f'Node id already exist:{duplicate_id}', http_code=406)
                return

        except Exception:
            self.add_error(error_type='param_error', message='Incorrect nodes container, expected a dict', http_code=406)
            return

        nodes = GraphEncoder().deserialize_nodes(project.nodes)
        graph = Graph(nodes)
        new_nodes = graph.add_nodes(req.nodes)
        if not new_nodes:
            self.add_errors(graph.get_errors, http_code=406)
            return
        else:
            object_list = GraphEncoder().serialize_nodes(new_nodes, project.id)
            self.session.add_all(object_list)
            await self.session.commit()
            return {'project_id': project.id, 'nodes': new_nodes}


class PutNodeUC(BaseUC):
    """Modifies an existing nodes"""
    ReqDTO = PutNodeDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(id=req.project_id, user_id=req.user_id)
        query = query.options(noload(Project.user), noload(Project.documents), noload(Project.templates))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='business_error', message='Project does not exist', http_code=404)
            return

        nodes = GraphEncoder().deserialize_nodes(project.nodes)
        graph = Graph(nodes)
        changed_nodes = graph.change_nodes(req.nodes)
        if not changed_nodes:
            self.add_errors(graph.get_errors, http_code=406)
            return
        else:
            change_list = GraphEncoder().serialize_to_dict(changed_nodes, project.id)
            query = select(Node).filter(and_(Node.project_id == project.id, Node.id.in_(change_list.keys())))
            find_nodes = await self.session.execute(query)
            nodes_for_change = find_nodes.scalars()

            for obj in nodes_for_change:
                for field, value in change_list[str(obj.id)].items():
                    setattr(obj, field, value)

            await self.session.commit()
            return {'project_id': project.id, 'nodes': changed_nodes}


class DeleteNodeUC(BaseUC):
    """Removes nodes based on the incoming list of their id and project id"""
    ReqDTO = DeleteNodeDTO

    async def process_request(self, req) -> dict | None:
        query = select(Project).filter_by(id=req.project_id, user_id=req.user_id)
        query = query.options(noload(Project.user), noload(Project.documents), noload(Project.templates))
        find_project = await self.session.execute(query)
        project = find_project.scalar()
        if not project:
            self.add_error(error_type='business_error', message='Project does not exist', http_code=404)
            return

        nodes = GraphEncoder().deserialize_nodes(project.nodes)
        graph = Graph(nodes)
        node_changes = graph.remove_nodes(req.delete_list)

        if not node_changes:
            self.add_errors(graph.get_errors, http_code=406)
            return
        else:
            query = Node.__table__.delete().where(and_(Node.project_id == project.id, Node.id.in_(node_changes[0])))
            await self.session.execute(query)

            change_list = GraphEncoder().serialize_to_dict(node_changes[1], project.id)
            query = select(Node).filter(and_(Node.project_id == project.id, Node.id.in_(change_list.keys())))
            find_nodes = await self.session.execute(query)

            nodes_for_change = find_nodes.scalars()
            for obj in nodes_for_change:
                for field, value in change_list[str(obj.id)].items():
                    setattr(obj, field, value)

            await self.session.commit()
            return {'project_id': project.id, 'removed_nodes': node_changes[0], 'changed_nodes': node_changes[1]}

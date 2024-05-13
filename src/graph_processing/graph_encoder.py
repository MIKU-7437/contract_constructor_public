from uuid import UUID

from models.models import Node


class GraphEncoder:
    __permanent_fields = [
        'id',
        'parent_id',
        'name',
        'description',
        'data_type',
        'node_type',
        'x',
        'y',
        'active'
    ]

    def deserialize_nodes(self, nodes: list) -> dict:
        """Converts a set of node fields for use in the graph"""
        graph = {}
        for node_obj in nodes:
            non_permanent_fields = node_obj.json
            permanent_fields = self.__get_permanent_fields(node_obj)
            node_id = str(node_obj.id)
            graph[node_id] = {**permanent_fields, **non_permanent_fields}
        return graph

    def __get_permanent_fields(self, node_obj: Node) -> dict:
        fields = {}
        for field in self.__permanent_fields:
            attr = getattr(node_obj, field)
            fields[field] = str(attr) if isinstance(attr, UUID) else attr
        return fields

    def serialize_nodes(self, nodes: dict, project_id: int) -> list:
        """Converts a set of node fields for use in the database"""
        object_list = []
        for node_id, node_fields in nodes.items():
            non_permanent_fields = {}
            permanent_fields = {}
            for key, value in node_fields.items():
                if key in self.__permanent_fields:
                    permanent_fields[key] = value
                else:
                    if not value and not isinstance(value, bool):
                        continue
                    non_permanent_fields[key] = value
            obj = Node(id=node_id, json=non_permanent_fields, project_id=project_id, **permanent_fields)
            object_list.append(obj)
        return object_list

    def serialize_to_dict(self, nodes: dict, project_id: int) -> dict:
        """Sets the set of node fields to be used in models and server responses"""
        object_list = {}
        for node_id, node_fields in nodes.items():
            non_permanent_fields = {}
            permanent_fields = {}
            for key, value in node_fields.items():
                if key in self.__permanent_fields:
                    permanent_fields[key] = value
                else:
                    if not value and not isinstance(value, bool):
                        continue
                    non_permanent_fields[key] = value
            object_list[node_id] = {'json': non_permanent_fields, 'project_id': project_id, **permanent_fields}
        return object_list

from copy import deepcopy
from uuid import uuid4

import pytest
from fixtures.graph.base_example import BASE_GRAPH
from fixtures.graph.test_examples import ADD_CASE, CHANGE_CASE,\
    CHANGE_CONTENTS_CASE, REMOVE_NODES_CASE, UNLOAD_CASE, REMOVE_BRANCHES_CASE, SURVIVOR_BRANCHES
from graph_processing.graph import Graph


INCORRECT_GRAPH_CONTAINERS = ['string', b'string', 500, 50.5, [4, 5, 7], {5, 7, 8}]


@pytest.fixture
def container(request) -> Graph:
    return Graph(request.param)


@pytest.mark.parametrize('container', INCORRECT_GRAPH_CONTAINERS, indirect=True)
def test_graph_init_wrong_container(container):
    assert len(container.get_errors) != 0, 'the graph does not return an error for an invalid container'


@pytest.fixture
def container_to_reload_func(request) -> Graph:
    graph_instance = Graph()
    graph_instance.reload(request.param)
    return graph_instance


@pytest.mark.parametrize('container_to_reload_func', INCORRECT_GRAPH_CONTAINERS, indirect=True)
def test_graph_reload_wrong_container(container_to_reload_func):
    assert len(container_to_reload_func.get_errors) != 0, 'the graph does not return an error for an invalid container by reload function'


@pytest.fixture
def incorrect_id() -> dict:
    bad_id_set = {}
    bad_parent_id_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        bad_id = node_id[0:-2]
        bad_parent_id = deepcopy(fields)
        if bad_parent_id['parent_id']:
            bad_parent_id['parent_id'] = bad_parent_id['parent_id'][0:-2]
        bad_id_set[bad_id] = deepcopy(fields)
        bad_parent_id_set[node_id] = bad_parent_id

    wrong_id_graph = Graph(bad_id_set)
    wrong_parent_id_graph = Graph(bad_parent_id_set)

    wrong_id_errors = len(wrong_id_graph.get_errors)
    wrong_parent_id = len(wrong_parent_id_graph.get_errors)

    return {
        'wrong_id_errors': wrong_id_errors,
        'wrong_parent_id': wrong_parent_id,
    }


def test_graph_wrong_id(incorrect_id):
    assert incorrect_id['wrong_id_errors'], 'the graph does not respond to incorrect id'
    assert incorrect_id['wrong_parent_id'], 'the graph does not respond to incorrect parent_id'


@pytest.fixture
def non_exist_required_field(request) -> int:
    without_field_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        fields.pop(request.param)
        without_field_set[node_id] = fields

    wrong_graph = Graph(without_field_set)
    return len(wrong_graph.get_errors)


REQUIRED_FIELDS = ['name', 'data_type', 'node_type']


@pytest.mark.parametrize('non_exist_required_field', REQUIRED_FIELDS, indirect=True)
def test_graph_non_exist_required_field(non_exist_required_field):
    assert non_exist_required_field, 'the graph does not respond with an error to a non-existent required field'


@pytest.fixture
def non_exist_parent() -> int:
    bad_nodes_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        new_id = str(uuid4())
        bad_nodes_set[new_id] = fields

    wrong_graph = Graph(bad_nodes_set)
    return len(wrong_graph.get_errors)


def test_graph_non_exist_parent(non_exist_parent):
    assert incorrect_id, 'the graph does not respond to non exist parents'


@pytest.fixture
def non_exist_name() -> int:
    without_name_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        fields.pop('name')
        without_name_set[node_id] = fields

    wrong_graph = Graph(without_name_set)
    return len(wrong_graph.get_errors)


def test_graph_non_exist_name(non_exist_name):
    assert non_exist_name, 'the graph does not respond with an error to a non-existent "name" field'


@pytest.fixture
def incorrect_name(request) -> int:
    bad_nodes_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        fields['name'] = request.param
        bad_nodes_set[node_id] = fields

    wrong_graph = Graph(bad_nodes_set)
    return len(wrong_graph.get_errors)


INCORRECT_NODE_NAME = [b'string', 500, 50.5, [4, 5], {5, 7}, None]


@pytest.mark.parametrize('incorrect_name', INCORRECT_NODE_NAME, indirect=True)
def test_graph_incorrect_name(incorrect_name):
    assert incorrect_name, 'the graph does not respond with an error to a wrong "name" value'


@pytest.fixture
def incorrect_description(request) -> int:
    bad_nodes_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        fields['description'] = request.param
        bad_nodes_set[node_id] = fields

    wrong_graph = Graph(bad_nodes_set)
    return len(wrong_graph.get_errors)


INCORRECT_NODE_DESCRIPTION = [b'string', [4, 5], {5, 7}, {'a': 5, 'b': 7}]


@pytest.mark.parametrize('incorrect_description', INCORRECT_NODE_DESCRIPTION, indirect=True)
def test_graph_incorrect_description(incorrect_description):
    assert incorrect_description, 'the graph does not respond with an error to a wrong "description" value'



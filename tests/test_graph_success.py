from copy import deepcopy

import pytest
from fixtures.graph.base_example import BASE_GRAPH
from fixtures.graph.test_examples import ADD_CASE, CHANGE_CASE,\
    CHANGE_CONTENTS_CASE, REMOVE_NODES_CASE, UNLOAD_CASE, REMOVE_BRANCHES_CASE, SURVIVOR_BRANCHES
from graph_processing.graph import Graph


INCORRECT_GRAPH_CONTAINERS = ['string', b'string', 500, 50.5, [4, 5, 7], {5, 7, 8}]


@pytest.fixture
def correct_graph() -> Graph:
    return Graph(BASE_GRAPH)


@pytest.fixture
def container(request) -> Graph:
    return Graph(request.param)


def test_graph_init_success(correct_graph):
    assert isinstance(correct_graph.get_errors, list), 'get_errors function returns unexpected data type'
    assert len(correct_graph.get_errors) == 0, 'get_errors function triggered by correct graph'


@pytest.mark.parametrize('container', INCORRECT_GRAPH_CONTAINERS, indirect=True)
def test_graph_init_wrong_container(container):
    assert len(container.get_errors) != 0, 'the graph does not return an error for an invalid container'


@pytest.fixture
def graph() -> Graph:
    graph_instance = Graph()
    graph_instance.reload(BASE_GRAPH)
    return graph_instance


@pytest.fixture
def container_to_reload_func(request) -> Graph:
    graph_instance = Graph()
    graph_instance.reload(request.param)
    return graph_instance


def test_graph_reload_success(graph):
    assert isinstance(graph.get_errors, list), 'get_errors function returns unexpected data type by reload function'
    assert len(graph.get_errors) == 0, 'get_errors function triggered by correct graph with reload function'


@pytest.mark.parametrize('container_to_reload_func', INCORRECT_GRAPH_CONTAINERS, indirect=True)
def test_graph_reload_wrong_container(container_to_reload_func):
    assert len(container_to_reload_func.get_errors) != 0, 'the graph does not return an error for an invalid container by reload function'


@pytest.fixture
def non_exist_optional_field(request) -> dict:
    without_field_set = {}
    base_graph = deepcopy(BASE_GRAPH)
    for node_id, fields in base_graph.items():
        if request.param in fields:
            fields.pop(request.param)
            without_field_set[node_id] = fields

    graph = Graph(without_field_set)
    return {'error': len(graph.get_errors), 'current_field': request.param}


OPTIONAL_FIELDS = [
    'parent_id',
    'description',
    'content',
    'condition',
    'trigger',
    'x',
    'y',
    'active',
    'view_type'
]


@pytest.mark.parametrize('non_exist_optional_field', OPTIONAL_FIELDS, indirect=True)
def test_graph_non_exist_optional_field(non_exist_optional_field):
    assert not non_exist_optional_field['error'], 'error when optional field does not exist'


@pytest.fixture
def unload_func() -> dict:
    graph = Graph(BASE_GRAPH)
    unload_result = graph.unload
    graph_errors = len(graph.get_errors)

    lost_nodes = []
    for node_id, _ in BASE_GRAPH.items():
        if node_id not in unload_result:
            lost_nodes.append(node_id)

    not_calculated_nodes = []
    for node_id, fields in unload_result.items():
        if fields['active'] != UNLOAD_CASE[node_id]:
            not_calculated_nodes.append(node_id)

    return {
        'unload_result': unload_result,
        'graph_errors': graph_errors,
        'lost_nodes': lost_nodes,
        'not_calculated_nodes': not_calculated_nodes
    }


def test_unload_func(unload_func):
    assert unload_func['graph_errors'] == 0, 'error when unload nodes correctly'
    assert isinstance(unload_func['unload_result'], dict), 'the unload function does not return a dictionary'
    assert not unload_func['lost_nodes'], 'unload function does not return all nodes'
    assert not unload_func['not_calculated_nodes'], 'some nodes were not calculated'


@pytest.fixture
def unload__active_func() -> dict:
    graph = Graph(BASE_GRAPH)
    unload_result = graph.unload
    unload_active_result = graph.unload_active
    graph_errors = len(graph.get_errors)

    lost_active_nodes = []
    received_not_active_nodes = []
    for node_id, fields in unload_result.items():
        if fields['active'] is True and node_id not in unload_active_result:
            lost_active_nodes.append(node_id)

        if fields['active'] is False and node_id in unload_active_result:
            received_not_active_nodes.append(node_id)

    return {
        'unload_active_result': unload_active_result,
        'graph_errors': graph_errors,
        'lost_active_nodes': lost_active_nodes,
        'received_not_active_nodes': received_not_active_nodes
    }


def test_unload_active_func(unload__active_func):
    assert unload__active_func['graph_errors'] == 0, 'error when unload_active nodes correctly'
    assert isinstance(unload__active_func['unload_active_result'], dict), 'the unload_active function does not return a dictionary'
    assert not unload__active_func['lost_active_nodes'], 'the unload_active function does not return all active nodes'
    assert not unload__active_func['received_not_active_nodes'], 'the unload_active function returns inactive nodes'



@pytest.fixture
def add_nodes() -> dict:
    graph = Graph(BASE_GRAPH)
    new_nodes = graph.add_nodes(ADD_CASE)
    graph_errors = len(graph.get_errors)
    new_graph_kit = graph.unload

    not_added_nodes = []
    for node in new_nodes.keys():
        if node not in new_graph_kit.keys():
            not_added_nodes.append(node)

    return {
        'graph_errors': graph_errors,
        'new_nodes': new_nodes,
        'not_added_nodes': not_added_nodes,
    }


def test_add_nodes_success(add_nodes):
    assert add_nodes['graph_errors'] == 0, 'error when adding nodes correctly'
    assert add_nodes['new_nodes'], 'add_nodes function does not return anything'
    assert isinstance(add_nodes['new_nodes'], dict), 'the add_nodes function does not return a dict'
    assert not add_nodes['not_added_nodes'], 'the add_nodes function did not add all nodes or the unload function does not work correctly'


@pytest.fixture
def change_nodes() -> dict:
    graph = Graph(BASE_GRAPH)
    graph_errors = len(graph.get_errors)
    updated_nodes = graph.change_nodes(CHANGE_CASE)

    non_changed_nodes = []
    for node in CHANGE_CASE.keys():
        if node not in updated_nodes:
            non_changed_nodes.append(node)

    non_changed_fields = []
    for node_id, fields in CHANGE_CASE.items():
        for field, target_value in fields.items():
            result_value = updated_nodes[node_id][field]
            if target_value != result_value and field != 'active':
                non_changed_fields.append(node_id)

    return {
        'graph_errors': graph_errors,
        'updated_nodes': updated_nodes,
        'non_changed_nodes': non_changed_nodes,
        'non_changed_fields': non_changed_fields,
        }


def test_change_nodes_success(change_nodes):
    assert change_nodes['graph_errors'] == 0, 'error when changing nodes correctly'
    assert change_nodes['updated_nodes'], 'add_nodes function does not return anything'
    assert isinstance(change_nodes['updated_nodes'], dict), 'the add_nodes function does not return a dict'
    assert not change_nodes['non_changed_nodes'], 'the change_nodes function did not return all changed nodes'
    assert not change_nodes['non_changed_fields'], 'the change_nodes function did not change all fields'


@pytest.fixture
def change_nodes_contents() -> dict:
    graph = Graph(BASE_GRAPH)
    graph.change_nodes_content(CHANGE_CONTENTS_CASE)
    graph_errors = len(graph.get_errors)
    updated_nodes = graph.unload_active
    all_nodes = graph.unload

    non_changed_nodes = []
    for node_id, target_content in CHANGE_CONTENTS_CASE.items():
        result_content = all_nodes[node_id]['content']
        if result_content != target_content:
            non_changed_nodes.append(node_id)

    return {
        'graph_errors': graph_errors,
        'updated_nodes': updated_nodes,
        'non_changed_nodes': non_changed_nodes,
    }


def test_change_nodes_contents_success(change_nodes_contents):
    assert change_nodes_contents['graph_errors'] == 0, 'error when changing nodes content correctly'
    assert change_nodes_contents['updated_nodes'], 'change_nodes_contents did not change the contents of the nodes or the unload_active function does not work correctly'
    assert not change_nodes_contents['non_changed_nodes'], 'the change_nodes_content function did not change content all specified nodes'


@pytest.fixture
def remove_nodes() -> dict:
    graph = Graph(BASE_GRAPH)
    removed_result = graph.remove_nodes(REMOVE_NODES_CASE)
    graph_errors = len(graph.get_errors)
    remaining_nodes = graph.unload
    removed_nodes = removed_result[0]
    changed_nodes = removed_result[1]

    non_removed_nodes = []
    for node_id in REMOVE_NODES_CASE:
        if node_id in remaining_nodes:
            non_removed_nodes.append(node_id)

    return {
        'graph_errors': graph_errors,
        'removed_nodes': removed_nodes,
        'changed_nodes': changed_nodes,
        'non_removed_nodes': non_removed_nodes
    }


def test_remove_nodes_success(remove_nodes):
    assert remove_nodes['graph_errors'] == 0, 'error when removing nodes correctly'
    assert remove_nodes['removed_nodes'], 'the removed_nodes function did not return a list of removed nodes'
    assert remove_nodes['changed_nodes'], 'the removed_nodes function did not return changed nodes'
    assert not remove_nodes['non_removed_nodes'], 'the removed_nodes function did not remove all specified nodes'


@pytest.fixture
def remove_branches() -> dict:
    graph = Graph(BASE_GRAPH)
    removed_result = graph.remove_nodes(REMOVE_BRANCHES_CASE, remove_branches=True)
    graph_errors = len(graph.get_errors)
    remaining_nodes = graph.unload
    removed_nodes_list = removed_result[0]
    changed_nodes = removed_result[1]

    excess_removed_nodes = []
    for node_id in SURVIVOR_BRANCHES:
        if node_id not in remaining_nodes:
            excess_removed_nodes.append(node_id)

    removed_nodes = set(BASE_GRAPH.keys()).difference(set(SURVIVOR_BRANCHES))
    non_removed_nodes = []
    for node_id in remaining_nodes:
        if node_id in removed_nodes:
            non_removed_nodes.append(node_id)

    incorrect_removing_list = []
    for node_id in removed_nodes:
        if node_id not in removed_nodes_list:
            incorrect_removing_list.append(node_id)

    return {
        'graph_errors': graph_errors,
        'removed_nodes_list': removed_nodes_list,
        'changed_nodes': changed_nodes,
        'excess_removed_nodes': excess_removed_nodes,
        'non_removed_nodes': non_removed_nodes,
        'incorrect_removing_list': incorrect_removing_list,
    }


def test_remove_branches_success(remove_branches):
    assert remove_branches['graph_errors'] == 0, 'error when removing branches correctly'
    assert isinstance(remove_branches['removed_nodes_list'], list), 'the removed_branches function did not return a list of removed nodes'
    assert isinstance(remove_branches['changed_nodes'], dict), 'the removed_branches function not returns a dict'
    assert not remove_branches['non_removed_nodes'], 'the removed_branches function did not remove all specified nodes'
    assert not remove_branches['incorrect_removing_list'], 'the removed_branches function returns an incomplete list of remote nodes'
    assert not remove_branches['excess_removed_nodes'], 'the removed_branches function remove excess nodes'

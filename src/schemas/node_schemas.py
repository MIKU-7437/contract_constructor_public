"""Available params:
'type':(class,),
'min_length':int,
'max_length':int,
'default': any,
'uuid4': True,
'email': True,
'f_level_type': (str,)
"""


from shared.base_input_dto import BaseDTO


class CreateNodeDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    nodes = {'type': (dict,)}


class PutNodeDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    nodes = {'type': (dict,)}


class DeleteNodeDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    delete_list = {'type': (list,), 'f_level_type': (str,)}

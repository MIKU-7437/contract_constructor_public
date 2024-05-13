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


class CreateProjectDTO(BaseDTO):
    user_id = {'type': (int,)}
    name = {'type': (str,), 'min_length': 1}


class UpdateProjectDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    name = {'type': (str,), 'min_length': 1}


class DeleteProjectDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}


class ListProjectsDTO(BaseDTO):
    user_id = {'type': (int,)}


class DetailProjectsDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}

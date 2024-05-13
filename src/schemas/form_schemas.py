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


class GetFormDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}


class GetUpdatedFormDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    contents = {'type': (dict,)}

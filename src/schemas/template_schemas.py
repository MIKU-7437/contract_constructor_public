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
from starlette.datastructures import UploadFile


class CreateTemplateDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    name = {'type': (str,), 'min_length': 1}
    html = {'type': (str,)}


class UpdateTemplateDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    template_id = {'type': (int,)}
    name = {'type': (str,), "default": None, 'min_length': 1}
    html = {'type': (str,), "default": None}


class DeleteTemplateDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    template_id = {'type': (int,)}


class TemplateFromDocxDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    file = {'type': (UploadFile,)}

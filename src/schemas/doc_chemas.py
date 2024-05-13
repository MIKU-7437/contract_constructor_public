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


class DocxFromTemplateSaveDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    name = {'type': (str,), 'min_length': 1}
    html = {'type': (str,)}


class DocxFromTemplateDTO(BaseDTO):
    user_id = {'type': (int,)}
    name = {'type': (str,)}
    html = {'type': (str,)}


class GetDocDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    document_id = {'type': (int,)}


class DeleteDocDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    document_id = {'type': (int,)}


class UpdateDocDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}
    document_id = {'type': (int,)}
    name = {'type': (str,), 'default': None}
    html = {'type': (str,), 'default': None}


class ListDocsDTO(BaseDTO):
    user_id = {'type': (int,)}
    project_id = {'type': (int,)}

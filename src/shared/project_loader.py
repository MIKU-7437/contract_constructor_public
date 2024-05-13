from sqlalchemy import select

from config import DEMO_PROJECT_DIR
from graph_processing.graph_encoder import replace_id, GraphEncoder
from models.models import Project, Document, Template
from shared.file_transporter import load_json, copy_file


class ProjectLoaderException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


async def add_project(session, user_id: int) -> None:
    """Loads a project from a dump into the specified user account."""
    project_dump = load_json(DEMO_PROJECT_DIR.joinpath('dump', 'dump.json'))
    if not project_dump:
        raise ProjectLoaderException('Error: Project dump does not exist')

    project_name = project_dump['name']

    query = select(Project.name).filter_by(user_id=user_id, name=project_name)
    find_duplicate_name = await session.execute(query)
    duplicate_name = find_duplicate_name.scalar()
    if duplicate_name:
        raise ProjectLoaderException(f'Error: Project name "{project_name}" already exists for user account "{user_id}"')

    new_project = Project(name=project_name, user_id=user_id)
    session.add(new_project)

    for doc in project_dump['documents']:
        new_doc = Document(name=doc['name'], project=new_project)
        session.add(new_doc)
        await session.flush()
        old_filepath = DEMO_PROJECT_DIR.joinpath('dump', 'documents', str(doc['id'])).with_suffix('.docx')
        copy_file(old_filepath, new_doc.file_path.parent, new_name=new_doc.file_path.name)

    for temp in project_dump['templates']:
        new_temp = Template(name=temp['name'], project=new_project)
        session.add(new_temp)
        await session.flush()
        old_filepath = DEMO_PROJECT_DIR.joinpath('dump', 'templates', str(temp['id'])).with_suffix('.html')
        copy_file(old_filepath, new_temp.file_path.parent, new_name=new_temp.file_path.name)

    nodes = replace_id(project_dump['nodes'])
    object_list = GraphEncoder().serialize_nodes(nodes, new_project.id)
    session.add_all(object_list)
    await session.commit()

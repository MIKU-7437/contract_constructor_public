"""
A CLI script to download the target project from a user account, save it to the file system,
and load the dump back into the specified user account.
Used to create demo user accounts and work with the demo project.

Commands:
Download project to dump.
cli_demo_project.py dump <project_id>

Upload project to user account.
cli_demo_project.py load <user_id>
"""


import asyncio
from platform import system
import sys

from sqlalchemy import select
from sqlalchemy.orm import noload

from config import DEMO_PROJECT_DIR
from db_connect.connect import async_session
from graph_processing.graph_encoder import GraphEncoder
from models.models import User, Project
from shared.file_transporter import copy_file, save_json, remove_folder
from shared.project_loader import add_project, ProjectLoaderException


async def dump_project(project_id: int) -> None:
    """Saving the target project to the file system"""
    async with async_session() as session:
        query = select(Project).filter_by(id=project_id)
        query = query.options(noload(Project.user))
        find_project = await session.execute(query)
        project = find_project.scalar()

        if not project:
            print(f'Error: Project "{project_id}" does not exist')
            sys.exit(1)

        def get_templates(project_templates: list) -> list:
            templates = []
            for temp in project_templates:
                copy_file(temp.file_path, DEMO_PROJECT_DIR.joinpath('dump', 'templates'))
                templates.append({
                    'id': temp.id,
                    'name': temp.name,
                })
            return templates

        def get_documents(project_docs: list) -> list:
            docs = []
            for doc in project_docs:
                copy_file(doc.file_path, DEMO_PROJECT_DIR.joinpath('dump', 'documents'))
                docs.append({
                    'id': doc.id,
                    'name': doc.name,
                })
            return docs

        remove_folder(DEMO_PROJECT_DIR.joinpath('dump'))

        dump_data = {
            'id': project_id,
            'name': project.name,
            'templates': get_templates(project.templates),
            'documents': get_documents(project.documents),
            'nodes': GraphEncoder().deserialize_nodes(project.nodes)
        }
        save_json(DEMO_PROJECT_DIR.joinpath('dump', 'dump.json'), dump_data)
        print(f'Project "{project_id}" successfully saved')


async def load_project(user_id: int) -> None:
    """Loading a project from the file system into a specified user account"""
    async with async_session() as session:
        query = select(User.id).filter_by(id=user_id)
        find_user_id = await session.execute(query)

        if not find_user_id:
            print(f'Error: User "{user_id}" does not exist')
            sys.exit(1)

        try:
            await add_project(session, user_id)
        except ProjectLoaderException as exc:
            print(exc)
            sys.exit(1)

        print(f'Project successfully added to user "{user_id}"')


def create_loop(operation_type: str, identifier: int) -> None:
    if system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if operation_type == 'dump':
        asyncio.run(dump_project(identifier))
    if operation_type == 'load':
        asyncio.run(load_project(identifier))


def run_cli(launch_args: list) -> None:
    if len(launch_args) < 2:
        print('Error: 2 positional arguments required: "dump" and "<project_id>" or "load" and "<user_id>"')
        sys.exit(1)

    if launch_args[1] not in ['dump', 'load']:
        print('Error: The first positional argument should be "dump" or "load"')
        sys.exit(1)

    try:
        obj_id = int(launch_args[2])
    except Exception:
        print('Error: The second positional argument should be integer')
        sys.exit(1)

    create_loop(launch_args[1], obj_id)


args = sys.argv
run_cli(args)

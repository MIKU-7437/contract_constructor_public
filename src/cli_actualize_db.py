"""
The CLI script updates the "active" state of all database nodes according to the current graph configuration.

Command:
    cli_actualize_db.py
"""


import asyncio
from platform import system
import sys

from sqlalchemy import select

from db_connect.connect import async_session
from graph_processing.graph import Graph
from graph_processing.graph_encoder import GraphEncoder
from models.models import Project


async def actualize_database() -> None:
    """Runs all project nodes through the graph, updating their state in the database"""
    async with async_session() as session:
        get_projects_id = await session.execute(select(Project.id))
        projects_id = get_projects_id.scalars().all()

        for project_id in projects_id:
            project = await session.get(Project, project_id)
            nodes = project.nodes
            if not nodes:
                continue

            deserialized_nodes = GraphEncoder().deserialize_nodes(nodes)
            graph = Graph(deserialized_nodes)
            actualize_nodes = graph.unload

            if not actualize_nodes:
                print(f'ACTUALIZE ERROR: {graph.get_errors}')
                sys.exit(1)

            change_list = GraphEncoder().serialize_to_dict(actualize_nodes, project_id)

            for node in nodes:
                for field, value in change_list[str(node.id)].items():
                    setattr(node, field, value)

            await session.flush()

        await session.commit()
        print('The database has been successfully actualized')


def create_loop() -> None:
    if system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(actualize_database())


create_loop()



"""
A CLI script creates the superuser.

Command for create superuser (by one call):
    cli_create_superuser.py <login> <password> <email>
Or just run script:
    cli_create_superuser.py
and fill all data in interactive mode.
"""


import asyncio
from platform import system
import sys

from sqlalchemy import select

from auth.key_tools import get_hash
from db_connect.connect import async_session
from models.models import User, SimpleEntry


async def create_superuser(ad_login: str, ad_password: str, ad_email: str) -> None:
    async with async_session() as session:
        query = select(User.email).filter_by(email=ad_email)
        duplicate_user_mail = await session.execute(query)
        duplicate_email = duplicate_user_mail.scalar()

        if duplicate_email:
            print(f'Error: user email "{ad_email}" is already exist')
            sys.exit(1)

        query = select(SimpleEntry.login).filter_by(login=ad_login)
        duplicate_user_login = await session.execute(query)
        duplicate_login = duplicate_user_login.scalar()
        if duplicate_login:
            print(f'Error: user login "{ad_login}" is already exist')
            sys.exit(1)

        hashed_password = get_hash(ad_password)
        new_entry = SimpleEntry(login=ad_login, hashed_password=hashed_password)
        new_user = User(name='admin', email=ad_email, simple_entry=new_entry, is_superuser=True, is_active=True, is_verified=True)
        session.add(new_user)
        await session.commit()
        print(f'Superuser "{ad_login}" successfully registered')


def create_loop(ad_login: str, ad_password: str, ad_email: str) -> None:
    if system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_superuser(ad_login, ad_password, ad_email))


def for_program(launch_args: list) -> None:
    if len(launch_args) < 4:
        print('Error: Requires "login", "password", "email" arguments')
        sys.exit(1)
    else:
        create_loop(launch_args[1], launch_args[2], launch_args[3])


def for_user(launch_args: list) -> None:
    if len(launch_args) < 4:
        ad_login = input('Enter your login: ')
        ad_password = input('Enter your password: ')
        ad_email = input('Enter your email: ')
    else:
        ad_login, ad_password, ad_email = launch_args[1], launch_args[2], launch_args[3]
    create_loop(ad_login, ad_password, ad_email)


args = sys.argv


if sys.__stdin__.isatty():
    for_user(args)
else:
    for_program(args)






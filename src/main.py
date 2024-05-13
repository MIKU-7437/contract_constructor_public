import asyncio

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqladmin import Admin

from admin_panel.auth_admin import AdminAuth
from admin_panel.interface import Users, DemoUsers, UserSessions, Projects, Documents, Templates, Nodes
from db_connect.connect import engine
from routers.doc_router import doc_router
from routers.form_router import form_router
from routers.project_router import project_router
from routers.node_router import node_router
from routers.template_router import template_router
from shared.exception_handlers import validation_exception_handler, http_exception_handler, general_exception_handler
from auth.auth_router import auth_router
from models.models_events import events_initialize
from config import API_V1
from background.tasks import run_background_task


app = FastAPI()

# admin panel
authentication_backend = AdminAuth(secret_key="123")
admin = Admin(app, engine, authentication_backend=authentication_backend, title='CID Admin')
admin.add_view(Users)
admin.add_view(DemoUsers)
admin.add_view(UserSessions)
admin.add_view(Projects)
admin.add_view(Documents)
admin.add_view(Templates)
admin.add_view(Nodes)


# app routers
app.include_router(auth_router, prefix=API_V1)
app.include_router(project_router, prefix=API_V1)
app.include_router(node_router, prefix=API_V1)
app.include_router(template_router, prefix=API_V1)
app.include_router(form_router, prefix=API_V1)
app.include_router(doc_router, prefix=API_V1)


# exception handlers used to reduce to a single form of response
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# run sqlalchemy events
events_initialize()


# cyclic launch of background tasks
evl = asyncio.get_running_loop()
evl.create_task(run_background_task())


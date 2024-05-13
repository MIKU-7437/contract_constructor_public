from datetime import timedelta

from sqladmin import ModelView

from models.models import User, DemoUser, Session, Project, Document, Template, Node


class Users(ModelView, model=User):
    can_create = False
    icon = "fa fa-users"
    category = "Database"
    column_list = [User.id, User.name, 'login', User.email, User.is_active, User.is_verified, User.is_superuser,
                   User.created_at, User.updated_at]
    column_searchable_list = [User.email, User.created_at]
    column_sortable_list = [User.id, User.is_active, User.is_verified, User.is_superuser, User.name, User.created_at,
                            User.updated_at]
    column_default_sort = [(User.created_at, True)]
    form_columns = [User.name, User.email, User.is_active, User.is_verified]
    column_formatters = {
        User.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        User.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None)
    }

    page_size = 50


class DemoUsers(ModelView, model=DemoUser):
    can_create = False
    icon = "fa fa-user-secret"
    category = "Database"
    column_list = [DemoUser.user_id, DemoUser.created_at, DemoUser.updated_at, 'expiration']
    column_searchable_list = [DemoUser.created_at]
    column_sortable_list = [DemoUser.user_id, DemoUser.created_at]
    column_default_sort = [(DemoUser.created_at, True)]
    column_formatters = {
        DemoUser.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        DemoUser.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        'expiration': lambda m, a: str(m.expiration).split('.')[0]
    }
    page_size = 50


class UserSessions(ModelView, model=Session):
    can_create = False
    can_edit = False
    icon = "fa fa-exchange"
    category = "Database"
    column_list = [Session.id, Session.user_id, 'user_name', 'user_email', Session.created_at, Session.updated_at,
                   'expiration']
    column_searchable_list = [Session.created_at]
    column_sortable_list = [Session.id, Session.user_id, Session.created_at, Session.updated_at]
    column_default_sort = [(Session.created_at, True)]
    column_formatters = {
        Session.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        Session.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        'expiration': lambda m, a: str(m.expiration).split('.')[0] if m.expiration > timedelta(seconds=0) else timedelta(seconds=0)
    }
    page_size = 50


class Projects(ModelView, model=Project):
    icon = "fa fa-object-group"
    category = "Database"
    column_list = [Project.id, Project.name, Project.user_id, Project.user, Project.created_at, Project.updated_at]
    column_searchable_list = [Project.user_id, Project.name]
    column_sortable_list = [Project.id, Project.name, Project.user_id, Project.created_at, Project.updated_at]
    column_default_sort = [(Project.created_at, True)]
    form_excluded_columns = [Project.created_at, Project.updated_at, Project.documents, Project.templates, Project.nodes]
    column_formatters = {
        Project.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        Project.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None)
    }
    page_size = 50


class Documents(ModelView, model=Document):
    icon = "fa fa-shopping-bag"
    category = "Database"
    can_create = False
    column_list = [Document.id, Document.name, Document.project_id, Document.project, Document.created_at, Document.updated_at]
    column_searchable_list = [Document.project_id, Document.name]
    column_sortable_list = [Document.id, Document.name, Document.project_id, Document.created_at, Document.updated_at]
    column_default_sort = [(Document.created_at, True)]
    form_excluded_columns = [Document.created_at, Document.updated_at]
    column_formatters = {
        Document.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        Document.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None)
    }
    page_size = 50


class Templates(ModelView, model=Template):
    icon = "fa fa-file"
    category = "Database"
    can_create = False
    column_list = [Template.id, Template.name, Template.project_id, Template.project, Template.created_at, Template.updated_at]
    column_searchable_list = [Template.project_id, Template.name]
    column_sortable_list = [Template.id, Template.project_id, Template.name, Template.created_at, Template.updated_at]
    column_default_sort = [(Template.created_at, True)]
    form_excluded_columns = [Template.created_at, Template.updated_at]
    column_formatters = {
        Template.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        Template.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None)
    }
    page_size = 50


class Nodes(ModelView, model=Node):
    icon = "fa fa-share-alt"
    category = "Database"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [Node.id, Node.name, Node.project_id, Node.project, Node.created_at, Node.updated_at]
    column_searchable_list = [Node.project_id]
    column_sortable_list = [Node.name, Node.project_id, Node.created_at, Node.updated_at]
    column_default_sort = [(Node.created_at, True)]
    column_formatters = {
        Node.created_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None),
        Node.updated_at: lambda m, a: m.created_at.replace(microsecond=0, tzinfo=None)
    }
    page_size = 50

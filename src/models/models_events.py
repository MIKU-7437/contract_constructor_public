from sqlalchemy import event

from shared.file_transporter import remove_file, remove_folder
from models.models import Template, Document, Project


def events_initialize():
    @event.listens_for(Template, 'after_delete')
    def intercept_deleted_to_detached(mapper, connection, target):
        remove_file(target.file_path)

    @event.listens_for(Document, 'after_delete')
    def intercept_deleted_to_detached(mapper, connection, target):
        remove_file(target.file_path)

    @event.listens_for(Project, 'after_delete')
    def intercept_deleted_to_detached(mapper, connection, target):
        remove_folder(target.folder_path)

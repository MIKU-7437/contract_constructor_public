import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import String, ForeignKey, Column, Boolean, DateTime, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID

from config import MEDIA_DIR, DEMO_USER_EXPIRATION
from shared.time_utils import now_utc

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)

    simple_entry: Mapped['SimpleEntry'] = relationship(back_populates='user', cascade='all, delete', lazy='selectin')
    demo_user: Mapped['DemoUser'] = relationship(back_populates='user', cascade='all, delete')
    projects = relationship('Project', back_populates='user', cascade='all, delete')
    sessions = relationship('Session', back_populates='user', cascade='all, delete')

    def __str__(self):
        return f'{self.name} (id: {self.id}, email: {self.email})'

    @property
    def login(self):
        return self.simple_entry.login


class DemoUser(Base):
    __tablename__ = 'demo_users'

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='demo_user', lazy='selectin')

    def __str__(self):
        return str(self.id)

    @property
    def expiration(self):
        return self.created_at + timedelta(seconds=DEMO_USER_EXPIRATION) - now_utc()


class SimpleEntry(Base):
    __tablename__ = 'simple_entries'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='simple_entry', lazy='selectin')

    def __str__(self):
        return str(self.login)


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    refresh = Column(UUID(as_uuid=True), default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)
    expired_at = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='sessions', lazy='selectin')

    def __str__(self):
        return str(self.id)

    @property
    def user_name(self) -> str:
        return self.user.name

    @property
    def user_email(self) -> str:
        return self.user.email

    @property
    def expiration(self):
        return self.expired_at - now_utc()


class Project(Base):
    __tablename__ = 'projects'
    __table_args__ = (UniqueConstraint('name', 'user_id'),)

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='projects', lazy='selectin')
    documents = relationship('Document', back_populates='project', cascade='all, delete', lazy='selectin')
    templates = relationship('Template', back_populates='project', cascade='all, delete', lazy='selectin')
    nodes = relationship('Node', back_populates='project', cascade='all, delete', lazy='selectin')

    def __str__(self):
        return self.name

    @property
    def folder_path(self):
        return MEDIA_DIR.joinpath(str(self.id))


class Document(Base):
    __tablename__ = 'documents'
    __table_args__ = (UniqueConstraint('name', 'project_id'),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)

    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    project = relationship('Project', back_populates='documents')

    @property
    def file_path(self):
        return MEDIA_DIR.joinpath(str(self.project_id), 'documents', str(self.id)).with_suffix('.docx')

    def __str__(self):
        return str(self.id)


class Template(Base):
    __tablename__ = 'templates'
    __table_args__ = (UniqueConstraint('name', 'project_id'),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)

    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    project = relationship('Project', back_populates='templates')

    @property
    def file_path(self):
        return MEDIA_DIR.joinpath(str(self.project_id), 'templates', str(self.id)).with_suffix('.html')

    def __str__(self):
        return str(self.id)


class Node(Base):
    __tablename__ = 'nodes'

    id = Column(UUID(as_uuid=True), primary_key=True)
    parent_id = Column(UUID(as_uuid=True))
    name = Column(String, nullable=False)
    description = Column(String)
    data_type = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    x = Column(Integer)
    y = Column(Integer)
    active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=now_utc, default=now_utc)
    json = Column(JSON)

    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    project = relationship('Project', back_populates='nodes')

    def __str__(self):
        return str(self.id)

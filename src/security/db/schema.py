from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, \
    UniqueConstraint, Boolean

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    yoauth_uid = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)


class UserAccess(Base):
    __tablename__ = 'accesses'
    id = Column(Integer, primary_key=True, autoincrement=True)

    read = Column(Boolean, default=True, nullable=False)
    write = Column(Boolean, default=True, nullable=False)
    grant = Column(Boolean, default=True, nullable=False)

    user_id = Column(Integer,
                     ForeignKey('users.id', onupdate="CASCADE",
                                ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer,
                        ForeignKey('projects.id', onupdate="CASCADE",
                                   ondelete="CASCADE"), nullable=False)


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    access_r = relationship("UserAccess", cascade="all,delete",
                            backref="projects")

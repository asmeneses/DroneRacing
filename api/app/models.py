from sqlalchemy import create_engine, Column, String, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum as StatusEnum
from werkzeug.security import generate_password_hash, check_password_hash
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id            = Column(Integer, primary_key=True)
    username      = Column(String(20), unique=True, nullable=False)
    email         = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Status(StatusEnum):
    UPLOADING = "uploading"
    UPLOADED  = "uploaded"
    CONVERTED = "converted"

class Video(Base):
    __tablename__ = 'videos'
    id              = Column(Integer, primary_key=True)
    filename        = Column(String, nullable=False)
    status          = Column(Enum(Status), default=Status.UPLOADING)

    def json(self):
        return {"id": self.id, "filename": self.filename, "status": self.status.__str__()}

engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
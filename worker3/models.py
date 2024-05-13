from sqlalchemy import create_engine, Column, String, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum as StatusEnum
import os

Base = declarative_base()

class Status(StatusEnum):
    UPLOADING = "uploading"
    UPLOADED  = "uploaded"
    CONVERTED = "converted"

class Video(Base):
    __tablename__ = 'videos'
    id              = Column(Integer, primary_key=True)
    filename        = Column(String, nullable=False)
    status          = Column(Enum(Status), default=Status.UPLOADING)
    bucket_filename = Column(String, nullable=False)

engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
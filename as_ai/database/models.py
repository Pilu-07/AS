from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Fallback to sqlite if no DB url provided, else PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.db"))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    datasets = relationship("Dataset", back_populates="owner")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("User")
    members = relationship("TeamMember", back_populates="team")
    datasets = relationship("Dataset", back_populates="team")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="viewer") # owner, editor, viewer
    
    team = relationship("Team", back_populates="members")
    user = relationship("User")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    file_path = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    rows = Column(Integer, default=0)
    columns = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("User", back_populates="datasets")
    team = relationship("Team", back_populates="datasets")
    insights = relationship("DatasetInsight", back_populates="dataset", cascade="all, delete-orphan")
    dashboard = relationship("DatasetDashboard", back_populates="dataset", uselist=False, cascade="all, delete-orphan")

class DatasetDashboard(Base):
    __tablename__ = "dataset_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), unique=True)
    dashboard_config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="dashboard")

class DatasetInsight(Base):
    __tablename__ = "dataset_insights"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    insight_type = Column(String, index=True)
    description = Column(String)
    importance_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="insights")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

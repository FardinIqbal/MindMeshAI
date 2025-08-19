from sqlalchemy import Column, Integer, String, ForeignKey, Float, Enum, JSON, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid

from .database import Base


class NodeType(str, enum.Enum):
    claim = "claim"
    counter = "counter"
    rebuttal = "rebuttal"
    evidence = "evidence"


class SourceTier(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    created_at = Column(String)
    updated_at = Column(String)

    nodes = relationship("Node", back_populates="project")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(String, ForeignKey("nodes.id"))
    type = Column(Enum(NodeType), nullable=False)
    text = Column(String, nullable=False)
    strength = Column(Integer, default=0)
    fallacies = Column(JSON)
    lens = Column(JSON)

    project = relationship("Project", back_populates="nodes")
    parent = relationship("Node", remote_side=[id])
    citations = relationship("Citation", back_populates="node")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String)
    tier = Column(Enum(SourceTier))
    confidence = Column(Float)

    node = relationship("Node", back_populates="citations")

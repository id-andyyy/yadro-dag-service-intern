from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base


class Graph(Base):
    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True)
    nodes = relationship("Node", cascade="all, delete", backref="graph")
    edges = relationship("Edge", cascade="all, delete", backref="graph")

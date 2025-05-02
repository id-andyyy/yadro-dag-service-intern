from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    graph_id = Column(Integer, ForeignKey(
        "graphs.id", ondelete="CASCADE"), nullable=False)

    edges_from = relationship("Edge", back_populates="source_node",
                              foreign_keys="Edge.source_id", cascade="all, delete")
    edges_to = relationship("Edge", back_populates="target_node",
                            foreign_keys="Edge.target_id", cascade="all, delete")

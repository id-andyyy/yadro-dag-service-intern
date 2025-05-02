from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    graph_id = Column(Integer, ForeignKey(
        "graphs.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey(
        "nodes.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey(
        "nodes.id", ondelete="CASCADE"), nullable=False)

    source_node = relationship("Node", foreign_keys=[source_id],
                               back_populates="edges_from")
    target_node = relationship("Node", foreign_keys=[target_id],
                               back_populates="edges_to")

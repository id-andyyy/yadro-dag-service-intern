from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing_extensions import Annotated

from app.db.base import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(unique=True)
    graph_id: Mapped[int] = mapped_column(ForeignKey("graphs.id", ondelete="CASCADE"))

    edges_from: Mapped[list["Edge"]] = relationship(
        back_populates="source_node",
        cascade="all, delete-orphan",
        foreign_keys="Edge.source_id",
    )
    edges_to: Mapped[list["Edge"]] = relationship(
        back_populates="target_node",
        cascade="all, delete-orphan",
        foreign_keys="Edge.target_id",
    )
    graph: Mapped["Graph"] = relationship(
        back_populates="nodes",
    )


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[intpk]
    graph_id: Mapped[int] = mapped_column(ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)

    source_node: Mapped["Node"] = relationship(
        back_populates="edges_from",
        foreign_keys=[source_id],
    )
    target_node: Mapped["Node"] = relationship(
        back_populates="edges_to",
        foreign_keys=[target_id],
    )
    graph: Mapped["Graph"] = relationship(
        back_populates="edges",
    )

    @property
    def source(self) -> str:
        return self.source_node.name

    @property
    def target(self) -> str:
        return self.target_node.name


class Graph(Base):
    __tablename__ = "graphs"

    id: Mapped[intpk]

    nodes: Mapped[list["Node"]] = relationship(
        back_populates="graph",
        cascade="all, delete-orphan",
    )
    edges: Mapped[list["Edge"]] = relationship(
        back_populates="graph",
        cascade="all, delete-orphan",
    )

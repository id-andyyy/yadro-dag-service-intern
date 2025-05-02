from sqlalchemy import Column, Integer
from app.db.base import Base


class Graph(Base):
    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True)

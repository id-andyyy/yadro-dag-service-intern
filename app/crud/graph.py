from app.models.graph import Graph, Node, Edge
from sqlalchemy.orm import Session


def crud_create_graph(db: Session, names: list[str], edges: list[tuple[str, str]]) -> Graph:
    graph = Graph()
    db.add(graph)
    db.flush()

    nodes = [Node(name=name, graph_id=graph.id) for name in names]
    db.add_all(nodes)
    db.flush()

    edges_objs = [
        Edge(
            graph_id=graph.id,
            source_id=next(n.id for n in nodes if n.name == source),
            target_id=next(n.id for n in nodes if n.name == target),
        )
        for source, target in edges
    ]
    db.add_all(edges_objs)

    db.commit()
    db.refresh(graph)
    return graph


def get_graph_by_id(db: Session, graph_id: int):
    graph = db.query(Graph).filter(Graph.id == graph_id).first()
    return graph

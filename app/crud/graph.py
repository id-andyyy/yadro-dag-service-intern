from app.models.graph import Graph, Node, Edge
from sqlalchemy.orm import Session


class NotFoundError(Exception):
    pass


def db_create_graph(db: Session, names: list[str], edges: list[tuple[str, str]]) -> Graph:
    graph = Graph()
    db.add(graph)
    db.flush()
    graph_id = graph.id

    nodes = [Node(name=name, graph_id=graph_id) for name in names]
    db.bulk_save_objects(nodes)
    db.flush()

    rows = (
        db.query(Node.id, Node.name)
          .filter(Node.graph_id == graph_id)
          .all()
    )
    name_to_id = {name: _id for _id, name in rows}

    edge_objs = [
        Edge(
            graph_id=graph_id,
            source_id=name_to_id[source],
            target_id=name_to_id[target],
        )
        for source, target in edges
    ]
    db.bulk_save_objects(edge_objs)

    db.commit()

    return graph


def db_get_graph_by_id(db: Session, graph_id: int):
    graph = db.query(Graph).filter(Graph.id == graph_id).first()
    if graph is None:
        raise NotFoundError("Graph not found")
    return graph

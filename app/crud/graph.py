from app.models.graph import Graph, Node, Edge
from sqlalchemy.orm import Session


class NotFoundError(Exception):
    pass


def db_create_graph(db: Session, names: list[str], edges: list[tuple[str, str]]) -> Graph:
    graph: Graph = Graph()
    db.add(graph)
    db.flush()
    graph_id: int = graph.id

    nodes: list[Node] = [Node(name=name, graph_id=graph_id) for name in names]
    db.bulk_save_objects(nodes)
    db.flush()

    rows = (
        db.query(Node.id, Node.name)
        .filter(Node.graph_id == graph_id)
        .all()
    )
    name_to_id: dict[str, int] = {name: _id for _id, name in rows}

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


def db_get_graph_by_id(db: Session, graph_id: int) -> Graph:
    graph: Graph | None = db.query(Graph).filter(Graph.id == graph_id).first()
    if graph is None:
        raise NotFoundError("Graph not found")
    return graph


def db_delete_node(db: Session, graph_id: int, node_name: str) -> None:
    graph: Graph = db_get_graph_by_id(db, graph_id)

    node: Node | None = db.query(Node).filter(
        Node.graph_id == graph_id,
        Node.name == node_name
    ).first()
    if node is None:
        raise NotFoundError("Node not found")

    db.delete(node)
    db.commit()

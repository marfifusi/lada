from rdflib import Graph
from rdflib.term import Node


# Verifica assignee: se c'è, la party della request deve essere lui o stare nella sua collection. Non ancora implementato.
def matches(policy: Graph, permission: Node, request: Graph) -> bool:
    raise NotImplementedError("Assignee check is not implemented yet")

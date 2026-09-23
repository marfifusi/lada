from rdflib import Graph
from rdflib.term import Node


# Verifica le refinement di azione, target e assignee della Permission sulla request. Non ancora implementato.
def satisfied(policy: Graph, permission: Node, request: Graph) -> bool:
    raise NotImplementedError("Refinement check is not implemented yet")

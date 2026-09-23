from rdflib import Graph
from rdflib.term import Node


# Verifica se il target della request è quello della Permission o è nella sua collection. Non ancora implementato.
def matches(policy: Graph, permission: Node, request: Graph) -> bool:
    raise NotImplementedError("Target check is not implemented yet")

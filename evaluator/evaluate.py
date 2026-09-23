from rdflib import Graph
from rdflib.term import Node

from evaluator.vocab import namespaces


# Apre un file JSON-LD e lo carica come grafo RDF
def open_rdflib(file: str) -> Graph:
    graph = Graph()
    graph.parse(file, format="json-ld")
    # Associa i prefissi noti per stampare URI in forma compatta
    for prefix, ns in namespaces.items():
        graph.bind(prefix, ns)
    return graph


# Apre un file JSON-LD e stampa le triple del grafo RDF
def print_rdflib(file: str) -> None:
    graph = open_rdflib(file)
    nm = graph.namespace_manager
    print(f"Opened {file}: {len(graph)} triples")
    # n3(nm) rende soggetto, predicato e oggetto con i prefissi
    for s, p, o in graph:
        print(f"  {s.n3(nm)} {p.n3(nm)} {o.n3(nm)}")


# Permitted se la Permission è active e coincidono classe, target, assignee e refinement.
# Il controllo completo non è ancora implementato.
def is_permitted(policy: Graph, permission: Node, request: Graph) -> bool:
    raise NotImplementedError("Permission evaluation is not implemented yet")

from rdflib import Graph
from rdflib.term import Node

from evaluator import n3_engine
from evaluator.vocab import namespaces

# Regole N3 che traducono i requestParameter in lada:requestAssertion.
REQUEST_MAP = "policies/samples/maps/ev_requests_map.n3"


# Apre un file JSON-LD e lo carica come grafo RDF
def open_rdflib(file: str) -> Graph:
    graph = Graph()
    graph.parse(file, format="json-ld")
    # Associa i prefissi noti per stampare URI in forma compatta
    for prefix, ns in namespaces.items():
        graph.bind(prefix, ns)
    return graph


# Apre una EvaluationRequest JSON-LD e vi applica le regole di ev_requests_map.n3.
def open_evaluation_request(file: str) -> Graph:
    graph = open_rdflib(file)
    n3_engine.apply(graph, REQUEST_MAP)
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

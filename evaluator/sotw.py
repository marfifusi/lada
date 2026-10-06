# Carica lo State of the World e vi applica le regole N3.
# Il grafo resta in questo modulo: la valutazione lo legge da qui
# e non lo riceve come parametro.

from rdflib import Graph

from evaluator import n3_engine
from evaluator import ontology_cache
from evaluator.vocab import namespaces

# Regole N3 che traducono il contesto dello SOTW in lada:SotwAction.
SOTW_MAP = "policies/samples/maps/sotw_map.n3"

# Sorgente SOTW corrente (path del file JSON-LD) e grafo usato solo qui.
_source_path: str | None = None
_graph: Graph | None = None


# Imposta il file JSON-LD dello SOTW e vi applica le regole di sotw_map.n3.
def set_source(path: str | None) -> None:
    global _source_path, _graph
    _source_path = path
    _graph = None
    if path is not None:
        _graph = _load_graph(path)
        n3_engine.apply(_graph, SOTW_MAP)


# Grafo SOTW già caricato, oppure None se non c'è una sorgente.
def graph() -> Graph | None:
    return _graph


# Carica il file SOTW come grafo RDF, senza esporlo alle funzioni di valutazione.
def _load_graph(path: str) -> Graph:
    ontology_cache.install()
    graph = Graph()
    graph.parse(path, format="json-ld")
    for prefix, ns in namespaces.items():
        graph.bind(prefix, ns)
    return graph

# Interfaccia verso lo State of the World (SOTW).
# Lo SOTW può essere molto grande: non si passa come Graph RDF alle funzioni
# di valutazione. Questa interfaccia interroga in SPARQL un file o una
# base di dati per ottenere solo le informazioni necessarie a valutare
# una EvaluationRequest. Il grafo RDF resta privato al modulo.

from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import Node

from evaluator.vocab import namespaces

# Sorgente SOTW corrente (path del file JSON-LD) e grafo usato solo qui.
_source_path: str | None = None
_graph: Graph | None = None

# Pagamenti collegati a una duty: importo, valuta e beneficiario.
_PAYMENTS_FOR_CONDITION = prepareQuery(
    """
    SELECT ?amount ?currency ?payee
    WHERE {
      ?payment a pay:Payment .
      ?payment sotw:conditionId ?duty .
      OPTIONAL { ?payment pay:netAmount ?amount }
      OPTIONAL { ?payment pay:currency ?currency }
      OPTIONAL { ?payment pay:payee ?payee }
    }
    """,
    initNs={
        "pay": namespaces["pay"],
        "sotw": namespaces["sotw"],
    },
)


# Imposta il file JSON-LD dello SOTW da interrogare (None = nessuno).
def set_source(path: str | None) -> None:
    global _source_path, _graph
    _source_path = path
    _graph = None
    if path is not None:
        _graph = _load_graph(path)


# Carica il file SOTW come grafo RDF privato, senza esporlo all'esterno.
def _load_graph(path: str) -> Graph:
    graph = Graph()
    graph.parse(path, format="json-ld")
    for prefix, ns in namespaces.items():
        graph.bind(prefix, ns)
    return graph


# Restituisce i pagamenti SOTW collegati alla duty (conditionId), via SPARQL.
def payments_for_condition(duty: Node) -> list[dict[str, Node | None]]:
    if _graph is None:
        return []
    rows = _graph.query(_PAYMENTS_FOR_CONDITION, initBindings={"duty": duty})
    return [
        {
            "amount": row.amount,
            "currency": row.currency,
            "payee": row.payee,
        }
        for row in rows
    ]

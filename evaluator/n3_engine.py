from pathlib import Path

from rdflib import Graph

import pyling

# Applica al grafo le regole N3 con il reasoner pyling.
# I fatti di partenza restano; si aggiungono solo le triple inferite.
def apply(graph: Graph, rules_path: str) -> None:
    facts = graph.serialize(format="turtle")
    rules = Path(rules_path).read_text(encoding="utf-8")
    derived = pyling.reason_graph(
        {"sources": [facts, rules]},
        include_input_facts_in_closure=False,
    )
    for triple in derived:
        graph.add(triple)

from rdflib import Graph, Namespace

from evaluator.prefixes import prefixes


# Apre un file JSON-LD e lo carica come grafo RDF
def open_rdflib(file: str):
    graph = Graph()
    graph.parse(file, format="json-ld")
    # Associa i prefissi noti per stampare URI in forma compatta
    for prefix, uri in prefixes.items():
        graph.bind(prefix, Namespace(uri))

    nm = graph.namespace_manager
    print(f"Opened {file}: {len(graph)} triples")
    # n3(nm) rende soggetto, predicato e oggetto con i prefissi
    for s, p, o in graph:
        print(f"  {s.n3(nm)} {p.n3(nm)} {o.n3(nm)}")

    return graph


if __name__ == "__main__":
    # Esempio: carica la policy di esempio A1 (path relativo alla root del progetto)
    open_rdflib("policies/sample/a1_policy.json")

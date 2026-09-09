from rdflib import Graph, Namespace
from prefixes import prefixes

# Apro un file Json+ld con la libreria RDFLib
def open_rdflib(file: str):
    graph = Graph()
    graph.parse(file, format="json-ld")
    for prefix, uri in prefixes.items():
        graph.bind(prefix, Namespace(uri))

    nm = graph.namespace_manager
    print(f"Opened {file}: {len(graph)} triples")
    for s, p, o in graph:
        print(f"  {s.n3(nm)} {p.n3(nm)} {o.n3(nm)}")

    return graph


if __name__ == "__main__":
    open_rdflib("../policies/cc-by4.0.json")

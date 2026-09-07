from pathlib import Path
from rdflib import Graph

# Apro un file Json+ld con la libreria RDFLib
def open_rdflib(file: str):
    project_root = Path(__file__).resolve().parent
    path = project_root / file

    graph = Graph()
    graph.parse(path, format="json-ld")

    print(f"Opened {path.name}: {len(graph)} triples")
    for s, p, o in graph:
        print(f"  {s} {p} {o}")

    return graph


if __name__ == "__main__":
    open_rdflib("policies/cc-by4.0.json")

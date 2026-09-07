from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS


CC = Namespace("http://creativecommons.org/ns#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
SPDX = Namespace("http://spdx.org/rdf/terms#")


# Questa funzione dovrebbe aprire un file json+ld (comincia con cc-by4.0)
# nella cartella policies utilizzando la libreria rdflib e stampare qualcosa
# per verificare che il file è stato aperto correttamente
def open_rdflib(file: str):
    project_root = Path(__file__).resolve().parent
    path = project_root / file

    graph = Graph()
    graph.bind("cc", CC)
    graph.bind("dct", DCTERMS)
    graph.bind("foaf", FOAF)
    graph.bind("odrl", ODRL)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("spdx", SPDX)
    graph.parse(path, format="json-ld")

    ns = graph.namespace_manager
    print(f"Opened {path.name}: {len(graph)} triples")
    for s, p, o in graph:
        print(f"  {s.n3(ns)} {p.n3(ns)} {o.n3(ns)}")

    return graph


if __name__ == "__main__":
    open_rdflib("policies/cc-by4.0.json")

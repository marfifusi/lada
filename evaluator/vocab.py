from rdflib import Namespace
from rdflib.term import Node

# Prefissi → URI in forma di stringa.
prefixes = {
    "cc": "http://creativecommons.org/ns#",
    "dct": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "spdx": "http://spdx.org/rdf/terms#",
    "purl": "http://purl.org/NET/rdflicense/",
    "sotw": "https://w3id.org/force/sotw#",
    "ex_policy": "http://example.com/policy/",
    "ex_rule": "http://example.com/rule/",
    "ex_document": "http://example.com/document/",
    "ex_party": "http://example.com/party/",
    "ex_constraint": "http://example.com/constraint/",
}

# Prefissi → Namespace rdflib, derivati dagli URI in prefixes.
namespaces = {prefix: Namespace(uri) for prefix, uri in prefixes.items()}

# Per ogni leftOperand di un constraint, elenca i describesFeature da
# cercare nei requestParameter (in ordine di priorità: il primo disponibile vince).
LEFT_OPERAND_TO_FEATURE: dict[Node, list[Node]] = {
    namespaces["odrl"].dateTime: [
        namespaces["sotw"].TemporalData,
        namespaces["sotw"].CurrentXSDDateTime,
        namespaces["sotw"].CurrentXSDDate,
    ],
    namespaces["odrl"].resolution: [
        namespaces["sotw"].Resolution,
    ],
}

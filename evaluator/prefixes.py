from rdflib import Namespace

# Prefissi → URI, usati per bind sui grafi e per costruire i Namespace.
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

ODRL = Namespace(prefixes["odrl"])
SOTW = Namespace(prefixes["sotw"])

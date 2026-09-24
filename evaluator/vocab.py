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
    "pay": "https://www.epimorphics.com/guide-to-the-payments-ontology/",
    "ex": "http://example.com/ns#",
    "ex_policy": "http://example.com/policy/",
    "ex_rule": "http://example.com/rule/",
    "ex_document": "http://example.com/document/",
    "ex_party": "http://example.com/party/",
    "ex_constraint": "http://example.com/constraint/",
}

# Prefissi → Namespace rdflib, derivati dagli URI in prefixes.
namespaces = {prefix: Namespace(uri) for prefix, uri in prefixes.items()}

# Feature temporali ammesse in una EvaluationRequest: solo data e dateTime.
# dayOfWeek non è un parametro della request: si ricava da questi valori.
REQUEST_TEMPORAL_FEATURES: list[Node] = [
    namespaces["sotw"].TemporalData,
    namespaces["sotw"].CurrentXSDDateTime,
    namespaces["sotw"].CurrentXSDDate,
]

# Per ogni leftOperand di un constraint, elenca i describesFeature da
# cercare nei requestParameter (in ordine di priorità: il primo disponibile vince).
# I leftOperand dayOfWeek non stanno qui: usano REQUEST_TEMPORAL_FEATURES.
LEFT_OPERAND_TO_FEATURE: dict[Node, list[Node]] = {
    namespaces["odrl"].dateTime: REQUEST_TEMPORAL_FEATURES,
    namespaces["odrl"].resolution: [
        namespaces["sotw"].Resolution,
    ],
}

# Per ogni leftOperand di una refinement di un duty, indica la proprietà
# dello SOTW da confrontare con il rightOperand.
LEFT_OPERAND_TO_SOTW_PROPERTY: dict[Node, Node] = {
    namespaces["odrl"].payAmount: namespaces["pay"].netAmount,
}

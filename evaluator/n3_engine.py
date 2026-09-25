from datetime import date
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import XSD

import pyling
from evaluator.vocab import namespaces

# Namespace usati per collegare l'asserzione al parametro e al suo valore.
ODRL = namespaces["odrl"]
LADA = namespaces["lada"]
SOTW = namespaces["sotw"]

# Segnaposto scritto dalla regola N3 al posto del nome del giorno.
_WEEKDAY_PLACEHOLDER = Literal("dowPlaceholder", datatype=XSD.string)

# Nomi inglesi fissi (Monday = 0 … Sunday = 6), come date.weekday().
_WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


# Applica al grafo le regole N3 con il reasoner pyling.
# I fatti di partenza restano; si aggiungono solo le triple inferite.
# Poi il segnaposto del giorno della settimana diventa il nome inglese.
def apply(graph: Graph, rules_path: str) -> None:
    facts = graph.serialize(format="turtle")
    rules = Path(rules_path).read_text(encoding="utf-8")
    derived = pyling.reason_graph(
        {"sources": [facts, rules]},
        include_input_facts_in_closure=False,
    )
    for triple in derived:
        graph.add(triple)
    _fill_weekday_placeholders(graph)


# Sostituisce dowPlaceholder con il giorno del valore del parametro collegato.
def _fill_weekday_placeholders(graph: Graph) -> None:
    assertions = list(graph.subjects(ODRL.rightOperand, _WEEKDAY_PLACEHOLDER))
    for assertion in assertions:
        param = graph.value(assertion, LADA.fromParameter)
        value = graph.value(param, SOTW.value) if param is not None else None
        name = Literal(_weekday_name(value), datatype=XSD.string)
        graph.remove((assertion, ODRL.rightOperand, _WEEKDAY_PLACEHOLDER))
        graph.add((assertion, ODRL.rightOperand, name))


# Nome inglese del giorno da un xsd:date o xsd:dateTime.
def _weekday_name(value: object) -> str:
    if not isinstance(value, Literal):
        raise NotImplementedError(
            "Weekday placeholder: the request parameter value is not an xsd:date or xsd:dateTime."
        )
    py = value.toPython()
    # datetime è una sottoclasse di date: valgono sia xsd:date sia xsd:dateTime.
    if not isinstance(py, date):
        raise NotImplementedError(
            "Weekday placeholder: the request parameter value is not an xsd:date or xsd:dateTime."
        )
    return _WEEKDAY_NAMES[py.weekday()]

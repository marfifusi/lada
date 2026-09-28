# Copia di rollback dell'engine N3 scritto a mano, prima del passaggio a pyling.
# L'evaluator non la usa: il reasoning sta in n3_engine.py.

from datetime import date

from rdflib import BNode, Dataset, Graph, Literal, Namespace, Variable
from rdflib.namespace import XSD
from rdflib.term import Node

# log:implies collega premessa e conclusione di una regola N3.
LOG = Namespace("http://www.w3.org/2000/10/swap/log#")

# time:dayOfWeek ricava da date o dateTime il nome inglese del giorno.
TIME = Namespace("http://www.w3.org/2000/10/swap/time#")

# Nomi inglesi fissi (Monday = 0 … Sunday = 6), come datetime.weekday().
_WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


# Applica al grafo regole N3 fatte di triple.
# L'unico built-in è time:dayOfWeek; le formule annidate non sono supportate.
# Le conclusioni delle regole precedenti restano visibili a quelle successive.
def apply(graph: Graph, rules_path: str) -> None:
    rules = Dataset()
    rules.parse(rules_path, format="n3")
    for antecedent, _, consequent in rules.triples((None, LOG.implies, None)):
        if not isinstance(antecedent, Graph) or not isinstance(consequent, Graph):
            raise NotImplementedError("N3 rule is not a pair of triple formulas")
        patterns = list(antecedent.triples((None, None, None)))
        _reject_nested_formulas(patterns)
        conclusions = list(consequent.triples((None, None, None)))
        _reject_nested_formulas(conclusions)
        # Si raccolgono prima le conclusioni: il match non vede triple aggiunte a metà scansione.
        inferred = [
            triple
            for bindings in _solutions(graph, patterns)
            for triple in _instantiate(conclusions, bindings)
        ]
        for triple in inferred:
            graph.add(triple)


# Rifiuta una formula che contiene un'altra formula: questo applicatore non la valuta.
def _reject_nested_formulas(triples: list[tuple[Node, Node, Node]]) -> None:
    for triple in triples:
        for term in triple:
            if isinstance(term, Graph):
                raise NotImplementedError("Nested N3 formulas are not supported yet")


# Soluzioni della premessa sul grafo: ogni variabile o blank è un posto da legare.
def _solutions(graph: Graph, patterns: list[tuple[Node, Node, Node]], bindings: dict | None = None):
    if bindings is None:
        bindings = {}
    if not patterns:
        yield dict(bindings)
        return
    subject, predicate, obj = patterns[0]
    rest = patterns[1:]
    # time:dayOfWeek non è una tripla del grafo: si calcola da date o dateTime.
    # La formula non conserva l'ordine del file: se il soggetto è libero, prima gli altri pattern.
    if predicate == TIME.dayOfWeek:
        if _query_term(subject, bindings) is None and rest:
            for bound in _solutions(graph, rest, bindings):
                yield from _solutions(graph, [(subject, predicate, obj)], bound)
            return
        for bound in _day_of_week_solutions(subject, obj, bindings):
            yield from _solutions(graph, rest, bound)
        return
    query = (
        _query_term(subject, bindings),
        _query_term(predicate, bindings),
        _query_term(obj, bindings),
    )
    for triple in graph.triples(query):
        bound = dict(bindings)
        if (
            _unify(subject, triple[0], bound)
            and _unify(predicate, triple[1], bound)
            and _unify(obj, triple[2], bound)
        ):
            yield from _solutions(graph, rest, bound)


# Soluzioni di time:dayOfWeek: da date o dateTime ricava il nome inglese, xsd:string.
def _day_of_week_solutions(subject: Node, obj: Node, bindings: dict):
    subject_value = _query_term(subject, bindings)
    if not isinstance(subject_value, Literal):
        return

    value = subject_value.toPython()
    # xsd:date diventa date; xsd:dateTime diventa datetime, che è una date.
    if not isinstance(value, date):
        return

    day_name = Literal(_WEEKDAY_NAMES[value.weekday()], datatype=XSD.string)
    bound = dict(bindings)
    if _unify(obj, day_name, bound):
        yield bound


# Termine già noto per la ricerca; una variabile libera diventa jolly.
def _query_term(term: Node, bindings: dict) -> Node | None:
    if isinstance(term, (Variable, BNode)):
        return bindings.get(term)
    return term


# Lega una variabile o un blank al nodo, oppure verifica che un termine fisso coincida.
def _unify(term: Node, node: Node, bindings: dict) -> bool:
    if isinstance(term, (Variable, BNode)):
        existing = bindings.get(term)
        if existing is None:
            bindings[term] = node
            return True
        return existing == node
    return term == node


# Istanzia la conclusione: le variabili prendono il binding, i blank nuovi restano nuovi.
def _instantiate(conclusions: list[tuple[Node, Node, Node]], bindings: dict):
    fresh: dict[BNode, BNode] = {}
    for subject, predicate, obj in conclusions:
        yield (
            _head_term(subject, bindings, fresh),
            _head_term(predicate, bindings, fresh),
            _head_term(obj, bindings, fresh),
        )


# Termine della conclusione sotto una soluzione della premessa.
def _head_term(term: Node, bindings: dict, fresh: dict[BNode, BNode]) -> Node:
    if isinstance(term, Variable):
        if term not in bindings:
            raise NotImplementedError(f"Unbound variable in N3 rule head: {term}")
        return bindings[term]
    if isinstance(term, BNode):
        if term in bindings:
            return bindings[term]
        if term not in fresh:
            fresh[term] = BNode()
        return fresh[term]
    return term

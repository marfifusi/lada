from datetime import date, datetime

from rdflib import Graph, Namespace
from rdflib.term import Node

from evaluator.prefixes import ODRL, SOTW, prefixes


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


# Valuta se un Permission è active sull'azione della request nello State of the World:
# tutti i Constraint sono satisfied e tutti i Duty sono fulfilled oppure inactive.
def is_permission_active(
    policy: Graph,
    permission: Node,
    request: Graph,
    sotw: Graph | None = None,
) -> bool:
    """Un Permission è active su a in S sse:
    1. tutti i suoi Constraint sono satisfied da a
    2. tutti i suoi Duty sono fulfilled oppure inactive in S rispetto ad a
    """
    sotw = sotw or Graph()

    constraints = list(policy.objects(permission, ODRL.constraint))
    if not all(
        is_constraint_satisfied(policy, constraint, request, sotw)
        for constraint in constraints
    ):
        return False

    duties = list(policy.objects(permission, ODRL.duty))
    if not all(
        is_duty_fulfilled_or_inactive(policy, duty, request, sotw)
        for duty in duties
    ):
        return False

    return True


# Verifica se un Constraint del Permission è satisfied rispetto alla request (A1-1: dateTime).
def is_constraint_satisfied(
    policy: Graph,
    constraint: Node,
    request: Graph,
    sotw: Graph,
) -> bool:
    """Per A1-1: dateTime della request < 2018-01-01."""
    left = policy.value(constraint, ODRL.leftOperand)
    operator = policy.value(constraint, ODRL.operator)
    right = policy.value(constraint, ODRL.rightOperand)

    if left == ODRL.dateTime:
        actual = _current_datetime(request, sotw)
        if actual is None or operator is None or right is None:
            return False
        return _compare_datetimes(actual, operator, right)

    raise NotImplementedError(f"Constraint leftOperand not supported yet: {left}")


# Verifica se un Duty è fulfilled oppure inactive; A1 non ha duty, quindi non è ancora implementato.
def is_duty_fulfilled_or_inactive(
    policy: Graph,
    duty: Node,
    request: Graph,
    sotw: Graph,
) -> bool:
    # A1 non ha duty; da implementare da C1 in poi
    raise NotImplementedError("Duty evaluation is not implemented yet")


# Legge la data/ora corrente (sotw:CurrentXSDDateTime) dalla request o dallo State of the World.
def _current_datetime(request: Graph, sotw: Graph) -> Node | None:
    for graph in (request, sotw):
        for param in graph.subjects(SOTW.describesFeature, SOTW.CurrentXSDDateTime):
            value = graph.value(param, SOTW.value)
            if value is not None:
                return value
    return None


# Confronta due date/ora con l'operatore ODRL (lt, lteq, gt, gteq, eq, neq).
def _compare_datetimes(left: Node, operator: Node, right: Node) -> bool:
    left_dt = _to_datetime(left)
    right_dt = _to_datetime(right)
    if operator == ODRL.lt:
        return left_dt < right_dt
    if operator == ODRL.lteq:
        return left_dt <= right_dt
    if operator == ODRL.gt:
        return left_dt > right_dt
    if operator == ODRL.gteq:
        return left_dt >= right_dt
    if operator == ODRL.eq:
        return left_dt == right_dt
    if operator == ODRL.neq:
        return left_dt != right_dt
    raise NotImplementedError(f"Constraint operator not supported yet: {operator}")


# Converte un valore RDF (xsd:date o xsd:dateTime) in un datetime Python.
def _to_datetime(value: Node) -> datetime:
    py = value.toPython() if hasattr(value, "toPython") else value
    if isinstance(py, datetime):
        return py
    if isinstance(py, date):
        return datetime.combine(py, datetime.min.time())
    return datetime.fromisoformat(str(py))


if __name__ == "__main__":
    # Caso A1-1: policy A1 + request del 2017-12-19 → permesso active
    policy = open_rdflib("policies/sample/a1_policy.json")
    request = open_rdflib("ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")

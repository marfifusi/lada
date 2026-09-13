from datetime import date, datetime

from rdflib import Graph
from rdflib.term import Node

from evaluator.vocab import LEFT_OPERAND_TO_FEATURE, namespaces

# Namespace ODRL e SOTW usati nella valutazione delle policy.
ODRL = namespaces["odrl"]
SOTW = namespaces["sotw"]


# Apre un file JSON-LD e lo carica come grafo RDF
def open_rdflib(file: str) -> Graph:
    graph = Graph()
    graph.parse(file, format="json-ld")
    # Associa i prefissi noti per stampare URI in forma compatta
    for prefix, ns in namespaces.items():
        graph.bind(prefix, ns)
    return graph


# Apre un file JSON-LD e stampa le triple del grafo RDF
def print_rdflib(file: str) -> None:
    graph = open_rdflib(file)
    nm = graph.namespace_manager
    print(f"Opened {file}: {len(graph)} triples")
    # n3(nm) rende soggetto, predicato e oggetto con i prefissi
    for s, p, o in graph:
        print(f"  {s.n3(nm)} {p.n3(nm)} {o.n3(nm)}")


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


# Verifica se un Constraint è satisfied: il RequestParameter la cui feature
# è mappata al leftOperand deve soddisfare operator/rightOperand; se manca, False.
def is_constraint_satisfied(
    policy: Graph,
    constraint: Node,
    request: Graph,
    sotw: Graph,
) -> bool:
    """Il constraint è satisfied sse LEFT_OPERAND_TO_FEATURE collega il
    leftOperand a un describesFeature presente nella request e il confronto vale.
    Senza mapping o senza parametro il constraint non è verificabile → False.
    """
    left = policy.value(constraint, ODRL.leftOperand)
    operator = policy.value(constraint, ODRL.operator)
    right = policy.value(constraint, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False

    actual = _request_parameter_value(request, left)
    if actual is None:
        return False

    if left == ODRL.dateTime:
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


# Cerca il RequestParameter la cui feature è quella mappata al leftOperand.
def _request_parameter_value(request: Graph, left_operand: Node) -> Node | None:
    feature = LEFT_OPERAND_TO_FEATURE.get(left_operand)
    if feature is None:
        return None
    for param in request.subjects(SOTW.describesFeature, feature):
        value = request.value(param, SOTW.value)
        if value is not None:
            return value
    return None


# Confronta data/ora nella request (left) e nella policy (right) con gli operatori ODRL
# lt, lteq, gt, gteq, eq, neq. I quattro casi:
# 1. entrambi datetime → confronto sull'ora esatta
# 2. entrambi date → confronto sul giorno giorno
# 3. request datetime e policy date → si tronca l'ora della policy e si confronta per giorno
# 4. request date e policy datetime → False: senza l'ora dell'azione
#    non siamo sicuri che il vincolo valga, nel dubbio valutiamo la policy non attiva
def _compare_datetimes(left: Node, operator: Node, right: Node) -> bool:
    left_val = _to_date_or_datetime(left)
    right_val = _to_date_or_datetime(right)
    # Request solo date e policy datetime: senza l'ora dell'azione non siamo
    # sicuri che il vincolo valga, nel dubbio valutiamo la policy non attiva
    if not isinstance(left_val, datetime) and isinstance(right_val, datetime):
        return False
    # In tutti gli altri casi, procedo con il confronto tra date o datetime
    left_cmp, right_cmp = _align_temporal_granularity(left_val, right_val)
    if operator == ODRL.lt:
        return left_cmp < right_cmp
    if operator == ODRL.lteq:
        return left_cmp <= right_cmp
    if operator == ODRL.gt:
        return left_cmp > right_cmp
    if operator == ODRL.gteq:
        return left_cmp >= right_cmp
    if operator == ODRL.eq:
        return left_cmp == right_cmp
    if operator == ODRL.neq:
        return left_cmp != right_cmp
    raise NotImplementedError(f"Constraint operator not supported yet: {operator}")


# Interpreta un valore RDF (xsd:date o xsd:dateTime) senza inventare l'ora.
def _to_date_or_datetime(value: Node) -> date | datetime:
    py = value.toPython() if hasattr(value, "toPython") else value
    if isinstance(py, datetime):
        return py
    if isinstance(py, date):
        return py
    text = str(py)
    try:
        return date.fromisoformat(text)
    except ValueError:
        return datetime.fromisoformat(text)


# Allinea la granularità: se la policy è solo date, tronca l'ora della request.
def _align_temporal_granularity(
    left: date | datetime, right: date | datetime
) -> tuple[date, date] | tuple[datetime, datetime]:
    if isinstance(left, datetime) and isinstance(right, datetime):
        return left, right
    left_date = left.date() if isinstance(left, datetime) else left
    right_date = right.date() if isinstance(right, datetime) else right
    return left_date, right_date

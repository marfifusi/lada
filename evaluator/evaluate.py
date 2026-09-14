from rdflib import Graph
from rdflib.term import Node

from evaluator import time_compare as tc
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


# Verifica se un Constraint è satisfied: il RequestParameter della prima
# feature mappata al leftOperand deve soddisfare operator/rightOperand; se manca, False.
def is_constraint_satisfied(
    policy: Graph,
    constraint: Node,
    request: Graph,
    sotw: Graph,
) -> bool:
    """Il constraint è satisfied se LEFT_OPERAND_TO_FEATURE collega il
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
        return tc.compare_datetimes(actual, operator, right)

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


# Cerca il RequestParameter provando i describesFeature mappati al leftOperand,
# in ordine di priorità; restituisce il primo valore trovato.
def _request_parameter_value(request: Graph, left_operand: Node) -> Node | None:
    features = LEFT_OPERAND_TO_FEATURE.get(left_operand)
    if not features:
        return None
    for feature in features:
        for param in request.subjects(SOTW.describesFeature, feature):
            value = request.value(param, SOTW.value)
            if value is not None:
                return value
    return None

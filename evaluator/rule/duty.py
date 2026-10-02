from rdflib import Graph
from rdflib.term import Node

from evaluator import sotw
from evaluator.rule import compare as cmp
from evaluator.rule import permission_active as active
from evaluator.vocab import namespaces

# Namespace ODRL, RDF e LADA per duty, refinement e azioni dello SOTW.
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
LADA = namespaces["lada"]

# Tripla leftOperand / operator / rightOperand, confrontata a parte.
_OPERANDS = frozenset({ODRL.leftOperand, ODRL.operator, ODRL.rightOperand})


# True se la duty non ha constraint, o se sono tutti satisfied sulla request.
# Stesso confronto dei constraint di una Permission: is_constraint_satisfied.
def is_active(policy: Graph, duty: Node, request: Graph) -> bool:
    constraints = list(policy.objects(duty, ODRL.constraint))
    if not constraints:
        return True
    return all(
        active.is_constraint_satisfied(policy, constraint, request)
        for constraint in constraints
    )


# True se la duty è fulfilled: active, una SotwAction con lo stesso id,
# data dell'azione antecedente al dateTime della request, e ogni refinement
# soddisfatta da un ConstraintSatisfier di quell'azione.
# Target e assignee della duty non entrano in questo controllo.
def is_fulfilled(policy: Graph, duty: Node, request: Graph) -> bool:
    if not is_active(policy, duty, request):
        return False
    action = policy.value(duty, ODRL.action)
    if action is None:
        return False
    request_time = active.request_datetime(request)
    if request_time is None:
        return False
    refinements = list(policy.objects(action, ODRL.refinement))
    for sotw_action in actions_for_duty(duty):
        action_time = sotw_action["action_datetime"]
        if action_time is None:
            continue
        if not cmp.compare_datetimes(action_time, ODRL.lt, request_time):
            continue
        if all(
            _refinement_satisfied(policy, refinement, request, sotw_action)
            for refinement in refinements
        ):
            return True
    return False


# True se un ConstraintSatisfier di questa SotwAction soddisfa la refinement.
def _refinement_satisfied(
    policy: Graph,
    refinement: Node,
    request: Graph,
    sotw_action: dict,
) -> bool:
    return any(
        _satisfier_matches(policy, refinement, request, satisfier)
        for satisfier in sotw_action["satisfiers"]
    )


# Operandi confrontati come un constraint, e parametri extra uguali sul satisfier.
def _satisfier_matches(
    policy: Graph,
    refinement: Node,
    request: Graph,
    satisfier: dict,
) -> bool:
    if not _operands_match(policy, refinement, request, satisfier):
        return False
    return _extra_triples_match(policy, refinement, satisfier)


# Se la refinement ha la tripla leftOperand-operator-rightOperand, il satisfier
# ha lo stesso leftOperand, operator eq, e il rightOperand passa is_constraint_satisfied.
def _operands_match(
    policy: Graph,
    refinement: Node,
    request: Graph,
    satisfier: dict,
) -> bool:
    if not _has_operand(policy, refinement):
        return True
    if policy.value(refinement, ODRL.leftOperand) != satisfier["left"]:
        return False
    if satisfier["operator"] != ODRL.eq:
        return False
    return active.is_constraint_satisfied(
        policy, refinement, request, satisfier["right"], use_request=False
    )


# True se sulla refinement c'è almeno un elemento della tripla degli operandi.
def _has_operand(policy: Graph, refinement: Node) -> bool:
    return any(policy.value(refinement, predicate) is not None for predicate in _OPERANDS)


# Ogni predicato extra della refinement, con lo stesso valore, sta sul ConstraintSatisfier.
def _extra_triples_match(policy: Graph, refinement: Node, satisfier: dict) -> bool:
    for predicate, obj in policy.predicate_objects(refinement):
        if predicate in _OPERANDS or predicate == RDF.type:
            continue
        if (predicate, obj) not in satisfier["triples"]:
            return False
    return True


# Azioni SOTW (lada:SotwAction) il cui lada:dutyReference è la duty.
# Ogni azione porta la data dell'azione e i ConstraintSatisfier.
def actions_for_duty(duty: Node) -> list[dict]:
    graph = sotw.graph()
    if graph is None:
        return []
    return [
        _action_record(action)
        for action in graph.subjects(RDF.type, LADA.SotwAction)
        if graph.value(action, LADA.dutyReference) == duty
    ]


# Data dell'azione e satisfier di una SotwAction.
def _action_record(action: Node) -> dict:
    return {
        "action_datetime": _action_datetime(action),
        "satisfiers": _satisfiers(action),
    }


# ConstraintSatisfier collegati all'azione.
def _satisfiers(action: Node) -> list[dict]:
    graph = sotw.graph()
    if graph is None:
        return []
    return [
        _satisfier_record(satisfier)
        for satisfier in graph.objects(action, LADA.hasConstraintSatisfier)
        if (satisfier, RDF.type, LADA.ConstraintSatisfier) in graph
    ]


# Letterale lada:actionDateTime dell'azione.
def _action_datetime(action: Node) -> Node | None:
    graph = sotw.graph()
    if graph is None:
        return None
    return graph.value(action, LADA.actionDateTime)


# Operandi del ConstraintSatisfier e le altre sue triple, escluso rdf:type.
def _satisfier_record(satisfier: Node) -> dict:
    graph = sotw.graph()
    if graph is None:
        return {"left": None, "operator": None, "right": None, "triples": []}
    return {
        "left": graph.value(satisfier, ODRL.leftOperand),
        "operator": graph.value(satisfier, ODRL.operator),
        "right": graph.value(satisfier, ODRL.rightOperand),
        "triples": [
            (predicate, obj)
            for predicate, obj in graph.predicate_objects(satisfier)
            if predicate != RDF.type
        ],
    }

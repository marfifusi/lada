from rdflib import Graph
from rdflib.term import Node

from evaluator import sotw
from evaluator.rule import permission_active as active
from evaluator.vocab import namespaces

# Namespace ODRL, RDF e LADA per refinement e asserzioni dello SOTW.
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
LADA = namespaces["lada"]

# Predicati della SotwAssertion che non si confrontano con la refinement.
_SKIPPED = frozenset({LADA.fromContext, RDF.type})
# Già valutati dal confronto leftOperand / operator / rightOperand.
_OPERANDS = frozenset({ODRL.leftOperand, ODRL.operator, ODRL.rightOperand})


# Verifica le refinement di azione, target e assignee della Permission sulla request.
# Stesso controllo dei constraint: is_constraint_satisfied.
def satisfied(policy: Graph, permission: Node, request: Graph) -> bool:
    for node in _refined_nodes(policy, permission):
        for refinement in policy.objects(node, ODRL.refinement):
            if not active.is_constraint_satisfied(policy, refinement, request):
                return False
    return True


# Nodi della Permission che possono portare odrl:refinement.
def _refined_nodes(policy: Graph, permission: Node):
    for predicate in (ODRL.action, ODRL.target, ODRL.assignee):
        yield from policy.objects(permission, predicate)


# True se una lada:SotwAssertion dello SOTW soddisfa la refinement della duty.
def satisfied_by_sotw(
    policy: Graph,
    refinement: Node,
    request: Graph,
    duty: Node,
    action: Node,
) -> bool:
    for triples in sotw.assertions():
        if _assertion_satisfies(policy, refinement, request, triples, duty, action):
            return True
    return False


# True se questa asserzione supera il confronto degli operandi e i predicati extra.
def _assertion_satisfies(
    policy: Graph,
    refinement: Node,
    request: Graph,
    triples: list[tuple[Node, Node]],
    duty: Node,
    action: Node,
) -> bool:
    if not _operands_satisfy(policy, refinement, request, triples):
        return False
    references = {
        LADA.dutyReference: duty,
        LADA.actionReference: action,
        LADA.refinementReference: refinement,
    }
    for predicate, obj in triples:
        if predicate in _SKIPPED or predicate in _OPERANDS:
            continue
        if predicate in references:
            if obj != references[predicate]:
                return False
            continue
        if (refinement, predicate, obj) not in policy:
            return False
    return True


# Stesso confronto dei constraint: leftOperand uguale, operatore eq sull'asserzione,
# rightOperand dell'asserzione contro operator e rightOperand della refinement.
def _operands_satisfy(
    policy: Graph,
    refinement: Node,
    request: Graph,
    triples: list[tuple[Node, Node]],
) -> bool:
    left = _single(triples, ODRL.leftOperand)
    operator = _single(triples, ODRL.operator)
    right = _single(triples, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False
    if policy.value(refinement, ODRL.leftOperand) != left:
        return False
    if operator != ODRL.eq:
        return False
    return active.is_constraint_satisfied(
        policy, refinement, request, right, use_request=False
    )


# Oggetto unico del predicato sull'asserzione; None se manca o è ripetuto.
def _single(
    triples: list[tuple[Node, Node]], predicate: Node
) -> Node | None:
    values = [obj for pred, obj in triples if pred == predicate]
    if len(values) != 1:
        return None
    return values[0]


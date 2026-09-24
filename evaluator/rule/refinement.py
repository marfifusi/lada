from rdflib import Graph
from rdflib.term import Node

from evaluator.rule import compare as cmp
from evaluator.rule import permission_active as active
from evaluator.vocab import namespaces

# Namespace ODRL per azione, target, assignee e refinement.
ODRL = namespaces["odrl"]


# Verifica le refinement di azione, target e assignee della Permission sulla request.
# I leftOperand temporali (dateTime, dayOfWeek) usano data e dateTime della request.
# Gli altri leftOperand non sono ancora implementati.
def satisfied(policy: Graph, permission: Node, request: Graph) -> bool:
    for node in _refined_nodes(policy, permission):
        for refinement in policy.objects(node, ODRL.refinement):
            if not _holds(policy, refinement, request):
                return False
    return True


# Nodi della Permission che possono portare odrl:refinement.
def _refined_nodes(policy: Graph, permission: Node):
    for predicate in (ODRL.action, ODRL.target, ODRL.assignee):
        yield from policy.objects(permission, predicate)


# True se la refinement è soddisfatta. I leftOperand temporali passano dal confronto comune.
def _holds(policy: Graph, refinement: Node, request: Graph) -> bool:
    left = policy.value(refinement, ODRL.leftOperand)
    operator = policy.value(refinement, ODRL.operator)
    right = policy.value(refinement, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False
    if cmp.is_temporal_left_operand(left):
        return active.temporal_holds(request, left, operator, right)
    raise NotImplementedError(f"Refinement leftOperand not supported yet: {left}")

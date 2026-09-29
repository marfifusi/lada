from rdflib import Graph
from rdflib.term import Node

from evaluator.rule import permission_active as active
from evaluator.vocab import namespaces

# Namespace ODRL per le refinement della Permission.
ODRL = namespaces["odrl"]


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


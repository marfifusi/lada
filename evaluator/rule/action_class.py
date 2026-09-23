from rdflib import Graph
from rdflib.term import Node

from evaluator.vocab import namespaces

# Namespace ODRL, RDF e SOTW (evaluatedAction sull'EvaluationRequest).
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
SOTW = namespaces["sotw"]


# True se evaluatedAction della request è una delle classi odrl:action della Permission.
def matches(policy: Graph, permission: Node, request: Graph) -> bool:
    evaluated = _evaluated_action(request)
    if evaluated is None:
        return False
    return any(
        action_type(policy, action) == evaluated
        for action in policy.objects(permission, ODRL.action)
    )


# Classe ODRL dell'azione: rdf:value se il nodo la dichiara, altrimenti il nodo stesso.
def action_type(graph: Graph, action: Node) -> Node:
    value = graph.value(action, RDF.value)
    return value if value is not None else action


# sotw:evaluatedAction dell'EvaluationRequest; None se manca.
def _evaluated_action(request: Graph) -> Node | None:
    for evaluation in request.subjects(RDF.type, SOTW.EvaluationRequest):
        action = request.value(evaluation, SOTW.evaluatedAction)
        if action is not None:
            return action
    return None

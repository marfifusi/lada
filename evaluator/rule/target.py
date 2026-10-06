from rdflib import Graph
from rdflib.term import Node

from evaluator import sotw
from evaluator.vocab import namespaces

# Namespace ODRL, RDF e SOTW (evaluatedTarget sull'EvaluationRequest).
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
SOTW = namespaces["sotw"]


# True se sotw:evaluatedTarget della request è uguale a odrl:target della Permission,
# oppure se nello SOTW evaluatedTarget odrl:partOf quel target.
def matches(policy: Graph, permission: Node, request: Graph) -> bool:
    evaluated = _evaluated_target(request)
    if evaluated is None:
        return False
    return any(
        target == evaluated or _part_of(evaluated, target)
        for target in policy.objects(permission, ODRL.target)
    )


# True se nello SOTW c'è la tripla member odrl:partOf collection.
def _part_of(member: Node, collection: Node) -> bool:
    graph = sotw.graph()
    if graph is None:
        return False
    return (member, ODRL.partOf, collection) in graph


# sotw:evaluatedTarget dell'EvaluationRequest; None se manca.
def _evaluated_target(request: Graph) -> Node | None:
    for evaluation in request.subjects(RDF.type, SOTW.EvaluationRequest):
        target = request.value(evaluation, SOTW.evaluatedTarget)
        if target is not None:
            return target
    return None

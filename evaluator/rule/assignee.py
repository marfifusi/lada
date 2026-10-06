from rdflib import Graph
from rdflib.term import Node

from evaluator import sotw
from evaluator.vocab import namespaces

# Namespace ODRL, RDF e SOTW (evaluatedParty sull'EvaluationRequest).
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
SOTW = namespaces["sotw"]


# True se la Permission non ha assignee, oppure se evaluatedParty è quell'assignee
# o nello SOTW evaluatedParty odrl:partOf l'assignee.
def matches(policy: Graph, permission: Node, request: Graph) -> bool:
    assignees = list(policy.objects(permission, ODRL.assignee))
    if not assignees:
        return True
    evaluated = _evaluated_party(request)
    if evaluated is None:
        return False
    return any(
        assignee == evaluated or _part_of(evaluated, assignee)
        for assignee in assignees
    )


# True se nello SOTW c'è la tripla member odrl:partOf collection.
def _part_of(member: Node, collection: Node) -> bool:
    graph = sotw.graph()
    if graph is None:
        return False
    return (member, ODRL.partOf, collection) in graph


# sotw:evaluatedParty dell'EvaluationRequest; None se manca.
def _evaluated_party(request: Graph) -> Node | None:
    for evaluation in request.subjects(RDF.type, SOTW.EvaluationRequest):
        party = request.value(evaluation, SOTW.evaluatedParty)
        if party is not None:
            return party
    return None

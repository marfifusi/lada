from rdflib import Graph, URIRef
from rdflib.term import Node

from evaluator.vocab import namespaces

# Namespace ODRL, RDF e SOTW (evaluatedAction sull'EvaluationRequest).
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
SOTW = namespaces["sotw"]


# True se evaluatedAction della request è una delle classi odrl:action della Permission.
def matches(policy: Graph, permission: Node, request: Graph) -> bool:
    evaluated = evaluated_action(request)
    # Senza evaluatedAction non c'è una classe da confrontare.
    if evaluated is None:
        return False
    return any(
        action_type(policy, action) == evaluated
        for action in policy.objects(permission, ODRL.action)
    )


# IRI citabile dell'azione. Un blank node non ne ha uno: si usa la classe ODRL.
def reference(graph: Graph, action: Node) -> str:
    if isinstance(action, URIRef):
        return str(action)
    return str(action_type(graph, action))


# Classe ODRL dell'azione: rdf:value se il nodo la dichiara, altrimenti il nodo stesso.
def action_type(graph: Graph, action: Node) -> Node:
    value = graph.value(action, RDF.value)
    return value if value is not None else action


# sotw:evaluatedAction dell'EvaluationRequest; None se manca.
def evaluated_action(request: Graph) -> Node | None:
    for evaluation in request.subjects(RDF.type, SOTW.EvaluationRequest):
        action = request.value(evaluation, SOTW.evaluatedAction)
        if action is not None:
            return action
    return None

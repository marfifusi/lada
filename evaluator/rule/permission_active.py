from rdflib import Graph
from rdflib.term import Node

from evaluator.rule import compare as cmp
from evaluator.rule import duty as duty_rule
from evaluator.vocab import namespaces

# Namespace ODRL, RDF e LADA.
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
LADA = namespaces["lada"]


# Valuta se un Permission è active sull'azione della request:
# tutti i Constraint sono satisfied e tutti i Duty sono fulfilled oppure inactive.
# Lo State of the World non arriva come Graph: si interroga da sotw.py.
def is_permission_active(
    policy: Graph,
    permission: Node,
    request: Graph,
) -> bool:
    """Un Permission è active su a in S sse:
    1. tutti i suoi Constraint sono satisfied da a
    2. tutti i suoi Duty sono fulfilled oppure inactive in S rispetto ad a
    """
    constraints = list(policy.objects(permission, ODRL.constraint))
    if not all(
        is_constraint_satisfied(policy, constraint, request)
        for constraint in constraints
    ):
        return False

    duties = list(policy.objects(permission, ODRL.duty))
    if not all(
        is_duty_fulfilled_or_inactive(policy, duty, request)
        for duty in duties
    ):
        return False

    return True


# Verifica se un Constraint o una Refinement è satisfied.
# Senza valore esplicito lo legge da un ConstraintSatisfier dell'action intention (stesso leftOperand).
# Con use_request=False usa actual, per esempio il rightOperand di un ConstraintSatisfier dello SOTW.
def is_constraint_satisfied(
    policy: Graph,
    constraint: Node,
    request: Graph,
    actual: Node | None = None,
    *,
    use_request: bool = True,
) -> bool:
    """Il nodo è satisfied se operator e rightOperand confrontano un valore.
    Di default il valore è il ConstraintSatisfier dell'action intention con lo stesso leftOperand.
    Con use_request=False si usa actual; se manca, False.
    Il tipo dei due valori sceglie il confronto.
    """
    left = policy.value(constraint, ODRL.leftOperand)
    operator = policy.value(constraint, ODRL.operator)
    right = policy.value(constraint, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False
    if use_request:
        actual = _constraint_satisfier_value(request, left)
    if actual is None:
        return False
    return cmp.compare_by_types(actual, operator, right)


# Verifica se un Duty è fulfilled nello SOTW, oppure inactive perché
# almeno un suo constraint non è satisfied rispetto alla request.
def is_duty_fulfilled_or_inactive(
    policy: Graph,
    duty: Node,
    request: Graph,
) -> bool:
    """Un Duty è inactive se ha constraint non satisfied; altrimenti
    deve essere fulfilled da un'azione compiuta nello SOTW.
    """
    # Duty inactive (constraint non satisfied) ⇒ la permission può restare active
    if not duty_rule.is_active(policy, duty, request):
        return True
    return duty_rule.is_fulfilled(policy, duty, request)


# rightOperand del ConstraintSatisfier con leftOperand odrl:dateTime. None se manca.
def request_datetime(request: Graph) -> Node | None:
    return _constraint_satisfier_value(request, ODRL.dateTime)


# rightOperand del ConstraintSatisfier appeso a lada:actionIntention
# (operatore eq) con quel leftOperand. None se manca.
def _constraint_satisfier_value(request: Graph, left: Node) -> Node | None:
    for satisfier in request.objects(LADA.actionIntention, LADA.hasConstraintSatisfier):
        if (satisfier, RDF.type, LADA.ConstraintSatisfier) not in request:
            continue
        if request.value(satisfier, ODRL.leftOperand) != left:
            continue
        if request.value(satisfier, ODRL.operator) != ODRL.eq:
            continue
        value = request.value(satisfier, ODRL.rightOperand)
        if value is not None:
            return value
    return None



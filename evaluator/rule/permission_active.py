from rdflib import Graph
from rdflib.term import Node

from evaluator import sotw
from evaluator.rule import action_class
from evaluator.rule import compare as cmp
from evaluator.rule import refinement as refn
from evaluator.vocab import namespaces

# Namespace ODRL, RDF e LADA.
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
LADA = namespaces["lada"]


# Valuta se un Permission è active sull'azione della request:
# tutti i Constraint sono satisfied e tutti i Duty sono fulfilled oppure inactive.
# Lo State of the World non arriva come Graph: si interroga via SPARQL da sotw.py.
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
# Senza valore esplicito lo legge dalla request (stesso leftOperand).
# Con use_request=False usa actual, per esempio il rightOperand di una SotwAssertion.
def is_constraint_satisfied(
    policy: Graph,
    constraint: Node,
    request: Graph,
    actual: Node | None = None,
    *,
    use_request: bool = True,
) -> bool:
    """Il nodo è satisfied se operator e rightOperand confrontano un valore.
    Di default il valore è la requestAssertion con lo stesso leftOperand.
    Con use_request=False si usa actual; se manca, False.
    Il tipo dei due valori sceglie il confronto.
    """
    left = policy.value(constraint, ODRL.leftOperand)
    operator = policy.value(constraint, ODRL.operator)
    right = policy.value(constraint, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False
    if use_request:
        actual = _request_value_for_constraint(request, left)
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
    constraints = list(policy.objects(duty, ODRL.constraint))
    # Duty inactive (constraint non satisfied) ⇒ la permission può restare active
    if constraints and not all(
        is_constraint_satisfied(policy, constraint, request)
        for constraint in constraints
    ):
        return True
    return _is_duty_fulfilled(policy, duty, request)


# Un Duty è fulfilled se nello SOTW esiste un'azione compiuta che
# corrisponde al tipo di azione e alle refinement della duty.
def _is_duty_fulfilled(policy: Graph, duty: Node, request: Graph) -> bool:
    action = policy.value(duty, ODRL.action)
    if action is None:
        return False
    # C1 usa un nodo azione con rdf:value, non l'URI odrl:compensate diretto
    action_type = action_class.action_type(policy, action)
    if action_type == ODRL.compensate:
        return _is_compensate_fulfilled(policy, duty, action, request)
    raise NotImplementedError(f"Duty action not supported yet: {action_type}")


# Il compensate è fulfilled se un Payment collegato alla duty ha come payee
# il beneficiario e ogni refinement è soddisfatta da una SotwAssertion.
def _is_compensate_fulfilled(
    policy: Graph, duty: Node, action: Node, request: Graph
) -> bool:
    beneficiary = _compensate_beneficiary(policy, duty, action)
    refinements = list(policy.objects(action, ODRL.refinement))
    # SPARQL su sotw.py: solo i Payment con conditionId = URI della duty
    for payment in sotw.payments_for_condition(duty):
        # Il payer può essere un terzo; conta il beneficiario (payee)
        if beneficiary is not None and payment["payee"] != beneficiary:
            continue
        # Ogni refinement deve essere soddisfatta da una SotwAssertion.
        if all(
            refn.satisfied_by_sotw(policy, refinement, request, duty, action)
            for refinement in refinements
        ):
            return True
    return False


# Beneficiario del compensate: odrl:compensatedParty se c'è, altrimenti
# l'assigner della permission che contiene la duty.
def _compensate_beneficiary(
    policy: Graph, duty: Node, action: Node
) -> Node | None:
    compensated = policy.value(action, ODRL.compensatedParty)
    if compensated is not None:
        return compensated
    # C1 non dichiara compensatedParty: i soldi vanno all'assigner (sony)
    for permission in policy.subjects(ODRL.duty, duty):
        assigner = policy.value(permission, ODRL.assigner)
        if assigner is not None:
            return assigner
    return None


# Valore della request con lo stesso leftOperand. Senza asserzione, None.
def _request_value_for_constraint(request: Graph, left: Node) -> Node | None:
    return _request_assertion(request, left)


# rightOperand della lada:RequestAssertion (operatore eq) con quel leftOperand.
# Un nodo con gli stessi operandi ma senza quel tipo viene ignorato; None se manca.
def _request_assertion(request: Graph, left: Node) -> Node | None:
    for assertion in request.subjects(ODRL.leftOperand, left):
        if (assertion, RDF.type, LADA.RequestAssertion) not in request:
            continue
        if request.value(assertion, ODRL.operator) != ODRL.eq:
            continue
        value = request.value(assertion, ODRL.rightOperand)
        if value is not None:
            return value
    return None



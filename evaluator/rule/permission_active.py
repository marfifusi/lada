from rdflib import Graph
from rdflib.term import Node

from evaluator import sotw
from evaluator.rule import action_class
from evaluator.rule import compare as cmp
from evaluator.vocab import (
    LEFT_OPERAND_TO_FEATURE,
    LEFT_OPERAND_TO_SOTW_PROPERTY,
    namespaces,
)

# Namespace ODRL, SOTW, pagamenti e vocabolario esempio (ex:dayOfWeek).
ODRL = namespaces["odrl"]
SOTW = namespaces["sotw"]
PAY = namespaces["pay"]
EX = namespaces["ex"]


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


# Verifica se un Constraint è satisfied: il RequestParameter della prima
# feature mappata al leftOperand deve soddisfare operator/rightOperand; se manca, False.
def is_constraint_satisfied(
    policy: Graph,
    constraint: Node,
    request: Graph,
) -> bool:
    """Il constraint è satisfied se LEFT_OPERAND_TO_FEATURE collega il
    leftOperand a un describesFeature presente nella request e il confronto vale.
    Senza mapping o senza parametro il constraint non è verificabile → False.
    """
    left = policy.value(constraint, ODRL.leftOperand)
    operator = policy.value(constraint, ODRL.operator)
    right = policy.value(constraint, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False

    actual = _request_parameter_value(request, left)
    if actual is None:
        return False

    if left == ODRL.dateTime:
        return cmp.compare_datetimes(actual, operator, right)

    # C2: ex:dayOfWeek si ricava dal datetime della request, poi eq case-insensitive
    if left == EX.dayOfWeek:
        return cmp.compare_strings(
            cmp.weekday_from_datetime(actual), operator, right
        )

    raise NotImplementedError(f"Constraint leftOperand not supported yet: {left}")


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
    return _is_duty_fulfilled(policy, duty)


# Un Duty è fulfilled se nello SOTW esiste un'azione compiuta che
# corrisponde al tipo di azione e alle refinement della duty.
def _is_duty_fulfilled(policy: Graph, duty: Node) -> bool:
    action = policy.value(duty, ODRL.action)
    if action is None:
        return False
    # C1 usa un nodo azione con rdf:value, non l'URI odrl:compensate diretto
    action_type = action_class.action_type(policy, action)
    if action_type == ODRL.compensate:
        return _is_compensate_fulfilled(policy, duty, action)
    raise NotImplementedError(f"Duty action not supported yet: {action_type}")


# Il compensate è fulfilled se un Payment collegato alla duty soddisfa
# tutte le refinement e ha come payee il beneficiario (assigner).
def _is_compensate_fulfilled(policy: Graph, duty: Node, action: Node) -> bool:
    beneficiary = _compensate_beneficiary(policy, duty, action)
    refinements = list(policy.objects(action, ODRL.refinement))
    # SPARQL su sotw.py: solo i Payment con conditionId = URI della duty
    for payment in sotw.payments_for_condition(duty):
        # Il payer può essere un terzo; conta il beneficiario (payee)
        if beneficiary is not None and payment["payee"] != beneficiary:
            continue
        # Un solo Payment deve soddisfare tutte le refinement insieme
        if all(
            _refinement_satisfied_by_payment(policy, refinement, payment)
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


# Confronta una refinement col Payment: payAmount vs netAmount, unit vs currency.
def _refinement_satisfied_by_payment(
    policy: Graph, refinement: Node, payment: dict[str, Node | None]
) -> bool:
    left = policy.value(refinement, ODRL.leftOperand)
    operator = policy.value(refinement, ODRL.operator)
    right = policy.value(refinement, ODRL.rightOperand)
    if left is None or operator is None or right is None:
        return False
    # payAmount non è una proprietà RDF del Payment: va tradotto (→ netAmount)
    prop = LEFT_OPERAND_TO_SOTW_PROPERTY.get(left)
    if prop is None:
        raise NotImplementedError(
            f"Refinement leftOperand not supported yet: {left}"
        )
    actual = _payment_property_value(payment, prop)
    if actual is None:
        return False
    if prop == PAY.netAmount:
        if not cmp.compare_numbers(actual, operator, right):
            return False
        # odrl:unit della refinement corrisponde a pay:currency nello SOTW
        unit = policy.value(refinement, ODRL.unit)
        if unit is not None and payment["currency"] != unit:
            return False
        return True
    raise NotImplementedError(f"Payment property not supported yet: {prop}")


# Legge dal Payment il valore della proprietà SOTW mappata al leftOperand.
def _payment_property_value(
    payment: dict[str, Node | None], prop: Node
) -> Node | None:
    # Il dict espone "amount", non l'URI pay:netAmount usato nel mapping
    if prop == PAY.netAmount:
        return payment["amount"]
    return None


# Cerca il RequestParameter provando i describesFeature mappati al leftOperand,
# in ordine di priorità; restituisce il primo valore trovato.
def _request_parameter_value(request: Graph, left_operand: Node) -> Node | None:
    features = LEFT_OPERAND_TO_FEATURE.get(left_operand)
    if not features:
        return None
    for feature in features:
        for param in request.subjects(SOTW.describesFeature, feature):
            value = request.value(param, SOTW.value)
            if value is not None:
                return value
    return None

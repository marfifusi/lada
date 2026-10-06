from evaluator import sotw
from evaluator.evaluate import is_permitted, open_evaluation_request, open_rdflib
from evaluator.rule import action_class
from evaluator.rule import assignee
from evaluator.rule import refinement
from evaluator.rule import target
from evaluator.rule.permission_active import ODRL, is_permission_active


# test_active: la Permission è active (constraint satisfied, duty fulfilled o inactive).

# Caso A1-1: policy A1 + request del 2017-12-19 → permesso active
def test_active_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso A1-2: policy A1 + request del 2019-12-19 → permesso inactive
def test_active_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso B1-1: policy B1 + print a 800 dpi → permesso active (nessun constraint/duty)
def test_active_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso B1-2: policy B1 + print a 2400 dpi → permesso active (nessun constraint/duty)
def test_active_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C1-1: policy C1 + SOTW senza pagamento → permesso inactive
def test_active_c1_1():
    sotw.set_source("policies/samples/sotws/c1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C1-2: policy C1 + pagamento 5.00 EUR nello SOTW → permesso active
def test_active_c1_2():
    sotw.set_source("policies/samples/sotws/c1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C2-1: martedì, SOTW vuoto → duty inactive → permesso active
def test_active_c2_1():
    sotw.set_source("policies/samples/sotws/c2-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C2-2: domenica, SOTW vuoto → duty active not-set → permesso inactive
def test_active_c2_2():
    sotw.set_source("policies/samples/sotws/c2-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C2-3: domenica, pagamento 5.00 EUR → duty fulfilled → permesso active
def test_active_c2_3():
    sotw.set_source("policies/samples/sotws/c2-3_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# test_action: l'azione della request appartiene alla classe della Permission.

# Caso A1-1: distribute nella request e nella policy
def test_action_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso A1-2: distribute nella request e nella policy
def test_action_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso B1-1: print nella request e rdf:value della policy
def test_action_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso B1-2: print nella request e rdf:value della policy
def test_action_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C1-1: play nella request e nella policy
def test_action_c1_1():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C1-2: play nella request e nella policy
def test_action_c1_2():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C2-1: play nella request e nella policy
def test_action_c2_1():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C2-2: play nella request e nella policy
def test_action_c2_2():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C2-3: play nella request e nella policy
def test_action_c2_3():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# test_target: evaluatedTarget della request è uguale a odrl:target della Permission.

# Caso A1-1: document/1234 nella request e nella policy
def test_target_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso A1-2: document/1234 nella request e nella policy
def test_target_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso B1-1: document/1234 nella request e nella policy
def test_target_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso B1-2: document/1234 nella request e nella policy
def test_target_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso C1-1: music/1999.mp3 nella request e nella policy
def test_target_c1_1():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso C1-2: music/1999.mp3 nella request e nella policy
def test_target_c1_2():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso C2-1: music/1999.mp3 nella request e nella policy
def test_target_c2_1():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso C2-2: music/1999.mp3 nella request e nella policy
def test_target_c2_2():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# Caso C2-3: music/1999.mp3 nella request e nella policy
def test_target_c2_3():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = target.matches(policy, permission, request)
    print(f"Permission {permission} target: {matched}")


# test_assignee: se la Permission ha un assignee, evaluatedParty è lui
# oppure nello SOTW evaluatedParty odrl:partOf quell'assignee.

# Caso A1-1: la Permission non ha assignee
def test_assignee_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso A1-2: la Permission non ha assignee
def test_assignee_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso B1-1: la Permission non ha assignee
def test_assignee_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso B1-2: la Permission non ha assignee
def test_assignee_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso C1-1: assignee e evaluatedParty sono party/billie
def test_assignee_c1_1():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso C1-2: assignee e evaluatedParty sono party/billie
def test_assignee_c1_2():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso C2-1: assignee e evaluatedParty sono party/billie
def test_assignee_c2_1():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso C2-2: assignee e evaluatedParty sono party/billie
def test_assignee_c2_2():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# Caso C2-3: assignee e evaluatedParty sono party/billie
def test_assignee_c2_3():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = assignee.matches(policy, permission, request)
    print(f"Permission {permission} assignee: {matched}")


# test_refinement: le refinement di azione, target e assignee della Permission sono satisfied.

# Caso A1-1: la Permission non ha refinement
def test_refinement_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso A1-2: la Permission non ha refinement
def test_refinement_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso B1-1: print a 800 dpi, refinement resolution lteq 1200
def test_refinement_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso B1-2: print a 2400 dpi, refinement resolution lteq 1200
def test_refinement_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso C1-1: la refinement payAmount sta sulla duty, non sulla Permission
def test_refinement_c1_1():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso C1-2: la refinement payAmount sta sulla duty, non sulla Permission
def test_refinement_c1_2():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso C2-1: la refinement payAmount sta sulla duty, non sulla Permission
def test_refinement_c2_1():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso C2-2: la refinement payAmount sta sulla duty, non sulla Permission
def test_refinement_c2_2():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# Caso C2-3: la refinement payAmount sta sulla duty, non sulla Permission
def test_refinement_c2_3():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = refinement.satisfied(policy, permission, request)
    print(f"Permission {permission} refinement: {matched}")


# test_permitted: i cinque controlli della Permission sono tutti veri.

# Caso A1-1: active, distribute, document/1234, nessun assignee né refinement
def test_permitted_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso A1-2: constraint dateTime non satisfied → non permitted
def test_permitted_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso B1-1: print a 800 dpi, refinement resolution soddisfatta
def test_permitted_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso B1-2: print a 2400 dpi, refinement resolution non soddisfatta
def test_permitted_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso C1-1: SOTW senza pagamento → duty non fulfilled → non permitted
def test_permitted_c1_1():
    sotw.set_source("policies/samples/sotws/c1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso C1-2: pagamento 5.00 EUR → duty fulfilled → permitted
def test_permitted_c1_2():
    sotw.set_source("policies/samples/sotws/c1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso C2-1: martedì, duty inactive → permitted
def test_permitted_c2_1():
    sotw.set_source("policies/samples/sotws/c2-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso C2-2: domenica, SOTW vuoto → duty non fulfilled → non permitted
def test_permitted_c2_2():
    sotw.set_source("policies/samples/sotws/c2-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso C2-3: domenica, pagamento 5.00 EUR → duty fulfilled → permitted
def test_permitted_c2_3():
    sotw.set_source("policies/samples/sotws/c2-3_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


if __name__ == "__main__":
    # Attivazione della Permission (constraint e duty).
    test_active_a1_1()
    test_active_a1_2()
    test_active_b1_1()
    test_active_b1_2()
    test_active_c1_1()
    test_active_c1_2()
    test_active_c2_1()
    test_active_c2_2()
    test_active_c2_3()
    # Classe di azioni della Permission rispetto all'azione della request.
    test_action_a1_1()
    test_action_a1_2()
    test_action_b1_1()
    test_action_b1_2()
    test_action_c1_1()
    test_action_c1_2()
    test_action_c2_1()
    test_action_c2_2()
    test_action_c2_3()
    # Target della Permission rispetto a evaluatedTarget della request.
    test_target_a1_1()
    test_target_a1_2()
    test_target_b1_1()
    test_target_b1_2()
    test_target_c1_1()
    test_target_c1_2()
    test_target_c2_1()
    test_target_c2_2()
    test_target_c2_3()
    # Assignee della Permission rispetto a evaluatedParty della request.
    test_assignee_a1_1()
    test_assignee_a1_2()
    test_assignee_b1_1()
    test_assignee_b1_2()
    test_assignee_c1_1()
    test_assignee_c1_2()
    test_assignee_c2_1()
    test_assignee_c2_2()
    test_assignee_c2_3()
    # Refinement di azione, target e assignee della Permission.
    test_refinement_a1_1()
    test_refinement_a1_2()
    test_refinement_b1_1()
    test_refinement_b1_2()
    test_refinement_c1_1()
    test_refinement_c1_2()
    test_refinement_c2_1()
    test_refinement_c2_2()
    test_refinement_c2_3()
    # Permitted: i cinque controlli insieme.
    test_permitted_a1_1()
    test_permitted_a1_2()
    test_permitted_b1_1()
    test_permitted_b1_2()
    test_permitted_c1_1()
    test_permitted_c1_2()
    test_permitted_c2_1()
    test_permitted_c2_2()
    test_permitted_c2_3()

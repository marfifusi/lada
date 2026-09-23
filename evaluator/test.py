from evaluator import sotw
from evaluator.evaluate import open_rdflib
from evaluator.rule import action_class
from evaluator.rule.permission_active import ODRL, is_permission_active


# test_active: la Permission è active (constraint satisfied, duty fulfilled o inactive).

# Caso A1-1: policy A1 + request del 2017-12-19 → permesso active
def test_active_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso A1-2: policy A1 + request del 2019-12-19 → permesso inactive
def test_active_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso B1-1: policy B1 + print a 800 dpi → permesso active (nessun constraint/duty)
def test_active_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso B1-2: policy B1 + print a 2400 dpi → permesso active (nessun constraint/duty)
def test_active_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C1-1: policy C1 + SOTW senza pagamento → permesso inactive
def test_active_c1_1():
    sotw.set_source("policies/samples/sotws/c1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C1-2: policy C1 + pagamento 5.00 EUR nello SOTW → permesso active
def test_active_c1_2():
    sotw.set_source("policies/samples/sotws/c1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C2-1: martedì, SOTW vuoto → duty inactive → permesso active
def test_active_c2_1():
    sotw.set_source("policies/samples/sotws/c2-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C2-2: domenica, SOTW vuoto → duty active not-set → permesso inactive
def test_active_c2_2():
    sotw.set_source("policies/samples/sotws/c2-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso C2-3: domenica, pagamento 5.00 EUR → duty fulfilled → permesso active
def test_active_c2_3():
    sotw.set_source("policies/samples/sotws/c2-3_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# test_action: l'azione della request appartiene alla classe della Permission.

# Caso A1-1: distribute nella request e nella policy
def test_action_a1_1():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso A1-2: distribute nella request e nella policy
def test_action_a1_2():
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso B1-1: print nella request e rdf:value della policy
def test_action_b1_1():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso B1-2: print nella request e rdf:value della policy
def test_action_b1_2():
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/b1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C1-1: play nella request e nella policy
def test_action_c1_1():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C1-2: play nella request e nella policy
def test_action_c1_2():
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C2-1: play nella request e nella policy
def test_action_c2_1():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c2-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C2-2: play nella request e nella policy
def test_action_c2_2():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c2-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


# Caso C2-3: play nella request e nella policy
def test_action_c2_3():
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    request = open_rdflib("policies/samples/ev_requests/c2-3_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    matched = action_class.matches(policy, permission, request)
    print(f"Permission {permission} action class: {matched}")


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

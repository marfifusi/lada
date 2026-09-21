from evaluator.evaluate import ODRL, is_permission_active, open_rdflib


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


if __name__ == "__main__":
    test_active_a1_1()
    test_active_a1_2()
    test_active_b1_1()
    test_active_b1_2()

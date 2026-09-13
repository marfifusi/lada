from evaluator.evaluate import ODRL, is_permission_active, open_rdflib


# Caso A1-1: policy A1 + request del 2017-12-19 → permesso active
def test_a1_1():
    policy = open_rdflib("policies/sample/a1_policy.json")
    request = open_rdflib("ev_requests/a1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


# Caso A1-2: policy A1 + request del 2019-12-19 → permesso inactive
def test_a1_2():
    policy = open_rdflib("policies/sample/a1_policy.json")
    request = open_rdflib("ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    active = is_permission_active(policy, permission, request)
    print(f"Permission {permission} active: {active}")


if __name__ == "__main__":
    test_a1_1()
    test_a1_2()

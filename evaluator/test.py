from evaluator import sotw
from evaluator.evaluate import get_ev_report, is_permitted, open_evaluation_request, open_rdflib
from evaluator.rule.permission_active import ODRL


# test_permitted: i cinque controlli della Permission sono tutti veri.
# Ogni test carica lo SOTW del caso prima di is_permitted, anche se la
# valutazione non lo consulta: l'evaluation report userà il suo @id.

# Caso A1-1: active, distribute, document/1234, nessun assignee né refinement
def test_permitted_a1_1():
    sotw.set_source("policies/samples/sotws/a1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-1_request.json")
    # Gli esempi hanno una sola Permission: next prende quella.
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso A1-2: constraint dateTime non satisfied → non permitted
def test_permitted_a1_2():
    sotw.set_source("policies/samples/sotws/a1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/a1-2_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso B1-1: print a 800 dpi, refinement resolution soddisfatta
def test_permitted_b1_1():
    sotw.set_source("policies/samples/sotws/b1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    request = open_evaluation_request("policies/samples/ev_requests/b1-1_request.json")
    permission = next(policy.objects(None, ODRL.permission))
    permitted = is_permitted(policy, permission, request)
    print(f"Permission {permission} permitted: {permitted}")


# Caso B1-2: print a 2400 dpi, refinement resolution non soddisfatta
def test_permitted_b1_2():
    sotw.set_source("policies/samples/sotws/b1-2_sotw.json")
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


# Caso A1-1: report con permission active e constraint satisfied.
def test_report_a1_1():
    sotw.set_source("policies/samples/sotws/a1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/a1-1_request.json")
    print(f"Report: {report}")


# Caso A1-2: report con permission inactive e constraint not-satisfied.
def test_report_a1_2():
    sotw.set_source("policies/samples/sotws/a1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/a1_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/a1-2_request.json")
    print(f"Report: {report}")


# Caso B1-1: report con permission active e refinement satisfied.
def test_report_b1_1():
    sotw.set_source("policies/samples/sotws/b1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/b1-1_request.json")
    print(f"Report: {report}")


# Caso B1-2: report con permission active e refinement not-satisfied.
def test_report_b1_2():
    sotw.set_source("policies/samples/sotws/b1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/b1_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/b1-2_request.json")
    print(f"Report: {report}")


# Caso C1-1: report con duty active non fulfilled e permission inactive.
def test_report_c1_1():
    sotw.set_source("policies/samples/sotws/c1-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/c1-1_request.json")
    print(f"Report: {report}")


# Caso C1-2: report con duty fulfilled e permission active.
def test_report_c1_2():
    sotw.set_source("policies/samples/sotws/c1-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c1_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/c1-2_request.json")
    print(f"Report: {report}")


# Caso C2-1: report con duty inactive e permission active.
def test_report_c2_1():
    sotw.set_source("policies/samples/sotws/c2-1_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/c2-1_request.json")
    print(f"Report: {report}")


# Caso C2-2: report con duty active non fulfilled e permission inactive.
def test_report_c2_2():
    sotw.set_source("policies/samples/sotws/c2-2_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/c2-2_request.json")
    print(f"Report: {report}")


# Caso C2-3: report con duty fulfilled e permission active.
def test_report_c2_3():
    sotw.set_source("policies/samples/sotws/c2-3_sotw.json")
    policy = open_rdflib("policies/samples/policies/c2_policy.json")
    report = get_ev_report(policy, "policies/samples/ev_requests/c2-3_request.json")
    print(f"Report: {report}")


if __name__ == "__main__":
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
    # Report: un file per caso.
    test_report_a1_1()
    test_report_a1_2()
    test_report_b1_1()
    test_report_b1_2()
    test_report_c1_1()
    test_report_c1_2()
    test_report_c2_1()
    test_report_c2_2()
    test_report_c2_3()

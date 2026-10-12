import json
import re
from datetime import datetime, timezone
from pathlib import Path

from rdflib import Graph
from rdflib.term import Node

from evaluator import n3_engine
from evaluator import ontology_cache
from evaluator import sotw
from evaluator.rule import action_class
from evaluator.rule import assignee
from evaluator.rule import duty as duty_rule
from evaluator.rule import permission_active
from evaluator.rule import refinement
from evaluator.rule import target
from evaluator.vocab import namespaces

# Regole N3 che traducono i requestParameter in lada:ConstraintSatisfier.
REQUEST_MAP = "policies/samples/maps/ev_requests_map.n3"


# Apre un file JSON-LD e lo carica come grafo RDF
def open_rdflib(file: str) -> Graph:
    ontology_cache.install()
    graph = Graph()
    graph.parse(file, format="json-ld")
    # Associa i prefissi noti per stampare URI in forma compatta
    for prefix, ns in namespaces.items():
        graph.bind(prefix, ns)
    return graph


# Apre una EvaluationRequest JSON-LD e vi applica le regole di ev_requests_map.n3.
def open_evaluation_request(file: str) -> Graph:
    graph = open_rdflib(file)
    n3_engine.apply(graph, REQUEST_MAP)
    return graph


# Apre un file JSON-LD e stampa le triple del grafo RDF
def print_rdflib(file: str) -> None:
    graph = open_rdflib(file)
    nm = graph.namespace_manager
    print(f"Opened {file}: {len(graph)} triples")
    # n3(nm) rende soggetto, predicato e oggetto con i prefissi
    for s, p, o in graph:
        print(f"  {s.n3(nm)} {p.n3(nm)} {o.n3(nm)}")


# True se la Permission è active e coincidono classe, target, assignee e refinement.
def is_permitted(policy: Graph, permission: Node, request: Graph) -> bool:
    return (
        permission_active.is_permission_active(policy, permission, request)
        and action_class.matches(policy, permission, request)
        and target.matches(policy, permission, request)
        and assignee.matches(policy, permission, request)
        and refinement.satisfied(policy, permission, request)
    )


# Cartella dei report generati. Il nome del file è {codice}_report.json.
_EV_REPORT_DIR = Path("policies/samples/ev_report")
# Nome atteso del file di request: {codice}_request.json.
_REQUEST_NAME = re.compile(r"^(.+)_request\.json$")

# Namespace ODRL, RDF e SOTW per policy, request e stato.
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
SOTW = namespaces["sotw"]


# Scrive l'evaluation report del caso e restituisce il path del file.
# request è il path del JSON-LD, non il grafo: il nome del report si ricava da lì.
# Lo State of the World è quello già caricato con sotw.set_source.
def get_ev_report(policy: Graph, request: str) -> str:
    code = _request_code(request)
    request_graph = open_evaluation_request(request)
    document = _compliance_report(policy, request_graph, code)
    path = _EV_REPORT_DIR / f"{code}_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return str(path)


# Codice del caso dal nome del file, oppure ValueError se il pattern non torna.
def _request_code(request: str) -> str:
    match = _REQUEST_NAME.fullmatch(Path(request).name)
    if match is None:
        raise ValueError(
            "Evaluation request name must match {code}_request.json, "
            f"got {Path(request).name!r}"
        )
    return match.group(1)


# Documento JSON-LD del ComplianceReport per questa policy e questa request.
def _compliance_report(policy: Graph, request: Graph, code: str) -> dict:
    policy_id = _single(
        policy.subjects(ODRL.permission),
        "Policy graph must contain one policy",
    )
    request_id = _single(
        request.subjects(RDF.type, SOTW.EvaluationRequest),
        "Evaluation request must contain one EvaluationRequest",
    )
    state_id = _sotw_id()
    permissions = list(policy.objects(policy_id, ODRL.permission))
    permission_reports = []
    constraint_reports = []
    condition_reports = []
    action_reports = []
    for permission in permissions:
        permission_reports.append(
            _permission_report(policy, permission, request, code)
        )
        constraint_reports.extend(
            _permission_constraint_reports(policy, permission, request, code)
        )
        for duty in policy.objects(permission, ODRL.duty):
            fulfilled = duty_rule.is_fulfilled(policy, duty, request)
            condition_reports.append(
                _condition_report(policy, duty, request, code, fulfilled)
            )
            constraint_reports.extend(
                _duty_constraint_reports(policy, duty, request, code)
            )
            action = policy.value(duty, ODRL.action)
            if action is not None:
                action_reports.append(_action_report(action, code, fulfilled))
    document = {
        "@context": {
            "odrl": "http://www.w3.org/ns/odrl.jsonld",
            "ex": "http://example.org/",
            "report": "http://example.com/report/temp/",
            "dct": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@id": f"http://example.com/policy-report/{code}",
        "@type": "report:ComplianceReport",
        "dct:created": {
            "@value": _created_now(),
            "@type": "xsd:dateTime",
        },
        "report:policy": str(policy_id),
        "report:evaluationRequest": str(request_id),
        "report:state": str(state_id),
    }
    _put_reports(document, "ex:permissionReport", permission_reports)
    _put_reports(document, "ex:constraintReport", constraint_reports)
    _put_reports(document, "ex:conditionReport", condition_reports)
    _put_reports(document, "ex:actionReport", action_reports)
    return document


# Un solo nodo, oppure ValueError se manca o ce n'è più di uno.
def _single(nodes, message: str) -> Node:
    found = list(nodes)
    if len(found) != 1:
        raise ValueError(message)
    return found[0]


# @id dello SotW già caricato.
def _sotw_id() -> Node:
    world = sotw.graph()
    if world is None:
        raise ValueError("State of the World is not loaded")
    return _single(
        world.subjects(RDF.type, SOTW.SotW),
        "State of the World must contain one SotW",
    )


# Istante UTC di creazione, con i millisecondi.
def _created_now() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


# RuleReport della Permission: activation dai constraint e dalle duty, control da is_permitted.
def _permission_report(
    policy: Graph,
    permission: Node,
    request: Graph,
    code: str,
) -> dict:
    active = permission_active.is_permission_active(policy, permission, request)
    permitted = is_permitted(policy, permission, request)
    return {
        "@id": f"http://example.com/policy-report/{code}/permission/{_local_name(permission)}",
        "@type": "report:ruleReport",
        "report:rule": str(permission),
        "report:activationState": "report:Active" if active else "report:Inactive",
        "report:controlState": "report:Permit" if permitted else "report:Deny",
    }


# ConstraintReport dei constraint della Permission e delle sue refinement.
def _permission_constraint_reports(
    policy: Graph,
    permission: Node,
    request: Graph,
    code: str,
) -> list[dict]:
    reports = [
        _constraint_report(policy, constraint, request, code)
        for constraint in policy.objects(permission, ODRL.constraint)
    ]
    for node in _refined_nodes(policy, permission):
        for refinement_node in policy.objects(node, ODRL.refinement):
            reports.append(
                _constraint_report(policy, refinement_node, request, code)
            )
    return reports


# ConstraintReport dei constraint di una duty.
def _duty_constraint_reports(
    policy: Graph,
    duty: Node,
    request: Graph,
    code: str,
) -> list[dict]:
    return [
        _constraint_report(policy, constraint, request, code)
        for constraint in policy.objects(duty, ODRL.constraint)
    ]


# Nodi della Permission che possono portare odrl:refinement.
def _refined_nodes(policy: Graph, permission: Node):
    for predicate in (ODRL.action, ODRL.target, ODRL.assignee):
        yield from policy.objects(permission, predicate)


# ConstraintReport: satisfied o not-satisfied sullo stesso confronto dei constraint.
def _constraint_report(
    policy: Graph,
    constraint: Node,
    request: Graph,
    code: str,
) -> dict:
    satisfied = permission_active.is_constraint_satisfied(policy, constraint, request)
    return {
        "@id": f"http://example.com/policy-report/{code}/constraint/{_local_name(constraint)}",
        "@type": "report:ConstraintReport",
        "report:constraint": str(constraint),
        "report:satisfactionState": (
            "report:Satisfied" if satisfied else "report:Not-Satisfied"
        ),
    }


# ConditionReport della duty. fulfilled è già calcolato: deontic Fulfilled oppure Not-set.
def _condition_report(
    policy: Graph,
    duty: Node,
    request: Graph,
    code: str,
    fulfilled: bool,
) -> dict:
    active = duty_rule.is_active(policy, duty, request)
    return {
        "@id": f"http://example.com/policy-report/{code}/condition/{_local_name(duty)}",
        "@type": "report:ConditionReport",
        "report:condition": str(duty),
        "report:activationState": "report:Active" if active else "report:Inactive",
        "report:deonticState": "report:Fulfilled" if fulfilled else "report:Not-set",
    }


# ActionReport dell'azione della duty: Performed se la duty è fulfilled.
def _action_report(action: Node, code: str, fulfilled: bool) -> dict:
    return {
        "@id": f"http://example.com/policy-report/{code}/action/{_local_name(action)}",
        "@type": "report:ActionReport",
        "report:action": str(action),
        "report:performanceState": (
            "report:Performed" if fulfilled else "report:Unperformed"
        ),
    }


# Inserisce i report sotto la chiave: un oggetto se è uno solo, una lista se sono di più.
def _put_reports(document: dict, key: str, reports: list[dict]) -> None:
    if not reports:
        return
    document[key] = reports[0] if len(reports) == 1 else reports


# Ultimo frammento dell'IRI, per gli @id dei report annidati.
def _local_name(node: Node) -> str:
    text = str(node)
    for separator in ("#", "/"):
        if separator in text:
            text = text.rsplit(separator, 1)[-1]
    return text or "blank"

import json
import re
import secrets
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

# Namespace ODRL, RDF e SOTW per policy, request e stato.
ODRL = namespaces["odrl"]
RDF = namespaces["rdf"]
SOTW = namespaces["sotw"]

# Regole N3 che traducono i requestParameter in lada:ConstraintSatisfier.
REQUEST_MAP = "policies/samples/maps/ev_requests_map.n3"
# Cartella in cui vengono scritti i report generati.
_EV_REPORT_DIR = Path("policies/samples/ev_report/generated")
# Base degli @id: un token esadecimale casuale, i nodi interni sono frammenti.
_REPORT_IRI = "https://w3id.org/lada/report/"
# Se il file è {codice}_request.json, il report prende il nome {codice}_report.json.
_REQUEST_NAME = re.compile(r"^(.+)_request\.json$")


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


# Scrive l'evaluation report del caso e restituisce il path del file.
# request è il path del JSON-LD, non il grafo: il nome del file si ricava da lì.
# Lo State of the World è quello già caricato con sotw.set_source.
def get_ev_report(policy: Graph, request: str) -> str:
    request_graph = open_evaluation_request(request)
    document = _policy_report(policy, request_graph)
    path = _EV_REPORT_DIR / _report_file_name(request)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return str(path)


# Nome del file di report a partire dal nome della request.
# {codice}_request.json diventa {codice}_report.json; altrimenti {nome}_report.json.
def _report_file_name(request: str) -> str:
    name = Path(request).name
    match = _REQUEST_NAME.fullmatch(name)
    if match is not None:
        return f"{match.group(1)}_report.json"
    return f"{Path(name).stem}_report.json"


# Documento JSON-LD del PolicyReport per questa policy e questa request.
def _policy_report(policy: Graph, request: Graph) -> dict:
    ids = _new_report_ids()
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
    # Per ogni Permission: stato della regola, i constraint e le duty collegate.
    for permission in permissions:
        permission_reports.append(
            _permission_report(policy, permission, request, ids)
        )
        constraint_reports.extend(
            _permission_constraint_reports(policy, permission, request, ids)
        )
        for duty in policy.objects(permission, ODRL.duty):
            # None se nessuna SotwAction nello SOTW compie la duty.
            fulfilling = duty_rule.fulfilling_action(policy, duty, request)
            fulfilled = fulfilling is not None
            condition_reports.append(
                _condition_report(policy, duty, request, ids, fulfilled, fulfilling)
            )
            constraint_reports.extend(
                _duty_constraint_reports(policy, duty, request, ids)
            )
            action = policy.value(duty, ODRL.action)
            # Senza odrl:action la duty non ha un ActionReport.
            if action is not None:
                action_reports.append(_action_report(action, ids, fulfilled))
    document = {
        # Prefissi allineati agli esempi in policies/samples/ev_report/reference/.
        "@context": {
            "odrl": "http://www.w3.org/ns/odrl.jsonld",
            "ex": "http://example.org/",
            "report": "http://example.com/report/temp/",
            "dct": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@id": _policy_report_id(ids),
        "@type": "report:PolicyReport",
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


# Un solo nodo distinto, oppure ValueError se manca o ce n'è più di uno.
# Lo stesso soggetto può uscire una volta per tripla: più permission non sono più policy.
def _single(nodes, message: str) -> Node:
    # fromkeys toglie i duplicati e tiene l'ordine: lo stesso soggetto esce una volta per tripla.
    found = list(dict.fromkeys(nodes))
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
    # Millisecondi a tre cifre: datetime dà i microsecondi, qui si tengono solo i primi tre.
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


# Codice esadecimale di 16 cifre, condiviso dagli @id di un PolicyReport.
def _new_report_ids() -> dict:
    return {"code": secrets.token_hex(8), "n": {}}


# @id del PolicyReport: https://w3id.org/lada/report/{code}.
def _policy_report_id(ids: dict) -> str:
    return f"{_REPORT_IRI}{ids['code']}"


# Frammento del report: {iri}#{kind}-N, con N progressivo per kind.
def _child_report_id(ids: dict, kind: str) -> str:
    # Parte da 1: permission-1, constraint-1, condition-1, …
    ids["n"][kind] = ids["n"].get(kind, 0) + 1
    return f"{_policy_report_id(ids)}#{kind}-{ids['n'][kind]}"


# RuleReport della Permission: activation dai constraint e dalle duty, control da is_permitted.
def _permission_report(
    policy: Graph,
    permission: Node,
    request: Graph,
    ids: dict,
) -> dict:
    # Active non implica Permit: il control state aggiunge classe, target, assignee e refinement.
    active = permission_active.is_permission_active(policy, permission, request)
    permitted = is_permitted(policy, permission, request)
    return {
        "@id": _child_report_id(ids, "permission"),
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
    ids: dict,
) -> list[dict]:
    reports = [
        _constraint_report(policy, constraint, request, ids)
        for constraint in policy.objects(permission, ODRL.constraint)
    ]
    for node in _refined_nodes(policy, permission):
        # Le refinement su action, target e assignee entrano anch'esse come ConstraintReport.
        for refinement_node in policy.objects(node, ODRL.refinement):
            reports.append(
                _constraint_report(policy, refinement_node, request, ids)
            )
    return reports


# ConstraintReport dei constraint di una duty.
def _duty_constraint_reports(
    policy: Graph,
    duty: Node,
    request: Graph,
    ids: dict,
) -> list[dict]:
    return [
        _constraint_report(policy, constraint, request, ids)
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
    ids: dict,
) -> dict:
    satisfied = permission_active.is_constraint_satisfied(policy, constraint, request)
    return {
        "@id": _child_report_id(ids, "constraint"),
        "@type": "report:ConstraintReport",
        "report:constraint": str(constraint),
        "report:satisfactionState": (
            "report:Satisfied" if satisfied else "report:Not-Satisfied"
        ),
    }


# ConditionReport della duty. fulfillingAction c'è solo se una SotwAction la soddisfa.
def _condition_report(
    policy: Graph,
    duty: Node,
    request: Graph,
    ids: dict,
    fulfilled: bool,
    fulfilling: Node | None,
) -> dict:
    active = duty_rule.is_active(policy, duty, request)
    report = {
        "@id": _child_report_id(ids, "condition"),
        "@type": "report:ConditionReport",
        "report:condition": str(duty),
        "report:activationState": "report:Active" if active else "report:Inactive",
        "report:deonticState": "report:Fulfilled" if fulfilled else "report:Not-set",
    }
    if fulfilling is not None:
        report["report:fulfillingAction"] = str(fulfilling)
    return report


# ActionReport dell'azione della duty: Performed se la duty è fulfilled.
def _action_report(action: Node, ids: dict, fulfilled: bool) -> dict:
    return {
        "@id": _child_report_id(ids, "action"),
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
    # Lista solo quando i report sono più di uno.
    document[key] = reports[0] if len(reports) == 1 else reports

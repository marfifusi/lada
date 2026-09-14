import sys
from datetime import date, datetime, time

from rdflib.term import Node

from evaluator.vocab import namespaces

# Namespace ODRL usato nel confronto degli operatori dateTime.
ODRL = namespaces["odrl"]


# Confronta request (left) e policy (right) come finestre (inizio, fine).
# lt: tutta left è prima di tutta right; gt: tutta left è dopo tutta right.
# eq: right contiene left (un istante cade in quel giorno, o finestre uguali).
#     Se left contiene right non siamo sicuri → False e avviso su stderr.
# lteq/gteq: lt/gt oppure eq; neq: le finestre non si sovrappongono.
#     Se left contiene right, eq/neq/lteq/gteq non sono sicuri → False e avviso.
def compare_datetimes(left: Node, operator: Node, right: Node) -> bool:
    left_win = _to_time_window(left)
    right_win = _to_time_window(right)
    uncertain = _request_window_contains_policy(left_win, right_win)
    if operator == ODRL.lt:
        return _window_entirely_before(left_win, right_win)
    if operator == ODRL.gt:
        return _window_entirely_after(left_win, right_win)
    if operator == ODRL.eq:
        if uncertain:
            _warn_uncertain_containment("eq")
        return _windows_eq(left_win, right_win)
    if operator == ODRL.lteq:
        if uncertain:
            _warn_uncertain_containment("lteq")
        return _window_entirely_before(left_win, right_win) or _windows_eq(
            left_win, right_win
        )
    if operator == ODRL.gteq:
        if uncertain:
            _warn_uncertain_containment("gteq")
        return _window_entirely_after(left_win, right_win) or _windows_eq(
            left_win, right_win
        )
    if operator == ODRL.neq:
        if uncertain:
            _warn_uncertain_containment("neq")
        return not _windows_overlap(left_win, right_win)
    raise NotImplementedError(f"Constraint operator not supported yet: {operator}")


# Interpreta un valore RDF come finestra (inizio, fine):
# date → [mezzanotte, fine giornata], datetime → [istante, istante].
def _to_time_window(value: Node) -> tuple[datetime, datetime]:
    py = value.toPython() if hasattr(value, "toPython") else value
    if isinstance(py, datetime):
        return py, py
    if isinstance(py, date):
        return datetime.combine(py, time.min), datetime.combine(py, time.max)
    text = str(py)
    try:
        parsed_date = date.fromisoformat(text)
        return (
            datetime.combine(parsed_date, time.min),
            datetime.combine(parsed_date, time.max),
        )
    except ValueError:
        parsed_dt = datetime.fromisoformat(text)
        return parsed_dt, parsed_dt


# True se entrambi gli estremi di left sono < di entrambi gli estremi di right.
def _window_entirely_before(
    left: tuple[datetime, datetime], right: tuple[datetime, datetime]
) -> bool:
    left_start, left_end = left
    right_start, right_end = right
    return (
        left_start < right_start
        and left_start < right_end
        and left_end < right_start
        and left_end < right_end
    )


# True se entrambi gli estremi di left sono > di entrambi gli estremi di right.
def _window_entirely_after(
    left: tuple[datetime, datetime], right: tuple[datetime, datetime]
) -> bool:
    left_start, left_end = left
    right_start, right_end = right
    return (
        left_start > right_start
        and left_start > right_end
        and left_end > right_start
        and left_end > right_end
    )


# True se outer contiene inner (estremi compresi).
def _window_contains(
    outer: tuple[datetime, datetime], inner: tuple[datetime, datetime]
) -> bool:
    return outer[0] <= inner[0] and inner[1] <= outer[1]


# True se left contiene right in modo stretto (request-giorno vs policy-istante).
def _request_window_contains_policy(
    left: tuple[datetime, datetime], right: tuple[datetime, datetime]
) -> bool:
    return _window_contains(left, right) and not _window_contains(right, left)


# Avvisa che senza un istante preciso il confronto non è decidibile.
def _warn_uncertain_containment(operator_name: str) -> None:
    print(
        f"Constraint dateTime {operator_name}: la finestra temporale della request contiene "
        "quella della policy; senza avere un istante preciso non siamo sicuri, "
        "valutiamo la policy come inattiva.",
        file=sys.stderr,
    )


# eq: right contiene left. Se left contiene right, non siamo sicuri → False.
def _windows_eq(
    left: tuple[datetime, datetime], right: tuple[datetime, datetime]
) -> bool:
    if _window_contains(right, left):
        return True
    return False


# True se le due finestre hanno almeno un istante in comune.
def _windows_overlap(
    left: tuple[datetime, datetime], right: tuple[datetime, datetime]
) -> bool:
    return left[0] <= right[1] and right[0] <= left[1]

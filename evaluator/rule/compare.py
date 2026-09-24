# Logica di confronto tra grandezze (finestre temporali, giorno della settimana, numeri, …).
from datetime import date, datetime, time
from decimal import Decimal

from rdflib.term import Node

from evaluator.vocab import namespaces

# Namespace ODRL usato nel confronto degli operatori (dateTime, numeri, stringhe).
ODRL = namespaces["odrl"]

# Nome locale del leftOperand «giorno della settimana», indipendente dal namespace.
_WEEKDAY_LOCAL_NAME = "dayOfWeek"

# Nomi inglesi (Monday=0 … Sunday=6), fissi e indipendenti dal locale.
_WEEKDAYS_EN = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


# Confronto dateTime non decidibile: la finestra della request contiene
# quella della policy e manca un istante preciso.
class UncertainTimeWindowError(Exception):
    pass


# Confronta request (left) e policy (right) come finestre (inizio, fine).
# lt: tutta left è prima di tutta right; gt: tutta left è dopo tutta right.
# eq: right contiene left (un istante cade in quel giorno, o finestre uguali).
#     Se left contiene right non siamo sicuri → UncertainTimeWindowError.
# lteq/gteq: lt/gt oppure eq; neq: le finestre non si sovrappongono.
#     Se left contiene right, eq/neq/lteq/gteq non sono sicuri → UncertainTimeWindowError.
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
            _raise_uncertain_containment("eq")
        return _windows_eq(left_win, right_win)
    if operator == ODRL.lteq:
        if uncertain:
            _raise_uncertain_containment("lteq")
        return _window_entirely_before(left_win, right_win) or _windows_eq(
            left_win, right_win
        )
    if operator == ODRL.gteq:
        if uncertain:
            _raise_uncertain_containment("gteq")
        return _window_entirely_after(left_win, right_win) or _windows_eq(
            left_win, right_win
        )
    if operator == ODRL.neq:
        if uncertain:
            _raise_uncertain_containment("neq")
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


# Solleva UncertainTimeWindowError: senza un istante preciso il confronto non è decidibile.
def _raise_uncertain_containment(operator_name: str) -> None:
    raise UncertainTimeWindowError(
        f"Constraint dateTime {operator_name}: the request time window contains "
        "the policy time window; without an exact instant the comparison is uncertain."
    )


# eq: right contiene left (istante nella giornata, o finestre uguali).
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


# Confronto temporale su un valore date o dateTime.
# odrl:dateTime confronta le finestre; un leftOperand dayOfWeek ricava il weekday e confronta stringhe.
def compare_temporal(
    left_operand: Node, actual: Node, operator: Node, right: Node
) -> bool:
    if is_weekday_left_operand(left_operand):
        return compare_strings(weekday_from_datetime(actual), operator, right)
    if is_datetime_left_operand(left_operand):
        return compare_datetimes(actual, operator, right)
    raise NotImplementedError(
        f"Temporal leftOperand not supported yet: {left_operand}"
    )


# True se il leftOperand è odrl:dateTime (confronto fra finestre temporali).
def is_datetime_left_operand(left: Node) -> bool:
    return left == ODRL.dateTime


# True se il leftOperand è un giorno della settimana, in qualunque namespace.
def is_weekday_left_operand(left: Node) -> bool:
    return _local_name(left) == _WEEKDAY_LOCAL_NAME


# True se il leftOperand si valuta su data o dateTime (finestra oppure weekday).
def is_temporal_left_operand(left: Node) -> bool:
    return is_datetime_left_operand(left) or is_weekday_left_operand(left)


# Nome locale di un termine RDF: il tratto dopo l'ultimo # o /.
def _local_name(term: Node) -> str:
    text = str(term)
    cut = max(text.rfind("#"), text.rfind("/"))
    return text[cut + 1 :]


# True se il valore RDF è un intero (xsd:integer e i tipi derivati, non un booleano).
def is_integer(value: Node) -> bool:
    if not hasattr(value, "toPython"):
        return False
    py = value.toPython()
    return isinstance(py, int) and not isinstance(py, bool)


# Confronta due numeri RDF con l'operatore ODRL (eq, neq, lt, gt, lteq, gteq).
def compare_numbers(left: Node, operator: Node, right: Node) -> bool:
    left_n = _to_decimal(left)
    right_n = _to_decimal(right)
    if operator == ODRL.eq:
        return left_n == right_n
    if operator == ODRL.neq:
        return left_n != right_n
    if operator == ODRL.lt:
        return left_n < right_n
    if operator == ODRL.gt:
        return left_n > right_n
    if operator == ODRL.lteq:
        return left_n <= right_n
    if operator == ODRL.gteq:
        return left_n >= right_n
    raise NotImplementedError(f"Numeric operator not supported yet: {operator}")


# Giorno della settimana in inglese (Monday…Sunday) da un RDF xsd:date o xsd:dateTime.
def weekday_from_datetime(value: Node) -> str:
    start, end = _to_time_window(value)
    # Una finestra su più giorni non ha un unico weekday.
    if start.date() != end.date():
        raise UncertainTimeWindowError(
            "weekday: the time window spans more than one day; "
            "without an exact instant or date the weekday is uncertain."
        )
    return _WEEKDAYS_EN[start.weekday()]


# Confronta due stringhe con l'operatore ODRL, ignorando maiuscole/minuscole.
def compare_strings(left: Node | str, operator: Node, right: Node | str) -> bool:
    left_s = _to_str(left).casefold()
    right_s = _to_str(right).casefold()
    if operator == ODRL.eq:
        return left_s == right_s
    if operator == ODRL.neq:
        return left_s != right_s
    raise NotImplementedError(f"String operator not supported yet: {operator}")


# Interpreta un valore RDF o una stringa Python come testo.
def _to_str(value: Node | str) -> str:
    if isinstance(value, str):
        return value
    py = value.toPython() if hasattr(value, "toPython") else value
    return str(py)


# Interpreta un valore RDF come Decimal (xsd:decimal, int o stringa numerica).
def _to_decimal(value: Node) -> Decimal:
    # rdflib: xsd:decimal → Decimal, gli altri tipi numerici → int/float/str
    py = value.toPython() if hasattr(value, "toPython") else value
    if isinstance(py, Decimal):
        return py
    return Decimal(str(py))

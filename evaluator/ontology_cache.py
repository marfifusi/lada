# Cache dei documenti JSON-LD remoti: memoria, poi file in .cache/json-ld, poi rete.

import copy
import json
from pathlib import Path
from urllib.parse import urlparse

# Cartella generata dal programma: .cache/json-ld/<host>/<path dell'URL>.
_CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache" / "json-ld"

# Documenti già letti in questa esecuzione, indicizzati dall'URL richiesto.
_memory: dict[str, dict | list] = {}

# True dopo la prima installazione sul parser JSON-LD di rdflib.
_installed = False

# source_to_json originale di rdflib, usata per i file locali e per il primo download.
_original = None


# Sostituisce source_to_json di rdflib così i context http(s) passano dalla cache.
# Se .cache o json-ld non ci sono, le crea prima di popolare la cache.
def install() -> None:
    global _installed, _original
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if _installed:
        return
    from rdflib.plugins.shared.jsonld import context as jsonld_context

    _original = jsonld_context.source_to_json
    jsonld_context.source_to_json = _source_to_json
    _installed = True


# Gli URL http(s) escono dalla cache; ogni altro source resta al parser originale.
def _source_to_json(source, fragment_id=None, extract_all_scripts=False):
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        return _load(source), None
    return _original(source, fragment_id, extract_all_scripts)


# JSON dell'URL: dalla memoria, dal file locale, oppure scaricato e salvato.
def _load(url: str) -> dict | list:
    cached = _memory.get(url)
    if cached is not None:
        return copy.deepcopy(cached)
    path = _local_path(url)
    if path.is_file():
        document = json.loads(path.read_text(encoding="utf-8"))
        _memory[url] = document
        return copy.deepcopy(document)
    document, _base = _original(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _memory[url] = document
    return copy.deepcopy(document)


# Percorso sotto .cache/json-ld ricavato da host e path dell'URL.
def _local_path(url: str) -> Path:
    parsed = urlparse(url)
    parts = [_segment(part) for part in parsed.path.split("/") if part]
    if not parts:
        parts = ["index.json"]
    path = (_CACHE_DIR / _segment(parsed.netloc) / Path(*parts)).resolve()
    if not path.is_relative_to(_CACHE_DIR.resolve()):
        raise ValueError(f"Ontology cache path escapes the cache directory: {url}")
    return path


# Rende un segmento di path sicuro come nome di file.
def _segment(part: str) -> str:
    cleaned = "".join("_" if c in '<>:"|?*' or ord(c) < 32 else c for c in part)
    if cleaned in ("", ".", ".."):
        return "_"
    return cleaned

"""
Regex-based Threat Intelligence extractor.

Extracts from raw text:
  - CVE references (CVE-YYYY-NNNNN)
  - MITRE ATT&CK technique IDs (Txxxx)
  - MD5, SHA1, SHA256 hashes
  - Defanged URLs / domains (e.g. example[.]com)

The defanging notation characters are read from Settings so they can be
configured in .env without touching this file.
"""

import re
from datetime import date

from .config import Settings
from .models import TIRecord

# ── Patterns that do NOT depend on Settings ──────────────────────────────────

_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
_MITRE_RE = re.compile(r"\bT\d{3,5}\b")
_MD5_RE = re.compile(r"\b[0-9a-fA-F]{32}\b")
_SHA1_RE = re.compile(r"\b[0-9a-fA-F]{40}\b")
_SHA256_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")


def _build_url_re(open_char: str, close_char: str) -> re.Pattern[str]:
    """Build defanged-URL regex from configurable bracket characters."""
    o = re.escape(open_char)
    c = re.escape(close_char)
    # Matches patterns like: example[.]com or sub[.]domain[.]tld
    return re.compile(rf"\b[\w{o}{c}\.]*{o}\.{c}[\w{o}{c}\.]*\b")


def _defang(url: str, open_char: str, close_char: str) -> str:
    """Strip defanging brackets to recover the real domain/URL."""
    return url.replace(open_char, "").replace(close_char, "")


def extract_ti(
    text: str,
    name: str,
    rule_id: int,
    whitelist: set[str],
    unique_sets: dict[str, set[str]],
    settings: Settings,
) -> TIRecord | None:
    """
    Parse *text* for TI indicators and return a TIRecord, or None if no
    signatures were found.

    unique_sets is mutated in-place so callers share cross-file deduplication.
    """
    url_re = _build_url_re(settings.defang_open, settings.defang_close)

    # ── Raw extraction ────────────────────────────────────────────────────────
    raw_refs = [m.upper() for m in _CVE_RE.findall(text)] + _MITRE_RE.findall(text)
    raw_md5 = _MD5_RE.findall(text)
    raw_sha1 = _SHA1_RE.findall(text)
    raw_sha256 = _SHA256_RE.findall(text)
    raw_urls = [
        _defang(m, settings.defang_open, settings.defang_close)
        for m in url_re.findall(text)
    ]

    # ── Cross-file deduplication + whitelist filtering ────────────────────────
    refs = _dedup(raw_refs, unique_sets["refs"])
    md5 = _dedup(raw_md5, unique_sets["md5"])
    sha1 = _dedup(raw_sha1, unique_sets["sha1"])
    sha256 = _dedup(raw_sha256, unique_sets["sha256"])
    urls = _dedup_with_whitelist(raw_urls, unique_sets["url"], whitelist)

    signatures = md5 + sha1 + sha256 + urls
    if not signatures:
        return None

    types: list[str] = []
    if md5 or sha1 or sha256:
        types.append("hash")
    if urls:
        types.append("url")

    return TIRecord(
        rule_id=rule_id,
        name=name,
        references=refs,
        area=settings.ti_area,
        types=types,
        agency=settings.site_tp,
        lastUpdate=date.today().isoformat(),
        user=settings.reg_user_id,
        signatures=signatures,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _dedup(values: list[str], seen: set[str]) -> list[str]:
    """Return values not already in *seen*, and add them to *seen*."""
    new = [v for v in values if v not in seen]
    # Preserve first-occurrence order while removing duplicates within this batch
    new = list(dict.fromkeys(new))
    seen.update(new)
    return new


def _dedup_with_whitelist(
    values: list[str], seen: set[str], whitelist: set[str]
) -> list[str]:
    """Deduplicate and drop any value that contains a whitelisted domain."""
    new = _dedup(values, seen)
    return [v for v in new if not any(w in v for w in whitelist)]

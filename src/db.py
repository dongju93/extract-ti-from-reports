"""
SQLite3-backed whitelist store.

The database file (whitelist.db) is created on first run and seeded with
the default domain list. Entries can be added/removed at any time using any
SQLite browser or the helper functions below.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("whitelist.db")

# Default domains considered benign (migrated from legacy/envs/whitelist.py)
_DEFAULT_DOMAINS: list[str] = [
    "trendmicro.com",
    "attack.mitre.org",
    "www.ithome.com.tw",
    "hitcon.org",
    "github.com",
    "securelist.com",
    "www.symantec.com",
    "researchcenter.paloaltonetworks.com",
    "twitter.com",
    "www.clearskysec.com",
    "www.fireeye.com",
    "unit42.paloaltonetworks.com",
    "www.welivesecurity.com",
    "en.wikipedia.org",
    "www.arbornetworks.com",
    "www.virustotal.com",
    "threatconnect.com",
    "www.mcafee.com",
    "blog.talosintelligence.com",
    "www.facebook.com",
    "www.proofpoint.com",
    "mcafee",
    "reuters.com",
    "crowdstrike",
    "msdn.microsoft.com",
    "www.nytimes.com",
    "www.youtube.com",
    "securityintelligence.com",
    "www.secureworks.com",
    "washingtonpost.com",
    "us-cert.gov",
    "kaspersky.com",
    "wikileaks.org",
    "dragos.com",
    "threatpost.com",
    "cve.mitre.org",
    "krebsonsecurity.com",
    "research.checkpoint.com",
    "ti.360.net",
    "www.microsoft.com",
    "technet.microsoft.com",
    "docs.microsoft.com",
    "portal.msrc.microsoft.com",
    "blogs.microsoft.com",
    "blogs.technet.microsoft.com",
    "support.microsoft.com",
    "cloudblogs.microsoft.com",
    "blogs.msdn.microsoft.com",
    "social.msdn.microsoft.com",
    "www.linkedin.com",
    "www.zdnet.com",
    "pwc.blogs.com",
    "www.bloomberg.com",
    "www.bbc.com",
    "www.wired.com",
    "citizenlab.org",
    "www.wsj.com",
    "arstechnica.com",
]


def init_db() -> None:
    """Create tables and seed defaults if not already present."""
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS url_whitelist (
                domain TEXT PRIMARY KEY
            )
            """
        )
        con.executemany(
            "INSERT OR IGNORE INTO url_whitelist (domain) VALUES (?)",
            [(d,) for d in _DEFAULT_DOMAINS],
        )
        con.commit()


def get_url_whitelist() -> set[str]:
    """Return the full set of whitelisted domains."""
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute("SELECT domain FROM url_whitelist").fetchall()
    return {row[0] for row in rows}


def add_domain(domain: str) -> None:
    """Add a domain to the whitelist (idempotent)."""
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT OR IGNORE INTO url_whitelist (domain) VALUES (?)", (domain,)
        )
        con.commit()


def remove_domain(domain: str) -> None:
    """Remove a domain from the whitelist."""
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM url_whitelist WHERE domain = ?", (domain,))
        con.commit()

# extract-ti-from-reports

Extract Threat Intelligence (TI) indicators from security report PDFs and plain-text files.

## What it does

Scans every `.pdf` and `.txt` file placed in `input/` and extracts:

| Indicator type          | Pattern matched                       |
| ----------------------- | ------------------------------------- |
| CVE references          | `CVE-YYYY-NNNNN`                      |
| MITRE ATT&CK IDs        | `Txxxx` / `Txxxxx`                    |
| MD5 hashes              | 32-char hex                           |
| SHA-1 hashes            | 40-char hex                           |
| SHA-256 hashes          | 64-char hex                           |
| Defanged URLs / domains | `example[.]com`, `sub[.]domain[.]tld` |

Indicators are deduplicated **across all processed files** in a single run. URLs that match whitelisted domains (security vendors, news sites, etc.) are silently dropped. The result is written to `output/ti_YYYYMMDD_HHMMSS.json`.

## Project layout

```
extract-ti-from-reports/
├── main.py               # Entry point — orchestrates the full pipeline
├── src/
│   ├── config.py         # pydantic-settings config loaded from .env
│   ├── db.py             # SQLite3 URL whitelist (whitelist.db)
│   ├── models.py         # TIRecord Pydantic output model
│   ├── pdf_converter.py  # PDF → plain text via pdfminer.six
│   └── ti_extractor.py   # Regex-based extraction + deduplication
├── input/                # Place report files here before running
├── output/               # Timestamped JSON output written here
├── whitelist.db          # Auto-created on first run
├── .env                  # Runtime configuration (copy from .env.example)
├── .env.example          # Configuration template
└── pyproject.toml
```

## Quick start

```bash
# 1. Install dependencies (requires uv)
uv sync

# 2. Copy and edit configuration
cp .env.example .env

# 3. Drop report files into input/
cp /path/to/report.pdf input/

# 4. Run
uv run main.py
```

Output appears in `output/ti_YYYYMMDD_HHMMSS.json`.

## Configuration (`.env`)

| Variable        | Default    | Description                                           |
| --------------- | ---------- | ----------------------------------------------------- |
| `DEFANG_OPEN`   | `[`        | Opening bracket used in defanged indicators           |
| `DEFANG_CLOSE`  | `]`        | Closing bracket used in defanged indicators           |
| `START_RULE_ID` | `10000000` | Starting value for auto-incremented `rule_id`         |
| `START_TI_NO`   | `1000`     | Starting value for `ti_no` counter                    |
| `TI_AREA`       | `endpoint` | Value written to the `area` field in output records   |
| `SITE_TP`       | `internal` | Value written to the `agency` field in output records |
| `REG_USER_ID`   | `admin`    | Value written to the `user` field in output records   |

## Output schema

Each entry in the output JSON array corresponds to one source file and follows `TIRecord`:

```json
{
  "rule_id": 10000000,
  "name": "report-filename-stem",
  "description": "",
  "references": ["CVE-2021-44228", "T1059"],
  "samples": "",
  "weight": 0.0,
  "area": "endpoint",
  "types": ["hash", "url"],
  "apply": true,
  "agency": "internal",
  "lastStatus": "added",
  "lastUpdate": "2026-02-22",
  "user": "admin",
  "signatures": [
    "d41d8cd98f00b204e9800998ecf8427e",
    "malicious-c2[.]example.com"
  ]
}
```

`signatures` contains hashes and defanged URLs. `references` holds CVE and MITRE ATT&CK identifiers. Files that yield zero signatures are skipped and not included in the output.

## Whitelist

`whitelist.db` is a SQLite3 database created automatically on first run. It is seeded with ~50 benign domains (security vendors, news outlets, Microsoft docs, etc.). Any extracted URL that contains a whitelisted domain substring is excluded from output.

To manage the whitelist programmatically:

```python
from src.db import add_domain, remove_domain

add_domain("example-vendor.com")
remove_domain("twitter.com")
```

Or use any SQLite browser to edit `whitelist.db` directly.

## Dependencies

| Package             | Purpose                            |
| ------------------- | ---------------------------------- |
| `pdfminer.six`      | PDF text extraction                |
| `pydantic`          | Output data model and validation   |
| `pydantic-settings` | `.env`-based configuration loading |

Requires Python ≥ 3.13.

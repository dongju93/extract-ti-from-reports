"""
Extract Threat Intelligence from security report PDFs.

Usage:
    uv run main.py

Place PDF (or TXT) report files in the input/ directory before running.
The extracted TI is written to output/ti_YYYYMMDD_HHMMSS.json.
"""

import json
from datetime import datetime
from pathlib import Path

from src.config import settings
from src.db import get_url_whitelist, init_db
from src.models import TIRecord
from src.pdf_converter import pdf_to_text
from src.ti_extractor import extract_ti


def main() -> None:
    # ── Initialise ────────────────────────────────────────────────────────────
    init_db()
    whitelist = get_url_whitelist()

    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Collect all report files (PDFs first, then plain-text)
    pdf_files = sorted(input_dir.glob("**/*.pdf"))
    txt_files = sorted(input_dir.glob("**/*.txt"))
    all_files = [(p, "pdf") for p in pdf_files] + [(p, "txt") for p in txt_files]

    if not all_files:
        print(
            "No report files found in input/. Place .pdf or .txt files there and re-run."
        )
        return

    # Shared sets for cross-file deduplication
    unique_sets: dict[str, set[str]] = {
        "refs": set(),
        "md5": set(),
        "sha1": set(),
        "sha256": set(),
        "url": set(),
    }

    records: list[TIRecord] = []
    rule_id = settings.start_rule_id

    # ── Process each file ─────────────────────────────────────────────────────
    for path, kind in all_files:
        print(f"  processing {path.name} …", end=" ", flush=True)

        if kind == "pdf":
            text = pdf_to_text(path)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")

        record = extract_ti(
            text=text,
            name=path.stem,
            rule_id=rule_id,
            whitelist=whitelist,
            unique_sets=unique_sets,
            settings=settings,
        )

        if record is None:
            print("no signatures found, skipped.")
            continue

        records.append(record)
        rule_id += 1
        print(f"extracted {len(record.signatures)} signatures.")

    # ── Write output ──────────────────────────────────────────────────────────
    if not records:
        print("No TI records produced. Nothing written.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"ti_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(
            [r.model_dump() for r in records],
            fh,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nDone. {len(records)} TI record(s) → {output_path}")


if __name__ == "__main__":
    main()

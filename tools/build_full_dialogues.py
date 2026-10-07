from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


PREFIX = "data/text/dialogues/english/"
PART_RE = re.compile(r"<dlgPart>(.*?)</dlgPart>", re.DOTALL)
ANSWER_RE = re.compile(r"<dlgAnsw>(.*?)</dlgAnsw>", re.DOTALL)


def inner_span(block: str, tag: str, base: int = 0):
    match = re.search(rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", block, re.DOTALL)
    if match is None:
        return None
    return base + match.start(1), base + match.end(1), match.group(1)


def active_target(row: dict[str, str]) -> str:
    return row.get("target_ja", "").strip() or row.get("target_draft", "").strip()


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sheet_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def replacement(text: str) -> str:
    return html.escape(text, quote=False)


def decode_xml(data: bytes) -> tuple[str, bool]:
    bom = data.startswith(b"\xef\xbb\xbf")
    return data.decode("utf-8-sig" if bom else "utf-8"), bom


def encode_xml(text: str, bom: bool) -> bytes:
    data = text.encode("utf-8")
    return b"\xef\xbb\xbf" + data if bom else data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    archive_path = Path(args.archive)
    csv_path = Path(args.csv)
    out_dir = Path(args.out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise SystemExit(f"output directory is not empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_file: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        if source_hash(row["source"]) != row["source_hash"]:
            raise SystemExit(f"source hash mismatch: {row['id']}")
        filename = Path(row["source_file"].split("::", 1)[-1]).name
        if row["id"] in by_file[filename]:
            raise SystemExit(f"duplicate ID: {row['id']}")
        by_file[filename][row["id"]] = row

    translated = 0
    untouched = 0
    missing_ids: list[str] = []
    source_mismatches: list[str] = []
    output_hashes: dict[str, str] = {}
    seen_ids: set[str] = set()

    with zipfile.ZipFile(archive_path) as package:
        names = sorted(
            name for name in package.namelist()
            if name.startswith(PREFIX) and name.lower().endswith(".xml")
        )
        for name in names:
            filename = Path(name).name
            file_rows = by_file.get(filename, {})
            original = package.read(name)
            text, bom = decode_xml(original)
            stem = Path(filename).stem
            replacements: list[tuple[int, int, str, str]] = []

            parts_start = text.find("<parts>")
            header = text if parts_start < 0 else text[:parts_start]
            header_speaker = inner_span(header, "def_speaker_name")
            default_speaker = html.unescape(header_speaker[2]) if header_speaker else ""
            default_targets: set[str] = set()

            for part_index, match in enumerate(PART_RE.finditer(text)):
                block = match.group(1)
                base = match.start(1)
                uid_span = inner_span(block, "UID")
                uid = uid_span[2].strip() if uid_span else f"index_{part_index}"

                part_speaker = inner_span(block, "speaker_name", base)
                effective_speaker = html.unescape(part_speaker[2]) if part_speaker and part_speaker[2] else default_speaker
                speaker_id = f"dialogue/{stem}/{uid}/speaker"
                speaker_row = file_rows.get(speaker_id)
                if effective_speaker.strip() and effective_speaker.strip().lower() != "none":
                    if speaker_row is None:
                        missing_ids.append(speaker_id)
                    else:
                        seen_ids.add(speaker_id)
                        if speaker_row["source"] != sheet_text(effective_speaker):
                            source_mismatches.append(speaker_id)
                        target = active_target(speaker_row)
                        if target:
                            if part_speaker:
                                replacements.append((part_speaker[0], part_speaker[1], replacement(target), speaker_id))
                            elif default_speaker == effective_speaker:
                                default_targets.add(target)
                            translated += 1
                        else:
                            untouched += 1

                body_span = inner_span(block, "npc_text", base)
                if body_span and html.unescape(body_span[2]).strip():
                    entry_id = f"dialogue/{stem}/{uid}/body"
                    row = file_rows.get(entry_id)
                    if row is None:
                        missing_ids.append(entry_id)
                    else:
                        seen_ids.add(entry_id)
                        if row["source"] != sheet_text(html.unescape(body_span[2])):
                            source_mismatches.append(entry_id)
                        target = active_target(row)
                        if target:
                            replacements.append((body_span[0], body_span[1], replacement(target), entry_id))
                            translated += 1
                        else:
                            untouched += 1

                for answer_index, answer_match in enumerate(ANSWER_RE.finditer(block)):
                    answer_block = answer_match.group(1)
                    answer_base = base + answer_match.start(1)
                    answer_span = inner_span(answer_block, "text", answer_base)
                    if not answer_span or not html.unescape(answer_span[2]).strip():
                        continue
                    entry_id = f"dialogue/{stem}/{uid}/choice_{answer_index}"
                    row = file_rows.get(entry_id)
                    if row is None:
                        missing_ids.append(entry_id)
                    else:
                        seen_ids.add(entry_id)
                        if row["source"] != sheet_text(html.unescape(answer_span[2])):
                            source_mismatches.append(entry_id)
                        target = active_target(row)
                        if target:
                            replacements.append((answer_span[0], answer_span[1], replacement(target), entry_id))
                            translated += 1
                        else:
                            untouched += 1

            if len(default_targets) > 1:
                raise SystemExit(f"inconsistent default speaker translation in {filename}: {sorted(default_targets)}")
            if header_speaker and default_targets:
                target = next(iter(default_targets))
                replacements.append((header_speaker[0], header_speaker[1], replacement(target), f"{stem}/header"))

            previous = len(text) + 1
            for start, end, value, entry_id in sorted(replacements, reverse=True):
                if end > previous:
                    raise SystemExit(f"overlapping replacement near {entry_id}")
                text = text[:start] + value + text[end:]
                previous = start

            output = out_dir / filename
            output.write_bytes(encode_xml(text, bom))
            output_hashes[filename] = hashlib.sha256(output.read_bytes()).hexdigest()

    csv_ids = {row["id"] for row in rows}
    unseen = sorted(csv_ids - seen_ids)
    report = {
        "status": "PASS" if not missing_ids and not source_mismatches and not unseen else "FAIL",
        "csv_rows": len(rows),
        "files_built": len(output_hashes),
        "translated_rows": translated,
        "source_rows_left_unchanged": untouched,
        "missing_ids": missing_ids[:50],
        "source_mismatches": source_mismatches[:50],
        "unseen_csv_ids": unseen[:50],
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "output_hashes": output_hashes,
    }
    (out_dir / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "output_hashes"}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

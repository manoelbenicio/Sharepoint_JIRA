#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".xml",
    ".ps1",
    ".sh",
}


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str  # "file" | "zip"
    needle: str
    location: str  # line number or zip member
    preview: str


def iter_text_files(root: Path) -> list[Path]:
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for filename in filenames:
            p = Path(dirpath) / filename
            if p.suffix.lower() in TEXT_EXTENSIONS:
                results.append(p)
    return results


def iter_zip_files(root: Path, patterns: list[str]) -> list[Path]:
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for filename in filenames:
            if not filename.lower().endswith(".zip"):
                continue
            if patterns and not any(fnmatch.fnmatch(filename, pat) for pat in patterns):
                continue
            results.append(Path(dirpath) / filename)
    return results


def search_in_text_file(file_path: Path, needles: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        findings.append(
            Finding(
                path=str(file_path),
                kind="file",
                needle="__READ_ERROR__",
                location="n/a",
                preview=str(e),
            )
        )
        return findings

    for i, line in enumerate(content, start=1):
        for needle in needles:
            if needle and needle in line:
                findings.append(
                    Finding(
                        path=str(file_path),
                        kind="file",
                        needle=needle,
                        location=f"line:{i}",
                        preview=line.strip()[:400],
                    )
                )
    return findings


def search_in_zip(zip_path: Path, needles: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                if not info.filename.lower().endswith("definition.json") and not info.filename.lower().endswith(
                    ".json"
                ):
                    continue
                try:
                    data = zf.read(info.filename).decode("utf-8", errors="replace").splitlines()
                except Exception as e:
                    findings.append(
                        Finding(
                            path=str(zip_path),
                            kind="zip",
                            needle="__READ_ERROR__",
                            location=info.filename,
                            preview=str(e),
                        )
                    )
                    continue
                for i, line in enumerate(data, start=1):
                    for needle in needles:
                        if needle and needle in line:
                            findings.append(
                                Finding(
                                    path=str(zip_path),
                                    kind="zip",
                                    needle=needle,
                                    location=f"{info.filename}:line:{i}",
                                    preview=line.strip()[:400],
                                )
                            )
    except zipfile.BadZipFile as e:
        findings.append(Finding(path=str(zip_path), kind="zip", needle="__BAD_ZIP__", location="n/a", preview=str(e)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit references to the queue list name/GUID across the repo (docs + flow zip exports). "
            "Use this before TD-008 cutover to guarantee no stale references remain."
        )
    )
    parser.add_argument("--root", default=".", help="Root directory to scan (default: .)")
    parser.add_argument(
        "--needles",
        nargs="+",
        default=["StatusReports_Queue"],
        help="Strings to search for (default: StatusReports_Queue)",
    )
    parser.add_argument(
        "--zip-pattern",
        action="append",
        default=[],
        help="Optional zip filename glob(s) to include (e.g., --zip-pattern 'flow*.zip'). If omitted, scans all zips.",
    )
    parser.add_argument(
        "--out",
        default="tools/reports/queue_list_reference_audit.json",
        help="Output JSON report path",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    needles = [n for n in args.needles if n]

    findings: list[Finding] = []
    for file_path in iter_text_files(root):
        findings.extend(search_in_text_file(file_path, needles))
    for zip_path in iter_zip_files(root, args.zip_pattern):
        findings.extend(search_in_zip(zip_path, needles))

    report = {
        "root": str(root),
        "needles": needles,
        "total_findings": len(findings),
        "findings": [f.__dict__ for f in findings],
    }
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote report: {out_path}")
    print(f"Total findings: {len(findings)}")
    if len(findings) > 0:
        print("Top findings (first 20):")
        for f in findings[:20]:
            print(f"- {f.kind}:{f.path} {f.location} needle={f.needle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


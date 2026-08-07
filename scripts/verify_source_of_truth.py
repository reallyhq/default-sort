#!/usr/bin/env python3
"""Verify that the public Default Sort files identify one current version."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CSV_FILE = ROOT / "default-sort.csv"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


readme = README.read_text(encoding="utf-8")

current = re.search(
    r"## Current approved specification\s+"
    r"\*\*v(?P<label>\d+\.\d+)\b.*?"
    r"\[Default-Sort-Algorithm-v(?P<link>\d+\.\d+)\.md\]"
    r"\(\./Default-Sort-Algorithm-v(?P<target>\d+\.\d+)\.md\)",
    readme,
    flags=re.DOTALL,
)
if current is None:
    fail("README does not identify the current approved specification.")

versions = {current.group("label"), current.group("link"), current.group("target")}
if len(versions) != 1:
    fail(f"README current-version label and link disagree: {sorted(versions)}")

version = current.group("label")
spec_path = ROOT / f"Default-Sort-Algorithm-v{version}.md"
if not spec_path.is_file():
    fail(f"README points to missing specification: {spec_path.name}")

if "single authoritative published specification" not in readme:
    fail("README does not identify the single authoritative published specification.")

if "[default-sort.csv](./default-sort.csv)" not in readme:
    fail("README does not link to default-sort.csv.")

spec = spec_path.read_text(encoding="utf-8")
spec_version = re.search(r"^\*\*Version:\*\*\s*(\d+\.\d+)\s*$", spec, flags=re.MULTILINE)
if spec_version is None:
    fail(f"{spec_path.name} does not contain a Version field.")
if spec_version.group(1) != version:
    fail(
        f"README identifies v{version}, but {spec_path.name} identifies "
        f"v{spec_version.group(1)}."
    )

with CSV_FILE.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

metadata_versions = [
    row.get("max_points_or_value", "").strip()
    for row in rows
    if row.get("section") == "metadata" and row.get("item") == "algorithm_version"
]
if metadata_versions != [version]:
    fail(
        "default-sort.csv must contain exactly one metadata algorithm_version "
        f"row equal to {version}; found {metadata_versions!r}."
    )

print(
    f"PASS: README.md, {spec_path.name}, and default-sort.csv "
    f"all identify algorithm v{version}."
)

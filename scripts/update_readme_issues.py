#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from pathlib import Path


START_MARKER = "AUTO-GENERATED-ISSUES-START"
END_MARKER = "AUTO-GENERATED-ISSUES-END"
TITLE_PREFIX = "#+title:"


def collect_issue_files(issues_dir: Path) -> list[Path]:
    files: list[Path] = []
    for org_file in issues_dir.glob("*/**/*.org"):
        if org_file.is_file():
            files.append(org_file)
    return files


def extract_title(org_file: Path) -> str:
    for line in org_file.read_text(encoding="utf-8").splitlines():
        if line.lower().startswith(TITLE_PREFIX):
            return line.split(":", 1)[1].strip()
    return ""


def build_issue_links(files: list[Path], repo_root: Path) -> str:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for org_file in files:
        year = org_file.parent.name
        grouped[year].append(org_file)

    lines: list[str] = []
    for year in sorted(grouped.keys(), reverse=True):
        lines.append(f"** {year}")
        year_files = sorted(grouped[year], key=lambda path: path.stem, reverse=True)
        for org_file in year_files:
            issue_number = org_file.stem
            rel_path = org_file.relative_to(repo_root).as_posix()
            issue_title = extract_title(org_file)
            label = f"Issue {issue_number}"
            if issue_title:
                label = f"{label} - {issue_title}"
            lines.append(f"- [[{rel_path}][{label}]]")
    return "\n".join(lines)


def replace_block(content: str, new_block: str) -> str:
    lines = content.splitlines()
    start_indices = [i for i, line in enumerate(lines) if START_MARKER in line]
    end_indices = [i for i, line in enumerate(lines) if END_MARKER in line]
    if not start_indices or not end_indices:
        raise ValueError("README missing auto-generated markers")

    start_index = start_indices[0]
    end_index = end_indices[0]
    if start_index >= end_index:
        raise ValueError("README marker order is invalid")

    new_lines = lines[: start_index + 1]
    if new_block:
        new_lines.extend(new_block.splitlines())
    new_lines.extend(lines[end_index:])
    return "\n".join(new_lines) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    readme_path = repo_root / "README.org"
    issues_dir = repo_root / "issues"

    issue_files = collect_issue_files(issues_dir)
    issue_links = build_issue_links(issue_files, repo_root)

    readme_content = readme_path.read_text(encoding="utf-8")
    updated_content = replace_block(readme_content, issue_links)

    readme_path.write_text(updated_content, encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


START_MARKER = "AUTO-GENERATED-ISSUES-START"
END_MARKER = "AUTO-GENERATED-ISSUES-END"


def collect_issue_files(issues_dir: Path) -> list[Path]:
    files: list[Path] = []
    for org_file in issues_dir.glob("*/**/*.org"):
        if org_file.is_file():
            files.append(org_file)
    return sorted(files, key=lambda path: (path.parent.name, path.stem))


def build_issue_links(files: list[Path], repo_root: Path) -> str:
    lines: list[str] = []
    for org_file in files:
        issue_number = org_file.stem
        rel_path = org_file.relative_to(repo_root).as_posix()
        lines.append(f"- [[{rel_path}][Issue {issue_number}]]")
    return "\n".join(lines)


def replace_block(content: str, new_block: str) -> str:
    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("README missing auto-generated markers")

    start_index = content.index(START_MARKER) + len(START_MARKER)
    end_index = content.index(END_MARKER)
    return content[:start_index] + "\n" + new_block + "\n" + content[end_index:]


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

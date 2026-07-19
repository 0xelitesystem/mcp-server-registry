#!/usr/bin/env python3
"""Generate and validate the MCP server index."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SCALAR_PATTERN = re.compile(r"^(?P<key>[a-z_][a-z0-9_]*):(?:[ \t]*(?P<value>.*))?$")
LIST_ITEM_PATTERN = re.compile(r"^ +-[ \t]+(?P<value>.+?)\s*$")
SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CONTROL_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f\u2028\u2029]")
REQUIRED_FIELDS = ("name", "slug", "language", "transport", "auth", "status")
CATEGORY_DESCRIPTIONS = (
    ("database", "query and manipulate databases"),
    ("filesystem", "read/write local files"),
    ("version-control", "git, GitHub, GitLab, etc."),
    ("communication", "Slack, email, chat platforms"),
    ("search", "web search, code search"),
    ("productivity", "calendars, notes, task managers"),
    ("development", "dev tooling, CI, deployment"),
    ("reasoning", "meta-tools for structured AI thinking"),
    ("web", "fetch URLs, scrape, browse"),
    ("ai", "wraps other AI services"),
    ("data", "data warehouses, analytics, formats"),
    ("finance", "banking, payments, accounting"),
    ("other", "utilities that don't fit elsewhere"),
)
ALLOWED_CATEGORIES = frozenset(name for name, _ in CATEGORY_DESCRIPTIONS)
ALLOWED_VALUES = {
    "auth": frozenset(("none", "oauth", "api-key", "bearer-token", "custom")),
    "status": frozenset(("stable", "beta", "alpha", "unmaintained")),
    "transport": frozenset(("stdio", "sse", "http")),
}
LANGUAGE_LABELS = {
    "javascript": "JavaScript",
    "node": "Node",
    "typescript": "TypeScript",
}


class RegistryFormatError(ValueError):
    """Report an invalid server entry."""


@dataclass(frozen=True)
class ServerEntry:
    """Fields used by the generated server table."""

    name: str
    slug: str
    language: str
    transport: str
    auth: str
    status: str
    categories: tuple[str, ...]
    relative_path: str


def _strip_comment(value: str) -> str:
    """Remove an unquoted inline YAML comment from a scalar."""
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in {"'", '"'}:
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if character == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _parse_scalar(raw_value: str, path: Path, line_number: int) -> str:
    """Parse the plain or quoted scalar forms used by registry fields."""
    value = _strip_comment(raw_value).strip()
    if not value:
        raise RegistryFormatError(f"{path}:{line_number}: expected a scalar value")
    if value[0] == '"':
        if len(value) < 2 or value[-1] != '"':
            raise RegistryFormatError(f"{path}:{line_number}: unterminated quoted scalar")
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise RegistryFormatError(f"{path}:{line_number}: invalid quoted scalar") from error
        if not isinstance(decoded, str):
            raise RegistryFormatError(f"{path}:{line_number}: expected a string scalar")
        value = decoded
    elif value[0] == "'":
        if len(value) < 2 or value[-1] != "'":
            raise RegistryFormatError(f"{path}:{line_number}: unterminated quoted scalar")
        inner = value[1:-1]
        parts: list[str] = []
        index = 0
        while index < len(inner):
            if inner[index] != "'":
                parts.append(inner[index])
                index += 1
                continue
            if index + 1 >= len(inner) or inner[index + 1] != "'":
                raise RegistryFormatError(f"{path}:{line_number}: invalid quoted scalar")
            parts.append("'")
            index += 2
        value = "".join(parts)
    if not value:
        raise RegistryFormatError(f"{path}:{line_number}: scalar value cannot be empty")
    return value


def parse_server(path: Path, root: Path) -> ServerEntry:
    """Read the table fields from one server YAML entry."""
    values: dict[str, str] = {}
    categories: list[str] = []
    active_list: str | None = None

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace():
            indentation = line[: len(line) - len(line.lstrip(" \t"))]
            if "\t" in indentation:
                raise RegistryFormatError(
                    f"{path}:{line_number}: tabs cannot be used for YAML indentation"
                )
            if active_list == "categories":
                item = LIST_ITEM_PATTERN.match(line)
                if item is not None:
                    categories.append(_parse_scalar(item.group("value"), path, line_number))
            continue

        field = SCALAR_PATTERN.match(line)
        if field is None:
            active_list = None
            continue
        key = field.group("key")
        raw_value = _strip_comment(field.group("value") or "").strip()
        active_list = key if not raw_value else None
        if key in REQUIRED_FIELDS:
            values[key] = _parse_scalar(raw_value, path, line_number)

    missing = [field for field in REQUIRED_FIELDS if field not in values]
    if missing:
        raise RegistryFormatError(f"{path}: missing required table fields: {', '.join(missing)}")
    if not categories:
        raise RegistryFormatError(f"{path}: categories must contain at least one item")

    slug = values["slug"]
    if SLUG_PATTERN.fullmatch(slug) is None:
        raise RegistryFormatError(f"{path}: invalid slug {slug!r}")
    if path.name != f"{slug}.yaml":
        raise RegistryFormatError(f"{path}: filename must match slug {slug!r}")

    unsupported = sorted(set(categories) - ALLOWED_CATEGORIES)
    if unsupported:
        raise RegistryFormatError(f"{path}: unsupported categories: {', '.join(unsupported)}")
    for field, allowed_values in ALLOWED_VALUES.items():
        if values[field] not in allowed_values:
            allowed = ", ".join(sorted(allowed_values))
            raise RegistryFormatError(
                f"{path}: unsupported {field} {values[field]!r}; expected one of: {allowed}"
            )

    return ServerEntry(
        name=values["name"],
        slug=slug,
        language=values["language"],
        transport=values["transport"],
        auth=values["auth"],
        status=values["status"],
        categories=tuple(categories),
        relative_path=path.relative_to(root).as_posix(),
    )


def load_servers(root: Path) -> list[ServerEntry]:
    """Load all server entries and reject duplicate identities."""
    entries = [parse_server(path, root) for path in sorted((root / "servers").glob("*.yaml"))]
    seen_names: set[str] = set()
    seen_slugs: set[str] = set()
    for entry in entries:
        normalized_name = entry.name.casefold()
        if normalized_name in seen_names:
            raise RegistryFormatError(f"duplicate server name: {entry.name}")
        if entry.slug in seen_slugs:
            raise RegistryFormatError(f"duplicate server slug: {entry.slug}")
        seen_names.add(normalized_name)
        seen_slugs.add(entry.slug)
    return sorted(entries, key=lambda entry: (entry.name.casefold(), entry.slug))


def _escape_text(value: str) -> str:
    escaped = CONTROL_PATTERN.sub(" ", value).replace("\\", "\\\\")
    escaped = escaped.replace("<", "&lt;").replace(">", "&gt;")
    for character in ("|", "[", "]", "`"):
        escaped = escaped.replace(character, f"\\{character}")
    return escaped


def _language_label(value: str) -> str:
    return LANGUAGE_LABELS.get(value.casefold(), value.capitalize())


def render_servers(entries: list[ServerEntry]) -> str:
    """Render the complete deterministic server index."""
    lines = [
        "# Servers",
        "",
        "Auto-generated table from `servers/*.yaml`. To regenerate after adding entries:",
        "",
        "```bash",
        "python3 scripts/generate_servers_md.py",
        "```",
        "",
        "| Server | Lang | Transport | Auth | Status | Categories |",
        "|---|---|---|---|---|---|",
    ]
    for entry in entries:
        cells = (
            f"[{_escape_text(entry.name)}]({entry.relative_path})",
            _escape_text(_language_label(entry.language)),
            _escape_text(entry.transport),
            _escape_text(entry.auth),
            _escape_text(entry.status),
            _escape_text(", ".join(entry.categories)),
        )
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(("", "## Categories", ""))
    for category, description in CATEGORY_DESCRIPTIONS:
        lines.append(f"- **{category}**, {description}")

    lines.extend(
        (
            "",
            "## Filters",
            "",
            "To filter by attribute, search this file:",
            "",
            '- All Python servers: search "Python"',
            '- All servers requiring auth: search "api-key" OR "bearer-token" OR "oauth"',
            '- All search-related: search "search,"',
            "",
        )
    )
    return "\n".join(lines)


def update_index(root: Path, check: bool) -> bool:
    """Write the index or verify that the committed index is current."""
    target = root / "SERVERS.md"
    rendered = render_servers(load_servers(root))
    if check:
        return target.is_file() and target.read_text(encoding="utf-8") == rendered
    target.write_text(rendered, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when SERVERS.md is stale")
    arguments = parser.parse_args()
    try:
        current = update_index(ROOT, arguments.check)
    except RegistryFormatError as error:
        print(error, file=sys.stderr)
        return 1
    if not current:
        print("SERVERS.md is stale. Run python3 scripts/generate_servers_md.py.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from scripts.generate_servers_md import (
    RegistryFormatError,
    load_servers,
    parse_server,
    render_servers,
    update_index,
)


def write_server(root: Path, slug: str, name: str, categories: tuple[str, ...]) -> Path:
    path = root / "servers" / f"{slug}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    category_lines = "\n".join(f"  - {category}" for category in categories)
    path.write_text(
        "\n".join(
            (
                f"name: {name}",
                f"slug: {slug}",
                "language: python",
                "transport: stdio",
                "auth: none",
                "status: stable",
                "categories:",
                category_lines,
                "",
            )
        ),
        encoding="utf-8",
    )
    return path


class ServerIndexTests(unittest.TestCase):
    def test_current_registry_index_is_generated(self) -> None:
        root = Path(__file__).resolve().parents[1]

        self.assertEqual(
            (root / "SERVERS.md").read_text(encoding="utf-8"),
            render_servers(load_servers(root)),
        )

    def test_entries_are_sorted_by_name(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_server(root, "zulu", "Zulu", ("other",))
            write_server(root, "alpha", "Alpha", ("data", "search"))

            entries = load_servers(root)

            self.assertEqual([entry.slug for entry in entries], ["alpha", "zulu"])
            self.assertIn(
                "| [Alpha](servers/alpha.yaml) | Python | stdio | none | stable | data, search |",
                render_servers(entries),
            )

    def test_typescript_uses_canonical_casing(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "typed", "Typed", ("development",))
            contents = path.read_text(encoding="utf-8").replace(
                "language: python", "language: typescript"
            )
            path.write_text(contents, encoding="utf-8")

            self.assertIn("| TypeScript |", render_servers(load_servers(root)))

    def test_markdown_control_characters_are_escaped(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(
                root,
                "escaped",
                "Good](https://attacker.example) [Bad",
                ("other",),
            )
            contents = path.read_text(encoding="utf-8").replace(
                "language: python", "language: <script>|`code`"
            )
            path.write_text(contents, encoding="utf-8")

            rendered = render_servers(load_servers(root))

            self.assertIsNone(re.search(r"(?<!\\)\]\(https://attacker\.example\)", rendered))
            self.assertIn(r"Good\](https://attacker.example) \[Bad", rendered)
            self.assertIn(r"&lt;script&gt;\|\`code\`", rendered)

    def test_comment_after_categories_key_is_supported(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "commented", "Commented", ("data",))
            contents = path.read_text(encoding="utf-8").replace(
                "categories:\n", "categories: # allowed values follow\n"
            )
            path.write_text(contents, encoding="utf-8")

            self.assertEqual(parse_server(path, root).categories, ("data",))

    def test_unterminated_quoted_scalar_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "quoted", "Quoted", ("other",))
            contents = path.read_text(encoding="utf-8").replace(
                "name: Quoted", 'name: "unterminated'
            )
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(RegistryFormatError, "unterminated quoted scalar"):
                parse_server(path, root)

    def test_invalid_single_quoted_scalar_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "quoted", "Quoted", ("other",))
            contents = path.read_text(encoding="utf-8").replace(
                "name: Quoted", "name: 'foo'bar'"
            )
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(RegistryFormatError, "invalid quoted scalar"):
                parse_server(path, root)

    def test_decoded_control_characters_cannot_break_table_rows(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "control", "Control", ("other",))
            contents = path.read_text(encoding="utf-8").replace(
                "name: Control", r'name: "Control\r# Injected"'
            )
            path.write_text(contents, encoding="utf-8")

            rendered = render_servers(load_servers(root))

            self.assertNotIn("\r", rendered)
            self.assertNotIn("\n# Injected", rendered)
            self.assertIn("[Control # Injected](servers/control.yaml)", rendered)

    def test_missing_required_field_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "incomplete", "Incomplete", ("other",))
            contents = path.read_text(encoding="utf-8").replace("auth: none\n", "")
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(RegistryFormatError, "missing required table fields: auth"):
                parse_server(path, root)

    def test_invalid_category_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "invalid", "Invalid", ("not-a-category",))

            with self.assertRaisesRegex(RegistryFormatError, "unsupported categories: not-a-category"):
                parse_server(path, root)

    def test_invalid_enum_value_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "invalid", "Invalid", ("other",))
            contents = path.read_text(encoding="utf-8").replace(
                "transport: stdio", "transport: typo"
            )
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(RegistryFormatError, "unsupported transport 'typo'"):
                parse_server(path, root)

    def test_tab_indentation_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_server(root, "tabbed", "Tabbed", ("other",))
            contents = path.read_text(encoding="utf-8").replace(
                "  - other", "\t- other"
            )
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(
                RegistryFormatError, "tabs cannot be used for YAML indentation"
            ):
                parse_server(path, root)

    def test_check_detects_and_repairs_stale_index(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_server(root, "example", "Example", ("other",))
            (root / "SERVERS.md").write_text("stale\n", encoding="utf-8")

            self.assertFalse(update_index(root, check=True))
            self.assertTrue(update_index(root, check=False))
            self.assertTrue(update_index(root, check=True))


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
from textwrap import dedent

import frontmatter

from vault_migrator import migrate_notes


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Using dedent here ensures leading spaces from the code's indentation
    # don't end up in the actual file content.
    path.write_text(dedent(content), encoding="utf-8")


def read_yaml_keys(path: Path):
    post = frontmatter.load(str(path))
    return list(post.metadata.keys()), post


def test_books_file_metadata_order(tmp_path: Path):
    src_root = tmp_path / "Fiction"
    dest_root = tmp_path / "Out"
    book_file = src_root / "Books" / "Some Author" / "note.md"

    # DO NOT INDENT THESE LINES.
    # They must start at the very beginning of the line in your editor.
    content = """---
tags:
  - horror
---

## Inline metadata
[author:: [[Some Author]]]
[started:: 2026-03-01]
[personal-rating:: 4]

Body text here.
"""
    write_markdown(book_file, content)

    migrate_notes(src_root, dest_root)

    out_file = dest_root / "Books" / "Some Author" / "note.md"
    assert out_file.exists()
    keys, post = read_yaml_keys(out_file)

    expected_order = [
        "author",
        "started",
        "personal-rating",
        "image",
        "type",
        "tags",
    ]

    assert keys == expected_order


def test_movies_file_and_empty(tmp_path: Path):
    src_root = tmp_path / "Fiction"
    dest_root = tmp_path / "Out"

    mov_file = src_root / "Movies" / "film.md"
    write_markdown(
        mov_file,
        """\
        ## Inline metadata
        [director:: John Doe]
        [personal-rating:: 5]
        
        Some movie notes.
        """,
    )

    empty_file = src_root / "Books" / "empty.md"
    write_markdown(empty_file, "")

    migrate_notes(src_root, dest_root)

    out_mov = dest_root / "Movies" / "film.md"
    assert out_mov.exists()
    keys, post = read_yaml_keys(out_mov)

    # Verification based on SECTION_CONFIG['Movies']
    assert keys[0] == "director"
    assert post.metadata["type"] == "movie"
    assert post.metadata["personal-rating"] == "5"

    out_empty = dest_root / "Books" / "empty.md"
    assert out_empty.exists()


def test_tree_structure_preserved(tmp_path: Path):
    src_root = tmp_path / "Fiction"
    dest_root = tmp_path / "Out"
    deep_file = src_root / "Books" / "A" / "B" / "C" / "nested.md"
    write_markdown(deep_file, "Content")

    migrate_notes(src_root, dest_root)

    out_deep = dest_root / "Books" / "A" / "B" / "C" / "nested.md"
    assert out_deep.exists()

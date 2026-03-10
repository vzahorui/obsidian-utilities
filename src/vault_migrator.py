import os
import re
import argparse
from pathlib import Path
import frontmatter

# Default roots; can be overridden with command-line arguments
SOURCE_ROOT_DEFAULT = Path("data/Fiction")
DEST_ROOT_DEFAULT = Path("data/Thoughts/12 Fiction")

# Configuration per section (first directory under source root)
SECTION_CONFIG = {
    "Books": {
        "type": "book-summary",
        "order": [
            "author",
            "started",
            "finished",
            "series",
            "number-in-series",
            "coauthor",
            "published",
            "personal-rating",
            "image",
            "type",
            "tags",
        ],
        "defaults": {"image": ""},
    },
    "Movies": {
        "type": "movie",
        "order": [
            "director",
            "watched",
            "series",
            "country",
            "release-year",
            "personal-rating",
            "image",
            "type",
            "tags",
        ],
        "defaults": {"image": ""},
    },
    "Series": {
        "type": "series",
        "order": [
            "director",
            "started",
            "finished",
            "series",
            "season",
            "country",
            "release-year",
            "personal-rating",
            "image",
            "type",
            "tags",
        ],
        "defaults": {"image": ""},
    },
}

# The inline metadata pattern. Handles: Key:: value, [Key:: value], and leading spaces.
INLINE_REGEX = r"^\s*\[?([\w-]+)::\s*(.*?)\]?$"

def migrate_notes(source_root: Path, dest_root: Path) -> None:
    """Traverse source_root for markdown files. If '## Inline metadata' is found,
    migrate metadata to YAML. Otherwise, copy the file unchanged.
    """
    for src_path in source_root.rglob("*.md"):
        if not src_path.is_file():
            continue

        rel_path = src_path.relative_to(source_root)
        dest_path = dest_root.joinpath(rel_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with src_path.open("r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Flag to track if we actually hit the migration trigger
        migration_triggered = False
        new_lines: list[str] = []
        seen_header = False
        
        # 1. Scan for the header and extract
        for line in post.content.splitlines():
            if not seen_header and line.strip().lower() == "## inline metadata":
                seen_header = True
                migration_triggered = True # We found it!
                continue
            
            if seen_header:
                match = re.match(INLINE_REGEX, line)
                if match:
                    key = match.group(1).strip().lower()
                    value = match.group(2).strip()
                    post.metadata.setdefault(key, value)
                    continue
                if line.strip() == "":
                    continue
                else:
                    seen_header = False
            
            new_lines.append(line)

        # 2. Conditional Execution
        if migration_triggered:
            # Only apply transformation logic if the header was found
            post.content = "\n".join(new_lines).strip()

            parts = rel_path.parts
            section = parts[0] if parts else ""
            config = SECTION_CONFIG.get(section, {})

            # Apply defaults and type
            defaults = config.get("defaults", {})
            for k, v in defaults.items():
                post.metadata.setdefault(k, v)

            if "type" not in post.metadata and config.get("type"):
                post.metadata["type"] = config["type"]

            # Reorder keys
            order_list = config.get("order", [])
            original_metadata = post.metadata.copy()
            post.metadata = {}
            for key in order_list:
                if key in original_metadata:
                    post.metadata[key] = original_metadata.pop(key)
            post.metadata.update(original_metadata)

            # Save modified version
            with dest_path.open("wb") as f:
                frontmatter.dump(post, f, sort_keys=False)
            print(f"Migrated: {src_path} -> {dest_path}")
        else:
            # No inline metadata found, perform a clean bit-for-bit copy
            import shutil
            shutil.copy2(src_path, dest_path)
            print(f"Copied (Unchanged): {src_path} -> {dest_path}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate Obsidian inline metadata into YAML frontmatter."
    )
    parser.add_argument(
        "--source", "-s", type=Path, default=SOURCE_ROOT_DEFAULT,
        help="Source root directory (walked recursively)."
    )
    parser.add_argument(
        "--dest", "-d", type=Path, default=DEST_ROOT_DEFAULT,
        help="Destination root directory."
    )
    args = parser.parse_args()
    migrate_notes(args.source, args.dest)

if __name__ == "__main__":
    main()

# Obsidian Utilities

A collection of Python-based tools designed to automate and enhance Obsidian vault management, specifically focused on data-heavy workflows and metadata transitions.

## Current Tools

### 1. Vault Migrator (`vault_migrator.py`)
This utility facilitates the migration of notes between vaults, specifically designed to transition from legacy **Dataview inline metadata** to native **Obsidian Properties (YAML)**.

**Key Features:**
* **Metadata Transformation:** Converts `Key:: Value` or `[Key:: Value]` inline strings into structured YAML frontmatter.
* **Property Standardizing:** Enforces specific property ordering (e.g., author, started, finished) and ensures consistent types (e.g., adding `image` properties for covers).
* **Schema Support:** Includes specialized configurations for **Books**, **Movies**, and **Series**.
* **Bulk Processing:** Recursively walks through source directories (like a "Fiction" vault) and mirrors the structure in a destination vault ("Thoughts").

## Getting Started

This project uses [Pixi](https://pixi.sh) for environment management.

### Installation
```bash
# Clone the repository
git clone [https://github.com/vzahorui/obsidian-utilities.git](https://github.com/vzahorui/obsidian-utilities.git)
cd obsidian-utilities

# Install dependencies and set up the environment
pixi install
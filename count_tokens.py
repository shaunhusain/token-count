#!/usr/bin/env python3
"""
Count tokens in source files within a directory using tiktoken.
Respects .gitignore files and scans common source file types.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Optional

import tiktoken
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

# Source file extensions to scan
SOURCE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JSX",
    ".tsx": "TSX",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".r": "R",
    ".R": "R",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".lua": "Lua",
    ".pl": "Perl",
    ".pm": "Perl Module",
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".fish": "Fish",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".xml": "XML",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".conf": "Config",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir Script",
    ".erl": "Erlang",
    ".hs": "Haskell",
    ".ml": "OCaml",
    ".clj": "Clojure",
    ".lisp": "Lisp",
    ".el": "Emacs Lisp",
    ".vim": "Vim Script",
    ".tf": "Terraform",
    ".proto": "Protocol Buffers",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    ".dockerfile": "Dockerfile",
    ".makefile": "Makefile",
}

# Filenames (no extension) to also scan
SOURCE_FILENAMES = {
    "Makefile", "Dockerfile", "Jenkinsfile", "Vagrantfile",
    "Gemfile", "Rakefile", "Procfile", ".env.example",
}

# Directories to always skip (dependencies, build outputs, caches)
IGNORED_DIRS = {
    # JS / Node
    "node_modules", "bower_components",
    # Build outputs
    "dist", "build", "out", "output", "_build",
    # Java / JVM
    "target", ".gradle", ".mvn",
    # Python
    ".venv", "venv", "env", "__pycache__", ".eggs", "*.egg-info",
    ".tox", ".nox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    # Angular / frontend caches
    ".angular", ".next", ".nuxt", ".svelte-kit", ".turbo",
    # Rust
    "target",
    # Go
    "vendor",
    # .NET
    "bin", "obj", "packages",
    # iOS / macOS
    "Pods", "DerivedData",
    # Coverage & test artifacts
    "coverage", ".nyc_output", "htmlcov",
    # IDE / editor
    ".idea", ".vs", ".vscode",
    # Version control
    ".git", ".hg", ".svn",
    # Misc
    ".cache", ".parcel-cache", ".webpack", "tmp", "temp",
    ".terraform", ".serverless",
}


def load_gitignore_spec(directory: Path) -> Optional[PathSpec]:
    """Load .gitignore patterns from directory and all parent dirs up to root."""
    patterns = []
    gitignore = directory / ".gitignore"
    if gitignore.is_file():
        patterns.extend(gitignore.read_text(errors="ignore").splitlines())
    return PathSpec.from_lines(GitWildMatchPattern, patterns) if patterns else None


def is_source_file(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in SOURCE_EXTENSIONS or path.suffix in SOURCE_EXTENSIONS:
        return True
    if path.name in SOURCE_FILENAMES:
        return True
    return False


def count_tokens_in_file(filepath: Path, encoder: tiktoken.Encoding) -> int:
    try:
        text = filepath.read_text(errors="ignore")
        return len(encoder.encode(text))
    except Exception:
        return 0


def main():
    parser = argparse.ArgumentParser(description="Count tokens in source files using tiktoken.")
    parser.add_argument("folder", help="Path to the folder to scan")
    parser.add_argument("--encoding", default="cl100k_base",
                        help="tiktoken encoding name (default: cl100k_base)")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"Error: '{args.folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    encoder = tiktoken.get_encoding(args.encoding)
    spec = load_gitignore_spec(folder)

    print(f"Scanning: {folder}")
    print(f"Encoding: {args.encoding}")
    print()
    print("Source file types scanned:")
    seen = sorted(set(SOURCE_EXTENSIONS.values()))
    for lang in seen:
        exts = [e for e, l in SOURCE_EXTENSIONS.items() if l == lang]
        print(f"  {lang}: {', '.join(exts)}")
    print(f"  Special filenames: {', '.join(sorted(SOURCE_FILENAMES))}")
    print()

    total_tokens = 0
    file_count = 0
    type_counts: Dict[str, int] = {}

    for root, dirs, files in os.walk(folder):
        rel_root = Path(root).relative_to(folder)
        # Filter dirs in-place: skip ignored dirs and gitignore matches
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        if spec:
            dirs[:] = [d for d in dirs if not spec.match_file(str(rel_root / d) + "/")]

        for fname in files:
            rel_path = str(rel_root / fname)
            if spec and spec.match_file(rel_path):
                continue
            fpath = Path(root) / fname
            if not is_source_file(fpath):
                continue
            tokens = count_tokens_in_file(fpath, encoder)
            total_tokens += tokens
            file_count += 1
            ext = fpath.suffix.lower() if fpath.suffix in SOURCE_EXTENSIONS or fpath.suffix.lower() in SOURCE_EXTENSIONS else fpath.name
            lang = SOURCE_EXTENSIONS.get(fpath.suffix, SOURCE_EXTENSIONS.get(fpath.suffix.lower(), fpath.name))
            type_counts[lang] = type_counts.get(lang, 0) + tokens
            print(f"  {rel_path}: {tokens:,} tokens")

    print()
    print("=== Summary ===")
    print(f"Files scanned: {file_count}")
    for lang, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {lang}: {count:,} tokens")
    print(f"Total tokens: {total_tokens:,}")


if __name__ == "__main__":
    main()

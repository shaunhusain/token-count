# token-count

Count tokens in source files using [tiktoken](https://github.com/openai/tiktoken). Respects `.gitignore` and scans 60+ source file types.

## Quick Start

### Option A: Docker (recommended)

```bash
# Build the image
docker build -t token-count .

# Count tokens in a local folder
docker run --rm -v /path/to/your/project:/workspace token-count
```

To use a different tiktoken encoding:

```bash
docker run --rm -v /path/to/your/project:/workspace token-count /workspace --encoding o200k_base
```

### Option B: Local Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python count_tokens.py /path/to/folder
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--encoding` | `cl100k_base` | tiktoken encoding (`cl100k_base`, `o200k_base`, `p50k_base`, etc.) |

## Supported File Types

The tool scans files with these extensions:

**Languages:** Python, JavaScript, TypeScript, JSX, TSX, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, R, Objective-C, Lua, Perl, Dart, Elixir, Erlang, Haskell, OCaml, Clojure, Lisp

**Shell:** Bash, Zsh, Fish, PowerShell, Shell

**Web:** HTML, CSS, SCSS, Sass, Less, Vue, Svelte

**Data/Config:** JSON, YAML, TOML, INI, XML, SQL, GraphQL, Protocol Buffers

**DevOps/Infra:** Terraform, Dockerfile, Makefile

**Docs:** Markdown, reStructuredText, Text

**Special filenames:** `Makefile`, `Dockerfile`, `Jenkinsfile`, `Vagrantfile`, `Gemfile`, `Rakefile`, `Procfile`, `.env.example`

## Automatically Ignored Directories

The following directories are always skipped (in addition to `.gitignore` rules):

- **JS/Node:** `node_modules`, `bower_components`
- **Build outputs:** `dist`, `build`, `out`, `output`, `_build`
- **Java/JVM:** `target`, `.gradle`, `.mvn`
- **Python:** `.venv`, `venv`, `env`, `__pycache__`, `.eggs`, `.tox`, `.nox`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`
- **Frontend caches:** `.angular`, `.next`, `.nuxt`, `.svelte-kit`, `.turbo`, `.parcel-cache`, `.webpack`
- **Rust:** `target`
- **Go:** `vendor`
- **.NET:** `bin`, `obj`, `packages`
- **iOS/macOS:** `Pods`, `DerivedData`
- **Coverage:** `coverage`, `.nyc_output`, `htmlcov`
- **IDE/Editor:** `.idea`, `.vs`, `.vscode`
- **VCS:** `.git`, `.hg`, `.svn`
- **Misc:** `.cache`, `tmp`, `temp`, `.terraform`, `.serverless`
# token-count

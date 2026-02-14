# AI Session Cleaner

Desktop GUI app to browse, preview, and bulk-delete chat session files from AI coding tools.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Why This Tool?

Most AI coding assistants (Factory/Droid, Claude Code, Codex CLI, OpenCode, etc.) store conversation sessions locally but **do not provide a built-in way to delete or manage them**. Over time, hundreds of session files accumulate on disk -- many of them blank or abandoned -- with no easy way to browse, filter, or clean them up.

This tool was built to solve that problem: a single app that lets you manage sessions across **multiple AI tools** in one place. Currently supports 4 sources, with more planned as new tools emerge.

## Screenshot

![AI Session Cleaner](screenshots/preview-ui.png)

## Supported Tools

| Tool | Session Location | Format |
|---|---|---|
| **Factory (Droid)** | `~/.factory/sessions/` | JSONL |
| **Claude Code** | `~/.claude/projects/` | JSONL |
| **Codex CLI** | `~/.codex/sessions/` | JSONL |
| **OpenCode** | `~/.local/share/opencode/storage/` | JSON |

## Features

- **Switch between tools** with one click
- **Search** by title, project, or date
- **Filter** by project, time range
- **Sort** by date, name, size, project
- **Group by** project, date, month, or age
- **Preview** conversation content (user/assistant messages)
- **Color-coded** projects for quick visual identification
- **Detect empty/blank sessions** (no messages, "New Session" without conversation)
- **Bulk delete** - select by age (>7/30/90 days), select all blank, or manual multi-select
- **Auto-cleanup** empty folders after deletion
- **Stats dashboard** - total sessions, projects, disk usage, blank count

## Requirements

- Python 3.8 or later
- `tkinter` (included with Python on Windows and most Linux distros)

No third-party packages needed. All imports are from the Python standard library.

### Installing tkinter (if missing)

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS (Homebrew):**
```bash
brew install python-tk
```

**Windows:** Included by default with the official Python installer.

## Usage

### Option 1: Run directly
```bash
python app.pyw
```

### Option 2: Double-click (Windows)
Double-click `run.bat` or `app.pyw`.

### Option 3: Create a desktop shortcut (Windows)
```bat
@echo off
start "" pythonw "C:\path\to\ai-session-cleaner\app.pyw"
```

## How It Works

The app reads session files directly from each tool's local storage directory. It does **not** connect to any API or send data anywhere. All operations are local file reads and deletes.

### What gets deleted

When you delete a session:

- **Factory**: `.jsonl` file + `.settings.json` if present
- **Claude Code**: `.jsonl` file + associated subfolder (file history snapshots)
- **Codex CLI**: `.jsonl` file + empty parent date folders
- **OpenCode**: session `.json` + message folder + part folders + session_diff file

## License

MIT

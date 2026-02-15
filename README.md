# AI Session Cleaner

Desktop GUI app to browse, preview, and bulk-delete chat session files from AI coding tools.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Why This Tool?

Most AI coding assistants (Factory/Droid, Claude Code, Codex CLI, OpenCode, etc.) store conversation sessions locally but **do not provide a built-in way to delete or manage them**. Over time, hundreds of session files accumulate on disk -- many of them blank or abandoned -- with no easy way to browse, filter, or clean them up.

This tool was built to solve that problem: a single app that lets you manage sessions across **multiple AI tools** in one place.

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
- **Open/Resume session** directly from the app (double-click, right-click, or button)
- **Right-click context menu** -- Open Session, Copy Session ID, Delete
- **Language toggle** -- Indonesian / English (ID/EN)
- **Color-coded** projects for quick visual identification
- **Detect empty/blank sessions** (no messages, "New Session" without conversation)
- **Bulk delete** -- select by age (>7/30/90 days), select all blank, or manual multi-select
- **Auto-cleanup** empty folders after deletion
- **Stats dashboard** -- total sessions, projects, disk usage, blank count

## Quick Start

### 1. Clone & Run

```bash
git clone https://github.com/RobithYusuf/ai-session-cleaner.git
cd ai-session-cleaner
python app.pyw
```

Or on Windows, double-click `run.bat`.

### 2. Select a source

Click the source button at the top right (Factory, Claude Code, Codex CLI, or OpenCode).

### 3. Browse & manage

- **Preview** -- Click a session to see the conversation in the preview panel
- **Open Session** -- Double-click a session or right-click > "Open Session" to resume it in terminal
- **Delete** -- Select sessions, then click "Delete Selected" or right-click > "Delete"
- **Clean blank** -- Click "Select Blank" then "Delete Selected", or use "Delete Blank Sessions"

## Open / Resume Session

Open a session directly from the app into a terminal. The behavior depends on the tool:

| Tool | Action |
|---|---|
| **Claude Code** | Opens terminal and runs `claude --resume <session-id>` -- resumes the conversation directly |
| **Codex CLI** | Opens terminal and runs `codex resume <session-id>` -- resumes the conversation directly |
| **Factory (Droid)** | Opens terminal with `droid` in the project folder. Type `/sessions` to select your session |
| **OpenCode** | Opens terminal with `opencode` in the project folder |

**How to use:**
- **Double-click** a session in the list
- **Right-click** > "Open Session"
- **Select a session** and click the "Open Session" button

## Requirements

- Python 3.8+
- `tkinter` (included with Python on Windows)

No third-party packages needed.

### Installing tkinter (if missing)

```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (Homebrew)
brew install python-tk
```

## How It Works

The app reads session files directly from each tool's local storage directory. It does **not** connect to any API or send data anywhere. All operations are local.

### What gets deleted

- **Factory**: `.jsonl` + `.settings.json`
- **Claude Code**: `.jsonl` + associated subfolder (file history snapshots)
- **Codex CLI**: `.jsonl` + empty parent date folders
- **OpenCode**: session `.json` + message folder + part folders + session_diff

## License

MIT

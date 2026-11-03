# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-11-03

### Added
- `/j <mesaj>` (owner only) relays a message to a leader agent session through its CLI; edited messages are ignored and control characters stripped.
- Approve / Reject buttons under an agent's approval request call `approve|reject <id>` on that CLI.
- Every message the bot sends on its own names its sender in a bold first line; bot notifications pass a shared humanizer.
- `/epic`, `/cwd`, `/remote`, `/promote`, `/demote`, `/revoke`, `/limit` (per-user daily cost cap) are documented.
- CI checks that `VERSION`, `pyproject.toml`, `src/main.py` and `src/__init__.py` carry the same version, and that a tag matches it.
- `/auto <iş>` (owner only; promoted admins are refused) puts a one-off task on the Claude autonomy queue as a oneshot job; `alan:<id>` picks the area, `/auto durum <id>` shows its runs. The bot writes no authority or human-only field, the area policy decides.
- `/ack` (owner only) runs `jarvis ack`: a Jarvis escalation seen on Telegram stops its ladder.

### Changed
- Claude replies go through a single sender (`send_claude_reply`): chunked, rendered as Telegram HTML, same chunk re-sent as plain text if Telegram rejects the HTML. All four handlers (text, document, photo, media) use it; a test fails if one bypasses it.

### Fixed
- Inline-keyboard buttons (`/new`, `/status`, `/help`) no longer crash on callback updates, which carry no `message`.
- A user whose access was revoked can no longer drive commands through old keyboards.
- A timed-out `claude` subprocess is killed instead of left running; `--resume` is only passed once Claude has actually started the session.
- Hardcoded home-directory paths are gone: integration CLIs and scripts default to `~` and can be set with `AUTONOMY_CLI`, `JARVIS_CLI`, `EPIC_CLAIM_SCRIPT`, `EPIC_CLAIM_PYTHON`; `scripts/run-bot.sh` locates the repo from its own path.
- `.env.example` used `MONITOR_ENABLED`, which the settings never read; it is `ENABLE_MONITOR`.
- README matched to the code: removed `/broadcast` and `/tunnel` (never registered), cost cap is daily not monthly, default timeout is 600 s, missing variables listed.

## [1.1.0] - 2026-06-09

### Fixed
- Duplicate config field and tunnel validation.
- The ngrok token is passed through an environment variable instead of a CLI argument.

---

## [1.0.0] - 2026-03-22

### Added

**Core bot**
- Multi-user Telegram bot with invite-token authentication
- Admin / user / viewer role hierarchy
- Context-aware inline keyboard quick actions
- `/start`, `/help`, `/ping`, `/new`, `/status`, `/ssh`, `/history`, `/about` commands
- Admin-only: `/invite`, `/users`, `/stats`, `/alerts`, `/broadcast`, `/tunnel`, `/sessions`

**Claude integration**
- `ClaudeSDKRunner` — SDK-first execution with automatic `claude` CLI fallback
- `SessionManager` — multi-turn conversation history with configurable timeout
- `CostTracker` — per-user and per-request spend caps
- `CredentialSanitizer` — strips secrets from all Claude output before delivery
- Agentic mode with configurable max turns and per-request timeout
- Session export as Markdown, JSON, or HTML

**Security**
- Invite-token based access control (`AccessManager`)
- Three-layer rate limiting: Claude requests, commands, invite generation
- Path validator restricting git operations to approved directories
- Full audit log persisted to SQLite

**System monitor**
- `MetricsCollector` — CPU, RAM, disk via psutil; SSH session counting
- `AlertManager` — threshold-based anomaly detection with state-change-only firing
- Configurable alert thresholds via environment variables

**SSH tunnel**
- `TunnelManager` — ngrok lifecycle management (start, health poll, auto-restart)
- `TunnelNotifier` — admin alerts on state transitions only
- Configurable retry count and poll interval

**Notification service**
- Rate-limited, dedup-aware delivery
- 5-minute dedup window per message type
- Hourly reports default OFF, toggled by admin with `/alerts on`

**Storage**
- SQLite in WAL mode via `aiosqlite`
- Repository pattern for users, sessions, audit log
- `StorageFacade` — unified async interface

**Event system**
- Async typed event bus
- Decoupled communication between tunnel, monitor, and notification modules

**Infrastructure**
- Pydantic v2 settings with full validation
- Feature flags for tunnel, monitor, API server, file uploads, git integration, voice messages
- `structlog` structured logging
- FastAPI HTTP server (optional, disabled by default)
- `scripts/install.sh` — automated setup: deps, database, systemd service, watchdog
- `scripts/wsl-watchdog.ps1` — Windows Task Scheduler watchdog for WSL resilience
- `pyproject.toml` with Poetry, Black, isort, flake8, mypy, pytest configuration
- 8 pytest test files covering auth, bot core, Claude bridge, config, monitor, storage, tunnel, validators

---

[1.0.0]: https://github.com/sudohakan/claude-remote-bot/releases/tag/v1.0.0

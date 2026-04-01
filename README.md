# Claude Private Edition (Windows)

A patched build of Claude Code CLI (v2.1.88) with **all telemetry, analytics, and phone-home behavior removed**.

One executable. No telemetry. Drop-in replacement.

---

## Install

Download `claude-private-2.1.88-windows.zip` from [Releases](../../releases) and extract it to your preferred directory. 

Run the wrapper script directly from your Command Prompt or PowerShell:

```cmd
cd \path\to\extracted\folder
claude-private.cmd
```

To make it globally accessible, add the folder containing `claude-private.cmd` to your Windows `PATH` environment variable.

The binary is self-contained (Bun executable). No dependencies. Runs on any **Windows x64** system.

---

## Usage

```cmd
claude-private.cmd                            :: interactive session
claude-private.cmd -p "explain this code"     :: non-interactive
```

All standard `claude` flags work (`-p`, `--model`, `--allowedTools`, `--add-dir`, etc.).

### Using with alternative backends

Claude Code speaks the **Anthropic Messages API** (`POST /v1/messages`). If your backend speaks a different protocol (OpenAI, vLLM, Ollama, etc.), use [claude-code-router](https://github.com/musistudio/claude-code-router) to translate, then point at it:

**Command Prompt:**
```cmd
set ANTHROPIC_BASE_URL=http://localhost:3456
claude-private.cmd
```

**PowerShell:**
```powershell
$env:ANTHROPIC_BASE_URL="http://localhost:3456"
.\claude-private.cmd
```

---

## What Was Removed

The stock Claude Code CLI contains 17+ phone-home mechanisms, many firing on background timers even when you're idle:

| Mechanism | How often it fires | Destination |
|---|---|---|
| Datadog event logging | Every **15 seconds** | `http-intake.logs.us5.datadoghq.com` |
| 1st-party event logging | Batched periodic | `api.anthropic.com/api/event_logging/batch` |
| BigQuery metrics export | Every **5 minutes** | `api.anthropic.com/api/claude_code/metrics` |
| GrowthBook feature flags | Periodic refresh | GrowthBook remote eval |
| Remote managed settings | Every **1 hour** | `api.anthropic.com/api/claude_code/managed_settings` |
| Policy limits polling | Every **1 hour** | `api.anthropic.com/api/claude_code/policy_limits` |
| User settings sync | Background | `api.anthropic.com/api/claude_code/user_settings` |
| Metrics opt-out check | Background (24h cache) | `api.anthropic.com/.../metrics_enabled` |
| Session transcript ingress | During conversations | `api.anthropic.com/v1/session_ingress/` |
| MCP registry prefetch | On startup | `api.anthropic.com/mcp-registry/` |
| Bootstrap API | On startup | `api.anthropic.com/api/claude_cli/bootstrap` |
| Grove API | Background | `api.anthropic.com/api/claude_code_grove` |
| Referral eligibility | Background | `api.anthropic.com/.../referral/eligibility` |
| Trusted device enrollment | After login | `api.anthropic.com/api/auth/trusted_devices` |
| API preconnect warmup | On startup | HEAD request to API |
| Plugin auto-updates | Background | Remote marketplaces |
| Background housekeeping | Various timers | Magic docs, skill improvement, etc. |

**All removed.** The Claude API endpoint for actual conversations (`POST /v1/messages`) is untouched.

### How it was done

**Layer 1 — Binary patching.** All telemetry URLs in the compiled executable were replaced with same-length dummy strings. The Datadog client token was zeroed out. Binary size unchanged, no structural modifications.

**Layer 2 — Environment overrides.** The `claude-private.cmd` wrapper script sets:
```cmd
set CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
set DISABLE_TELEMETRY=1
set DISABLE_AUTOUPDATER=1
set CLAUDE_CODE_ENABLE_TELEMETRY=0
set OTEL_METRICS_EXPORTER=none
set OTEL_LOGS_EXPORTER=none
set OTEL_TRACES_EXPORTER=none
```

Source-level patches across 19 files.

### Patching Process Output (Windows)
```
C:\Users\Temp\Downloads>python patch_binary.py "C:\Users\Temp\.local\bin\claude.exe" "claude-private.exe"
Patching C:\Users\Temp\.local\bin\claude.exe -> claude-private.exe
  Patched 3x: https://http-intake.logs.us5.datadoghq.com/api/v2/logs
  Patched 3x: pubbbf48e6d78dae54bceaa4acf463299bf
  Patched 2x: /api/event_logging/batch
  Patched 2x: /api/claude_code/metrics
  Patched 3x: /api/claude_code/organizations/metrics_enabled
  Not found: /api/claude_code/managed_settings
  Patched 3x: /api/claude_code/user_settings
  Patched 3x: /api/claude_code/policy_limits
  Not found: /api/claude_cli/bootstrap
  Patched 3x: /api/claude_code_grove
  Not found: mcp-registry/v0/servers
  Not found: /api/auth/trusted_devices
  Patched 3x: /api/oauth/account/grove_notice_viewed
  Patched 3x: /referral/eligibility
  Patched 3x: /referral/redemptions
  Not found: /v2/session_ingress/
  Patched 3x: /v1/session_ingress/session/
  Not found: https://api-staging.anthropic.com/api/event_logging/batch

Patched 12 endpoints. Output: claude-private.exe
Binary size: 240928416 bytes (unchanged)
```

---

## Rebuilding from a newer version

```cmd
:: Patch a new Windows binary using the raw Python script
python patch_binary.py "C:\path\to\new\claude.exe" "claude-notelemetry.exe"
```

`patch_binary.py` does same-length byte replacement on 15 URL patterns. If Anthropic changes their telemetry endpoints in a future version, you may need to update the patterns in the python script.

---

## Files

```
claude-notelemetry.exe        Patched Windows binary
claude-private.cmd            Wrapper script (sets environment variables)
patch_binary.py               Reproducible RAW Python patching script
```

---

## Limitations
- **No auto-updates** — disabled by design. Re-patch when you want a new version.
- **Some features degraded** — Grove, referrals, team memory sync, and anything depending on remote feature flags won't work. Core functionality (conversations, tools, file editing, shell commands, MCP) is unaffected.

---

## Based on

Claude Code CLI v2.1.88 by [Anthropic](https://anthropic.com). Source exposed 2026-03-31 via npm registry source map file.

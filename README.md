# Venice Chat 🚀

> **Uncensored, Privacy-First Terminal AI Interface & Local OpenAI-Compatible Bridge for Venice AI & DeepSeek V4.1 Flash**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Cross-Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-purple.svg)]()

---

## Highlights

- ⚡ **Zero-Balance Inference (`free` mode):** Chat with **DeepSeek V4.1 Flash (Uncensored)** with $0 balance, no API keys, and no credit card required.
- 🌉 **Automatic Local OpenAI Bridge:** Starting `venice` automatically launches an OpenAI-compatible API bridge in the background so tools like **OpenCode**, **Cursor**, **Aider**, or **Cline** can connect to `http://127.0.0.1:8088/v1` seamlessly.
- 🔌 **Venice API Transport Compliant:** Strict adherence to `VENICE_TRANSPORT_SPEC.md` (handles streaming usage chunk without choices, logs `CF-RAY`, and forwards `venice_parameters`).
- 🎨 **Rich Terminal UI (TUI):** Real-time streaming tokens, markdown rendering, syntax highlighting, conversation history, and in-chat slash commands.
- 🧹 **Complete Clean Uninstaller:** Run `venice uninstall` anytime to cleanly remove the global command and restore your system to normal.

---

## Quick Install

### macOS & Linux

```bash
git clone https://github.com/TH3L30/venice-chat.git
cd venice-chat
./install.sh
```

### Windows (PowerShell)

```powershell
git clone https://github.com/TH3L30/venice-chat.git
cd venice-chat
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Once installed, the global command `venice` is available from anywhere in your terminal!

---

## Usage

### 1. Launch Interactive Chat (Starts Bridge + Launches CLI)

Simply run:

```bash
venice
```

You will see the step-by-step startup process:
```text
[1/3] ⚙ Checking environment & dependencies...
      ✔ Environment verified (Python 3, OpenCode pipeline)
[2/3] 🚀 Starting Venice Local Bridge on port 8080...
      ✔ Local bridge active on http://127.0.0.1:8088/v1 (OpenCode can connect)
[3/3] 💬 Launching Venice Terminal Chat...
```

### 2. One-Shot Prompt (CLI Mode)

Run a direct question without entering the interactive loop:

```bash
venice -p "Explain quantum computing in one sentence"
```

### 3. Connect External Tools (OpenCode, Cursor, Aider)

While `venice` is running (or via `venice --serve`), you can point any OpenAI-compatible tool to:

* **Base URL:** `http://127.0.0.1:8088/v1` (or whichever port the bridge reports)
* **API Key:** `any-key` (or your Venice key)
* **Model:** `deepseek-v4.1-flash` or `default`

#### OpenCode Configuration Example (`~/.config/opencode/opencode.json`):
```json
{
  "model": "venice-local/deepseek-v4.1-flash",
  "providers": {
    "venice-local": {
      "name": "Venice Local Bridge",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "http://127.0.0.1:8088/v1"
      }
    }
  }
}
```

### 4. Standalone Bridge Server Mode

If you only want the local OpenAI server running in the background without entering the chat UI:

```bash
venice --serve
```

---

## In-Chat Commands

While in interactive mode, use these slash commands:

| Command | Description |
|---|---|
| `/help` | Display interactive command help |
| `/model <name>` | Switch active model (`deepseek-v4.1-flash`, `zai-org-glm-5-2`, `venice-uncensored-1-2`, `default`) |
| `/backend <free\|api>` | Switch between the **zero-balance** engine and paid Venice API |
| `/search <auto\|on\|off>` | Toggle Venice live web search parameter |
| `/system <prompt>` | Set custom system prompt for the conversation |
| `/clear` | Clear active conversation history |
| `/save` | Export conversation transcript to a Markdown file in `history/` |
| `/exit` or `/quit` | Stop the bridge and exit |

---

## Authentication & Session Management

Venice Chat supports three backends:

1. **Free Local Engine (`free` mode - Default):**
   * **Authentication:** **None required.**
   * Runs DeepSeek V4.1 Flash via the local client inference pipeline. No cookies, no token expiry, and no balance required.
2. **Venice Official API (`api` mode):**
   * **Authentication:** `Authorization: Bearer <VENICE_API_KEY>`
   * Reads from your `.env` file (`VENICE_API_KEY`). Keys are permanent unless revoked at [venice.ai/settings/api](https://venice.ai/settings/api).
3. **Venice Web Session (Cookies & Clerk):**
   * **How it works:** Venice's web chat uses Clerk authentication (`__session` cookie + short-lived Clerk JWT bearer tokens).
   * **How to refresh if expired:** Simply open [venice.ai/chat/agent](https://venice.ai/chat/agent) in your browser. Clerk automatically rotates and refreshes your session tokens seamlessly.

---

## Uninstallation

To completely remove the global command and restore your system to its original state:

```bash
venice uninstall
```

Or run non-interactively:

```bash
venice uninstall -y
```

This removes all global executables (`~/.local/bin/venice` or Windows CMD wrappers), cleans runtime caches, and restores your shell environment cleanly.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

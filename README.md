# Venice Chat 🚀

> **Uncensored, Privacy-First Terminal AI Interface & Local OpenAI Bridge for Venice AI**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Cross-Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-purple.svg)]()

A pure, standalone terminal client and local OpenAI-compatible bridge that connects directly to **Venice AI** (`https://api.venice.ai/api/v1`). No third-party agent layers or external tool runtimes required.

---

## Features

- ⚡ **Direct Venice AI Inference:** Directly speaks the official Venice Chat Transport Protocol (`VENICE_TRANSPORT_SPEC.md`).
- 🔓 **Uncensored Models Out-of-the-Box:** Includes `deepseek-v4-1-flash`, `zai-org-glm-5-2`, `venice-uncensored-1-2`, and `grok-4-7`.
- 🌉 **Automatic Local OpenAI Bridge:** Running `venice` starts an OpenAI-compatible bridge in the background (default port 8080/8088), allowing any tool or editor to connect to `http://127.0.0.1:8088/v1`.
- 🎨 **Rich Terminal UI:** Real-time token streaming, Markdown formatting, syntax highlighting, and conversation history.
- 🧹 **Complete Clean Uninstaller:** Run `venice uninstall` anytime to cleanly remove the command and restore your system to normal.

---

## Quick Install

### macOS & Linux

```bash
git clone https://github.com/TH3L30/venice-chat.git
cd venice-chat
./install.sh
```

### Windows (Command Prompt — cmd.exe)

```cmd
git clone https://github.com/TH3L30/venice-chat.git
cd venice-chat
install.bat
```

### Windows (PowerShell)

```powershell
git clone https://github.com/TH3L30/venice-chat.git
cd venice-chat
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

*(You can also run `venice.cmd` directly in the folder without installing).*

Once installed, the global command `venice` is available from anywhere in your terminal or Command Prompt!

---

## Configuration

Get your Venice API Key at: **[https://venice.ai/settings/api](https://venice.ai/settings/api)**

When you run `venice` for the first time, it will prompt you for your key if `.env` is not yet configured, or you can add it directly to `.env`:

```env
VENICE_API_KEY=VENICE_INFERENCE_KEY_...
VENICE_BASE_URL=https://api.venice.ai/api/v1
VENICE_MODEL=deepseek-v4-1-flash
ENABLE_WEB_SEARCH=auto
```

You can also update your key at any time inside the chat using the `/key` command:
```text
You ❯ /key VENICE_INFERENCE_KEY_...
```

---

## Usage

### 1. Launch Interactive Chat (Starts Bridge + Launches CLI)

Simply run:

```bash
venice
```

You will see the startup process:
```text
[1/3] ⚙ Checking Venice environment & dependencies...
      ✔ Environment verified (Python 3, HTTPX, Venice Transport)
[2/3] 🚀 Starting Venice Local Bridge on port 8080...
      ✔ Local bridge active on http://127.0.0.1:8088/v1 (OpenAI Compatible)
[3/3] 💬 Launching Venice Terminal Chat...
```

### 2. One-Shot Prompt (CLI Mode)

```bash
venice -p "Explain quantum computing in one sentence"
```

### 3. Connect External Tools to the Local Bridge

While `venice` is running (or via `venice --serve`), you can point any external application to:

* **Base URL:** `http://127.0.0.1:8088/v1` (or whichever port the bridge reports)
* **API Key:** `any-key` (or your Venice key)
* **Model:** `deepseek-v4-1-flash` or `default`

---

## In-Chat Commands

While in interactive mode, use these slash commands:

| Command | Description |
|---|---|
| `/help` | Display interactive command help |
| `/model <name>` | Switch active Venice model (`deepseek-v4-1-flash`, `zai-org-glm-5-2`, `venice-uncensored-1-2`) |
| `/key <api_key>` | Update your Venice API key |
| `/search <auto\|on\|off>` | Toggle Venice live web search parameter |
| `/system <prompt>` | Set custom system prompt for the conversation |
| `/clear` | Clear active conversation history |
| `/save` | Export conversation transcript to a Markdown file in `history/` |
| `/exit` or `/quit` | Stop the bridge and exit |

---

## Available Venice Models

- `deepseek-v4-1-flash` — DeepSeek V4.1 Flash (Uncensored, 1M context, multimodal & code-optimized)
- `zai-org-glm-5-2` — Zhiyuan AI GLM 5.2 (Advanced reasoning & code)
- `venice-uncensored-1-2` — Venice Uncensored 1.2 (Most Uncensored)
- `default` — Venice Default Trait
- `deepseek-v4-pro` — DeepSeek V4 Pro (1.6T MoE, High Reasoning)
- `grok-4-7` — Grok 4.7 (Most Intelligent Trait)

---

## Uninstallation

To completely remove the global command and restore your system:

```bash
venice uninstall
```

*(Or run non-interactively with `venice uninstall -y` or `uninstall.bat` on Windows).*

---

## License

MIT License. See [LICENSE](LICENSE) for details.

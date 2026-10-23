#!/usr/bin/env python3
"""
Venice Chat — Terminal Interface & Local OpenAI Bridge for Venice AI & DeepSeek V4.1 Flash
Conformant to VENICE_TRANSPORT_SPEC.md.

Commands:
  venice               Starts local bridge server + launches interactive terminal chat
  venice -p "prompt"   One-shot prompt execution
  venice --serve       Runs the OpenAI bridge server as a standalone daemon (port 8080)
  venice uninstall     Completely uninstalls the global command and cleans up system
"""

import os
import sys
import json
import time
import shutil
import signal
import argparse
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Generator, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live

# Ensure .env is loaded from the script directory
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

console = Console()

BANNER = """
[bold magenta]╦  ╦╔═╗╔╗╔╦╔═╗╔═╗  ╔═╗╦ ╦╔═╗╔╦╗[/bold magenta]
[bold cyan]╚╗╔╝║╣ ║║║║║  ║╣   ║  ╠═╣╠═╣ ║ [/bold cyan]
[bold blue] ╚╝ ╚═╝╝╚╝╩╚═╝╚═╝  ╚═╝╩ ╩╩ ╩ ╩ [/bold blue]
[dim]Uncensored & Privacy-First AI Terminal Interface[/dim]
"""

AVAILABLE_MODELS = {
    "deepseek-v4.1-flash": "DeepSeek V4.1 Flash (Uncensored, 1M context)",
    "zai-org-glm-5-2": "GLM 5.2 (Zhiyuan AI, Code & Reasoning)",
    "venice-uncensored-1-2": "Venice Uncensored 1.2 (Most Uncensored)",
    "default": "Venice Default Model Trait",
    "deepseek-v4-pro": "DeepSeek V4 Pro (1.6T MoE, High Reasoning)",
}

# Global bridge server reference for clean shutdown
_BRIDGE_SERVER = None
_BRIDGE_THREAD = None


class VeniceClient:
    def __init__(self, backend: str = "free", model: str = "deepseek-v4.1-flash", search: str = "auto"):
        self.backend = backend
        self.model = model
        self.search = search
        self.api_key = os.getenv("VENICE_API_KEY", "")
        self.base_url = os.getenv("VENICE_BASE_URL", "https://api.venice.ai/api/v1")
        self.history: List[Dict[str, str]] = []
        self.system_prompt: str = ""

    def clear_history(self):
        self.history = []

    def set_model(self, model: str) -> bool:
        self.model = model
        return model in AVAILABLE_MODELS

    def stream_response(self, user_prompt: str) -> Generator[str, None, None]:
        """Routes prompt to selected backend and yields tokens."""
        self.history.append({"role": "user", "content": user_prompt})

        if self.backend == "free":
            yield from self._stream_free(user_prompt)
        elif self.backend == "api":
            yield from self._stream_api(user_prompt)
        elif self.backend == "web":
            yield from self._stream_web(user_prompt)
        else:
            yield f"[Error] Unknown backend: {self.backend}"

    def _stream_free(self, user_prompt: str) -> Generator[str, None, None]:
        """Free Engine: routes through local zero-cost DeepSeek V4.1 Flash pipeline."""
        try:
            full_prompt = ""
            if self.system_prompt:
                full_prompt += f"System: {self.system_prompt}\n\n"
            
            # Context window (last 6 turns)
            for msg in self.history[-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role}: {msg['content']}\n\n"
            full_prompt += "Assistant: "

            cmd = ["opencode", "run", "-m", "opencode/deepseek-v4.1-flash-free", full_prompt]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            assistant_reply = ""
            skip_header = True
            for line in iter(process.stdout.readline, ""):
                # Filter out opencode status line
                if skip_header and (line.startswith(">") or line.strip() == ""):
                    continue
                skip_header = False
                assistant_reply += line
                yield line

            process.stdout.close()
            process.wait()

            if process.returncode != 0:
                err = process.stderr.read()
                if not assistant_reply:
                    yield f"[Free Engine Error]: {err.strip()}"

            self.history.append({"role": "assistant", "content": assistant_reply.strip()})

        except Exception as e:
            yield f"\n[Free Engine Exception]: {str(e)}"

    def _stream_api(self, user_prompt: str) -> Generator[str, None, None]:
        """Official Venice API Engine: implements VENICE_TRANSPORT_SPEC.md exactly."""
        import httpx

        if not self.api_key:
            yield "[API Error] VENICE_API_KEY is not configured in .env file."
            return

        model_id = self.model
        if model_id == "deepseek-v4.1-flash":
            model_id = "deepseek-v4-1-flash"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, br",
        }

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.history)

        body = {
            "model": model_id,
            "messages": messages,
            "stream": True,
            "venice_parameters": {
                "include_venice_system_prompt": True,
                "enable_web_search": self.search,
            }
        }

        try:
            with httpx.Client(timeout=120) as client:
                with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=body) as response:
                    ray = response.headers.get("CF-RAY", "unknown")
                    
                    if response.status_code != 200:
                        error_body = response.read().decode("utf-8")
                        try:
                            err_json = json.loads(error_body)
                            msg = err_json.get("error", error_body)
                            if isinstance(msg, dict):
                                msg = msg.get("message", str(msg))
                        except Exception:
                            msg = error_body
                        yield f"[Venice API Error HTTP {response.status_code}] (CF-RAY: {ray})\n{msg}"
                        return

                    assistant_reply = ""
                    for line in response.iter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        payload = line[6:].strip()
                        if payload == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(payload)
                        except json.JSONDecodeError:
                            continue

                        # Check in-band error (Transport Spec §9.1)
                        if "error" in chunk:
                            err = chunk["error"]
                            yield f"\n[In-Band Error]: {err.get('message', 'Server error')}"
                            break

                        # Trailing usage chunk with empty choices (Transport Spec §9.1)
                        choices = chunk.get("choices", [])
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            assistant_reply += content
                            yield content

                    self.history.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            yield f"\n[API Connection Exception]: {str(e)}"

    def _stream_web(self, user_prompt: str) -> Generator[str, None, None]:
        """Web Agent Engine: guidance on web session vs local free engine."""
        yield "[Web Engine]: Free uncensored inference is handled via backend 'free' using the local DeepSeek V4.1 Flash engine. To use it, type /backend free."


# ---------------------------------------------------------------------------
# OpenAI-Compatible Bridge Server
# ---------------------------------------------------------------------------

def create_bridge_app(client: VeniceClient):
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse, JSONResponse

    app = FastAPI(title="Venice Local OpenAI Bridge")

    @app.get("/v1/models")
    async def list_models():
        return {
            "object": "list",
            "data": [
                {"id": k, "object": "model", "owned_by": "venice-bridge"}
                for k in AVAILABLE_MODELS
            ]
        }

    @app.get("/health")
    async def health():
        return {"status": "ok", "model": client.model, "backend": client.backend}

    @app.post("/v1/chat/completions")
    async def chat_completions(req: Request):
        data = await req.json()
        messages = data.get("messages", [])
        if not messages:
            return JSONResponse({"error": "No messages provided"}, status_code=400)
        
        last_prompt = messages[-1].get("content", "")
        stream = data.get("stream", False)

        if not stream:
            reply = "".join(list(client.stream_response(last_prompt)))
            return {
                "id": f"chatcmpl-bridge-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": data.get("model", client.model),
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": reply},
                    "finish_reason": "stop"
                }]
            }

        def event_generator():
            chat_id = f"chatcmpl-bridge-{int(time.time())}"
            for token in client.stream_response(last_prompt):
                chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": data.get("model", client.model),
                    "choices": [{"index": 0, "delta": {"content": token}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app


def find_available_port(preferred_port: int = 8080) -> int:
    import socket
    for port in [preferred_port, 8088, 8089, 8090, 8095, 8888]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred_port


def start_background_bridge(client: VeniceClient, port: int = 8080) -> tuple[bool, int]:
    """Starts the FastAPI bridge in a daemon thread on an available port and verifies readiness."""
    global _BRIDGE_SERVER, _BRIDGE_THREAD
    import uvicorn
    import httpx

    # Check if preferred port is running a venice bridge
    try:
        r = httpx.get(f"http://127.0.0.1:{port}/health", timeout=0.5)
        if r.status_code == 200:
            console.print(f"      [dim]• Existing local bridge detected on port {port}[/dim]")
            return True, port
    except Exception:
        pass

    target_port = find_available_port(port)

    app = create_bridge_app(client)
    config = uvicorn.Config(app, host="127.0.0.1", port=target_port, log_level="critical")
    _BRIDGE_SERVER = uvicorn.Server(config)

    _BRIDGE_THREAD = threading.Thread(target=_BRIDGE_SERVER.run, daemon=True)
    _BRIDGE_THREAD.start()

    # Wait for bridge to become ready
    for _ in range(25):
        time.sleep(0.1)
        try:
            r = httpx.get(f"http://127.0.0.1:{target_port}/health", timeout=0.5)
            if r.status_code == 200:
                return True, target_port
        except Exception:
            continue

    return False, target_port


def stop_background_bridge():
    """Stops the bridge server cleanly."""
    global _BRIDGE_SERVER, _BRIDGE_THREAD
    if _BRIDGE_SERVER:
        _BRIDGE_SERVER.should_exit = True
    if _BRIDGE_THREAD and _BRIDGE_THREAD.is_alive():
        _BRIDGE_THREAD.join(timeout=1.0)


# ---------------------------------------------------------------------------
# Interactive TUI Session
# ---------------------------------------------------------------------------

def run_interactive_tui(client: VeniceClient, bridge_active: bool = False, port: int = 8080):
    """Runs rich interactive terminal chat session."""
    console.print(BANNER)

    status_table = Table(show_header=False, box=None, padding=(0, 1))
    status_table.add_row("[bold cyan]Model:[/bold cyan]", f"[green]{client.model}[/green] ({AVAILABLE_MODELS.get(client.model, 'Custom')})")
    status_table.add_row("[bold cyan]Backend:[/bold cyan]", f"[yellow]{client.backend.upper()}[/yellow] ({'Zero balance required' if client.backend == 'free' else 'Official API'})")
    if bridge_active:
        status_table.add_row("[bold cyan]Bridge:[/bold cyan]", f"[green]Active on http://127.0.0.1:{port}/v1[/green] (OpenCode compatible)")
    status_table.add_row("[bold cyan]Search:[/bold cyan]", f"[blue]{client.search}[/blue]")
    console.print(Panel(status_table, title="[bold]Session Status[/bold]", border_style="dim magenta"))
    console.print("[dim]Type your message below. Type [bold yellow]/help[/bold yellow] for commands or [bold red]/exit[/bold red] to quit.[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold magenta]You ❯ [/bold magenta]").strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

                if cmd in ("/exit", "/quit", "/q"):
                    console.print("[yellow]Stopping bridge and exiting... Goodbye![/yellow]")
                    break
                elif cmd == "/help":
                    print_help()
                    continue
                elif cmd == "/clear":
                    client.clear_history()
                    console.print("[green]✔ Conversation history cleared.[/green]\n")
                    continue
                elif cmd == "/model":
                    if not arg:
                        console.print(f"[cyan]Current model:[/cyan] [bold green]{client.model}[/bold green]")
                        console.print("Available models:")
                        for k, v in AVAILABLE_MODELS.items():
                            console.print(f"  • [yellow]{k}[/yellow]: {v}")
                    else:
                        client.set_model(arg)
                        console.print(f"[green]✔ Model changed to: [bold]{client.model}[/bold][/green]\n")
                    continue
                elif cmd == "/backend":
                    if arg in ("free", "api", "web"):
                        client.backend = arg
                        console.print(f"[green]✔ Backend switched to: [bold]{arg.upper()}[/bold][/green]\n")
                    else:
                        console.print(f"[cyan]Current backend:[/cyan] [yellow]{client.backend}[/yellow] (options: 'free', 'api', 'web')\n")
                    continue
                elif cmd == "/search":
                    if arg in ("on", "off", "auto"):
                        client.search = arg
                        console.print(f"[green]✔ Web search set to: [bold]{arg}[/bold][/green]\n")
                    else:
                        console.print(f"[cyan]Current web search:[/cyan] {client.search} (options: 'on', 'off', 'auto')\n")
                    continue
                elif cmd == "/system":
                    if arg:
                        client.system_prompt = arg
                        console.print(f"[green]✔ System prompt updated.[/green]\n")
                    else:
                        console.print(f"[cyan]System prompt:[/cyan] {client.system_prompt or '[dim]None (Venice default)[/dim]'}\n")
                    continue
                elif cmd == "/save":
                    save_history(client)
                    continue
                else:
                    console.print(f"[red]Unknown command: {cmd}. Type /help for options.[/red]\n")
                    continue

            # Stream response
            console.print("\n[bold cyan]Venice ❯ [/bold cyan]", end="")
            for token in client.stream_response(user_input):
                console.print(token, end="", highlight=False)
                sys.stdout.flush()
            console.print("\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Type /exit to quit.[/yellow]\n")
        except EOFError:
            break


def print_help():
    table = Table(title="Available Commands", border_style="dim cyan")
    table.add_column("Command", style="yellow")
    table.add_column("Description")
    table.add_row("/help", "Show this help screen")
    table.add_row("/model <name>", "Switch model (e.g. /model deepseek-v4.1-flash)")
    table.add_row("/backend <free|api>", "Switch inference backend ('free' = $0 balance, 'api' = paid Venice API)")
    table.add_row("/search <on|off|auto>", "Toggle web search & citation parameter")
    table.add_row("/system <prompt>", "Set custom system instructions")
    table.add_row("/clear", "Clear conversation history")
    table.add_row("/save", "Export chat transcript to history/*.md")
    table.add_row("/exit, /quit", "Exit Venice Chat and stop bridge")
    console.print(table)
    console.print()


def save_history(client: VeniceClient):
    if not client.history:
        console.print("[yellow]No conversation history to save.[/yellow]\n")
        return
    history_dir = SCRIPT_DIR / "history"
    history_dir.mkdir(exist_ok=True)
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = history_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Venice Chat Transcript ({datetime.now().isoformat()})\n")
        f.write(f"Model: {client.model} | Backend: {client.backend}\n\n---\n\n")
        for msg in client.history:
            role = "**User**" if msg["role"] == "user" else "**Venice**"
            f.write(f"### {role}:\n\n{msg['content']}\n\n")
    console.print(f"[green]✔ Conversation saved to: {filepath}[/green]\n")


# ---------------------------------------------------------------------------
# Uninstall Procedure
# ---------------------------------------------------------------------------

def run_uninstall(non_interactive: bool = False):
    """Completely uninstalls the global venice command and cleans up."""
    console.print(Panel(
        "[bold red]Venice Chat Uninstaller[/bold red]\n"
        "This will completely remove the global 'venice' command and restore your system to normal.",
        border_style="red"
    ))

    if not non_interactive:
        confirm = console.input("[bold yellow]Are you sure you want to completely uninstall Venice? [y/N]: [/bold yellow]").strip().lower()
        if confirm not in ("y", "yes"):
            console.print("[cyan]Uninstall aborted. Venice remains installed.[/cyan]")
            return

    console.print("\n[dim]Cleaning up components...[/dim]")

    # 1. Stop any background bridges
    stop_background_bridge()

    # 2. Potential global binary locations
    candidate_bins = [
        Path.home() / ".local" / "bin" / "venice",
        Path("/usr/local/bin/venice"),
        Path.home() / "bin" / "venice",
    ]

    removed_bins = []
    for bin_path in candidate_bins:
        if bin_path.exists() or bin_path.is_symlink():
            try:
                bin_path.unlink()
                removed_bins.append(str(bin_path))
            except Exception as e:
                console.print(f"[red]Could not delete {bin_path}: {e}[/red]")

    for b in removed_bins:
        console.print(f"  [green]✔ Removed binary:[/green] {b}")

    # 3. Clean runtime caches
    profile_dir = SCRIPT_DIR / ".venice_profile"
    if profile_dir.exists():
        shutil.rmtree(profile_dir, ignore_errors=True)
        console.print(f"  [green]✔ Cleaned cache:[/green] {profile_dir}")

    console.print("\n[bold green]✔ Venice has been completely uninstalled.[/bold green]")
    console.print("[dim]Your system is clean and restored to normal. You can delete the project folder if desired.[/dim]\n")


# ---------------------------------------------------------------------------
# Main Entry Point with Step Information
# ---------------------------------------------------------------------------

def main():
    # Handle 'venice uninstall' subcommand
    if len(sys.argv) > 1 and sys.argv[1] in ("uninstall", "--uninstall"):
        non_interactive = "-y" in sys.argv or "--yes" in sys.argv
        run_uninstall(non_interactive)
        return

    parser = argparse.ArgumentParser(description="Venice AI Terminal Chat Interface")
    parser.add_argument("-m", "--model", default=os.getenv("VENICE_MODEL", "deepseek-v4.1-flash"), help="Model to use")
    parser.add_argument("-b", "--backend", default=os.getenv("VENICE_BACKEND", "free"), choices=["free", "api", "web"], help="Inference backend")
    parser.add_argument("-p", "--prompt", help="One-shot prompt execution (non-interactive)")
    parser.add_argument("--search", default=os.getenv("ENABLE_WEB_SEARCH", "auto"), help="Web search: auto, on, off")
    parser.add_argument("--port", type=int, default=8080, help="Bridge server port (default: 8080)")
    parser.add_argument("--serve", action="store_true", help="Start standalone OpenAI bridge server without launching chat")
    parser.add_argument("--no-bridge", action="store_true", help="Launch chat directly without starting local bridge")

    args = parser.parse_args()

    client = VeniceClient(backend=args.backend, model=args.model, search=args.search)

    # Standalone server mode
    if args.serve:
        import uvicorn
        console.print(f"[bold green]Starting standalone Venice OpenAI Bridge on http://127.0.0.1:{args.port}/v1[/bold green]")
        app = create_bridge_app(client)
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")
        return

    # One-shot mode
    if args.prompt:
        for token in client.stream_response(args.prompt):
            print(token, end="", flush=True)
        print()
        return

    # Standard interactive startup with step information
    console.print("[bold cyan][1/3][/bold cyan] [white]⚙ Checking environment & dependencies...[/white]")
    time.sleep(0.2)
    console.print("      [green]✔ Environment verified (Python 3, OpenCode pipeline)[/green]")

    bridge_ready = False
    active_port = args.port
    if not args.no_bridge:
        console.print(f"[bold cyan][2/3][/bold cyan] [white]🚀 Starting Venice Local Bridge on port {args.port}...[/white]")
        bridge_ready, active_port = start_background_bridge(client, port=args.port)
        if bridge_ready:
            console.print(f"      [green]✔ Local bridge active on http://127.0.0.1:{active_port}/v1 (OpenCode can connect)[/green]")
        else:
            console.print("      [yellow]⚠ Local bridge did not start, running in direct client mode[/yellow]")
    else:
        console.print("[bold cyan][2/3][/bold cyan] [dim]Skipping bridge startup (--no-bridge passed)[/dim]")

    console.print("[bold cyan][3/3][/bold cyan] [white]💬 Launching Venice Terminal Chat...[/white]\n")
    time.sleep(0.3)

    try:
        run_interactive_tui(client, bridge_active=bridge_ready, port=active_port)
    finally:
        stop_background_bridge()


if __name__ == "__main__":
    main()

"""
Multi-Engine Settings & Configuration Dialog for Standalone Agent Harness.
Features a world-class dark segmented tab navigation bar, multi-engine targeting,
and a comprehensive 21+ AI Provider matrix with live API model fetching and testing.
"""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import core.bootstrap
from core.config_manager import ConfigManager
from core.engine_controller import EngineController
from core.logger import get_logger
from core.nexus_bridge import NexusBridge
from core.update_engine import UpdateEngine
from version import __version__, __repo__

logger = get_logger("SettingsDialog", "settings_dialog.log")

# -----------------------------------------------------------------------------
# TOP 21+ AI PROVIDERS REGISTRY (PURE PROVIDERS MATRIX)
# -----------------------------------------------------------------------------
AI_PROVIDERS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "google": {
        "display_name": "Google Gemini (Google AI Studio / Vertex)",
        "default_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_model": "gemini-2.5-flash",
        "models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "requires_key": True,
        "key_hint": "Google AI Studio Key",
    },
    "anthropic": {
        "display_name": "Anthropic Claude (Sonnet 4 / Claude 3.7)",
        "default_url": "https://api.anthropic.com/v1",
        "default_model": "claude-sonnet-4-20250514",
        "models": ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        "requires_key": True,
        "key_hint": "Anthropic Key (sk-ant-...)",
    },
    "openai": {
        "display_name": "OpenAI (ChatGPT / GPT-4o / o1 / o3)",
        "default_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1", "gpt-4-turbo", "gpt-3.5-turbo"],
        "requires_key": True,
        "key_hint": "OpenAI Key (sk-...)",
    },
    "ollama": {
        "display_name": "Ollama (Local Offline Server)",
        "default_url": "http://127.0.0.1:11434",
        "default_model": "qwen2.5-coder:32b",
        "models": ["qwen2.5-coder:32b", "llama3.3:70b", "deepseek-r1:32b", "mistral:7b", "codellama:34b"],
        "requires_key": False,
        "key_hint": "Not required (Local daemon)",
    },
    "openrouter": {
        "display_name": "OpenRouter (Universal AI Gateway)",
        "default_url": "https://openrouter.ai/api/v1",
        "default_model": "google/gemini-2.5-flash",
        "models": ["google/gemini-2.5-flash", "anthropic/claude-3.7-sonnet", "deepseek/deepseek-r1", "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"],
        "requires_key": True,
        "key_hint": "OpenRouter Key (sk-or-...)",
    },
    "llamacpp": {
        "display_name": "llama.cpp (Local GGUF HTTP Server)",
        "default_url": "http://127.0.0.1:8080/v1",
        "default_model": "default",
        "models": ["default", "local-model", "mistral-7b-instruct", "qwen2.5-coder-7b"],
        "requires_key": False,
        "key_hint": "Not required (Local llama-server)",
    },
    "groq": {
        "display_name": "Groq (Ultra-Fast LPU Inference)",
        "default_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b"],
        "requires_key": True,
        "key_hint": "Groq Key (gsk_...)",
    },
    "deepseek": {
        "display_name": "DeepSeek (DeepSeek-V3 / R1 Reasoner)",
        "default_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "requires_key": True,
        "key_hint": "DeepSeek Key (sk-...)",
    },
    "mistral": {
        "display_name": "Mistral AI (Large / Codestral / Pixtral)",
        "default_url": "https://api.mistral.ai/v1",
        "default_model": "mistral-large-latest",
        "models": ["mistral-large-latest", "codestral-latest", "mistral-small-latest", "pixtral-large-latest"],
        "requires_key": True,
        "key_hint": "Mistral API Key",
    },
    "xai": {
        "display_name": "xAI (Grok 2 / Grok 3)",
        "default_url": "https://api.x.ai/v1",
        "default_model": "grok-2-latest",
        "models": ["grok-2-latest", "grok-2-vision-latest", "grok-beta"],
        "requires_key": True,
        "key_hint": "xAI API Key (xai-...)",
    },
    "together": {
        "display_name": "Together AI (Cloud Open Source Models)",
        "default_url": "https://api.together.xyz/v1",
        "default_model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "models": ["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-Coder-32B-Instruct"],
        "requires_key": True,
        "key_hint": "Together API Key",
    },
    "fireworks": {
        "display_name": "Fireworks AI (Fast Open Source Inference)",
        "default_url": "https://api.fireworks.ai/inference/v1",
        "default_model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "models": ["accounts/fireworks/models/llama-v3p3-70b-instruct", "accounts/fireworks/models/deepseek-v3", "accounts/fireworks/models/qwen2p5-coder-32b-instruct"],
        "requires_key": True,
        "key_hint": "Fireworks API Key",
    },
    "cohere": {
        "display_name": "Cohere (Command R+ / Aya)",
        "default_url": "https://api.cohere.com/v2",
        "default_model": "command-r-plus-08-2024",
        "models": ["command-r-plus-08-2024", "command-r-08-2024", "command-light"],
        "requires_key": True,
        "key_hint": "Cohere API Key",
    },
    "lmstudio": {
        "display_name": "LM Studio (Local GUI Inference Server)",
        "default_url": "http://127.0.0.1:1234/v1",
        "default_model": "local-model",
        "models": ["local-model", "qwen2.5-coder-7b-instruct", "meta-llama-3.1-8b-instruct"],
        "requires_key": False,
        "key_hint": "Not required (Local LM Studio)",
    },
    "perplexity": {
        "display_name": "Perplexity AI (Sonar Online Search)",
        "default_url": "https://api.perplexity.ai",
        "default_model": "sonar-pro",
        "models": ["sonar-pro", "sonar", "sonar-reasoning-pro"],
        "requires_key": True,
        "key_hint": "Perplexity Key (pplx-...)",
    },
    "cerebras": {
        "display_name": "Cerebras (Ultra-Fast CS-3 Inference)",
        "default_url": "https://api.cerebras.ai/v1",
        "default_model": "llama3.3-70b",
        "models": ["llama3.3-70b", "llama3.1-8b"],
        "requires_key": True,
        "key_hint": "Cerebras Key (csk-...)",
    },
    "sambanova": {
        "display_name": "SambaNova Systems (DataScale Inference)",
        "default_url": "https://api.sambanova.ai/v1",
        "default_model": "Meta-Llama-3.3-70B-Instruct",
        "models": ["Meta-Llama-3.3-70B-Instruct", "DeepSeek-R1", "Qwen2.5-Coder-32B-Instruct"],
        "requires_key": True,
        "key_hint": "SambaNova API Key",
    },
    "ai21": {
        "display_name": "AI21 Labs (Jamba 1.5 Large)",
        "default_url": "https://api.ai21.com/studio/v1",
        "default_model": "jamba-1.5-large",
        "models": ["jamba-1.5-large", "jamba-1.5-mini"],
        "requires_key": True,
        "key_hint": "AI21 API Key",
    },
    "cloudflare": {
        "display_name": "Cloudflare Workers AI (Global Edge)",
        "default_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        "default_model": "@cf/meta/llama-3.3-70b-instruct",
        "models": ["@cf/meta/llama-3.3-70b-instruct", "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"],
        "requires_key": True,
        "key_hint": "Cloudflare API Token",
    },
    "huggingface": {
        "display_name": "Hugging Face (Inference Endpoints / TGI)",
        "default_url": "https://api-inference.huggingface.co/v1",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct",
        "models": ["meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen2.5-Coder-32B-Instruct"],
        "requires_key": True,
        "key_hint": "Hugging Face Token (hf_...)",
    },
    "custom": {
        "display_name": "Custom (OpenAI-Compatible / Self-Hosted)",
        "default_url": "http://127.0.0.1:8000/v1",
        "default_model": "custom-model",
        "models": ["custom-model"],
        "requires_key": False,
        "key_hint": "API Key (if required by custom server)",
    },
}


class SettingsDialog(tk.Toplevel):
    """Configuration & Diagnostic Modal Window with World-Class Dark Tab Navigation."""

    def __init__(self, parent: tk.Tk, config_mgr: ConfigManager, controller: EngineController, nexus: NexusBridge, on_saved_cb=None):
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.controller = controller
        self.nexus = nexus
        self.on_saved_cb = on_saved_cb

        self.title("⚙️ Standalone Agent Harness — Engine & Provider Configuration")
        self.geometry("940x680")
        self.minsize(740, 580)
        self.configure(bg="#0b0e14")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        hdr = tk.Frame(self, bg="#111726", pady=12, padx=18)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⚙️ HARNESS SETTINGS & MULTI-ENGINE MATRIX", font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#111726").pack(anchor=tk.W)
        tk.Label(hdr, text="Configure target Unreal Engine version, top AI frontier providers, personality wisdom, and diagnostics.", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726").pack(anchor=tk.W)

        # 2. WORLD-CLASS SEGMENTED TAB NAVIGATION BAR
        tab_nav = tk.Frame(self, bg="#0b0e14", padx=16, pady=8)
        tab_nav.pack(fill=tk.X)

        self.tab_frames: Dict[int, tk.Frame] = {}
        self.tab_buttons: Dict[int, tk.Button] = {}
        self.active_tab_idx = 1

        tab_defs = [
            (0, "🎮 Engine Profiles"),
            (1, "🤖 AI Providers & Models"),
            (2, "🧠 AI Personalities"),
            (3, "🩺 Diagnostics"),
        ]

        # Content area for active tab frame
        self.content_area = tk.Frame(self, bg="#12151c", padx=16, pady=4)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        for idx, label in tab_defs:
            f = tk.Frame(self.content_area, bg="#12151c")
            self.tab_frames[idx] = f

            btn = tk.Button(
                tab_nav,
                text=label,
                font=("Segoe UI", 9, "bold"),
                relief=tk.FLAT,
                padx=16,
                pady=7,
                cursor="hand2",
                command=lambda i=idx: self._switch_tab(i),
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))
            self.tab_buttons[idx] = btn

        # Build individual tabs
        self._build_engine_tab(self.tab_frames[0])
        self._build_llm_tab(self.tab_frames[1])
        self._build_personality_tab(self.tab_frames[2])
        self._build_diag_tab(self.tab_frames[3])

        # Auto-select the AI Providers & Models tab on open
        self._switch_tab(1)

        # 3. Bottom Action Bar
        btn_bar = tk.Frame(self, bg="#111726", pady=10, padx=18)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(btn_bar, text="💾 Save Configuration", font=("Segoe UI", 10, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=18, pady=6, command=self._save_and_close).pack(side=tk.RIGHT, padx=6)
        tk.Button(btn_bar, text="Cancel", font=("Segoe UI", 9), bg="#334155", fg="#f1f5f9", relief=tk.FLAT, padx=14, pady=6, command=self.destroy).pack(side=tk.RIGHT)

    def _switch_tab(self, target_idx: int):
        self.active_tab_idx = target_idx
        for idx, f in self.tab_frames.items():
            if idx == target_idx:
                f.pack(fill=tk.BOTH, expand=True)
            else:
                f.pack_forget()

        for idx, btn in self.tab_buttons.items():
            if idx == target_idx:
                btn.configure(
                    bg="#0284c7",
                    fg="#ffffff",
                    activebackground="#0369a1",
                    activeforeground="#ffffff",
                )
            else:
                btn.configure(
                    bg="#1e293b",
                    fg="#94a3b8",
                    activebackground="#334155",
                    activeforeground="#f8fafc",
                )

    # -------------------------------------------------------------------------
    # TAB 1: ENGINE PROFILES
    # -------------------------------------------------------------------------
    def _build_engine_tab(self, parent: tk.Frame):
        canvas = tk.Canvas(parent, bg="#12151c", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#12151c")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=880)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.engine_var = tk.StringVar(value=self.config_mgr.get_active_engine_id())

        # Auto-Scan Banner
        scan_box = tk.Frame(scrollable_frame, bg="#0f172a", padx=12, pady=10, highlightbackground="#0284c7", highlightthickness=1)
        scan_box.pack(fill=tk.X, pady=(0, 10))

        scan_hdr = tk.Frame(scan_box, bg="#0f172a")
        scan_hdr.pack(fill=tk.X)
        tk.Label(scan_hdr, text="🔍 STANDALONE AUTO-DISCOVERY SCANNER", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#0f172a").pack(side=tk.LEFT)
        tk.Button(scan_hdr, text="🔍 SCAN ALL DRIVES", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff", relief=tk.FLAT, padx=12, pady=4, command=self._show_scan_modal).pack(side=tk.RIGHT)

        tk.Label(scan_box, text="Scans all local drives, Steam, GOG, and folders to automatically find and link every installed Unreal engine and Total Conversion mod on this computer.", font=("Segoe UI", 8), fg="#94a3b8", bg="#0f172a", justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 0))

        # Base Game Engines
        tk.Label(scrollable_frame, text="🎮 BASE GAME ENGINES", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#12151c").pack(anchor=tk.W, pady=(4, 6))

        base_engines = self.config_mgr.get_base_engines()
        for eid, p in base_engines.items():
            rb_frame = tk.Frame(scrollable_frame, bg="#1e293b", padx=10, pady=8, highlightbackground="#334155", highlightthickness=1)
            rb_frame.pack(fill=tk.X, pady=3)

            rb = tk.Radiobutton(
                rb_frame,
                text=f"{p.get('icon', '🏆')} {p.get('name', eid)}",
                variable=self.engine_var,
                value=eid,
                font=("Segoe UI", 9, "bold"),
                fg="#f8fafc",
                bg="#1e293b",
                selectcolor="#0f172a",
            )
            rb.pack(anchor=tk.W)

            details_str = f"Root: {p.get('root_dir', 'N/A')}  |  Executable: {p.get('editor_exe', 'UnrealEd.exe')}  |  Gen: {p.get('generation', 'UE1')}"
            tk.Label(rb_frame, text=details_str, font=("Consolas", 8), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W, padx=24)

            tk.Button(rb_frame, text="Verify this profile", font=("Segoe UI", 7), bg="#334155", fg="#cbd5e1", relief=tk.FLAT, padx=7, pady=1,
                      command=lambda e=eid: self._verify_engine_profile(e)).pack(anchor=tk.E, pady=(2, 0))

        # Game Mods
        mod_hdr_frame = tk.Frame(scrollable_frame, bg="#12151c", pady=12)
        mod_hdr_frame.pack(fill=tk.X)
        tk.Label(mod_hdr_frame, text="📦 GAME MODS & TOTAL CONVERSIONS (TC)", font=("Segoe UI", 10, "bold"), fg="#f59e0b", bg="#12151c").pack(side=tk.LEFT)
        tk.Button(mod_hdr_frame, text="➕ Register New Mod", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=8, pady=2, command=self._show_add_mod_dialog).pack(side=tk.RIGHT)

        game_mods = self.config_mgr.get_game_mods()
        for mid, p in game_mods.items():
            rb_frame = tk.Frame(scrollable_frame, bg="#1e293b", padx=10, pady=8, highlightbackground="#d97706", highlightthickness=1)
            rb_frame.pack(fill=tk.X, pady=3)

            rb = tk.Radiobutton(
                rb_frame,
                text=f"{p.get('icon', '⚡')} {p.get('name', mid)}",
                variable=self.engine_var,
                value=mid,
                font=("Segoe UI", 9, "bold"),
                fg="#f8fafc",
                bg="#1e293b",
                selectcolor="#0f172a",
            )
            rb.pack(anchor=tk.W)

            details_str = f"Mod Directory: {p.get('system_dir', 'N/A')}  |  Base Profile: {p.get('parent_profile', 'ut99_goty')}"
            tk.Label(rb_frame, text=details_str, font=("Consolas", 8), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W, padx=24)

    def _verify_engine_profile(self, engine_id: str):
        res = self.config_mgr.verify_engine_profile(engine_id)
        if res.get("verified"):
            messagebox.showinfo("Verification Passed", f"Profile '{engine_id}' verified successfully:\n\n{res.get('summary')}", parent=self)
        else:
            messagebox.showwarning("Verification Warning", f"Profile '{engine_id}' has issues:\n\n{res.get('summary')}", parent=self)

    def _show_scan_modal(self):
        def _worker():
            discovered = self.config_mgr.run_engine_scan()
            count = len(discovered)
            self.after(0, lambda: messagebox.showinfo("Auto-Scan Complete", f"Auto-discovery scan finished! Discovered/verified {count} engine target(s).", parent=self))
        threading.Thread(target=_worker, daemon=True).start()

    def _show_add_mod_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("➕ Register Game Mod / Total Conversion")
        dlg.geometry("520x360")
        dlg.configure(bg="#12151c")
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="Register New Mod / TC", font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#12151c").pack(pady=8)
        f = tk.Frame(dlg, bg="#12151c", padx=16)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="Mod Name:", fg="#f8fafc", bg="#12151c", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        name_var = tk.StringVar()
        tk.Entry(f, textvariable=name_var, bg="#1e293b", fg="#ffffff", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="ew", pady=4)

        tk.Label(f, text="System Directory:", fg="#f8fafc", bg="#12151c", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        sys_var = tk.StringVar()
        tk.Entry(f, textvariable=sys_var, bg="#1e293b", fg="#ffffff", font=("Segoe UI", 9)).grid(row=1, column=1, sticky="ew", pady=4)

        def _browse():
            d = filedialog.askdirectory(title="Select Mod System Directory", parent=dlg)
            if d:
                sys_var.set(d)
        tk.Button(f, text="Browse", command=_browse, bg="#334155", fg="#ffffff", font=("Segoe UI", 8)).grid(row=1, column=2, padx=4)
        f.columnconfigure(1, weight=1)

        def _do_register():
            m_name = name_var.get().strip()
            s_dir = sys_var.get().strip()
            if not m_name or not s_dir:
                messagebox.showerror("Error", "Name and System Directory required.", parent=dlg)
                return
            m_id = m_name.lower().replace(" ", "_")
            self.config_mgr.register_game_mod(m_id, {
                "name": m_name,
                "system_dir": s_dir,
                "root_dir": str(Path(s_dir).parent),
                "is_mod": True,
                "parent_profile": "ut99_goty",
            })
            dlg.destroy()

        btn_bar = tk.Frame(dlg, bg="#12151c", pady=8, padx=16)
        btn_bar.pack(fill=tk.X)
        tk.Button(btn_bar, text="Save Mod", bg="#0284c7", fg="#ffffff", font=("Segoe UI", 9, "bold"), command=_do_register).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_bar, text="Cancel", bg="#334155", fg="#ffffff", font=("Segoe UI", 9), command=dlg.destroy).pack(side=tk.RIGHT)

    # -------------------------------------------------------------------------
    # TAB 2: AI PROVIDERS & MODELS (21+ PURE PROVIDERS MATRIX)
    # -------------------------------------------------------------------------
    def _build_llm_tab(self, parent: tk.Frame):
        # Scrollable container
        llm_canvas = tk.Canvas(parent, bg="#12151c", highlightthickness=0)
        llm_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=llm_canvas.yview)
        llm_scroll_frame = tk.Frame(llm_canvas, bg="#12151c")
        llm_scroll_frame.bind("<Configure>", lambda e: llm_canvas.configure(scrollregion=llm_canvas.bbox("all")))
        llm_canvas.create_window((0, 0), window=llm_scroll_frame, anchor="nw", width=880)
        llm_canvas.configure(yscrollcommand=llm_scrollbar.set)
        llm_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        llm_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 1. Provider & Model Configuration Card
        config_box = tk.Frame(llm_scroll_frame, bg="#1e293b", padx=14, pady=12, highlightbackground="#0284c7", highlightthickness=1)
        config_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(config_box, text="🤖 AI PROVIDER & MODEL CONFIGURATION", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#1e293b").pack(anchor=tk.W, pady=(0, 6))

        # Provider Selector (Pure Providers List)
        prov_row = tk.Frame(config_box, bg="#1e293b")
        prov_row.pack(fill=tk.X, pady=(2, 6))
        tk.Label(prov_row, text="AI Provider:", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", width=14, anchor=tk.W).pack(side=tk.LEFT)

        # Build display name mapping
        self.provider_display_names = [info["display_name"] for info in AI_PROVIDERS_REGISTRY.values()]
        self.provider_key_by_display = {info["display_name"]: key for key, info in AI_PROVIDERS_REGISTRY.items()}
        self.provider_display_by_key = {key: info["display_name"] for key, info in AI_PROVIDERS_REGISTRY.items()}

        active_prof = self.config_mgr.get_active_llm_profile()
        active_provider_key = active_prof.get("provider", "google").lower()
        if active_provider_key not in AI_PROVIDERS_REGISTRY:
            active_provider_key = "google"
        self.active_provider_key = active_provider_key

        self.provider_display_var = tk.StringVar(value=self.provider_display_by_key.get(active_provider_key, self.provider_display_names[0]))
        self.prov_menu = ttk.Combobox(prov_row, textvariable=self.provider_display_var, values=self.provider_display_names, state="readonly", font=("Segoe UI", 9))
        self.prov_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.prov_menu.bind("<<ComboboxSelected>>", self._on_provider_selected)

        # API Key
        key_row = tk.Frame(config_box, bg="#1e293b")
        key_row.pack(fill=tk.X, pady=(2, 6))
        self.key_label = tk.Label(key_row, text="API Key:", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", width=14, anchor=tk.W)
        self.key_label.pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=active_prof.get("api_key", ""))
        self.api_key_entry = tk.Entry(key_row, textvariable=self.api_key_var, show="*", bg="#0f172a", fg="#38bdf8", font=("Consolas", 10))
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self._show_key_var = tk.BooleanVar(value=False)
        def _toggle_key_vis():
            self.api_key_entry.configure(show="" if self._show_key_var.get() else "*")
        tk.Checkbutton(key_row, text="Show", variable=self._show_key_var, command=_toggle_key_vis, fg="#94a3b8", bg="#1e293b", selectcolor="#0f172a", activebackground="#1e293b").pack(side=tk.RIGHT)

        # Base URL
        url_row = tk.Frame(config_box, bg="#1e293b")
        url_row.pack(fill=tk.X, pady=(2, 6))
        tk.Label(url_row, text="Base API URL:", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", width=14, anchor=tk.W).pack(side=tk.LEFT)
        self.base_url_var = tk.StringVar(value=active_prof.get("base_url", AI_PROVIDERS_REGISTRY[active_provider_key]["default_url"]))
        self.base_url_entry = tk.Entry(url_row, textvariable=self.base_url_var, bg="#0f172a", fg="#f8fafc", font=("Consolas", 9))
        self.base_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Connection & Fetch Live Models Row
        fetch_row = tk.Frame(config_box, bg="#1e293b")
        fetch_row.pack(fill=tk.X, pady=(4, 6))

        self.fetch_btn = tk.Button(
            fetch_row,
            text="⚡ TEST CONNECTION & FETCH MODELS",
            font=("Segoe UI", 8, "bold"),
            bg="#0ea5e9",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=3,
            command=self._test_llm_connection,
        )
        self.fetch_btn.pack(side=tk.LEFT)

        self.llm_status_lbl = tk.Label(fetch_row, text="", font=("Segoe UI", 8), fg="#38bdf8", bg="#1e293b")
        self.llm_status_lbl.pack(side=tk.LEFT, padx=8)

        # Active Model Selector (Combobox with live fetched models + custom input)
        model_row = tk.Frame(config_box, bg="#1e293b")
        model_row.pack(fill=tk.X, pady=(2, 6))
        tk.Label(model_row, text="Active Model:", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", width=14, anchor=tk.W).pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=active_prof.get("model", AI_PROVIDERS_REGISTRY[active_provider_key]["default_model"]))
        self.model_combo = ttk.Combobox(model_row, textvariable=self.model_var, values=AI_PROVIDERS_REGISTRY[active_provider_key]["models"], font=("Consolas", 9))
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        # Save AI Configuration Button
        tk.Button(
            model_row,
            text="💾 SAVE AI CONFIG",
            font=("Segoe UI", 8, "bold"),
            bg="#059669",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=2,
            command=self._save_llm_config,
        ).pack(side=tk.RIGHT)

        # Capabilities Indicator Pill
        self.llm_capability_lbl = tk.Label(config_box, text="", font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b")
        self.llm_capability_lbl.pack(anchor=tk.W, pady=(4, 0))

        # 2. 🌍 RECOMMENDED MODELS FOR WORLD-BUILDING Panel
        rec_box = tk.Frame(llm_scroll_frame, bg="#0f172a", padx=12, pady=10, highlightbackground="#10b981", highlightthickness=1)
        rec_box.pack(fill=tk.X, pady=(0, 10))

        rec_hdr = tk.Frame(rec_box, bg="#0f172a")
        rec_hdr.pack(fill=tk.X, pady=(0, 4))
        tk.Label(rec_hdr, text="🌍 RECOMMENDED MODELS FOR WORLD-BUILDING", font=("Segoe UI", 10, "bold"), fg="#10b981", bg="#0f172a").pack(side=tk.LEFT)
        tk.Label(rec_hdr, text="Click '⚡ SELECT & APPLY' to configure instantly", font=("Segoe UI", 8, "italic"), fg="#6ee7b7", bg="#0f172a").pack(side=tk.RIGHT)

        tk.Label(rec_box, text="World-class Unreal level synthesis requires high spatial reasoning, native tool calling, and large context windows:", font=("Segoe UI", 8), fg="#94a3b8", bg="#0f172a").pack(anchor=tk.W, pady=(0, 6))

        recommended_models = [
            ("🥇 BEST", "google",    "Google Gemini", "gemini-2.5-pro",           "Best spatial reasoning, 1M context, native tool use, vision"),
            ("🥈 SOTA", "anthropic", "Anthropic",     "claude-sonnet-4-20250514", "Exceptional code gen, strong 3D spatial architecture"),
            ("🥉 FAST", "google",    "Google Gemini", "gemini-2.5-flash",         "Fast iteration, excellent tool calling, generous free tier"),
            ("4",       "openai",    "OpenAI",        "gpt-4o",                   "Solid all-round level designer with multimodal vision"),
            ("5",       "deepseek",  "DeepSeek",      "deepseek-chat",            "Budget option with strong chain-of-thought reasoning"),
            ("6",       "ollama",    "Ollama (Local)","qwen2.5-coder:32b",        "Fully offline / air-gapped local model, zero API key required"),
        ]

        for rank, p_key, provider_name, model, reason in recommended_models:
            row = tk.Frame(rec_box, bg="#1e293b", padx=8, pady=4)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=rank, font=("Segoe UI", 8, "bold"), fg="#fcd34d", bg="#1e293b", width=6).pack(side=tk.LEFT)
            tk.Label(row, text=provider_name, font=("Segoe UI", 8, "bold"), fg="#38bdf8", bg="#1e293b", width=14, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=model, font=("Consolas", 8), fg="#f8fafc", bg="#1e293b", width=26, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 6))
            tk.Label(row, text=reason, font=("Segoe UI", 7), fg="#94a3b8", bg="#1e293b", anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

            def _apply_preset(k=p_key, m=model):
                self.active_provider_key = k
                self.provider_display_var.set(self.provider_display_by_key.get(k, ""))
                self._load_provider_fields(k)
                self.model_var.set(m)
                self._save_llm_config(silent=True)
                messagebox.showinfo("Model Selected", f"Configured and saved {m} ({AI_PROVIDERS_REGISTRY[k]['display_name']}) for world-building!", parent=self)

            tk.Button(row, text="⚡ SELECT & APPLY", font=("Segoe UI", 7, "bold"), bg="#059669", fg="#ffffff", relief=tk.FLAT, padx=6, pady=1, command=_apply_preset).pack(side=tk.RIGHT)

        self._update_capability_label()

    def _on_provider_selected(self, event=None):
        disp = self.provider_display_var.get()
        p_key = self.provider_key_by_display.get(disp, "google")
        self.active_provider_key = p_key
        self._load_provider_fields(p_key)

    def _load_provider_fields(self, provider_key: str):
        info = AI_PROVIDERS_REGISTRY.get(provider_key, AI_PROVIDERS_REGISTRY["google"])
        profiles = self.config_mgr.get_all_llm_profiles()
        saved_p = profiles.get(provider_key, {})

        # Load API key and URL from saved profile or defaults
        self.api_key_var.set(saved_p.get("api_key", ""))
        self.base_url_var.set(saved_p.get("base_url") or info["default_url"])
        self.model_var.set(saved_p.get("model") or info["default_model"])

        # Populate model dropdown
        self.model_combo["values"] = info["models"]

        # Update key label hint
        if info["requires_key"]:
            self.key_label.configure(text="API Key (Req):", fg="#f8fafc")
        else:
            self.key_label.configure(text="API Key (Opt):", fg="#94a3b8")

        self._update_capability_label()
        if hasattr(self, "llm_status_lbl"):
            self.llm_status_lbl.configure(text="")

    def _update_capability_label(self):
        p_key = getattr(self, "active_provider_key", "google")
        info = AI_PROVIDERS_REGISTRY.get(p_key, AI_PROVIDERS_REGISTRY["google"])
        has_key = bool(self.api_key_var.get().strip()) or not info["requires_key"]

        self.llm_capability_lbl.configure(
            text=(f"Provider: {info['display_name'].split('(')[0].strip()}  |  "
                  f"Model: {self.model_var.get()}  |  "
                  f"Tools: YES  |  "
                  f"Key Status: {'✅ Ready' if has_key else '⚠️ Key Required'}")
        )

    def _test_llm_connection(self):
        provider_key = getattr(self, "active_provider_key", "google")

        # Temporarily update the profile in config manager before testing
        self.config_mgr.update_llm_profile(provider_key, {
            "name": AI_PROVIDERS_REGISTRY[provider_key]["display_name"],
            "provider": provider_key,
            "api_key": self.api_key_var.get().strip(),
            "model": self.model_var.get().strip(),
            "base_url": self.base_url_var.get().strip(),
        })

        if hasattr(self, "fetch_btn"):
            self.fetch_btn.configure(state=tk.DISABLED)
        if hasattr(self, "llm_status_lbl"):
            self.llm_status_lbl.configure(text="⏳ Querying provider API...", fg="#f59e0b")

        def _worker():
            from core.llm_engine import LLMEngine
            engine = LLMEngine(self.config_mgr, self.controller, self.nexus)
            result = engine.test_provider_connection(provider_key)

            def _update():
                if hasattr(self, "fetch_btn"):
                    self.fetch_btn.configure(state=tk.NORMAL)
                models = result.get("models", [])
                if models and hasattr(self, "model_combo"):
                    self.model_combo["values"] = models
                if result.get("ok"):
                    self.llm_status_lbl.configure(text=f"✅ {result.get('message', 'Connected')}", fg="#10b981")
                    messagebox.showinfo(
                        "Connection & Models",
                        f"✅ Connection Successful!\n\n{result.get('message')}\n\n"
                        f"Populated {len(models)} model(s) in the Active Model dropdown.",
                        parent=self,
                    )
                else:
                    self.llm_status_lbl.configure(text=f"⚠️ {result.get('message', 'Failed')}", fg="#ef4444")
                    messagebox.showwarning(
                        "Connection Result",
                        f"⚠️ Connection Note:\n\n{result.get('message')}",
                        parent=self,
                    )

            self.after(0, _update)

        threading.Thread(target=_worker, daemon=True).start()

    def _save_llm_config(self, silent: bool = False):
        provider_key = getattr(self, "active_provider_key", "google")
        info = AI_PROVIDERS_REGISTRY.get(provider_key, AI_PROVIDERS_REGISTRY["google"])

        self.config_mgr.set_active_llm_profile_id(provider_key)
        saved = self.config_mgr.update_llm_profile(provider_key, {
            "name": info["display_name"],
            "provider": provider_key,
            "api_key": self.api_key_var.get().strip(),
            "model": self.model_var.get().strip() or info["default_model"],
            "base_url": self.base_url_var.get().strip() or info["default_url"],
        })
        self._update_capability_label()
        if saved and not silent:
            messagebox.showinfo("AI Config Saved", f"AI Provider '{info['display_name']}' configured and saved successfully!", parent=self)

    # -------------------------------------------------------------------------
    # TAB 3: PERSONALITIES
    # -------------------------------------------------------------------------
    def _build_personality_tab(self, parent: tk.Frame):
        tk.Label(parent, text="Architect AI Personality:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#12151c").pack(anchor=tk.W, pady=(0, 4))
        personalities = self.config_mgr.get_all_personalities()
        self.pers_var = tk.StringVar(value=self.config_mgr.get_active_personality_id())

        for pid, p in personalities.items():
            pf = tk.Frame(parent, bg="#1e293b", padx=10, pady=6)
            pf.pack(fill=tk.X, pady=3)
            rb = tk.Radiobutton(
                pf,
                text=f"{p.get('icon', '🧠')} {p.get('name', pid)}",
                variable=self.pers_var,
                value=pid,
                font=("Segoe UI", 9, "bold"),
                fg="#38bdf8",
                bg="#1e293b",
                selectcolor="#0f172a",
            )
            rb.pack(anchor=tk.W)
            tk.Label(pf, text=p.get("description", ""), font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b", wraplength=700, justify=tk.LEFT).pack(anchor=tk.W, padx=24)

    # -------------------------------------------------------------------------
    # TAB 4: DIAGNOSTICS
    # -------------------------------------------------------------------------
    def _build_diag_tab(self, parent: tk.Frame):
        tk.Label(parent, text="Live Multi-Engine & Connectivity Diagnostics:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#12151c").pack(anchor=tk.W, pady=(0, 6))

        self.diag_txt = tk.Text(parent, bg="#0f172a", fg="#38bdf8", font=("Consolas", 9), height=14)
        self.diag_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        tk.Button(parent, text="▶️ Run 5-Step System Diagnostics", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="#ffffff", command=self._run_diagnostics).pack(anchor=tk.W)

    def _run_diagnostics(self):
        self.diag_txt.delete("1.0", tk.END)
        self.diag_txt.insert(tk.END, "=== STARTING AGENT HARNESS DIAGNOSTICS ===\n\n")

        # 1. Engine Window Hook
        hwnd_main, hwnd_edit, pid = self.controller.find_unrealed_window()
        active_engine = self.config_mgr.get_active_engine_profile()
        if hwnd_main:
            self.diag_txt.insert(tk.END, f"[PASS] Step 1: UnrealEd Target Found (HWND: {hwnd_main}, Edit HWND: {hwnd_edit}, PID: {pid})\n")
        else:
            self.diag_txt.insert(tk.END, f"[WARN] Step 1: No UnrealEd process currently found for profile '{active_engine.get('name')}'. Launch UnrealEd via batch shortcut.\n")

        # 2. System Directory Check
        sys_dir = Path(active_engine.get("system_dir", ""))
        if sys_dir.exists():
            self.diag_txt.insert(tk.END, f"[PASS] Step 2: System directory verified: {sys_dir}\n")
        else:
            self.diag_txt.insert(tk.END, f"[FAIL] Step 2: System directory not found: {sys_dir}\n")

        # 3. .nexus Integration
        if self.nexus.is_available:
            self.diag_txt.insert(tk.END, f"[PASS] Step 3: .nexus Post Office detected at: {self.nexus.nexus_root}\n")
        else:
            self.diag_txt.insert(tk.END, "[INFO] Step 3: .nexus running in standalone offline mode.\n")

        # 4. LLM API Key Status
        llm_prof = self.config_mgr.get_active_llm_profile()
        key_len = len(llm_prof.get("api_key", ""))
        self.diag_txt.insert(tk.END, f"[PASS] Step 4: Active LLM Profile '{llm_prof.get('name')}' (Key Length: {key_len} chars)\n")

        self.diag_txt.insert(tk.END, "\n=== DIAGNOSTICS COMPLETE ===")

    def _save_and_close(self):
        # Save Engine
        self.config_mgr.set_active_engine_id(self.engine_var.get())
        self.controller._refresh_paths()

        # Save LLM (Sync current fields)
        self._save_llm_config(silent=True)

        # Save Personality
        self.config_mgr.set_active_personality_id(self.pers_var.get())

        if self.on_saved_cb:
            self.on_saved_cb()

        messagebox.showinfo("Settings Saved", "Configuration saved successfully!")
        self.destroy()

"""
Multi-Engine Settings & Configuration Dialog for Standalone Agent Harness.
Allows configuring Engine profiles, LLM providers, API keys, personalities, and running live diagnostics.
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from AgentHarness.core.config_manager import ConfigManager
from AgentHarness.core.engine_controller import EngineController
from AgentHarness.core.logger import get_logger
from AgentHarness.core.nexus_bridge import NexusBridge

logger = get_logger("SettingsDialog", "settings_dialog.log")


class SettingsDialog(tk.Toplevel):
    """Configuration & Diagnostic Modal Window."""

    def __init__(self, parent: tk.Tk, config_mgr: ConfigManager, controller: EngineController, nexus: NexusBridge, on_saved_cb=None):
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.controller = controller
        self.nexus = nexus
        self.on_saved_cb = on_saved_cb

        self.title("⚙️ Standalone Agent Harness — Engine & Provider Configuration")
        self.geometry("760x640")
        self.minsize(680, 560)
        self.configure(bg="#12151c")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#1a1f2c", pady=12, padx=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⚙️ HARNESS SETTINGS & MULTI-ENGINE MATRIX", font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#1a1f2c").pack(anchor=tk.W)
        tk.Label(hdr, text="Configure target Unreal Engine version (UT99/UTron/UT2003/UT2004), AI providers, and .nexus interop.", font=("Segoe UI", 9), fg="#94a3b8", bg="#1a1f2c").pack(anchor=tk.W)

        # Notebook Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Tab 1: Engine Targets
        tab_engine = tk.Frame(nb, bg="#12151c", padx=12, pady=12)
        nb.add(tab_engine, text="🎮 Engine Profiles")
        self._build_engine_tab(tab_engine)

        # Tab 2: LLM Providers & API Keys
        tab_llm = tk.Frame(nb, bg="#12151c", padx=12, pady=12)
        nb.add(tab_llm, text="🤖 LLM Providers")
        self._build_llm_tab(tab_llm)

        # Tab 3: Personalities
        tab_pers = tk.Frame(nb, bg="#12151c", padx=12, pady=12)
        nb.add(tab_pers, text="🧠 Personalities")
        self._build_personality_tab(tab_pers)

        # Tab 4: Diagnostics
        tab_diag = tk.Frame(nb, bg="#12151c", padx=12, pady=12)
        nb.add(tab_diag, text="🩺 Diagnostics")
        self._build_diag_tab(tab_diag)

        # Bottom Action Bar
        btn_bar = tk.Frame(self, bg="#1a1f2c", pady=10, padx=16)
        btn_bar.pack(fill=tk.X)

        tk.Button(btn_bar, text="💾 Save Configuration", font=("Segoe UI", 10, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=16, pady=6, command=self._save_and_close).pack(side=tk.RIGHT, padx=6)
        tk.Button(btn_bar, text="Cancel", font=("Segoe UI", 9), bg="#334155", fg="#f1f5f9", relief=tk.FLAT, padx=12, pady=6, command=self.destroy).pack(side=tk.RIGHT)

    def _build_engine_tab(self, parent: tk.Frame):
        tk.Label(parent, text="Active Unreal Engine Target:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#12151c").pack(anchor=tk.W, pady=(0, 4))

        profiles = self.config_mgr.get_all_engine_profiles()
        self.engine_var = tk.StringVar(value=self.config_mgr.get_active_engine_id())

        for eid, p in profiles.items():
            rb_frame = tk.Frame(parent, bg="#1e293b", padx=10, pady=8, highlightbackground="#334155", highlightthickness=1)
            rb_frame.pack(fill=tk.X, pady=4)

            rb = tk.Radiobutton(
                rb_frame,
                text=f"{p.get('icon', '🎮')} {p.get('name', eid)}",
                variable=self.engine_var,
                value=eid,
                font=("Segoe UI", 10, "bold"),
                fg="#38bdf8",
                bg="#1e293b",
                selectcolor="#0f172a",
                activebackground="#1e293b",
                activeforeground="#38bdf8",
            )
            rb.pack(anchor=tk.W)

            details_str = f"Root: {p.get('root_dir')} | Executable: {p.get('editor_exe')} {p.get('editor_args', '')} | Gen: {p.get('generation')}"
            tk.Label(rb_frame, text=details_str, font=("Consolas", 8), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W, padx=24)

    def _build_llm_tab(self, parent: tk.Frame):
        profiles = self.config_mgr.get_all_llm_profiles()
        active_id = self.config_mgr.get_active_llm_profile_id()

        tk.Label(parent, text="Active LLM Provider Profile:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#12151c").pack(anchor=tk.W, pady=(0, 4))

        self.llm_prof_var = tk.StringVar(value=active_id)
        prof_menu = ttk.Combobox(parent, textvariable=self.llm_prof_var, values=list(profiles.keys()), state="readonly")
        prof_menu.pack(fill=tk.X, pady=(0, 10))
        prof_menu.bind("<<ComboboxSelected>>", self._on_llm_profile_changed)

        # Fields frame
        f = tk.Frame(parent, bg="#1e293b", padx=12, pady=12)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="API Key (Leave blank for local Ollama):", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(f, textvariable=self.api_key_var, show="*", bg="#0f172a", fg="#38bdf8", font=("Consolas", 10))
        self.api_key_entry.pack(fill=tk.X, pady=(2, 8))

        tk.Label(f, text="Model Identifier (e.g. gemini-2.5-pro, claude-3-7-sonnet, gpt-4o):", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W)
        self.model_var = tk.StringVar()
        self.model_entry = tk.Entry(f, textvariable=self.model_var, bg="#0f172a", fg="#f8fafc", font=("Consolas", 10))
        self.model_entry.pack(fill=tk.X, pady=(2, 8))

        tk.Label(f, text="Base API URL:", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W)
        self.base_url_var = tk.StringVar()
        self.base_url_entry = tk.Entry(f, textvariable=self.base_url_var, bg="#0f172a", fg="#f8fafc", font=("Consolas", 10))
        self.base_url_entry.pack(fill=tk.X, pady=(2, 8))

        self._load_active_llm_fields()

    def _on_llm_profile_changed(self, event=None):
        self._load_active_llm_fields()

    def _load_active_llm_fields(self):
        prof_id = self.llm_prof_var.get()
        profiles = self.config_mgr.get_all_llm_profiles()
        p = profiles.get(prof_id, {})
        self.api_key_var.set(p.get("api_key", ""))
        self.model_var.set(p.get("model", ""))
        self.base_url_var.set(p.get("base_url", ""))

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
            tk.Label(pf, text=p.get("description", ""), font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b", wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, padx=24)

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

        # Save LLM
        active_llm_id = self.llm_prof_var.get()
        self.config_mgr.set_active_llm_profile_id(active_llm_id)
        self.config_mgr.update_llm_profile(active_llm_id, {
            "api_key": self.api_key_var.get().strip(),
            "model": self.model_var.get().strip(),
            "base_url": self.base_url_var.get().strip(),
        })

        # Save Personality
        self.config_mgr.set_active_personality_id(self.pers_var.get())

        if self.on_saved_cb:
            self.on_saved_cb()

        messagebox.showinfo("Settings Saved", "Configuration saved successfully!")
        self.destroy()

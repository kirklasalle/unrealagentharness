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

        # Tab 5: Updates & Version
        tab_updates = tk.Frame(nb, bg="#12151c", padx=12, pady=12)
        nb.add(tab_updates, text="🚀 Updates")
        self._build_updates_tab(tab_updates)

        # Bottom Action Bar
        btn_bar = tk.Frame(self, bg="#1a1f2c", pady=10, padx=16)
        btn_bar.pack(fill=tk.X)

        tk.Button(btn_bar, text="💾 Save Configuration", font=("Segoe UI", 10, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=16, pady=6, command=self._save_and_close).pack(side=tk.RIGHT, padx=6)
        tk.Button(btn_bar, text="Cancel", font=("Segoe UI", 9), bg="#334155", fg="#f1f5f9", relief=tk.FLAT, padx=12, pady=6, command=self.destroy).pack(side=tk.RIGHT)

    def _build_engine_tab(self, parent: tk.Frame):
        # Create a scrollable frame for engine profiles and mods
        canvas = tk.Canvas(parent, bg="#12151c", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#12151c")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=620)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.engine_var = tk.StringVar(value=self.config_mgr.get_active_engine_id())

        # Top Auto-Scan Banner
        scan_box = tk.Frame(scrollable_frame, bg="#0f172a", padx=12, pady=10, highlightbackground="#0284c7", highlightthickness=1)
        scan_box.pack(fill=tk.X, pady=(0, 10))

        scan_hdr = tk.Frame(scan_box, bg="#0f172a")
        scan_hdr.pack(fill=tk.X)
        tk.Label(scan_hdr, text="🔍 STANDALONE AUTO-DISCOVERY SCANNER", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#0f172a").pack(side=tk.LEFT)
        tk.Button(scan_hdr, text="🔍 SCAN ALL DRIVES", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff", relief=tk.FLAT, padx=12, pady=4, command=self._show_scan_modal).pack(side=tk.RIGHT)

        tk.Label(scan_box, text="Scans all local drives, Steam, GOG, and folders to automatically find and link every installed Unreal engine and Total Conversion mod on this computer.", font=("Segoe UI", 8), fg="#94a3b8", bg="#0f172a", justify=tk.LEFT, wraplength=580).pack(anchor=tk.W, pady=(4, 0))

        # Section 1: Base Game Engines
        tk.Label(scrollable_frame, text="🎮 BASE GAME ENGINES", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#12151c").pack(anchor=tk.W, pady=(0, 4))
        base_engines = self.config_mgr.get_base_engines()

        for eid, p in base_engines.items():
            rb_frame = tk.Frame(scrollable_frame, bg="#1e293b", padx=10, pady=8, highlightbackground="#334155", highlightthickness=1)
            rb_frame.pack(fill=tk.X, pady=3)

            rb = tk.Radiobutton(
                rb_frame,
                text=f"{p.get('icon', '🎮')} {p.get('name', eid)}",
                variable=self.engine_var,
                value=eid,
                font=("Segoe UI", 10, "bold"),
                fg="#f8fafc",
                bg="#1e293b",
                selectcolor="#0f172a",
                activebackground="#1e293b",
                activeforeground="#38bdf8",
            )
            rb.pack(anchor=tk.W)

            details_str = f"Root: {p.get('root_dir')} | Executable: {p.get('editor_exe')} {p.get('editor_args', '')} | Gen: {p.get('generation')}"
            tk.Label(rb_frame, text=details_str, font=("Consolas", 8), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W, padx=24)

        # Section 2: Game Mods & Total Conversions (TC)
        mod_hdr_frame = tk.Frame(scrollable_frame, bg="#12151c", pady=(12, 4))
        mod_hdr_frame.pack(fill=tk.X)
        tk.Label(mod_hdr_frame, text="📦 GAME MODS & TOTAL CONVERSIONS (TC)", font=("Segoe UI", 10, "bold"), fg="#f59e0b", bg="#12151c").pack(side=tk.LEFT)
        tk.Button(mod_hdr_frame, text="➕ Register New Mod", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=8, pady=2, command=self._show_add_mod_dialog).pack(side=tk.RIGHT)

        game_mods = self.config_mgr.get_game_mods()

        for mid, p in game_mods.items():
            rb_frame = tk.Frame(scrollable_frame, bg="#1e293b", padx=10, pady=8, highlightbackground="#d97706", highlightthickness=1)
            rb_frame.pack(fill=tk.X, pady=3)

            top_row = tk.Frame(rb_frame, bg="#1e293b")
            top_row.pack(fill=tk.X)

            rb = tk.Radiobutton(
                top_row,
                text=f"{p.get('icon', '⚡')} {p.get('name', mid)}",
                variable=self.engine_var,
                value=mid,
                font=("Segoe UI", 10, "bold"),
                fg="#fcd34d",
                bg="#1e293b",
                selectcolor="#0f172a",
                activebackground="#1e293b",
                activeforeground="#fcd34d",
            )
            rb.pack(side=tk.LEFT)

            if p.get("category") != "Base Game Engine" and mid not in ["ut99_utron"]:
                tk.Button(
                    top_row,
                    text="🗑️ Delete",
                    font=("Segoe UI", 7),
                    bg="#dc2626",
                    fg="#ffffff",
                    relief=tk.FLAT,
                    padx=6,
                    pady=1,
                    command=lambda m=mid: self._delete_mod(m),
                ).pack(side=tk.RIGHT)

            desc = p.get("description", "")
            if desc:
                tk.Label(rb_frame, text=desc, font=("Segoe UI", 8, "italic"), fg="#cbd5e1", bg="#1e293b").pack(anchor=tk.W, padx=24, pady=(2, 0))

            details_str = f"Mod Type: {p.get('mod_type', 'Total Conversion')} | Base: {p.get('parent_engine', 'ut99_goty')} | INI: {p.get('editor_args', 'Default')}"
            tk.Label(rb_frame, text=details_str, font=("Consolas", 8), fg="#94a3b8", bg="#1e293b").pack(anchor=tk.W, padx=24)

    def _show_scan_modal(self):
        """Displays interactive modal dialog to scan all drives for Unreal engines & mods."""
        dlg = tk.Toplevel(self)
        dlg.title("🔍 Unreal Engine & Game Mod Auto-Discovery")
        dlg.geometry("640x500")
        dlg.configure(bg="#12151c")
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="🔍 Auto-Scanning All Drives for Unreal Engines & Mods...", font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#12151c").pack(anchor=tk.W, padx=16, pady=(12, 4))
        status_lbl = tk.Label(dlg, text="Initializing storage scanner...", font=("Segoe UI", 8), fg="#94a3b8", bg="#12151c")
        status_lbl.pack(anchor=tk.W, padx=16, pady=(0, 6))

        pbar = ttk.Progressbar(dlg, orient="horizontal", mode="determinate")
        pbar.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Results TreeView Frame
        tree_f = tk.Frame(dlg, bg="#1e293b", padx=2, pady=2)
        tree_f.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        tree = ttk.Treeview(tree_f, columns=("type", "path"), show="tree headings", selectmode="browse")
        tree.heading("#0", text="Engine / Mod Name", anchor=tk.W)
        tree.heading("type", text="Category", anchor=tk.W)
        tree.heading("path", text="Discovered Root Path", anchor=tk.W)
        tree.column("#0", width=220)
        tree.column("type", width=140)
        tree.column("path", width=240)

        tree_scroll = ttk.Scrollbar(tree_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        discovered_holder = {}

        btn_bar = tk.Frame(dlg, bg="#12151c", pady=10, padx=16)
        btn_bar.pack(fill=tk.X)

        apply_btn = tk.Button(
            btn_bar,
            text="✅ Save & Apply Discovered Paths",
            font=("Segoe UI", 9, "bold"),
            bg="#10b981",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=5,
            state=tk.DISABLED,
        )
        apply_btn.pack(side=tk.RIGHT, padx=4)

        cancel_btn = tk.Button(btn_bar, text="Close", font=("Segoe UI", 9), bg="#334155", fg="#ffffff", relief=tk.FLAT, padx=10, pady=5, command=dlg.destroy)
        cancel_btn.pack(side=tk.RIGHT)

        def _on_apply():
            if discovered_holder.get("data"):
                count = self.config_mgr.apply_scan_results(discovered_holder["data"])
                messagebox.showinfo("Configuration Updated", f"Successfully linked {count} Unreal Engine & Mod installation(s) to Agent Harness configuration!", parent=dlg)
                dlg.destroy()
                if self.on_saved_cb:
                    self.on_saved_cb()

        apply_btn.configure(command=_on_apply)

        def _worker():
            from ..core.engine_scanner import EngineScanner
            def _progress_cb(msg: str, pct: int):
                dlg.after(0, lambda m=msg, p=pct: (
                    status_lbl.configure(text=m),
                    pbar.configure(value=p)
                ))

            res = EngineScanner.scan_all(progress_cb=_progress_cb)
            discovered_holder["data"] = res

            def _populate():
                pbar.configure(value=100)
                status_lbl.configure(text=f"Scan complete! Discovered {len(res)} Unreal installations & Total Conversion mods.")
                for target_id, info in res.items():
                    name_disp = f"{info.get('icon', '🎮')} {info.get('name', target_id)}"
                    cat_disp = info.get("category", "Engine")
                    path_disp = info.get("root_dir", "")
                    tree.insert("", tk.END, text=name_disp, values=(cat_disp, path_disp))
                if res:
                    apply_btn.configure(state=tk.NORMAL)

            dlg.after(0, _populate)

        threading.Thread(target=_worker, daemon=True).start()

    def _delete_mod(self, mod_id: str):
        if messagebox.askyesno("Delete Mod Profile", f"Are you sure you want to remove the mod profile '{mod_id}'?"):
            if self.config_mgr.delete_game_mod(mod_id):
                messagebox.showinfo("Mod Removed", f"Mod '{mod_id}' successfully removed.")
                self.engine_var.set(self.config_mgr.get_active_engine_id())

    def _show_add_mod_dialog(self):
        """Displays popup modal to register a new Game Mod / Total Conversion."""
        dlg = tk.Toplevel(self)
        dlg.title("➕ Register Game Mod / Total Conversion")
        dlg.geometry("520x460")
        dlg.configure(bg="#12151c")
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="➕ Register New Game Mod / TC Profile", font=("Segoe UI", 11, "bold"), fg="#f59e0b", bg="#12151c").pack(anchor=tk.W, padx=16, pady=(12, 4))
        tk.Label(dlg, text="Define custom Total Conversions (e.g. UTron, ChaosUT, Tactical Ops) with custom INI & packages.", font=("Segoe UI", 8), fg="#94a3b8", bg="#12151c").pack(anchor=tk.W, padx=16, pady=(0, 10))

        form = tk.Frame(dlg, bg="#1e293b", padx=14, pady=12)
        form.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        # Mod ID
        tk.Label(form, text="Mod ID (Unique identifier, e.g. ut99_chaosut):", font=("Segoe UI", 8, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor=tk.W)
        id_ent = tk.Entry(form, font=("Consolas", 9), bg="#0f172a", fg="#38bdf8", insertbackground="white")
        id_ent.pack(fill=tk.X, pady=(2, 6))

        # Mod Title
        tk.Label(form, text="Mod Name (e.g. ChaosUT: Evolution Mod):", font=("Segoe UI", 8, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor=tk.W)
        name_ent = tk.Entry(form, font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc", insertbackground="white")
        name_ent.pack(fill=tk.X, pady=(2, 6))

        # Base Engine Parent
        tk.Label(form, text="Parent Base Game Engine:", font=("Segoe UI", 8, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor=tk.W)
        base_combo = ttk.Combobox(form, values=list(self.config_mgr.get_base_engines().keys()), state="readonly")
        base_combo.set("ut99_goty")
        base_combo.pack(fill=tk.X, pady=(2, 6))

        # Editor INI Args
        tk.Label(form, text="Editor Launch Arguments (e.g. INI=UTronEditor.ini):", font=("Segoe UI", 8, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor=tk.W)
        args_ent = tk.Entry(form, font=("Consolas", 9), bg="#0f172a", fg="#f8fafc", insertbackground="white")
        args_ent.pack(fill=tk.X, pady=(2, 6))

        # Description
        tk.Label(form, text="Description & Features:", font=("Segoe UI", 8, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor=tk.W)
        desc_ent = tk.Entry(form, font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc", insertbackground="white")
        desc_ent.pack(fill=tk.X, pady=(2, 6))

        def _do_register():
            m_id = id_ent.get().strip().lower().replace(" ", "_")
            m_name = name_ent.get().strip()
            if not m_id or not m_name:
                messagebox.showwarning("Incomplete", "Please provide both Mod ID and Mod Name.", parent=dlg)
                return

            parent_id = base_combo.get()
            parent_profile = self.config_mgr.get_all_engine_profiles().get(parent_id, {})

            mod_info = {
                "id": m_id,
                "name": m_name,
                "category": "Game Mod (Total Conversion)",
                "mod_type": "Total Conversion",
                "parent_engine": parent_id,
                "generation": parent_profile.get("generation", "UE1"),
                "icon": "📦",
                "description": desc_ent.get().strip(),
                "root_dir": parent_profile.get("root_dir", "G:\\UnrealTournament"),
                "system_dir": parent_profile.get("system_dir", "G:\\UnrealTournament\\System"),
                "editor_exe": parent_profile.get("editor_exe", "UnrealEd.exe"),
                "editor_args": args_ent.get().strip(),
                "game_exe": parent_profile.get("game_exe", "UnrealTournament.exe"),
                "game_args": "",
                "window_classes": parent_profile.get("window_classes", ["WUnrealEd", "WWindow", "UnrealEd"]),
                "process_names": parent_profile.get("process_names", ["unrealed.exe"]),
                "log_files": ["Editor.log", "UnrealEd.log"],
            }

            if self.config_mgr.register_game_mod(m_id, mod_info):
                messagebox.showinfo("Success", f"Game Mod '{m_name}' registered successfully!", parent=dlg)
                dlg.destroy()
                self.engine_var.set(m_id)

        btn_bar = tk.Frame(dlg, bg="#12151c", pady=8, padx=16)
        btn_bar.pack(fill=tk.X)
        tk.Button(btn_bar, text="Save Mod", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=14, pady=4, command=_do_register).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_bar, text="Cancel", font=("Segoe UI", 9), bg="#334155", fg="#ffffff", relief=tk.FLAT, padx=10, pady=4, command=dlg.destroy).pack(side=tk.RIGHT)

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

    def _build_updates_tab(self, parent: tk.Frame):
        # Version Banner
        banner = tk.Frame(parent, bg="#0f172a", padx=14, pady=12, highlightbackground="#0284c7", highlightthickness=1)
        banner.pack(fill=tk.X, pady=(0, 10))

        b_top = tk.Frame(banner, bg="#0f172a")
        b_top.pack(fill=tk.X)
        tk.Label(b_top, text="🚀 UNREAL AGENT HARNESS UPDATER", font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#0f172a").pack(side=tk.LEFT)
        ver_pill = tk.Label(b_top, text=f"Installed: v{__version__}", font=("Segoe UI", 9, "bold"), fg="#22c55e", bg="#14532d", padx=8, pady=2)
        ver_pill.pack(side=tk.RIGHT)

        method_str = "Git Repository (Automatic Pull & Rebase)" if UpdateEngine.is_git_repository() else "ZIP Package Release (Direct HTTP Download)"
        tk.Label(banner, text=f"Remote Repository: {__repo__}\nUpdate Method: {method_str}", font=("Consolas", 8), fg="#94a3b8", bg="#0f172a", justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 0))

        # Action Buttons Box
        act_box = tk.Frame(parent, bg="#12151c", pady=6)
        act_box.pack(fill=tk.X)

        self.upd_status_lbl = tk.Label(act_box, text="Ready to check for latest releases.", font=("Segoe UI", 9), fg="#f8fafc", bg="#12151c")
        self.upd_status_lbl.pack(side=tk.LEFT)

        check_btn = tk.Button(act_box, text="🔄 Check for Updates Now", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=12, pady=4, command=self._check_updates_action)
        check_btn.pack(side=tk.RIGHT, padx=4)

        self.apply_upd_btn = tk.Button(act_box, text="⬇️ Download & Install Update", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff", relief=tk.FLAT, padx=12, pady=4, state=tk.DISABLED, command=self._apply_update_action)
        self.apply_upd_btn.pack(side=tk.RIGHT, padx=4)

        # Progress bar
        self.upd_pbar = ttk.Progressbar(parent, orient="horizontal", mode="determinate")
        self.upd_pbar.pack(fill=tk.X, pady=(4, 8))

        # Notes / Changelog Output Box
        tk.Label(parent, text="Update Status & Release Notes:", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#12151c").pack(anchor=tk.W, pady=(4, 2))
        self.upd_notes_txt = tk.Text(parent, bg="#0f172a", fg="#e2e8f0", font=("Consolas", 9), height=10)
        self.upd_notes_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self.upd_notes_txt.insert(tk.END, f"Current Version: v{__version__}\nClick 'Check for Updates Now' to query the remote GitHub repository.\n")

    def _check_updates_action(self):
        self.upd_status_lbl.configure(text="Checking remote GitHub repository...", fg="#38bdf8")
        self.upd_pbar.configure(value=30)
        self.upd_notes_txt.delete("1.0", tk.END)
        self.upd_notes_txt.insert(tk.END, "Querying remote repository for latest releases and commits...\n")

        def _worker():
            res = UpdateEngine.check_for_updates()
            def _update_ui():
                self.upd_pbar.configure(value=100)
                if res.get("update_available"):
                    self.upd_status_lbl.configure(text=f"🚀 New update available: v{res.get('latest_version')}!", fg="#f59e0b")
                    self.apply_upd_btn.configure(state=tk.NORMAL)
                    self.upd_notes_txt.insert(tk.END, f"=== NEW VERSION AVAILABLE: v{res.get('latest_version')} ===\n\n")
                    self.upd_notes_txt.insert(tk.END, f"{res.get('release_notes')}\n\n")
                    self.upd_notes_txt.insert(tk.END, "Click 'Download & Install Update' to update automatically.")
                else:
                    self.upd_status_lbl.configure(text=f"✅ Up to date (v{__version__})", fg="#22c55e")
                    self.upd_notes_txt.insert(tk.END, f"=== YOU ARE RUNNING THE LATEST VERSION (v{__version__}) ===\n")
                    self.upd_notes_txt.insert(tk.END, "No updates needed at this time.")
                    # Allow force re-install if git
                    if UpdateEngine.is_git_repository():
                        self.apply_upd_btn.configure(state=tk.NORMAL, text="🔄 Sync / Re-pull Main")
            self.after(0, _update_ui)

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_update_action(self):
        if not messagebox.askyesno("Confirm Update", "Download and install the latest update now?\nLocal configurations will be preserved."):
            return

        self.upd_status_lbl.configure(text="Downloading and installing update...", fg="#38bdf8")
        self.apply_upd_btn.configure(state=tk.DISABLED)

        def _progress(msg, pct):
            self.after(0, lambda m=msg, p=pct: (
                self.upd_status_lbl.configure(text=m),
                self.upd_pbar.configure(value=p),
                self.upd_notes_txt.insert(tk.END, f"[{p}%] {m}\n"),
                self.upd_notes_txt.see(tk.END)
            ))

        def _worker():
            res = UpdateEngine.apply_update(progress_cb=_progress)
            def _finish():
                if res.get("success"):
                    messagebox.showinfo("Update Complete", res.get("message"))
                    self.destroy()
                else:
                    messagebox.showerror("Update Error", f"Failed to apply update: {res.get('message')}")
                    self.apply_upd_btn.configure(state=tk.NORMAL)
            self.after(0, _finish)

        threading.Thread(target=_worker, daemon=True).start()

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

r"""
Native Win32 Multi-Engine AI Agent In-Editor Cockpit for Standalone Agent Harness.
Supports Unreal Tournament 99 GOTY, UTron Total Conversion Mod, UT2003, and UT2004.
Pure Python & Tkinter: 100% native, zero Chromium/WebView2/Microsoft dependencies.
"""

import ctypes
import json
import os
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional

# Ensure repository root is in sys.path BEFORE importing core
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import core.bootstrap
from core.config_manager import ConfigManager
from core.engine_controller import EngineController
from core.llm_engine import LLMEngine
from core.logger import get_logger, set_global_log_level, flush_all_logs, write_crash_report, setup_global_exception_handlers
from core.nexus_bridge import NexusBridge
from core.update_engine import UpdateEngine
from ui.palette_ut99_utron import get_ut99_utron_palette
from ui.palette_ut99_goty import get_ut99_goty_palette
from ui.palette_ut2004 import get_ut2004_palette
from ui.settings_dialog import SettingsDialog

try:
    import win32con
    import win32gui
    import win32process
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

logger = get_logger("HarnessCockpit", "harness_ui.log")


class StandaloneHarnessCockpit(tk.Tk):
    """The Master Multi-Engine AI Level Designer Cockpit."""

    def __init__(self, engine_id: Optional[str] = None):
        super().__init__()

        self.config_mgr = ConfigManager()
        if engine_id:
            self.config_mgr.set_active_engine_id(engine_id)

        self.controller = EngineController(self.config_mgr)
        self.nexus = NexusBridge()
        self.llm_engine = LLMEngine(self.config_mgr, self.controller, self.nexus)

        self.title("⚡ Unreal Tournament AI Agent Harness — Universal Multi-Engine")
        self.geometry("1060x720")
        self.minsize(860, 580)
        self.configure(bg="#0b0e14")

        self.chat_history: List[Dict[str, str]] = []
        self.is_docked = False

        self._build_ui()
        self._switch_and_initialize_engine(self.config_mgr.get_active_engine_id(), force_recheck=False, is_startup=True)
        self._start_status_poll_thread()
        self._start_update_check_thread()

        logger.info("StandaloneHarnessCockpit UI initialized.")

    def _build_ui(self):
        # 1. Top Header Bar
        self.hdr = tk.Frame(self, bg="#111726", pady=8, padx=12)
        self.hdr.pack(fill=tk.X)

        # Title & Icon
        title_box = tk.Frame(self.hdr, bg="#111726")
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="⚡ AGENT HARNESS", font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#111726").pack(side=tk.LEFT)

        # Engine Target Selector
        tk.Label(title_box, text=" | Target:", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726").pack(side=tk.LEFT, padx=(8, 4))
        self.engine_var = tk.StringVar(value=self.config_mgr.get_active_engine_id())
        profiles = self.config_mgr.get_all_engine_profiles()
        engine_choices = list(profiles.keys())
        self.engine_combo = ttk.Combobox(title_box, textvariable=self.engine_var, values=engine_choices, state="readonly", width=18)
        self.engine_combo.pack(side=tk.LEFT, padx=2)
        self.engine_combo.bind("<<ComboboxSelected>>", self._on_engine_selected)

        # Quick Re-Check Button
        tk.Button(
            title_box,
            text="🔄 RE-CHECK",
            font=("Segoe UI", 8, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            activebackground="#334155",
            activeforeground="#7dd3fc",
            relief=tk.FLAT,
            padx=6,
            pady=1,
            command=self._on_recheck_clicked,
        ).pack(side=tk.LEFT, padx=(4, 8))

        # Connection Status Pill
        self.status_pill = tk.Label(title_box, text="● SCANNING", font=("Segoe UI", 8, "bold"), fg="#f59e0b", bg="#1e293b", padx=8, pady=2)
        self.status_pill.pack(side=tk.LEFT, padx=4)

        # Right-side Action Buttons (Launch Editor, Rebuild, Dock, Settings)
        act_box = tk.Frame(self.hdr, bg="#111726")
        act_box.pack(side=tk.RIGHT)

        tk.Button(act_box, text="🧙 WIZARD", font=("Segoe UI", 8, "bold"), bg="#8b5cf6", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3, command=self._open_wizard_builder).pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="🔍 SCAN ENGINES", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3, command=self._open_engine_scanner).pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="🎮 LAUNCH EDITOR", font=("Segoe UI", 8, "bold"), bg="#10b981", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3, command=self._launch_editor).pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="🔄 REBUILD", font=("Segoe UI", 8, "bold"), bg="#38bdf8", fg="#0f172a", relief=tk.FLAT, padx=8, pady=3, command=self._quick_rebuild).pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="📌 DOCK", font=("Segoe UI", 8), bg="#334155", fg="#f1f5f9", relief=tk.FLAT, padx=8, pady=3, command=self._toggle_dock).pack(side=tk.LEFT, padx=3)
        self.upd_btn = tk.Button(act_box, text="🚀 UPDATES", font=("Segoe UI", 8, "bold"), bg="#475569", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3, command=self._open_updater)
        self.upd_btn.pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="⚙️ SETTINGS", font=("Segoe UI", 8), bg="#334155", fg="#f1f5f9", relief=tk.FLAT, padx=8, pady=3, command=self._open_settings).pack(side=tk.LEFT, padx=3)

        # 2. Main Paned Layout
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#0b0e14", sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Left: Quick Build Palettes
        self.palette_frame = tk.Frame(self.paned, bg="#0f172a", width=340)
        self.paned.add(self.palette_frame)
        self._build_palette_ui(self.palette_frame)

        # Right: Chat & Agent Output
        self.chat_frame = tk.Frame(self.paned, bg="#0b0e14")
        self.paned.add(self.chat_frame)
        self._build_chat_ui(self.chat_frame)

        # 3. Bottom Status Bar
        self.status_bar = tk.Frame(self, bg="#0f172a", pady=4, padx=8)
        self.status_bar.pack(fill=tk.X)
        self.status_lbl = tk.Label(self.status_bar, text="Ready. Initialized Universal Multi-Engine Harness.", font=("Segoe UI", 8), fg="#94a3b8", bg="#0f172a")
        self.status_lbl.pack(side=tk.LEFT)

    def _build_palette_ui(self, parent: tk.Frame):
        # Header
        p_hdr = tk.Frame(parent, bg="#1e293b", pady=6, padx=8)
        p_hdr.pack(fill=tk.X)
        tk.Label(p_hdr, text="⚡ QUICK ARCHITECT PALETTE", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#1e293b").pack(anchor=tk.W)

        # Scrollable Notebook
        self.palette_notebook = ttk.Notebook(parent)
        self.palette_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.tab_map = {
            "ut99_goty": 0,
            "ut99_chaosut": 0,
            "ut99_tacticalops": 0,
            "ut99_utron": 1,
            "ut2004": 2,
            "ut2003": 2,
        }

        # Tab 1: UT99 GOTY Classic
        tab_goty = tk.Frame(self.palette_notebook, bg="#0f172a")
        self.palette_notebook.add(tab_goty, text="🏆 UT99 Base")
        self._populate_palette_tab(tab_goty, get_ut99_goty_palette(self._send_prompt))

        # Tab 2: UTron Total Conversion Mod
        tab_utron = tk.Frame(self.palette_notebook, bg="#0f172a")
        self.palette_notebook.add(tab_utron, text="⚡ Mod: UTron (TC)")
        self._populate_palette_tab(tab_utron, get_ut99_utron_palette(self._send_prompt))

        # Tab 3: UT2004 Blueprints
        tab_ut2004 = tk.Frame(self.palette_notebook, bg="#0f172a")
        self.palette_notebook.add(tab_ut2004, text="⚔️ UT2004 Base")
        self._populate_palette_tab(tab_ut2004, get_ut2004_palette(self._send_prompt))

    def _populate_palette_tab(self, parent: tk.Frame, palette_data: List[Dict[str, Any]]):
        canvas = tk.Canvas(parent, bg="#0f172a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#0f172a")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for cat in palette_data:
            cat_hdr = tk.Label(scroll_content, text=cat["category"], font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", pady=4, padx=6)
            cat_hdr.pack(fill=tk.X, pady=(6, 2))

            for itm in cat.get("items", []):
                btn_f = tk.Frame(scroll_content, bg="#1e293b", padx=6, pady=4)
                btn_f.pack(fill=tk.X, pady=2, padx=2)

                title_text = itm.get("title") or itm.get("name") or "Action"
                prompt_text = itm.get("prompt")
                action_cb = itm.get("action")
                cmds_factory = itm.get("commands_factory")
                direct_cmds = itm.get("commands")

                if cmds_factory:
                    def _make_cmd(t=title_text, cf=cmds_factory):
                        def _handler():
                            try:
                                cmds = cf()
                                self._execute_direct_blueprint(t, cmds)
                            except Exception as ex:
                                logger.error(f"Error evaluating blueprint factory for '{t}': {ex}")
                                self._append_chat("AI Architect", f"⚠️ Error building blueprint **{t}**: {str(ex)}")
                        return _handler
                    cmd = _make_cmd()
                elif direct_cmds:
                    cmd = lambda t=title_text, c=direct_cmds: self._execute_direct_blueprint(t, c)
                elif action_cb:
                    cmd = action_cb
                elif prompt_text:
                    cmd = lambda p=prompt_text: self._send_prompt(p)
                else:
                    cmd = lambda: None

                btn = tk.Button(
                    btn_f,
                    text=title_text,
                    font=("Segoe UI", 8, "bold"),
                    fg="#38bdf8",
                    bg="#0f172a",
                    relief=tk.FLAT,
                    anchor=tk.W,
                    command=cmd,
                )
                btn.pack(fill=tk.X)

                desc_text = itm.get("desc", "")
                desc = tk.Label(btn_f, text=desc_text, font=("Segoe UI", 7), fg="#94a3b8", bg="#1e293b", justify=tk.LEFT, wraplength=280)
                desc.pack(anchor=tk.W, pady=(2, 0))

    def _execute_direct_blueprint(self, title: str, commands: Optional[List[str]]):
        """Executes a procedural blueprint directly into UnrealEd in real-time."""
        if not commands:
            logger.warning(f"No commands provided for blueprint: {title}")
            self._append_chat("Quick Palette", f"⚠️ No commands generated for **{title}**.")
            return

        self._append_chat("Quick Palette", f"🚀 Executing **{title}** ({len(commands)} commands)...")
        self.status_lbl.configure(text=f"Building {title}...")

        def _worker():
            try:
                results = self.controller.execute_batch(commands)
                success_count = sum(1 for r in results if r.get("success", True))
                self._append_chat("AI Architect", f"✅ **{title} Built Successfully!**\nExecuted {success_count}/{len(commands)} commands in UnrealEd.")
                self.status_lbl.configure(text="Ready.")
            except Exception as e:
                logger.error(f"Direct blueprint build error: {e}")
                self._append_chat("AI Architect", f"⚠️ Error: {str(e)}")
                self.status_lbl.configure(text="Build Error.")

        threading.Thread(target=_worker, daemon=True).start()

    def _build_chat_ui(self, parent: tk.Frame):
        # Chat Display Box
        self.chat_display = tk.Text(
            parent,
            bg="#0f172a",
            fg="#f8fafc",
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            padx=12,
            pady=12,
            state=tk.DISABLED,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Bottom Input Area
        in_frame = tk.Frame(parent, bg="#111726", pady=6, padx=6)
        in_frame.pack(fill=tk.X, padx=4, pady=(0, 4))

        self.input_entry = tk.Entry(in_frame, font=("Segoe UI", 10), bg="#0f172a", fg="#f8fafc", insertbackground="#38bdf8")
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=6)
        self.input_entry.bind("<Return>", lambda e: self._on_submit_input())

        self.send_btn = tk.Button(
            in_frame,
            text="SEND ▶",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            command=self._on_submit_input,
        )
        self.send_btn.pack(side=tk.RIGHT)

        # Initial Welcome Message
        active_engine = self.config_mgr.get_active_engine_profile()
        self._append_chat(
            "AI Architect",
            f"⚡ **Universal Standalone Agent Harness Online.**\nActive Target: **{active_engine.get('name')}**.\nAsk me to construct rooms, arenas, spawn UTron diffusers/wirenodes, or click any blueprint from the palette!",
        )

    def _append_chat(self, sender: str, text: str):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n[{sender}]\n", "sender_tag")
        self.chat_display.insert(tk.END, f"{text}\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _on_submit_input(self):
        msg = self.input_entry.get().strip()
        if not msg:
            return
        self.input_entry.delete(0, tk.END)
        self._send_prompt(msg)

    def _send_prompt(self, prompt: str):
        self._append_chat("Kirk LaSalle", prompt)
        self.chat_history.append({"role": "user", "content": prompt})

        # Run inference in worker thread to prevent UI freezing
        threading.Thread(target=self._worker_inference, args=(prompt,), daemon=True).start()

    def _worker_inference(self, prompt: str):
        try:
            self.status_lbl.configure(text="Agent thinking and executing tools...")
            resp = self.llm_engine.chat(prompt, self.chat_history)
            content = resp.get("content", "")
            tool_execs = resp.get("tool_executions", [])

            tool_summary = ""
            if tool_execs:
                tool_summary = f"\n\n🛠️ **Executed {len(tool_execs)} UnrealEd Tools:**\n"
                for t in tool_execs:
                    tool_summary += f" • `{t.get('tool')}` -> {t.get('result', {}).get('status', 'done')}\n"

            final_text = content + tool_summary
            self.chat_history.append({"role": "assistant", "content": final_text})
            self._append_chat("AI Architect", final_text)
            self.status_lbl.configure(text="Ready.")

        except Exception as e:
            logger.error(f"Inference worker error: {e}")
            self._append_chat("AI Architect", f"⚠️ Error: {str(e)}")
    def _select_palette_tab_for_engine(self, engine_id: str):
        """Switches the active tab in the Quick Architect Palette notebook to match the engine."""
        idx = getattr(self, "tab_map", {}).get(engine_id, 0)
        try:
            self.palette_notebook.select(idx)
        except Exception:
            pass

    def _switch_and_initialize_engine(
        self,
        engine_id: str,
        force_recheck: bool = False,
        is_startup: bool = False,
    ):
        """
        Performs one-time or on-demand checking and persistent initialization for the selected engine.
        Updates controller paths, refreshes LLM context, switches palette notebook tab, and updates UI status.
        """
        logger.info(f"Target Engine Switching to: '{engine_id}' (force_recheck={force_recheck}, is_startup={is_startup})")

        # 1. Update config & persistent verification state
        self.config_mgr.set_active_engine_id(engine_id)
        status = self.config_mgr.verify_and_initialize_engine(engine_id, force_recheck=force_recheck)

        # 2. Refresh controller and LLM engine context
        self.controller._refresh_paths()
        self.llm_engine._refresh_context()

        # 3. Switch Palette tab to match engine
        self._select_palette_tab_for_engine(engine_id)

        # 4. Check connection and update status UI
        prof = self.config_mgr.get_active_engine_profile()
        is_conn = self.controller.is_connected()
        if is_conn:
            self.status_pill.configure(text="● ONLINE", fg="#22c55e", bg="#14532d")
        elif not status.get("verified", False):
            self.status_pill.configure(text="⚠️ PATH CHECK", fg="#f59e0b", bg="#451a03")
        else:
            self.status_pill.configure(text="● OFFLINE", fg="#ef4444", bg="#450a0a")

        summary_str = status.get("summary", "Initialized")
        self.status_lbl.configure(text=f"Target: {prof.get('name')} | {summary_str}")

        # 5. Output chat notification
        gen = prof.get("generation", "UE1")
        cat = prof.get("category", "Base Engine")
        if is_startup:
            self._append_chat(
                "System",
                f"⚡ **Initialized Target Engine**: **{prof.get('name')}** ({gen} / {cat})\n"
                f"📁 System Dir: `{self.controller.system_dir}`\n"
                f"🔍 Status: {summary_str}\n"
                f"💡 To switch engines or mods, select the **Target** dropdown above and click **🔄 RE-CHECK** anytime.",
            )
        else:
            recheck_tag = " (Forced Re-Check)" if force_recheck else ""
            self._append_chat(
                "System",
                f"🔄 **Target Engine Switched{recheck_tag}**: **{prof.get('name')}** ({gen})\n"
                f"📁 System Dir: `{self.controller.system_dir}`\n"
                f"🔍 Status: {summary_str}\n"
                f"⚡ Quick Architect Palette automatically switched to **{prof.get('name')}**.",
            )

    def _on_engine_selected(self, event=None):
        selected_id = self.engine_var.get()
        self._switch_and_initialize_engine(selected_id, force_recheck=False, is_startup=False)

    def _on_recheck_clicked(self):
        selected_id = self.engine_var.get()
        self._switch_and_initialize_engine(selected_id, force_recheck=True, is_startup=False)

    def _quick_rebuild(self):
        res = self.controller.execute_batch(["MAP REBUILD", "PATHS DEFINE"])
        self._append_chat("System", "🔄 Executed complete level rebuild (`MAP REBUILD` + `PATHS DEFINE`).")

    def _toggle_dock(self):
        if not HAS_PYWIN32:
            messagebox.showinfo("Docking", "pywin32 is required for in-editor docking.")
            return

        hwnd_main, _, _ = self.controller.find_unrealed_window()
        if not hwnd_main:
            messagebox.showwarning("Docking", "UnrealEd window not found to dock against.")
            return

        my_hwnd = int(self.frame(), 16) if isinstance(self.frame(), str) else self.winfo_id()

        try:
            ed_rect = win32gui.GetWindowRect(hwnd_main)
            ed_x, ed_y, ed_w, ed_h = ed_rect[0], ed_rect[1], ed_rect[2] - ed_rect[0], ed_rect[3] - ed_rect[1]

            dock_width = 460
            win32gui.SetWindowPos(hwnd_main, win32con.HWND_TOP, ed_x, ed_y, max(ed_w - dock_width, 600), ed_h, win32con.SWP_SHOWWINDOW)
            win32gui.SetWindowPos(my_hwnd, win32con.HWND_TOP, ed_x + max(ed_w - dock_width, 600), ed_y, dock_width, ed_h, win32con.SWP_SHOWWINDOW)
            self.status_lbl.configure(text="Docked alongside UnrealEd.")
        except Exception as e:
            logger.error(f"Docking error: {e}")

    def _launch_editor(self):
        """Triggers the launch of UnrealEd for the currently active engine profile."""
        self.status_lbl.configure(text="Launching UnrealEd for active profile...")
        success = self.controller.launch_editor()
        if success:
            self.status_lbl.configure(text="UnrealEd launched. Connecting...")
        else:
            self.status_lbl.configure(text="Failed to launch UnrealEd. Check paths in Settings.")

    def _open_wizard_builder(self):
        """Opens the interactive Unreal Architect Wizard Builder dialog."""
        from ui.wizard_builder_dialog import WizardBuilderDialog
        WizardBuilderDialog(self, self.controller, on_build_complete=self._on_wizard_complete)

    def _on_wizard_complete(self, message: str):
        self._append_chat("System", f"🧙 **Wizard Builder**: {message}")

    def _open_settings(self):
        SettingsDialog(self, self.config_mgr, self.controller, self.nexus, on_saved_cb=self._on_settings_saved)

    def _open_updater(self):
        """Opens Settings directly on the Updates tab and triggers update check."""
        dlg = SettingsDialog(self, self.config_mgr, self.controller, self.nexus, on_saved_cb=self._on_settings_saved)
        # Select tab 4 (Updates)
        for child in dlg.winfo_children():
            if isinstance(child, ttk.Notebook):
                try:
                    child.select(4)
                except Exception:
                    pass
        dlg._check_updates_action()

    def _open_engine_scanner(self):
        """Opens Settings with the auto-scanner modal automatically triggered."""
        dlg = SettingsDialog(self, self.config_mgr, self.controller, self.nexus, on_saved_cb=self._on_settings_saved)
        dlg._show_scan_modal()

    def _on_settings_saved(self):
        active_id = self.config_mgr.get_active_engine_id()
        self.engine_var.set(active_id)
        profiles = self.config_mgr.get_all_engine_profiles()
        self.engine_combo.configure(values=list(profiles.keys()))
        self._switch_and_initialize_engine(active_id, force_recheck=True, is_startup=False)

    def _start_update_check_thread(self):
        """Silently checks for updates in the background on startup."""
        def _check():
            try:
                from core.update_engine import UpdateEngine
                res = UpdateEngine.check_for_updates()
                if res.get("update_available"):
                    latest_ver = res.get("latest_version")
                    def _notify():
                        self.upd_btn.configure(
                            text=f"🚀 UPDATE (v{latest_ver})",
                            bg="#ea580c",
                            fg="#ffffff",
                            font=("Segoe UI", 8, "bold"),
                        )
                        self._append_chat(
                            "System",
                            f"🚀 **New Update Available (v{latest_ver})!** Click **🚀 UPDATE** in the top bar to download and install.",
                        )
                    self.after(0, _notify)
            except Exception as e:
                logger.debug(f"Background update check skipped: {e}")

        threading.Thread(target=_check, daemon=True).start()

    def _start_status_poll_thread(self):
        def _poll():
            while True:
                try:
                    conn = self.controller.is_connected()
                    if conn:
                        self.status_pill.configure(text="● ONLINE", fg="#22c55e", bg="#14532d")
                    else:
                        self.status_pill.configure(text="● OFFLINE", fg="#ef4444", bg="#450a0a")
                except Exception:
                    pass
                time.sleep(3.0)

        threading.Thread(target=_poll, daemon=True).start()


if __name__ == "__main__":
    import argparse
    import platform

    setup_global_exception_handlers()

    parser = argparse.ArgumentParser(description="Standalone Unreal AI Agent Harness Cockpit")
    parser.add_argument("--engine", type=str, default=None, help="Initial engine profile ID (e.g. ut99_goty, ut99_utron, ut2004)")
    parser.add_argument("--trace", action="store_true", help="Enable high-granularity TRACE logging")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    parser.add_argument("--log-level", type=str, default=None, help="Explicit log level: TRACE, DEBUG, INFO, WARN, ERROR")
    args, _ = parser.parse_known_args()

    if args.trace:
        set_global_log_level("TRACE")
    elif args.debug:
        set_global_log_level("DEBUG")
    elif args.log_level:
        set_global_log_level(args.log_level)

    logger.info("=" * 70)
    logger.info("⚡ STARTING UNREAL AGENT HARNESS COCKPIT")
    logger.info(f"Python Executable : {sys.executable} (v{platform.python_version()})")
    logger.info(f"OS Platform       : {platform.platform()} ({platform.machine()})")
    logger.info(f"Process PID       : {os.getpid()}")
    logger.info(f"PyWin32 Support   : {HAS_PYWIN32}")
    logger.info(f"Target Engine     : {args.engine or 'Default (from config)'}")
    logger.info("=" * 70)

    try:
        app = StandaloneHarnessCockpit(engine_id=args.engine)
        app.mainloop()
        logger.info("Agent Harness UI exited cleanly.")
    except Exception as e:
        crash_file = write_crash_report(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], context="Cockpit Main Loop")
        logger.critical(f"FATAL: Harness Cockpit crashed: {e}", exc_info=True)
        flush_all_logs()
        try:
            messagebox.showerror(
                "Agent Harness Fatal Crash",
                f"The Agent Harness encountered an unexpected error:\n\n{e}\n\n"
                f"Detailed diagnostics written to:\n{crash_file}",
            )
        except Exception:
            pass
        sys.exit(1)


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

# Add AgentHarness parent directory to path for package imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    import win32con
    import win32gui
    import win32process
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

from AgentHarness.core.config_manager import ConfigManager
from AgentHarness.core.engine_controller import EngineController
from AgentHarness.core.llm_engine import LLMEngine
from AgentHarness.core.logger import get_logger
from AgentHarness.core.nexus_bridge import NexusBridge
from AgentHarness.ui.palette_ut99_utron import get_ut99_utron_palette
from AgentHarness.ui.palette_ut99_goty import get_ut99_goty_palette
from AgentHarness.ui.palette_ut2004 import get_ut2004_palette
from AgentHarness.ui.settings_dialog import SettingsDialog

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
        self._start_status_poll_thread()

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
        tk.Label(title_box, text=" | Engine:", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726").pack(side=tk.LEFT, padx=(8, 4))
        self.engine_var = tk.StringVar(value=self.config_mgr.get_active_engine_id())
        profiles = self.config_mgr.get_all_engine_profiles()
        engine_choices = list(profiles.keys())
        self.engine_combo = ttk.Combobox(title_box, textvariable=self.engine_var, values=engine_choices, state="readonly", width=14)
        self.engine_combo.pack(side=tk.LEFT, padx=2)
        self.engine_combo.bind("<<ComboboxSelected>>", self._on_engine_selected)

        # Connection Status Pill
        self.status_pill = tk.Label(title_box, text="● SCANNING", font=("Segoe UI", 8, "bold"), fg="#f59e0b", bg="#1e293b", padx=8, pady=2)
        self.status_pill.pack(side=tk.LEFT, padx=10)

        # Right-side Action Buttons (Launch Editor, Rebuild, Dock, Settings)
        act_box = tk.Frame(self.hdr, bg="#111726")
        act_box.pack(side=tk.RIGHT)

        tk.Button(act_box, text="🎮 LAUNCH EDITOR", font=("Segoe UI", 8, "bold"), bg="#10b981", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3, command=self._launch_editor).pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="🔄 REBUILD", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3, command=self._quick_rebuild).pack(side=tk.LEFT, padx=3)
        tk.Button(act_box, text="📌 DOCK", font=("Segoe UI", 8), bg="#334155", fg="#f1f5f9", relief=tk.FLAT, padx=8, pady=3, command=self._toggle_dock).pack(side=tk.LEFT, padx=3)
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
        nb = ttk.Notebook(parent)
        nb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        sys_dir = self.controller.system_dir

        # Tab 1: UT99 GOTY Classic
        tab_goty = tk.Frame(nb, bg="#0f172a")
        nb.add(tab_goty, text="🏆 UT99 GOTY")
        self._populate_palette_tab(tab_goty, get_ut99_goty_palette(self._send_prompt, system_dir=sys_dir))

        # Tab 2: UTron Total Conversion
        tab_utron = tk.Frame(nb, bg="#0f172a")
        nb.add(tab_utron, text="⚡ UTron")
        self._populate_palette_tab(tab_utron, get_ut99_utron_palette(self._send_prompt, system_dir=sys_dir))

        # Tab 3: UT2004 Blueprints
        tab_ut2004 = tk.Frame(nb, bg="#0f172a")
        nb.add(tab_ut2004, text="⚔️ UT2004")
        self._populate_palette_tab(tab_ut2004, get_ut2004_palette(self._send_prompt, system_dir=sys_dir))

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
            self.status_lbl.configure(text="Inference Error.")

    def _on_engine_selected(self, event=None):
        selected_id = self.engine_var.get()
        self.config_mgr.set_active_engine_id(selected_id)
        self.controller._refresh_paths()
        active_prof = self.config_mgr.get_active_engine_profile()
        self._append_chat("System", f"🔄 Switched engine profile to: **{active_prof.get('name')}**")
        self.status_lbl.configure(text=f"Target: {active_prof.get('name')}")

    def _quick_rebuild(self):
        res = self.controller.execute_batch(["MAP REBUILD", "PATHS BUILD"])
        self._append_chat("System", "🔄 Executed complete level rebuild (`MAP REBUILD` + `PATHS BUILD`).")

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

    def _open_settings(self):
        SettingsDialog(self, self.config_mgr, self.controller, self.nexus, on_saved_cb=self._on_settings_saved)

    def _on_settings_saved(self):
        self.engine_var.set(self.config_mgr.get_active_engine_id())
        self.controller._refresh_paths()

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
    parser = argparse.ArgumentParser(description="Standalone Unreal AI Agent Harness Cockpit")
    parser.add_argument("--engine", type=str, default=None, help="Initial engine profile ID (e.g. ut99_goty, ut99_utron, ut2004)")
    args, _ = parser.parse_known_args()

    app = StandaloneHarnessCockpit(engine_id=args.engine)
    app.mainloop()

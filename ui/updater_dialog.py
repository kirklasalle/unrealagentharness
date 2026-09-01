"""
Dedicated Standalone System Updater Dialog for Unreal Agent Harness.
Checks remote Git repository/GitHub API, presents change logs, backs up configurations,
and applies updates with real-time progress reporting.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core.logger import get_logger
from core.update_engine import UpdateEngine

logger = get_logger("UpdaterDialog", "updater.log")


class UpdaterDialog(tk.Toplevel):
    """Dedicated standalone modal dialog for checking and applying software updates."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.title("🚀 Unreal Agent Harness — System Updater")
        self.geometry("640x520")
        self.configure(bg="#0b0e14")
        self.resizable(False, False)

        # Center relative to parent
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._check_updates()

    def _build_ui(self):
        # 1. Header Banner
        hdr = tk.Frame(self, bg="#111726", padx=16, pady=12)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="🚀 SOFTWARE UPDATER & VERSION CONTROL",
            font=("Segoe UI", 12, "bold"),
            fg="#38bdf8",
            bg="#111726",
        ).pack(anchor=tk.W)

        curr_ver = UpdateEngine.get_current_version()
        self.ver_label = tk.Label(
            hdr,
            text=f"Installed Version: v{curr_ver}  |  Checking remote repository...",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#111726",
        )
        self.ver_label.pack(anchor=tk.W, pady=(2, 0))

        # 2. Main Content Body
        body = tk.Frame(self, bg="#0b0e14", padx=16, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # Status Summary Card
        self.status_card = tk.Frame(body, bg="#1e293b", padx=12, pady=10, highlightbackground="#334155", highlightthickness=1)
        self.status_card.pack(fill=tk.X, pady=(0, 10))

        self.status_title = tk.Label(
            self.status_card,
            text="⏳ Checking for updates on origin/main...",
            font=("Segoe UI", 10, "bold"),
            fg="#f59e0b",
            bg="#1e293b",
        )
        self.status_title.pack(anchor=tk.W)

        self.status_desc = tk.Label(
            self.status_card,
            text="Connecting to remote repository to inspect latest commits and releases...",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#1e293b",
        )
        self.status_desc.pack(anchor=tk.W, pady=(2, 0))

        # Release Notes / Commit Log
        tk.Label(
            body,
            text="Repository Change Log & Release Notes:",
            font=("Segoe UI", 9, "bold"),
            fg="#cbd5e1",
            bg="#0b0e14",
        ).pack(anchor=tk.W, pady=(0, 4))

        self.log_txt = tk.Text(body, bg="#0f172a", fg="#38bdf8", font=("Consolas", 9), height=10, relief=tk.FLAT, padx=8, pady=8)
        self.log_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Progress Bar
        self.pbar = ttk.Progressbar(body, orient="horizontal", mode="determinate")
        self.pbar.pack(fill=tk.X, pady=(0, 6))

        self.progress_lbl = tk.Label(body, text="", font=("Segoe UI", 8), fg="#38bdf8", bg="#0b0e14")
        self.progress_lbl.pack(anchor=tk.W)

        # 3. Action Button Bar
        btn_bar = tk.Frame(self, bg="#111726", padx=16, pady=10)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.recheck_btn = tk.Button(
            btn_bar,
            text="🔄 RE-CHECK REPO",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self._check_updates,
        )
        self.recheck_btn.pack(side=tk.LEFT)

        tk.Button(
            btn_bar,
            text="CLOSE",
            font=("Segoe UI", 9),
            bg="#334155",
            fg="#f1f5f9",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.destroy,
        ).pack(side=tk.RIGHT, padx=(6, 0))

        self.apply_btn = tk.Button(
            btn_bar,
            text="📥 UPDATE TO LATEST VERSION",
            font=("Segoe UI", 9, "bold"),
            bg="#059669",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            state=tk.DISABLED,
            command=self._apply_update,
        )
        self.apply_btn.pack(side=tk.RIGHT)

    def _check_updates(self):
        self.recheck_btn.configure(state=tk.DISABLED)
        self.apply_btn.configure(state=tk.DISABLED)
        self.status_title.configure(text="⏳ Fetching remote changes from GitHub origin/main...", fg="#f59e0b")
        self.status_desc.configure(text="Running git fetch to compare local workspace against origin/main...")
        self.log_txt.delete("1.0", tk.END)
        self.log_txt.insert(tk.END, "Inspecting repository status...\n")

        def _worker():
            res = UpdateEngine.check_for_updates()
            self.after(0, lambda: self._on_check_complete(res))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_check_complete(self, res):
        self.recheck_btn.configure(state=tk.NORMAL)
        curr_ver = res.get("current_version", UpdateEngine.get_current_version())
        latest_ver = res.get("latest_version", curr_ver)
        commits_behind = res.get("commits_behind", 0)
        update_available = res.get("update_available", False)

        self.ver_label.configure(
            text=f"Installed Version: v{curr_ver}  |  Latest Remote: v{latest_ver}"
        )

        self.log_txt.delete("1.0", tk.END)
        self.log_txt.insert(tk.END, res.get("release_notes", "No release notes available.\n"))

        if update_available or commits_behind > 0:
            self.status_title.configure(
                text=f"🚀 Update Available ({commits_behind} new commit{'s' if commits_behind != 1 else ''} found)!",
                fg="#10b981",
            )
            self.status_desc.configure(
                text="A newer version is ready. Click 'UPDATE TO LATEST VERSION' to download and apply."
            )
            self.status_card.configure(highlightbackground="#10b981")
            self.apply_btn.configure(state=tk.NORMAL, bg="#059669")
        else:
            self.status_title.configure(
                text="✅ You are running the latest version!",
                fg="#38bdf8",
            )
            self.status_desc.configure(
                text=f"Local workspace is fully synchronized with origin/main (v{curr_ver})."
            )
            self.status_card.configure(highlightbackground="#0284c7")
            self.apply_btn.configure(state=tk.DISABLED, bg="#334155")

    def _apply_update(self):
        self.apply_btn.configure(state=tk.DISABLED)
        self.recheck_btn.configure(state=tk.DISABLED)
        self.pbar.configure(value=0)

        def _progress(msg, pct):
            self.after(0, lambda m=msg, p=pct: (
                self.progress_lbl.configure(text=f"[{p}%] {m}"),
                self.pbar.configure(value=p),
                self.log_txt.insert(tk.END, f"\n[{p}%] {m}"),
                self.log_txt.see(tk.END),
            ))

        def _worker():
            res = UpdateEngine.apply_update(progress_cb=_progress)
            self.after(0, lambda: self._on_apply_complete(res))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_apply_complete(self, res):
        self.recheck_btn.configure(state=tk.NORMAL)
        if res.get("success"):
            self.status_title.configure(text="🎉 Update Successfully Installed!", fg="#10b981")
            self.status_desc.configure(text=res.get("message", "Updated successfully."))
            messagebox.showinfo("Update Complete", res.get("message", "Update complete!"), parent=self)
            self.destroy()
        else:
            self.status_title.configure(text="❌ Update Encountered Error", fg="#ef4444")
            self.status_desc.configure(text=res.get("message", "Update failed."))
            self.apply_btn.configure(state=tk.NORMAL)
            messagebox.showerror("Update Error", f"Update failed: {res.get('message')}", parent=self)

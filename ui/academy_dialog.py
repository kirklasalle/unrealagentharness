r"""
Interactive Tkinter UI Dialog for the Unreal Academy & Research Lab.
Curriculum explorer, trick database, and research ingestion workbench.
"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from core.engine_controller import EngineController
from core.learning_engine import LearningEngine
from core.logger import get_logger

logger = get_logger("AcademyDialog", "academy_dialog.log")


class AcademyDialog(tk.Toplevel):
    """Interactive Unreal Academy & Research Lab Dialog."""

    def __init__(
        self,
        parent: tk.Tk,
        controller: EngineController,
        learning_engine: Optional[LearningEngine] = None,
        on_action_complete: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.learning_engine = learning_engine or LearningEngine()
        self.on_action_complete = on_action_complete

        self.title("🎓 Unreal Academy & Research Lab — Master Design & FX Tricks")
        self.geometry("920x680")
        self.minsize(780, 560)
        self.configure(bg="#0b0e14")
        self.transient(parent)
        self.grab_set()

        self.current_entries: List[Dict[str, Any]] = []

        self._build_ui()
        self._load_category("artistic_illusions_fx")
        logger.info("AcademyDialog initialized.")

    def _build_ui(self):
        # 1. Header Banner
        hdr = tk.Frame(self, bg="#111726", pady=12, padx=16)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="🎓 UNREAL ACADEMY & RESEARCH LAB",
            font=("Segoe UI", 13, "bold"),
            fg="#38bdf8",
            bg="#111726",
        ).pack(anchor=tk.W)

        tk.Label(
            hdr,
            text="Research compendium, 3D optical illusions, FX tricks, little-known engine quirks, and classic U1-U5 map deconstructions.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#111726",
        ).pack(anchor=tk.W, pady=(2, 0))

        # 2. Main Layout (Left: Category & Search / List, Right: Detailed Inspector)
        main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#0b0e14", sashwidth=4)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Left Column: Category & List
        left_col = tk.Frame(main_paned, bg="#0f172a", width=340)
        main_paned.add(left_col)

        # Category Buttons
        cat_box = tk.LabelFrame(left_col, text=" Curriculum Category ", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0f172a", padx=6, pady=6)
        cat_box.pack(fill=tk.X, padx=6, pady=(6, 4))

        self.cat_var = tk.StringVar(value="artistic_illusions_fx")
        cats = [
            ("🎭 3D Illusions & FX Tricks", "artistic_illusions_fx"),
            ("🏆 Classic Map Deconstructions", "classic_map_deconstructions"),
            ("💡 Tips, Tricks & Suggestions", "tips_and_tricks"),
            ("🕵️ Little-Known Facts & Quirks", "little_known_facts"),
            ("📚 Master Tutorials & CSG", "tutorials"),
        ]
        for label, val in cats:
            tk.Radiobutton(
                cat_box,
                text=label,
                variable=self.cat_var,
                value=val,
                font=("Segoe UI", 8),
                fg="#f1f5f9",
                bg="#0f172a",
                selectcolor="#0b0e14",
                activebackground="#0f172a",
                command=self._on_category_changed,
            ).pack(anchor=tk.W, pady=1)

        # Search Bar
        search_f = tk.Frame(left_col, bg="#0f172a")
        search_f.pack(fill=tk.X, padx=6, pady=4)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_f, textvariable=self.search_var, font=("Segoe UI", 9), bg="#1e293b", fg="#f1f5f9", insertbackground="#38bdf8", relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.search_entry.bind("<KeyRelease>", self._on_search_typed)

        tk.Button(search_f, text="🔍", font=("Segoe UI", 8), bg="#334155", fg="#ffffff", relief=tk.FLAT, padx=6, command=self._do_search).pack(side=tk.RIGHT, padx=(4, 0))

        # Items Listbox
        list_f = tk.Frame(left_col, bg="#0f172a")
        list_f.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self.item_listbox = tk.Listbox(
            list_f,
            bg="#111726",
            fg="#f1f5f9",
            font=("Segoe UI", 9),
            selectbackground="#0284c7",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
        )
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.item_listbox.bind("<<ListboxSelect>>", self._on_item_selected)

        sb = tk.Scrollbar(list_f, orient=tk.VERTICAL, command=self.item_listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_listbox.config(yscrollcommand=sb.set)

        # Ingest New Custom Trick Button
        tk.Button(
            left_col,
            text="📥 INGEST NEW TRICK / STUDY",
            font=("Segoe UI", 8, "bold"),
            bg="#10b981",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            command=self._open_ingest_modal,
        ).pack(fill=tk.X, padx=6, pady=(4, 6))

        # Right Column: Detailed Inspector
        right_col = tk.Frame(main_paned, bg="#0b0e14", padx=8, pady=4)
        main_paned.add(right_col)

        self.title_lbl = tk.Label(right_col, text="Select a topic to study", font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#0b0e14", anchor=tk.W)
        self.title_lbl.pack(fill=tk.X, pady=(0, 2))

        self.meta_lbl = tk.Label(right_col, text="Engine Target: - | Source: -", font=("Segoe UI", 8, "italic"), fg="#94a3b8", bg="#0b0e14", anchor=tk.W)
        self.meta_lbl.pack(fill=tk.X, pady=(0, 6))

        # Detail Text Area
        self.detail_text = tk.Text(
            right_col,
            bg="#111726",
            fg="#f1f5f9",
            font=("Segoe UI", 9),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # Bottom Action Bar
        bot = tk.Frame(self, bg="#111726", pady=8, padx=16)
        bot.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = tk.Label(bot, text="Ready.", font=("Segoe UI", 9), fg="#38bdf8", bg="#111726")
        self.status_lbl.pack(side=tk.LEFT)

        tk.Button(
            bot,
            text="⚡ EXECUTE / INJECT TRICK IN UNREALED",
            font=("Segoe UI", 9, "bold"),
            bg="#8b5cf6",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=5,
            command=self._execute_selected_trick,
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            bot,
            text="CLOSE",
            font=("Segoe UI", 9),
            bg="#334155",
            fg="#f1f5f9",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.destroy,
        ).pack(side=tk.RIGHT, padx=4)

    def _on_category_changed(self):
        cat = self.cat_var.get()
        self._load_category(cat)

    def _load_category(self, cat: str):
        self.current_entries = self.learning_engine.get_all_entries_by_category(cat)
        self.item_listbox.delete(0, tk.END)
        for e in self.current_entries:
            self.item_listbox.insert(tk.END, e.get("title", "Untitled"))
        if self.current_entries:
            self.item_listbox.selection_set(0)
            self._display_entry(self.current_entries[0])

    def _on_search_typed(self, event=None):
        query = self.search_var.get().strip()
        if len(query) >= 2:
            self._do_search()
        elif len(query) == 0:
            self._load_category(self.cat_var.get())

    def _do_search(self):
        query = self.search_var.get().strip()
        if not query:
            self._load_category(self.cat_var.get())
            return

        self.current_entries = self.learning_engine.query_academy(query=query)
        self.item_listbox.delete(0, tk.END)
        for e in self.current_entries:
            self.item_listbox.insert(tk.END, e.get("title", "Untitled"))
        if self.current_entries:
            self.item_listbox.selection_set(0)
            self._display_entry(self.current_entries[0])

    def _on_item_selected(self, event=None):
        sel = self.item_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self.current_entries):
            self._display_entry(self.current_entries[idx])

    def _display_entry(self, entry: Dict[str, Any]):
        self.title_lbl.config(text=entry.get("title", "Untitled Topic"))
        eng = entry.get("engine_target", "All Engines")
        auth = entry.get("author_reference", "Community")
        self.meta_lbl.config(text=f"Engine Target: {eng} | Reference / Origin: {auth}")

        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)

        text_blocks = [
            f"📖 SUMMARY & CONCEPT:\n{entry.get('summary', '')}\n",
        ]

        steps = entry.get("step_by_step", [])
        if steps:
            text_blocks.append("🔧 STEP-BY-STEP IMPLEMENTATION RECIPE:")
            for s in steps:
                text_blocks.append(f"  • {s}")
            text_blocks.append("")

        trick = entry.get("technical_trick", "")
        if trick:
            text_blocks.append(f"💡 MASTER TRICK / TECHNICAL SECRET:\n  {trick}\n")

        cmds = entry.get("t3d_commands", [])
        if cmds:
            text_blocks.append("⚡ EXECUTION COMMANDS (T3D):")
            for c in cmds:
                text_blocks.append(f"  {c}")
            text_blocks.append("")

        self.detail_text.insert(tk.END, "\n".join(text_blocks))
        self.detail_text.config(state=tk.DISABLED)

    def _execute_selected_trick(self):
        sel = self.item_listbox.curselection()
        if not sel:
            messagebox.showinfo("Academy", "Select a topic with execution commands first.")
            return
        entry = self.current_entries[sel[0]]
        cmds = entry.get("t3d_commands", [])
        if not cmds:
            messagebox.showinfo("Academy", f"Topic '{entry.get('title')}' is conceptual/tutorial; copy instructions from the detail view.")
            return

        self.status_lbl.config(text="⚡ Injecting Academy trick commands into UnrealEd...")

        def _worker():
            try:
                results = self.controller.execute_batch(cmds)
                self.after(0, lambda: self.status_lbl.config(text=f"✅ Done! Executed {len(cmds)} commands in UnrealEd."))
                if self.on_action_complete:
                    self.after(0, lambda: self.on_action_complete(f"Academy injected: {entry.get('title')}"))
            except Exception as e:
                self.after(0, lambda: self.status_lbl.config(text=f"⚠️ Error: {e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _open_ingest_modal(self):
        """Opens a modal to record and ingest a new trick or study finding."""
        dlg = tk.Toplevel(self)
        dlg.title("📥 Ingest Master Technique / Study")
        dlg.geometry("560x480")
        dlg.configure(bg="#0b0e14")
        dlg.transient(self)
        dlg.grab_set()

        f = tk.Frame(dlg, bg="#0b0e14", padx=16, pady=12)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="Topic Title:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0b0e14").pack(anchor=tk.W)
        t_var = tk.StringVar()
        tk.Entry(f, textvariable=t_var, font=("Segoe UI", 9), bg="#1e293b", fg="#f1f5f9", relief=tk.FLAT).pack(fill=tk.X, pady=(2, 6))

        tk.Label(f, text="Category:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0b0e14").pack(anchor=tk.W)
        c_var = tk.StringVar(value="artistic_illusions_fx")
        cb = ttk.Combobox(f, textvariable=c_var, values=LearningEngine.CATEGORIES, state="readonly")
        cb.pack(fill=tk.X, pady=(2, 6))

        tk.Label(f, text="Summary / Core Principle:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0b0e14").pack(anchor=tk.W)
        s_txt = tk.Text(f, height=4, bg="#1e293b", fg="#f1f5f9", font=("Segoe UI", 9), relief=tk.FLAT)
        s_txt.pack(fill=tk.X, pady=(2, 6))

        tk.Label(f, text="Technical Secret / Trick:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0b0e14").pack(anchor=tk.W)
        trick_txt = tk.Text(f, height=3, bg="#1e293b", fg="#f1f5f9", font=("Segoe UI", 9), relief=tk.FLAT)
        trick_txt.pack(fill=tk.X, pady=(2, 10))

        def _save():
            title = t_var.get().strip()
            summary = s_txt.get("1.0", tk.END).strip()
            trick = trick_txt.get("1.0", tk.END).strip()
            if not title or not summary:
                messagebox.showwarning("Validation", "Please provide a title and summary.")
                return

            ok = self.learning_engine.ingest_knowledge_entry(
                category=c_var.get(),
                title=title,
                summary=summary,
                technical_trick=trick,
                author_reference="User Research (Kirk LaSalle)",
            )
            if ok:
                messagebox.showinfo("Success", f"Ingested '{title}' into Academy Knowledgebase!")
                dlg.destroy()
                self._load_category(self.cat_var.get())

        tk.Button(f, text="💾 INGEST INTO LIFELONG KNOWLEDGEBASE", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="#ffffff", relief=tk.FLAT, pady=6, command=_save).pack(fill=tk.X)

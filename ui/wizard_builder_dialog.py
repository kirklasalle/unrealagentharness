r"""
Interactive Tkinter UI Dialog for the Unreal Architect Wizard Builder.
Allows mappers to build full worlds from scratch or non-destructively extend open maps in UnrealEd.
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from core.engine_controller import EngineController
from core.logger import get_logger
from core.wizard_builder import UnrealWizardBuilder

logger = get_logger("WizardDialog", "wizard_dialog.log")


class WizardBuilderDialog(tk.Toplevel):
    """Interactive multi-step Unreal Architect Wizard Dialog."""

    def __init__(
        self,
        parent: tk.Tk,
        controller: EngineController,
        on_build_complete: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.on_build_complete = on_build_complete

        self.title("🧙 Unreal Architect Wizard Builder — World-Class Level Synthesizer")
        self.geometry("780x640")
        self.minsize(680, 520)
        self.configure(bg="#0b0e14")
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        logger.info("WizardBuilderDialog initialized.")

    def _build_ui(self):
        # 1. Header Banner
        hdr = tk.Frame(self, bg="#111726", pady=12, padx=16)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="🧙 UNREAL ARCHITECT WIZARD BUILDER",
            font=("Segoe UI", 13, "bold"),
            fg="#38bdf8",
            bg="#111726",
        ).pack(anchor=tk.W)

        tk.Label(
            hdr,
            text="Synthesize full expansive campaign worlds or inject non-destructive wings into your active UnrealEd map.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#111726",
        ).pack(anchor=tk.W, pady=(2, 0))

        # Main Scrollable / Form Container
        body = tk.Frame(self, bg="#0b0e14", padx=20, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------
        # Section 1: Build Mode
        # -------------------------------------------------------------
        sec1 = tk.LabelFrame(body, text=" 1. Select Build Mode ", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#111726", padx=12, pady=8)
        sec1.pack(fill=tk.X, pady=(0, 10))

        self.mode_var = tk.StringVar(value="scratch")
        rb1 = tk.Radiobutton(
            sec1,
            text="✨ Build New Map from Scratch (Clean Slate Canvas)",
            variable=self.mode_var,
            value="scratch",
            font=("Segoe UI", 9, "bold"),
            fg="#f1f5f9",
            bg="#111726",
            selectcolor="#0b0e14",
            activebackground="#111726",
            command=self._on_mode_changed,
        )
        rb1.pack(anchor=tk.W)

        rb2 = tk.Radiobutton(
            sec1,
            text="➕ Non-Destructive Extension (Inject Wing/Crypt into Current Open Map)",
            variable=self.mode_var,
            value="inject",
            font=("Segoe UI", 9, "bold"),
            fg="#f1f5f9",
            bg="#111726",
            selectcolor="#0b0e14",
            activebackground="#111726",
            command=self._on_mode_changed,
        )
        rb2.pack(anchor=tk.W, pady=(4, 0))

        # -------------------------------------------------------------
        # Section 2: Game Generation & Lore Archetype
        # -------------------------------------------------------------
        sec2 = tk.LabelFrame(body, text=" 2. Game Era & Narrative Archetype ", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#111726", padx=12, pady=8)
        sec2.pack(fill=tk.X, pady=(0, 10))

        f_row = tk.Frame(sec2, bg="#111726")
        f_row.pack(fill=tk.X)

        tk.Label(f_row, text="Game Archetype:", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726", width=16, anchor=tk.W).pack(side=tk.LEFT)
        self.archetype_var = tk.StringVar(value="unreal1_rpg")
        self.combo_arch = ttk.Combobox(
            f_row,
            textvariable=self.archetype_var,
            values=[
                "Unreal 1 (1998) Narrative RPG Exploration",
                "UT99 Classic Tournament Arena",
                "UTron Cyberspace Void & Grids",
                "UT2004 Onslaught / Vehicle Battlefield",
            ],
            state="readonly",
            width=42,
        )
        self.combo_arch.pack(side=tk.LEFT, padx=6)
        self.combo_arch.bind("<<ComboboxSelected>>", self._on_arch_changed)

        # Preset / Campaign Lore Selector
        f_preset = tk.Frame(sec2, bg="#111726")
        f_preset.pack(fill=tk.X, pady=(6, 0))

        tk.Label(f_preset, text="Campaign / Theme:", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726", width=16, anchor=tk.W).pack(side=tk.LEFT)
        self.preset_var = tk.StringVar(value="chizra_temple")
        self.combo_preset = ttk.Combobox(
            f_preset,
            textvariable=self.preset_var,
            values=[
                "Chizra, Water God Temple (Nali Monks & Translator Logs)",
                "Skaarj Mothership Infiltration (High-Tech Alien Corridors)",
                "Bluff Eversmoking Mountain Fortress (Gothic Crypts)",
            ],
            state="readonly",
            width=42,
        )
        self.combo_preset.pack(side=tk.LEFT, padx=6)

        # -------------------------------------------------------------
        # Section 3: RPG & Story Modules (Translator, NPCs, Crypts)
        # -------------------------------------------------------------
        self.sec3 = tk.LabelFrame(body, text=" 3. RPG Story & Narrative Modules ", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#111726", padx=12, pady=8)
        self.sec3.pack(fill=tk.X, pady=(0, 10))

        self.var_lore = tk.BooleanVar(value=True)
        self.var_monks = tk.BooleanVar(value=True)
        self.var_crypt = tk.BooleanVar(value=True)
        self.var_guards = tk.BooleanVar(value=True)

        chk_f = tk.Frame(self.sec3, bg="#111726")
        chk_f.pack(fill=tk.X)

        tk.Checkbutton(chk_f, text="📜 TranslatorEvent Lore Tablets", variable=self.var_lore, fg="#f1f5f9", bg="#111726", selectcolor="#0b0e14", activebackground="#111726").pack(side=tk.LEFT, padx=(0, 12))
        tk.Checkbutton(chk_f, text="🧘 Indigenous Nali Monks", variable=self.var_monks, fg="#f1f5f9", bg="#111726", selectcolor="#0b0e14", activebackground="#111726").pack(side=tk.LEFT, padx=(0, 12))
        tk.Checkbutton(chk_f, text="🏰 Secret Subterranean Crypt", variable=self.var_crypt, fg="#f1f5f9", bg="#111726", selectcolor="#0b0e14", activebackground="#111726").pack(side=tk.LEFT, padx=(0, 12))
        tk.Checkbutton(chk_f, text="👹 Skaarj & Brute Guards", variable=self.var_guards, fg="#f1f5f9", bg="#111726", selectcolor="#0b0e14", activebackground="#111726").pack(side=tk.LEFT)

        # -------------------------------------------------------------
        # Section 4: Injection Options (Active only when mode='inject')
        # -------------------------------------------------------------
        self.sec4 = tk.LabelFrame(body, text=" 4. In-Situ Extension Parameters (Injection Mode) ", font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#111726", padx=12, pady=8)
        self.sec4.pack(fill=tk.X, pady=(0, 10))

        f_inj = tk.Frame(self.sec4, bg="#111726")
        f_inj.pack(fill=tk.X)

        tk.Label(f_inj, text="Direction to Extend:", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value="North")
        self.combo_dir = ttk.Combobox(f_inj, textvariable=self.dir_var, values=["North (+Y)", "South (-Y)", "East (+X)", "West (-X)"], state="readonly", width=14)
        self.combo_dir.pack(side=tk.LEFT, padx=8)

        tk.Label(f_inj, text="Wing Type:", font=("Segoe UI", 9), fg="#94a3b8", bg="#111726", padx=6).pack(side=tk.LEFT)
        self.wing_var = tk.StringVar(value="secret_crypt")
        self.combo_wing = ttk.Combobox(f_inj, textvariable=self.wing_var, values=["secret_crypt", "sniper_overlook", "armory_hall", "powernode_substation"], state="readonly", width=22)
        self.combo_wing.pack(side=tk.LEFT, padx=4)

        # -------------------------------------------------------------
        # Bottom Execution & Status Bar
        # -------------------------------------------------------------
        bot = tk.Frame(self, bg="#111726", pady=10, padx=16)
        bot.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = tk.Label(bot, text="Ready to build.", font=("Segoe UI", 9), fg="#38bdf8", bg="#111726")
        self.status_lbl.pack(side=tk.LEFT)

        tk.Button(
            bot,
            text="🧙 CONJURE & BUILD IN UNREALED",
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            command=self._execute_wizard_build,
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            bot,
            text="CLOSE",
            font=("Segoe UI", 9),
            bg="#334155",
            fg="#f1f5f9",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            command=self.destroy,
        ).pack(side=tk.RIGHT, padx=4)

    def _on_mode_changed(self):
        mode = self.mode_var.get()
        if mode == "inject":
            self.sec4.config(fg="#38bdf8")
            self.status_lbl.config(text="Injection Mode: Will connect new wing to current map in UnrealEd.")
        else:
            self.sec4.config(fg="#94a3b8")
            self.status_lbl.config(text="Clean Slate Mode: Will build complete new level from scratch.")

    def _on_arch_changed(self, event=None):
        arch = self.archetype_var.get()
        if "Unreal 1" in arch:
            self.combo_preset["values"] = [
                "Chizra, Water God Temple (Nali Monks & Translator Logs)",
                "Skaarj Mothership Infiltration (High-Tech Alien Corridors)",
                "Bluff Eversmoking Mountain Fortress (Gothic Crypts)",
            ]
            self.combo_preset.current(0)
            self.sec3.pack(fill=tk.X, pady=(0, 10))
        elif "UT99" in arch:
            self.combo_preset["values"] = [
                "Verdant Mountain Valley Fortress (Ultra Detail)",
                "Classic Tournament Colosseum (Semi-Solid Fluted Columns)",
                "Symmetrical Dual-Base CTF Outpost",
            ]
            self.combo_preset.current(0)
        elif "UTron" in arch:
            self.combo_preset["values"] = [
                "Master Control Program (MCP) Core Sanctum",
                "Light Cycle 90-Degree Combat Grid",
                "Discs of Tron Neon Cylindrical Platforms",
            ]
            self.combo_preset.current(0)
        elif "UT2004" in arch:
            self.combo_preset["values"] = [
                "Onslaught Desert Canyon (Torlan Layout)",
                "Arctic Outpost with Karma Vehicle Bays",
                "SkaarjPack Creature Invasion Arena",
            ]
            self.combo_preset.current(0)

    def _execute_wizard_build(self):
        mode = self.mode_var.get()
        arch = self.archetype_var.get()
        preset = self.preset_var.get()

        self.status_lbl.config(text="⚡ Executing Wizard commands in UnrealEd...")

        def _worker():
            try:
                cmds: List[str] = []
                if mode == "scratch":
                    if "Unreal 1" in arch:
                        key = "chizra_temple"
                        if "Skaarj" in preset:
                            key = "skaarj_mothership"
                        elif "Bluff" in preset:
                            key = "bluff_eversmoking"
                        cmds = UnrealWizardBuilder.build_unreal1_rpg_campaign_level(
                            preset_key=key,
                            system_dir=self.controller.system_dir,
                            include_secret_crypt=self.var_crypt.get(),
                            detail_level="ultra",
                        )
                    else:
                        from core.mind_synthesizer import MindSynthesizer
                        cmds = MindSynthesizer.synthesize_level_from_mind(
                            prompt=preset,
                            system_dir=self.controller.system_dir,
                            engine_id="ut99_goty",
                        )
                else:
                    # Injection Mode
                    direction = self.dir_var.get().split()[0]
                    wing = self.wing_var.get()
                    cmds = UnrealWizardBuilder.inject_wing_into_existing_map(
                        anchor_location=(0.0, 0.0, 0.0),
                        wing_type=wing,
                        direction=direction,
                        system_dir=self.controller.system_dir,
                    )

                results = self.controller.execute_batch(cmds)
                logger.info(f"Wizard completed execution of {len(cmds)} commands.")

                self.after(0, lambda: self.status_lbl.config(text=f"✅ Done! Built {len(cmds)} commands successfully."))
                if self.on_build_complete:
                    self.after(0, lambda: self.on_build_complete(f"Wizard generated {len(cmds)} commands ({mode}: {preset})"))

            except Exception as e:
                logger.error(f"Wizard execution error: {e}")
                self.after(0, lambda: self.status_lbl.config(text=f"⚠️ Error: {str(e)}"))

        threading.Thread(target=_worker, daemon=True).start()

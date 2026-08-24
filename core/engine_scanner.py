"""
Universal Unreal Engine & Game Mod Auto-Discovery Engine.
Scans local drives, Steam, GOG, Epic Games, and custom folders to discover
all installed Unreal Engine versions (UE1-UE5) and Total Conversion mods,
automatically configuring paths for standalone portable execution.
"""

import os
import string
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .logger import get_logger

logger = get_logger("EngineScanner", "engine_scanner.log")


class EngineScanner:
    """Scans storage drives and directories to detect Unreal Engine installations and game mods."""

    # Signature definitions for automatic engine & mod recognition
    ENGINE_SIGNATURES = {
        "ut99_goty": {
            "name": "Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e)",
            "category": "Base Game Engine",
            "generation": "UE1",
            "icon": "🏆",
            "editor_exe": "UnrealEd.exe",
            "game_exe": "UnrealTournament.exe",
            "required_files": ["System/UnrealTournament.exe", "System/Botpack.u"],
            "editor_args": "",
            "game_args": "INI=UnrealTournament.ini USERINI=User.ini",
        },
        "ut2004": {
            "name": "Unreal Tournament 2004 (UE2.5 / v3369+)",
            "category": "Base Game Engine",
            "generation": "UE2.5",
            "icon": "⚔️",
            "editor_exe": "UnrealEd.exe",
            "game_exe": "UT2004.exe",
            "required_files": ["System/UT2004.exe", "System/Onslaught.u"],
            "editor_args": "",
            "game_args": "",
        },
        "ut2003": {
            "name": "Unreal Tournament 2003 (UE2.0)",
            "category": "Base Game Engine",
            "generation": "UE2.0",
            "icon": "🕹️",
            "editor_exe": "UnrealEd.exe",
            "game_exe": "UT2003.exe",
            "required_files": ["System/UT2003.exe", "System/XWeapons.u"],
            "editor_args": "",
            "game_args": "",
        },
        "unreal1": {
            "name": "Unreal 1 / Unreal Gold (UE1 / 227)",
            "category": "Base Game Engine",
            "generation": "UE1",
            "icon": "🏰",
            "editor_exe": "UnrealEd.exe",
            "game_exe": "Unreal.exe",
            "required_files": ["System/Unreal.exe", "System/UnrealShare.u"],
            "editor_args": "",
            "game_args": "",
        },
        "ue5": {
            "name": "Unreal Engine 5 (UE5.x / Nanite & Lumen)",
            "category": "Base Game Engine",
            "generation": "UE5",
            "icon": "🌌",
            "editor_exe": "UnrealEditor.exe",
            "game_exe": "UnrealEditor.exe",
            "required_files": ["Engine/Binaries/Win64/UnrealEditor.exe"],
            "editor_args": "",
            "game_args": "-game",
        },
        "ue4": {
            "name": "Unreal Engine 4 (UE4.x)",
            "category": "Base Game Engine",
            "generation": "UE4",
            "icon": "🌌",
            "editor_exe": "UE4Editor.exe",
            "game_exe": "UE4Editor.exe",
            "required_files": ["Engine/Binaries/Win64/UE4Editor.exe"],
            "editor_args": "",
            "game_args": "-game",
        },
    }

    # Total Conversion Mod Signatures
    MOD_SIGNATURES = [
        {
            "id": "ut99_utron",
            "name": "UTron: Total Conversion Mod (UE1 / 469e)",
            "category": "Game Mod (Total Conversion)",
            "mod_type": "Total Conversion",
            "parent_engine": "ut99_goty",
            "generation": "UE1",
            "icon": "⚡",
            "description": "Cyberspace Total Conversion mod featuring Light Cycles, Discs of Tron, MCP Core, and cyber grids.",
            "editor_args": "INI=UTronEditor.ini",
            "game_args": "UTronIntro.unr INI=UTronProject.ini USERINI=UTronUser.ini",
            "indicator_files": [
                "UTronProject",
                "System/UTron.u",
                "Textures/Tron2002.utx",
                "Textures/UTron_Grids-Lines.utx",
            ],
        },
        {
            "id": "ut99_chaosut",
            "name": "ChaosUT: Evolution Mod (UE1 / 469e)",
            "category": "Game Mod (Total Conversion)",
            "mod_type": "Total Conversion",
            "parent_engine": "ut99_goty",
            "generation": "UE1",
            "icon": "⚔️",
            "description": "ChaosUT weapon and physics total conversion featuring Grappling Hooks, Crossbows, and Vortex mines.",
            "editor_args": "",
            "game_args": "",
            "indicator_files": ["System/ChaosUT.u", "System/ChaosGames.u"],
        },
        {
            "id": "ut99_tacticalops",
            "name": "Tactical Ops: Assault on Terror (UE1)",
            "category": "Game Mod (Total Conversion)",
            "mod_type": "Total Conversion",
            "parent_engine": "ut99_goty",
            "generation": "UE1",
            "icon": "🎯",
            "description": "Tactical counter-terrorist CQB total conversion mod for Unreal Engine 1.",
            "editor_args": "",
            "game_args": "INI=TacticalOps.ini USERINI=TOUser.ini",
            "indicator_files": ["System/TacticalOps.exe", "System/s_SWAT.u", "System/TOModels.u"],
        },
        {
            "id": "ut99_infiltration",
            "name": "Infiltration: Tactical Simulation (UE1)",
            "category": "Game Mod (Total Conversion)",
            "mod_type": "Total Conversion",
            "parent_engine": "ut99_goty",
            "generation": "UE1",
            "icon": "🪖",
            "description": "Realistic military simulation total conversion mod for UT99.",
            "editor_args": "",
            "game_args": "",
            "indicator_files": ["System/Infiltration.ini", "System/InfilGameType.u"],
        },
        {
            "id": "ut99_monsterhunt",
            "name": "Monster Hunt Mod (UE1)",
            "category": "Game Mod (Gameplay Mutator)",
            "mod_type": "Gameplay Mod",
            "parent_engine": "ut99_goty",
            "generation": "UE1",
            "icon": "👾",
            "description": "Co-op monster hunting and dungeon progression mod for UT99.",
            "editor_args": "",
            "game_args": "",
            "indicator_files": ["System/MonsterHunt.u"],
        },
        {
            "id": "ut2004_utron2004",
            "name": "UTron 2004 Mod (UE2.5)",
            "category": "Game Mod (Total Conversion)",
            "mod_type": "Total Conversion",
            "parent_engine": "ut2004",
            "generation": "UE2.5",
            "icon": "⚡",
            "description": "UTron Cyberspace conversion for Unreal Tournament 2004.",
            "editor_args": "",
            "game_args": "",
            "indicator_files": ["UTron2004", "System/UTron2004.u"],
        },
    ]

    @staticmethod
    def get_available_drives() -> List[str]:
        """Returns a list of active drive roots on Windows (e.g. ['C:\\', 'D:\\', 'G:\\'])."""
        drives = []
        for letter in string.ascii_uppercase:
            drive_str = f"{letter}:\\"
            if os.path.exists(drive_str):
                drives.append(drive_str)
        return drives

    @classmethod
    def scan_all(cls, progress_cb: Optional[Callable[[str, int], None]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Executes a comprehensive scan across all drives and common locations.
        Returns a dictionary of discovered engine and mod profiles keyed by ID.
        """
        discovered: Dict[str, Dict[str, Any]] = {}
        checked_dirs = set()

        # 1. Candidate Generation
        candidates = cls._generate_search_candidates()
        total_candidates = len(candidates)

        logger.info(f"Starting Unreal Auto-Discovery Scan across {total_candidates} candidate locations...")

        for idx, cand in enumerate(candidates):
            cand_path = Path(cand)
            if not cand_path.exists():
                continue

            resolved = str(cand_path.resolve()).lower()
            if resolved in checked_dirs:
                continue
            checked_dirs.add(resolved)

            if progress_cb:
                percent = int((idx / max(total_candidates, 1)) * 100)
                progress_cb(f"Scanning: {cand_path.name}", percent)

            # Check for Engine
            engine_info = cls.inspect_directory(cand_path)
            if engine_info:
                e_id = engine_info["id"]
                discovered[e_id] = engine_info
                logger.info(f"Discovered Engine Target: '{engine_info['name']}' at {cand_path}")

            # Check for Mods within this folder
            mods_found = cls.inspect_mods_in_directory(cand_path)
            for m in mods_found:
                m_id = m["id"]
                discovered[m_id] = m
                logger.info(f"Discovered Game Mod: '{m['name']}' at {cand_path}")

        if progress_cb:
            progress_cb("Scan Complete", 100)

        logger.info(f"Scan complete. Found {len(discovered)} total engine & mod targets.")
        return discovered

    @classmethod
    def inspect_directory(cls, directory: Path) -> Optional[Dict[str, Any]]:
        """Checks if a directory matches any base Unreal Engine signature."""
        if not directory.is_dir():
            return None

        for engine_id, sig in cls.ENGINE_SIGNATURES.items():
            matches = True
            for req_rel in sig["required_files"]:
                req_path = directory / req_rel
                if not req_path.exists():
                    matches = False
                    break

            if matches:
                system_dir = directory / "System"
                if not system_dir.exists():
                    if (directory / "Engine" / "Binaries" / "Win64").exists():
                        system_dir = directory / "Engine" / "Binaries" / "Win64"
                    else:
                        system_dir = directory

                return {
                    "id": engine_id,
                    "name": sig["name"],
                    "category": sig["category"],
                    "generation": sig["generation"],
                    "icon": sig["icon"],
                    "root_dir": str(directory.resolve()),
                    "system_dir": str(system_dir.resolve()),
                    "editor_exe": sig["editor_exe"],
                    "editor_args": sig.get("editor_args", ""),
                    "game_exe": sig["game_exe"],
                    "game_args": sig.get("game_args", ""),
                    "window_classes": ["WUnrealEd", "WWindow", "UnrealEd", "UnrealWindow", "Slate"],
                    "process_names": ["unrealed.exe", "unrealtournament.exe", "ut2004.exe", "unrealeditor.exe"],
                    "log_files": ["Editor.log", "UnrealEd.log", "UnrealTournament.log", "UT2004.log", "UnrealEditor.log"],
                }

        return None

    @classmethod
    def inspect_mods_in_directory(cls, directory: Path) -> List[Dict[str, Any]]:
        """Checks if a directory contains any known Total Conversion mods or custom packages."""
        mods_found = []
        if not directory.is_dir():
            return mods_found

        for mod_sig in cls.MOD_SIGNATURES:
            # Check if any indicator file exists
            has_indicator = False
            for ind in mod_sig["indicator_files"]:
                if (directory / ind).exists():
                    has_indicator = True
                    break

            if has_indicator:
                parent_id = mod_sig.get("parent_engine", "ut99_goty")
                system_dir = directory / "System"
                if not system_dir.exists():
                    system_dir = directory

                mods_found.append({
                    "id": mod_sig["id"],
                    "name": mod_sig["name"],
                    "category": mod_sig.get("category", "Game Mod (Total Conversion)"),
                    "mod_type": mod_sig.get("mod_type", "Total Conversion"),
                    "parent_engine": parent_id,
                    "generation": mod_sig.get("generation", "UE1"),
                    "icon": mod_sig.get("icon", "⚡"),
                    "description": mod_sig.get("description", ""),
                    "root_dir": str(directory.resolve()),
                    "system_dir": str(system_dir.resolve()),
                    "editor_exe": "UnrealEd.exe",
                    "editor_args": mod_sig.get("editor_args", ""),
                    "game_exe": "UnrealTournament.exe" if "ut99" in mod_sig["id"] else "UT2004.exe",
                    "game_args": mod_sig.get("game_args", ""),
                    "window_classes": ["WUnrealEd", "WWindow", "UnrealEd"],
                    "process_names": ["unrealed.exe", "utroneditor.exe", "unrealtournament.exe", "ut2004.exe"],
                    "log_files": ["Editor.log", "UnrealEd.log", "UTronProject.log", "UnrealTournament.log"],
                })

        return mods_found

    @classmethod
    def _generate_search_candidates(cls) -> List[str]:
        """Builds a prioritized list of directories to probe for Unreal engines and mods."""
        candidates = []

        # 1. Parent and current workspace directories (Portable clone support)
        curr_dir = Path(__file__).resolve().parent.parent.parent
        candidates.append(str(curr_dir))
        if curr_dir.parent.exists():
            candidates.append(str(curr_dir.parent))

        # 2. Known common game folder names
        folder_names = [
            "UnrealTournament",
            "UnrealTournament2004",
            "UT2004",
            "UT2003",
            "UT99",
            "Unreal",
            "UnrealGold",
            "UnrealEngine5",
            "UnrealEngine",
            "UTron",
            "UTronProject",
        ]

        # 3. Scan all active drives at root and shallow subfolders
        drives = cls.get_available_drives()
        for d in drives:
            for fname in folder_names:
                candidates.append(os.path.join(d, fname))
                candidates.append(os.path.join(d, "Games", fname))
                candidates.append(os.path.join(d, "GOG Games", fname))
                candidates.append(os.path.join(d, "SteamLibrary", "steamapps", "common", fname))
                candidates.append(os.path.join(d, "Program Files", fname))
                candidates.append(os.path.join(d, "Program Files (x86)", fname))
                candidates.append(os.path.join(d, "Program Files", "Epic Games", fname))
                candidates.append(os.path.join(d, "Projects", "GameDevelopment", fname))

            # Shallow drive root scan (depth 1)
            try:
                with os.scandir(d) as entries:
                    for entry in entries:
                        if entry.is_dir() and not entry.name.startswith(("$", ".")):
                            name_lower = entry.name.lower()
                            if "unreal" in name_lower or "ut99" in name_lower or "ut2004" in name_lower or "utron" in name_lower:
                                candidates.append(entry.path)
            except Exception:
                pass

        return candidates

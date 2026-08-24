"""
Configuration Manager for Standalone Multi-Engine Agent Harness.
Manages dynamic engine switching (UT99 UTron, UT99 GOTY, UT2003, UT2004),
LLM provider profiles, and personalities with full disk persistence.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger

logger = get_logger("ConfigManager", "config_mgr.log")


class ConfigManager:
    """Manages multi-engine targets, LLM profiles, personalities, and system configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path(__file__).resolve().parent.parent / "config"

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.engine_file = self.config_dir / "engine_profiles.json"
        self.llm_file = self.config_dir / "llm_profiles.json"
        self.personality_file = self.config_dir / "personality_profiles.json"

        self.engine_data: Dict[str, Any] = self._load_json(self.engine_file)
        self.llm_data: Dict[str, Any] = self._load_json(self.llm_file)
        self.personality_data: Dict[str, Any] = self._load_json(self.personality_file)

        logger.info(f"ConfigManager loaded. Active Engine: '{self.get_active_engine_id()}'")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
        return {}

    def _save_json(self, path: Path, data: Dict[str, Any]) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {path}: {e}")
            return False

    # -------------------------------------------------------------------------
    # ENGINE PROFILE ACCESSORS
    # -------------------------------------------------------------------------
    def get_active_engine_id(self) -> str:
        return self.engine_data.get("active_engine", "ut99_utron")

    def set_active_engine_id(self, engine_id: str) -> bool:
        if engine_id in self.engine_data.get("profiles", {}):
            self.engine_data["active_engine"] = engine_id
            self._save_json(self.engine_file, self.engine_data)
            logger.info(f"Active Engine Profile switched to: '{engine_id}'")
            return True
        logger.warning(f"Engine profile '{engine_id}' not found.")
        return False

    def get_active_engine_profile(self) -> Dict[str, Any]:
        engine_id = self.get_active_engine_id()
        return self.engine_data.get("profiles", {}).get(engine_id, {})

    def get_all_engine_profiles(self) -> Dict[str, Any]:
        return self.engine_data.get("profiles", {})

    def get_base_engines(self) -> Dict[str, Any]:
        """Returns only Base Game Engine profiles (UT99 GOTY, UT2003, UT2004, UE5)."""
        profiles = self.get_all_engine_profiles()
        return {
            k: v for k, v in profiles.items()
            if v.get("category") == "Base Game Engine" or "category" not in v
        }

    def get_game_mods(self) -> Dict[str, Any]:
        """Returns all Game Mods & Total Conversion profiles (e.g. UTron, ChaosUT, Tactical Ops)."""
        profiles = self.get_all_engine_profiles()
        return {
            k: v for k, v in profiles.items()
            if "Mod" in v.get("category", "") or v.get("mod_type") is not None
        }

    def register_game_mod(self, mod_id: str, mod_info: Dict[str, Any]) -> bool:
        """Registers a new Game Mod / Total Conversion profile into the engine registry."""
        if "profiles" not in self.engine_data:
            self.engine_data["profiles"] = {}

        mod_info["id"] = mod_id
        if "category" not in mod_info:
            mod_info["category"] = "Game Mod (Total Conversion)"
        if "mod_type" not in mod_info:
            mod_info["mod_type"] = "Total Conversion"

        self.engine_data["profiles"][mod_id] = mod_info
        success = self._save_json(self.engine_file, self.engine_data)
        if success:
            logger.info(f"Registered new Game Mod: '{mod_id}' ({mod_info.get('name')})")
        return success

    def delete_game_mod(self, mod_id: str) -> bool:
        """Deletes a custom Game Mod profile (Base Game engines cannot be deleted)."""
        profiles = self.engine_data.get("profiles", {})
        if mod_id in profiles and profiles[mod_id].get("category") != "Base Game Engine":
            del self.engine_data["profiles"][mod_id]
            if self.get_active_engine_id() == mod_id:
                self.set_active_engine_id("ut99_goty")
            self._save_json(self.engine_file, self.engine_data)
            logger.info(f"Deleted Game Mod profile: '{mod_id}'")
            return True
        return False

    def apply_scan_results(self, discovered: Dict[str, Dict[str, Any]]) -> int:
        """
        Updates paths of existing engine/mod profiles and registers newly discovered targets.
        Saves changes to disk immediately.
        """
        if "profiles" not in self.engine_data:
            self.engine_data["profiles"] = {}

        updated_count = 0
        for target_id, disc in discovered.items():
            if target_id in self.engine_data["profiles"]:
                # Update existing profile paths
                prof = self.engine_data["profiles"][target_id]
                prof["root_dir"] = disc.get("root_dir", prof.get("root_dir"))
                prof["system_dir"] = disc.get("system_dir", prof.get("system_dir"))
                if "editor_exe" in disc:
                    prof["editor_exe"] = disc["editor_exe"]
                if "game_exe" in disc:
                    prof["game_exe"] = disc["game_exe"]
                updated_count += 1
            else:
                # Add newly discovered engine or mod
                self.engine_data["profiles"][target_id] = disc
                updated_count += 1

        self._save_json(self.engine_file, self.engine_data)
        logger.info(f"Applied scan results: updated/registered {updated_count} engine/mod profiles.")
        return updated_count

    def run_engine_scan(self, progress_cb: Optional[Callable[[str, int], None]] = None) -> Dict[str, Dict[str, Any]]:
        """Invokes EngineScanner and automatically applies results to the active configuration."""
        from .engine_scanner import EngineScanner
        discovered = EngineScanner.scan_all(progress_cb=progress_cb)
        if discovered:
            self.apply_scan_results(discovered)
        return discovered

    # -------------------------------------------------------------------------
    # LLM PROFILE ACCESSORS
    # -------------------------------------------------------------------------
    def get_active_llm_profile_id(self) -> str:
        return self.llm_data.get("active_profile", "google-gemini")

    def set_active_llm_profile_id(self, profile_id: str) -> bool:
        if profile_id in self.llm_data.get("profiles", {}):
            self.llm_data["active_profile"] = profile_id
            self._save_json(self.llm_file, self.llm_data)
            logger.info(f"Active LLM Profile switched to: '{profile_id}'")
            return True
        return False

    def get_active_llm_profile(self) -> Dict[str, Any]:
        profile_id = self.get_active_llm_profile_id()
        return self.llm_data.get("profiles", {}).get(profile_id, {})

    def update_llm_profile(self, profile_id: str, updates: Dict[str, Any]) -> bool:
        if profile_id in self.llm_data.get("profiles", {}):
            self.llm_data["profiles"][profile_id].update(updates)
            return self._save_json(self.llm_file, self.llm_data)
        return False

    def get_all_llm_profiles(self) -> Dict[str, Any]:
        return self.llm_data.get("profiles", {})

    # -------------------------------------------------------------------------
    # PERSONALITY ACCESSORS
    # -------------------------------------------------------------------------
    def get_active_personality_id(self) -> str:
        return self.personality_data.get("active_personality", "architect")

    def set_active_personality_id(self, personality_id: str) -> bool:
        if personality_id in self.personality_data.get("personalities", {}):
            self.personality_data["active_personality"] = personality_id
            self._save_json(self.personality_file, self.personality_data)
            logger.info(f"Active Personality switched to: '{personality_id}'")
            return True
        return False

    def get_active_personality(self) -> Dict[str, Any]:
        pid = self.get_active_personality_id()
        return self.personality_data.get("personalities", {}).get(pid, {})

    def get_all_personalities(self) -> Dict[str, Any]:
        return self.personality_data.get("personalities", {})

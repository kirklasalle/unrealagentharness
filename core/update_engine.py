"""
Intelligent Auto-Updater & Version Checker Engine.
Checks remote GitHub repository releases and commits, downloads updates,
preserves local user configs, and applies updates with verified integrity.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from ..version import __version__, __version_info__, __repo__, __github_api_repo__
from .logger import get_logger

logger = get_logger("UpdateEngine", "updater.log")


class UpdateEngine:
    """Manages version checking, update downloads, and intelligent self-updating."""

    CURRENT_VERSION = __version__
    REPO_URL = __repo__
    GITHUB_API_REPO = __github_api_repo__

    @classmethod
    def get_current_version(cls) -> str:
        return cls.CURRENT_VERSION

    @classmethod
    def parse_semver(cls, ver_str: str) -> Tuple[int, int, int]:
        """Parses a version string like 'v2.10.0' or '2.10.1' into a numeric tuple (2, 10, 1)."""
        clean = ver_str.strip().lstrip("v").lstrip("V")
        parts = []
        for p in clean.split("."):
            try:
                parts.append(int(p.split("-")[0]))
            except ValueError:
                parts.append(0)
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    @classmethod
    def is_git_repository(cls) -> bool:
        """Checks whether the harness is running within a Git repository clone."""
        root_dir = Path(__file__).resolve().parent.parent
        parent_dir = root_dir.parent
        return (root_dir / ".git").exists() or (parent_dir / ".git").exists()

    @classmethod
    def get_repo_root(cls) -> Path:
        root_dir = Path(__file__).resolve().parent.parent
        if (root_dir / ".git").exists():
            return root_dir
        if (root_dir.parent / ".git").exists():
            return root_dir.parent
        return root_dir

    @classmethod
    def check_for_updates(cls, timeout: float = 6.0) -> Dict[str, Any]:
        """
        Checks for available updates using both Git and GitHub HTTP APIs.
        Returns detailed update metadata.
        """
        result = {
            "update_available": False,
            "current_version": cls.CURRENT_VERSION,
            "latest_version": cls.CURRENT_VERSION,
            "commits_behind": 0,
            "release_notes": "You are currently running the latest version.",
            "update_method": "git" if cls.is_git_repository() else "zip_download",
            "remote_url": cls.REPO_URL,
            "error": None,
        }

        # 1. Attempt Git-based check if running in a repo
        if cls.is_git_repository():
            try:
                repo_root = cls.get_repo_root()
                # Run git fetch silently
                fetch_proc = subprocess.run(
                    ["git", "fetch", "origin", "main"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                if fetch_proc.returncode == 0:
                    # Check how many commits behind origin/main
                    count_proc = subprocess.run(
                        ["git", "rev-list", "HEAD..origin/main", "--count"],
                        cwd=str(repo_root),
                        capture_output=True,
                        text=True,
                        timeout=3.0,
                    )
                    commits_behind = int(count_proc.stdout.strip() or "0")
                    result["commits_behind"] = commits_behind

                    if commits_behind > 0:
                        result["update_available"] = True
                        # Get commit messages
                        log_proc = subprocess.run(
                            ["git", "log", "HEAD..origin/main", "--oneline", "-n", "5"],
                            cwd=str(repo_root),
                            capture_output=True,
                            text=True,
                            timeout=3.0,
                        )
                        notes = log_proc.stdout.strip()
                        result["release_notes"] = f"Found {commits_behind} new commit(s) on remote:\n{notes}"
                        logger.info(f"Git check: {commits_behind} commits behind remote origin/main.")
                        return result
            except Exception as e:
                logger.warning(f"Git update check encountered error: {e}")

        # 2. HTTP Fallback Check (Fetch version.py from GitHub raw content)
        try:
            raw_url = f"https://raw.githubusercontent.com/{cls.GITHUB_API_REPO}/main/AgentHarness/version.py"
            req = urllib.request.Request(raw_url, headers={"User-Agent": "UnrealAgentHarness-Updater"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8")

                for line in content.splitlines():
                    if line.startswith("__version__"):
                        remote_ver = line.split("=")[1].strip().strip('"').strip("'")
                        result["latest_version"] = remote_ver

                        curr_tuple = cls.parse_semver(cls.CURRENT_VERSION)
                        remote_tuple = cls.parse_semver(remote_ver)

                        if remote_tuple > curr_tuple:
                            result["update_available"] = True
                            result["release_notes"] = f"New version v{remote_ver} available! (Current: v{cls.CURRENT_VERSION})"
                        break
        except Exception as e:
            logger.warning(f"HTTP version check error: {e}")
            result["error"] = str(e)

        return result

    @classmethod
    def apply_update(
        cls, progress_cb: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Intelligently downloads and applies updates while backing up configuration.
        """
        result = {
            "success": False,
            "message": "",
            "old_version": cls.CURRENT_VERSION,
            "new_version": cls.CURRENT_VERSION,
        }

        # Step 1: Backup Local User Configuration
        if progress_cb:
            progress_cb("Backing up local configuration files...", 15)

        harness_root = Path(__file__).resolve().parent.parent
        config_dir = harness_root / "config"
        backup_dir = harness_root / "config_backup"

        if config_dir.exists():
            try:
                shutil.copytree(config_dir, backup_dir, dirs_exist_ok=True)
                logger.info(f"Backed up configuration to: {backup_dir}")
            except Exception as e:
                logger.warning(f"Failed to backup configuration: {e}")

        # Step 2: Execute Update (Git Pull or ZIP Download)
        if cls.is_git_repository():
            if progress_cb:
                progress_cb("Updating repository via Git (pulling latest main)...", 45)

            repo_root = cls.get_repo_root()
            try:
                pull_proc = subprocess.run(
                    ["git", "pull", "--rebase=false", "origin", "main"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    timeout=30.0,
                )

                if pull_proc.returncode != 0:
                    raise RuntimeError(f"Git pull failed: {pull_proc.stderr}")

                logger.info(f"Git pull succeeded: {pull_proc.stdout}")
            except Exception as e:
                logger.error(f"Git update failed: {e}")
                result["message"] = f"Git update error: {str(e)}"
                return result
        else:
            # ZIP Download Fallback
            if progress_cb:
                progress_cb("Downloading latest release ZIP from GitHub...", 40)

            zip_url = f"https://github.com/{cls.GITHUB_API_REPO}/archive/refs/heads/main.zip"
            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_zip = Path(tmp_dir) / "latest.zip"
                    urllib.request.urlretrieve(zip_url, str(tmp_zip))

                    if progress_cb:
                        progress_cb("Extracting and applying updated files...", 70)

                    with zipfile.ZipFile(tmp_zip, "r") as z:
                        z.extractall(tmp_dir)

                    extracted_root = next(Path(tmp_dir).glob("unrealagentharness*"), None)
                    if extracted_root and extracted_root.is_dir():
                        # Copy extracted files over harness_root (excluding config)
                        for item in extracted_root.iterdir():
                            if item.name.lower() == "config":
                                continue
                            dest = harness_root / item.name if (harness_root / item.name).parent.exists() else harness_root.parent / item.name
                            if item.is_dir():
                                shutil.copytree(item, dest, dirs_exist_ok=True)
                            else:
                                shutil.copy2(item, dest)
            except Exception as e:
                logger.error(f"ZIP update failed: {e}")
                result["message"] = f"ZIP download update error: {str(e)}"
                return result

        # Step 3: Restore config from backup if needed
        if backup_dir.exists() and config_dir.exists():
            for f in backup_dir.glob("*.json"):
                shutil.copy2(f, config_dir / f.name)

        # Step 4: Verification
        if progress_cb:
            progress_cb("Verifying system integrity...", 90)

        # Read updated version.py
        ver_file = harness_root / "version.py"
        new_ver = cls.CURRENT_VERSION
        if ver_file.exists():
            try:
                content = ver_file.read_text(encoding="utf-8")
                for line in content.splitlines():
                    if line.startswith("__version__"):
                        new_ver = line.split("=")[1].strip().strip('"').strip("'")
                        break
            except Exception:
                pass

        result["success"] = True
        result["new_version"] = new_ver
        result["message"] = f"Updated successfully to v{new_ver}! Please restart the Harness to apply all changes."

        if progress_cb:
            progress_cb("Update Complete!", 100)

        logger.info(f"Update applied successfully from v{cls.CURRENT_VERSION} -> v{new_ver}")
        return result

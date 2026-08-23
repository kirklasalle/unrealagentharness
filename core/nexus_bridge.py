r"""
.nexus Platform Interoperability Bridge for UnrealEd Agent Harness.
Connects Agent Harness to Kirk LaSalle's .nexus Agent Post Office (AMTP v3.0) and Chirpy Micro-Broadcast Network.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger

logger = get_logger("NexusBridge", "nexus_bridge.log")

DEFAULT_NEXUS_ROOT = Path(r"d:\projects\.nexus")


class NexusBridge:
    """Provides protocol interop with .nexus for mail, chirps, and telemetry."""

    def __init__(self, nexus_dir: Optional[str] = None):
        if nexus_dir:
            self.nexus_root = Path(nexus_dir)
        else:
            self.nexus_root = DEFAULT_NEXUS_ROOT

        self.is_available = self._detect_nexus()
        self.agent_name = "UnrealEd Architect Agent"
        self.agent_address = "unrealed+harness@.nexus"
        self.operator = "Kirk LaSalle"
        self.platform = "UnrealEngine"

        if self.is_available:
            logger.info(f"Connected to .nexus Post Office at: {self.nexus_root}")
        else:
            logger.debug(f".nexus directory not found at {self.nexus_root}. Running in standalone offline mode.")

    def _detect_nexus(self) -> bool:
        return self.nexus_root.exists() and (self.nexus_root / "nexus.ps1").exists()

    def broadcast_chirp(self, message: str) -> bool:
        """Broadcasts a micro-signal to the Chirpy network via nexus.ps1."""
        if not self.is_available:
            return False

        # Enforce 150 char Chirpy limit
        chirp_msg = message[:145] if len(message) > 145 else message

        try:
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", str(self.nexus_root / "nexus.ps1"),
                "chirp", chirp_msg,
            ]
            result = subprocess.run(cmd, cwd=str(self.nexus_root), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Chirpy broadcast dispatched: '{chirp_msg}'")
                return True
            else:
                logger.warning(f"Chirpy broadcast warning: {result.stderr.strip()}")
                return False
        except Exception as e:
            logger.error(f"Failed to emit Chirp via .nexus: {e}")
            return False

    def send_agent_mail(self, to_address: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> bool:
        """Sends an AMTP message via the .nexus Post Office."""
        if not self.is_available:
            return False

        try:
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", str(self.nexus_root / "nexus.ps1"),
                "mail", "send",
                "-To", to_address,
                "-Subject", subject,
                "-Body", body,
            ]
            if attachments:
                cmd.extend(["-Attachments", ",".join(attachments)])

            result = subprocess.run(cmd, cwd=str(self.nexus_root), capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                logger.info(f"AMTP Mail sent to {to_address} (Subj: '{subject}')")
                return True
            else:
                logger.warning(f"AMTP Mail warning: {result.stderr.strip()}")
                return False
        except Exception as e:
            logger.error(f"Failed to send AMTP mail via .nexus: {e}")
            return False

    def report_build_event(self, engine_id: str, map_action: str, details: str) -> None:
        """Emits an automated telemetry chirp for level build events."""
        chirp_text = f"[{engine_id.upper()}] {map_action}: {details} #unreal #harness"
        self.broadcast_chirp(chirp_text)

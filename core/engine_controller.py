r"""
Multi-Engine UnrealEd Automation Controller for Standalone Agent Harness.
Supports Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e), UT2003 (UE2.0), and UT2004 (UE2.5).
Handles Win32 UI Handles, Command Bar injection, Log streaming, and Viewport Capture.
"""

import ctypes
import io
import json
import math
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import win32con
    import win32gui
    import win32process
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .bootstrap import get_dpi_scale_factor
from .config_manager import ConfigManager
from .logger import get_logger

logger = get_logger("EngineController", "engine_controller.log")


def get_process_image_name(pid: int) -> str:
    """Returns executable name for a given PID using Win32 API."""
    try:
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if hProcess:
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_ulong(1024)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(hProcess, 0, buf, ctypes.byref(size)):
                ctypes.windll.kernel32.CloseHandle(hProcess)
                return os.path.basename(buf.value).lower()
            ctypes.windll.kernel32.CloseHandle(hProcess)
    except Exception as e:
        logger.debug(f"Error querying image name for PID {pid}: {e}")
    return ""


class EngineController:
    """Universal controller targeting UnrealEd 2.x (UE1) and UnrealEd 3.x (UE2/2.5)."""

    def __init__(self, config_mgr: Optional[ConfigManager] = None):
        self.config_mgr = config_mgr or ConfigManager()
        self._hwnd_main: Optional[int] = None
        self._hwnd_edit: Optional[int] = None
        self._pid: Optional[int] = None
        self._last_log_offset = 0
        self._refresh_paths()

    def _refresh_paths(self) -> None:
        profile = self.config_mgr.get_active_engine_profile()
        self.system_dir = Path(profile.get("system_dir", r"G:\UnrealTournament\System"))
        self.script_file = self.system_dir / "AgentExec.txt"
        self.log_filenames = profile.get("log_files", ["Editor.log", "UnrealEd.log"])
        logger.info(f"EngineController re-targeted to: '{profile.get('name', 'Unknown')}' ({self.system_dir})")

    # -----------------------------------------------------------------
    # WIN32 WINDOW DISCOVERY
    # -----------------------------------------------------------------
    def find_unrealed_window(self) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Scans for the active UnrealEd main frame window and command line edit control.
        Supports UT99 (WUnrealEd / UnrealEd.exe), UTronEditor.exe, UT2003, and UT2004.
        """
        if not HAS_PYWIN32:
            logger.warning("pywin32 not available on system.")
            return None, None, None

        profile = self.config_mgr.get_active_engine_profile()
        target_procs = profile.get("process_names", ["unrealed.exe", "utroneditor.exe"])

        prev_hwnd = self._hwnd_main
        prev_edit = self._hwnd_edit
        self._hwnd_main = None
        self._hwnd_edit = None
        self._pid = None

        my_pid = os.getpid()
        candidates: List[Tuple[int, int, str, str]] = []

        def _enum_windows_callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == my_pid:
                    return True

                proc_name = get_process_image_name(pid)
                if proc_name in target_procs or "unrealed" in proc_name or "utron" in proc_name:
                    class_name = win32gui.GetClassName(hwnd)
                    title = win32gui.GetWindowText(hwnd)
                    candidates.append((hwnd, pid, class_name, title))
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(_enum_windows_callback, None)
        except Exception as e:
            logger.error(f"EnumWindows error: {e}")

        # Pick the best candidate
        for hwnd, pid, cls, title in candidates:
            logger.trace(f"Evaluating candidate HWND={hwnd}, PID={pid}, Class='{cls}', Title='{title}'")
            if "Unreal" in title or "WUnrealEd" in cls or "WWindow" in cls or "UTron" in title:
                self._hwnd_main = hwnd
                self._pid = pid
                if hwnd != prev_hwnd:
                    logger.info(f"Targeted UnrealEd Window -> HWND: {hwnd}, PID: {pid}, Class: '{cls}', Title: '{title}'")
                break

        # Fallback to any matching candidate
        if not self._hwnd_main and candidates:
            for hwnd, pid, cls, title in candidates:
                if "#32770" not in cls:
                    self._hwnd_main = hwnd
                    self._pid = pid
                    if hwnd != prev_hwnd:
                        logger.info(f"Targeted UnrealEd Window -> HWND: {hwnd}, PID: {pid}, Class: '{cls}', Title: '{title}'")
                    break

        if self._hwnd_main:
            edit_controls: List[Tuple[int, Tuple[int, int, int, int]]] = []

            def _enum_child_callback(hwnd, extra):
                try:
                    c_name = win32gui.GetClassName(hwnd)
                    if c_name.lower() == "edit":
                        rect = win32gui.GetWindowRect(hwnd)
                        w = rect[2] - rect[0]
                        if w > 60:
                            edit_controls.append((hwnd, rect))
                    elif c_name.lower() == "combobox":
                        inner_edit = win32gui.FindWindowEx(hwnd, 0, "Edit", None)
                        if inner_edit:
                            rect = win32gui.GetWindowRect(inner_edit)
                            edit_controls.append((inner_edit, rect))
                except Exception:
                    pass
                return True

            try:
                win32gui.EnumChildWindows(self._hwnd_main, _enum_child_callback, None)
            except Exception as e:
                logger.error(f"EnumChildWindows error: {e}")

            if edit_controls:
                # Command bar is typically at the bottom of the window (highest Y value)
                edit_controls.sort(key=lambda item: item[1][1], reverse=True)
                self._hwnd_edit = edit_controls[0][0]
                rect = edit_controls[0][1]
                logger.trace(f"Identified {len(edit_controls)} candidate edit controls; selected HWND {self._hwnd_edit}")
                if self._hwnd_edit != prev_edit:
                    logger.info(f"Located UnrealEd Command Edit Control -> HWND: {self._hwnd_edit}, Rect: {rect}")
            else:
                if prev_edit is not None:
                    logger.warning(f"No Edit child control found inside UnrealEd HWND {self._hwnd_main}")

        return self._hwnd_main, self._hwnd_edit, self._pid

    def is_connected(self) -> bool:
        hwnd_main, _, _ = self.find_unrealed_window()
        return hwnd_main is not None

    def launch_editor(self) -> bool:
        """Launches the targeted UnrealEd process for the active engine profile."""
        if self.is_connected():
            logger.info("UnrealEd is already running and connected.")
            return True

        profile = self.config_mgr.get_active_engine_profile()
        sys_dir = Path(profile.get("system_dir", str(self.system_dir)))
        editor_exe = profile.get("editor_exe", "UnrealEd.exe")
        editor_args = profile.get("editor_args", "").strip()

        exe_path = sys_dir / editor_exe
        if not exe_path.exists():
            logger.error(f"Editor executable not found at: {exe_path}")
            return False

        cmd = f'"{exe_path}"'
        if editor_args:
            cmd += f' {editor_args}'

        try:
            logger.info(f"Launching UnrealEd: {cmd} (cwd: {sys_dir})")
            subprocess.Popen(cmd, cwd=str(sys_dir), shell=True)
            return True
        except Exception as e:
            logger.error(f"Failed to launch UnrealEd: {e}")
            return False

    def launch_playtest(
        self,
        map_name: str = "Current",
        game_type: Optional[str] = None,
        num_bots: int = 0,
    ) -> Dict[str, Any]:
        """Saves the current editor map, validates it, and launches a playtest.

        The editor's in-memory level is never treated as playable until a
        deterministic map file exists on disk. This specifically prevents the
        historical ``Index.ut2``/stale-map launch failure.
        """
        profile = self.config_mgr.get_active_engine_profile()
        root_dir = Path(profile.get("root_dir", self.system_dir.parent))
        maps_dir = root_dir / "Maps"
        maps_dir.mkdir(parents=True, exist_ok=True)
        generation = str(profile.get("generation", "UE1")).upper()
        extension = ".ut2" if generation in {"UE2", "UE2.0", "UE2.5"} else ".unr"
        playtest_stem = str(map_name) if map_name and str(map_name).lower() != "current" else "AgentPlaytest"
        playtest_file = maps_dir / f"{playtest_stem}{extension}"

        if str(map_name).lower() == "current":
            save_result = self.execute_command(f'MAP SAVE FILE="{playtest_file}"')
            if not save_result.get("success"):
                return {"success": False, "stage": "save", "error": save_result.get("error", "Map save command failed")}
            deadline = time.time() + 8.0
            while time.time() < deadline and not playtest_file.exists():
                time.sleep(0.1)
            if not playtest_file.exists():
                return {"success": False, "stage": "save", "error": f"Editor did not create {playtest_file}"}

        log_gate = self.validate_editor_log()
        if not log_gate["ok"]:
            return {
                "success": False,
                "stage": "preflight",
                "error": "Editor log contains blocking build warnings",
                "validation": log_gate,
            }

        game_exe = profile.get("game_exe", "UnrealTournament.exe")
        game_path = self.system_dir / game_exe
        if not game_path.exists():
            return {"success": False, "stage": "launch", "error": f"Game executable not found: {game_path}"}

        selected_game = game_type or profile.get("signature_classes", {}).get("GameType", "Botpack.DeathMatchPlus")
        url = playtest_file.name
        if selected_game:
            url += f"?game={selected_game}"
        if num_bots > 0:
            url += f"?NumBots={int(num_bots)}"
        args = [url]
        args.extend(str(profile.get("game_args", "")).split())
        try:
            process = subprocess.Popen([str(game_path), *args], cwd=str(self.system_dir))
            return {"success": True, "stage": "launched", "map_file": str(playtest_file), "pid": process.pid, "args": args}
        except Exception as e:
            logger.error(f"Failed to launch playtest: {e}")
            return {"success": False, "stage": "launch", "error": str(e)}

    # -----------------------------------------------------------------
    # COMMAND EXECUTION
    # -----------------------------------------------------------------
    def execute_command(self, cmd: str) -> Dict[str, Any]:
        """Dispatches a single command to UnrealEd via Win32 Edit injection or batch EXEC."""
        start_time = time.time()
        logger.info(f"Executing Command: '{cmd}'")

        hwnd_main, hwnd_edit, pid = self.find_unrealed_window()

        if not hwnd_main:
            err_msg = f"Target UnrealEd process not found for profile '{self.config_mgr.get_active_engine_id()}'."
            logger.error(err_msg)
            return {"success": False, "command": cmd, "error": err_msg, "execution_time_ms": 0.0}

        # Method 1: Direct Win32 Edit Control injection
        if hwnd_edit and HAS_PYWIN32:
            try:
                win32gui.SendMessage(hwnd_edit, win32con.WM_SETTEXT, 0, cmd)
                time.sleep(0.01)
                win32gui.PostMessage(hwnd_edit, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(hwnd_edit, win32con.WM_CHAR, 13, 0)
                win32gui.PostMessage(hwnd_edit, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

                try:
                    parent_hwnd = win32gui.GetParent(hwnd_edit)
                    if parent_hwnd:
                        ctrl_id = win32gui.GetDlgCtrlID(hwnd_edit)
                        win32gui.PostMessage(parent_hwnd, win32con.WM_COMMAND,
                                             (win32con.EN_CHANGE << 16) | (ctrl_id & 0xFFFF), hwnd_edit)
                except Exception:
                    pass

                elapsed = (time.time() - start_time) * 1000.0
                return {
                    "success": True, "command": cmd,
                    "execution_time_ms": round(elapsed, 2),
                    "method": "win32_edit_injection", "target_hwnd": hwnd_edit,
                }
            except Exception as e:
                logger.warning(f"Win32 Edit injection failed: {e}. Falling back to batch script execution...")

        # Method 2: Batch script file EXEC injection
        try:
            with open(self.script_file, "w", encoding="utf-8") as f:
                f.write(cmd + "\n")
            if hwnd_edit and HAS_PYWIN32:
                script_cmd = f'EXEC "{self.script_file.name}"'
                win32gui.SendMessage(hwnd_edit, win32con.WM_SETTEXT, 0, script_cmd)
                win32gui.PostMessage(hwnd_edit, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(hwnd_edit, win32con.WM_CHAR, 13, 0)
                win32gui.PostMessage(hwnd_edit, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

            elapsed = (time.time() - start_time) * 1000.0
            return {"success": True, "command": cmd, "execution_time_ms": round(elapsed, 2), "method": "batch_script_exec"}
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"Command '{cmd}' failed: {e}")
            return {"success": False, "command": cmd, "error": str(e), "execution_time_ms": round(elapsed, 2)}

    def execute_batch(self, commands: List[str], delay_between: float = 0.08) -> List[Dict[str, Any]]:
        results = []
        for cmd in commands:
            c = cmd.strip()
            if not c:
                continue
            res = self.execute_command(c)
            results.append(res)

            # Heavy commands need extra breathing room for UnrealEd BSP/Path compiler
            c_upper = c.upper()
            if "PATHS BUILD" in c_upper:
                time.sleep(0.8)
                self.dismiss_dialogs()
            elif "REBUILD" in c_upper or "IMPORT" in c_upper or "SUBTRACT" in c_upper or "MAP NEW" in c_upper or "BRUSH ADD" in c_upper:
                time.sleep(0.4)
                self.dismiss_dialogs()
            elif delay_between > 0:
                time.sleep(delay_between)
        return results

    def execute_batch_staged(
        self,
        commands: List[str],
        stage_callback: Optional[Any] = None,
        delay_between: float = 0.08,
    ) -> Dict[str, Any]:
        """Executes commands in observable stages and returns a QA summary."""
        stages = [
            ("world", lambda c: c.startswith("MAP NEW") or c.startswith("OBJ LOAD") or "ValleyMain" in c),
            ("geometry", lambda c: "BRUSH" in c),
            ("actors", lambda c: "MAP IMPORT" in c or "ACTOR" in c),
            ("compile", lambda c: any(token in c for token in ("MAP REBUILD", "LIGHT APPLY", "PATHS BUILD", "PATHS DEFINE"))),
        ]
        results: List[Dict[str, Any]] = []
        current_stage = "prepare"
        for index, command in enumerate(commands):
            clean = command.strip()
            if not clean:
                continue
            for name, predicate in stages:
                if predicate(clean):
                    current_stage = name
                    break
            if stage_callback:
                stage_callback(current_stage, index + 1, len(commands), clean)
            result = self.execute_command(clean)
            results.append(result)
            if not result.get("success", False):
                return {"ok": False, "stage": current_stage, "index": index, "results": results}
            upper = clean.upper()
            if "PATHS BUILD" in upper:
                time.sleep(0.8)
                self.dismiss_dialogs()
            elif any(token in upper for token in ("REBUILD", "IMPORT", "SUBTRACT", "MAP NEW", "BRUSH ADD")):
                time.sleep(0.4)
                self.dismiss_dialogs()
            elif delay_between > 0:
                time.sleep(delay_between)
        return {"ok": True, "stage": current_stage, "results": results}

    def validate_editor_log(self, lines: Optional[List[str]] = None) -> Dict[str, Any]:
        """Classifies known UnrealEd geometry/navigation warnings for build gates."""
        source = lines if lines is not None else self.get_log_deltas()
        patterns = {
            "collapsed_polygon": "collapsed a point",
            "scout_didnt_fit": "scout didn't fit",
            "no_valid_start": "no valid start found",
            "failed_spawn": "failed to spawn player actor",
            "too_close": "may be too close",
        }
        findings = {
            key: [line for line in source if needle in line.lower()]
            for key, needle in patterns.items()
        }
        errors = {key: value for key, value in findings.items() if value}
        return {
            "ok": not errors,
            "findings": findings,
            "error_count": sum(len(value) for value in errors.values()),
        }

    def validate_t3d_actor_manifest(self, actor_file: Path) -> Dict[str, Any]:
        """Performs deterministic preflight checks on generated actor T3D."""
        text = Path(actor_file).read_text(encoding="utf-8", errors="replace")
        import re
        locations = []
        for match in re.finditer(
            r"Begin Actor Class=([^ ]+) Name=([^\r\n]+).*?Location=\(X=([-+0-9.]+),Y=([-+0-9.]+),Z=([-+0-9.]+)\)",
            text,
            flags=re.DOTALL,
        ):
            locations.append({
                "class": match.group(1), "name": match.group(2).strip(),
                "location": tuple(float(match.group(i)) for i in (3, 4, 5)),
            })

        starts = [a for a in locations if a["class"].endswith("PlayerStart")]
        warnings: List[str] = []
        for i, first in enumerate(starts):
            for second in starts[i + 1:]:
                distance = sum((first["location"][axis] - second["location"][axis]) ** 2 for axis in range(3)) ** 0.5
                if distance < 128.0:
                    warnings.append(f"Player starts too close: {first['name']} / {second['name']}")
        return {
            "ok": bool(starts) and not warnings,
            "actor_count": len(locations),
            "player_start_count": len(starts),
            "warnings": warnings,
        }

    def run_map_preflight(self, actor_file: Optional[Path] = None) -> Dict[str, Any]:
        """Combines generated-actor and editor-log gates for build orchestration."""
        report: Dict[str, Any] = {"ok": True, "checks": {}}
        if actor_file and Path(actor_file).exists():
            report["checks"]["actors"] = self.validate_t3d_actor_manifest(Path(actor_file))
            report["ok"] = report["ok"] and report["checks"]["actors"]["ok"]
        report["checks"]["editor_log"] = self.validate_editor_log()
        report["ok"] = report["ok"] and report["checks"]["editor_log"]["ok"]
        return report

    def validate_generated_map(self, actor_file: Optional[Path] = None) -> Dict[str, Any]:
        """Validates generated actor content without consuming live log state.

        Use :meth:`run_map_preflight` when the caller intentionally wants to
        combine this deterministic manifest check with current UnrealEd log
        findings. Keeping the two operations separate makes offline/unit
        validation reproducible and prevents an unrelated previous map's log
        warning from contaminating a newly generated manifest check.
        """
        if actor_file and Path(actor_file).exists():
            actors = self.validate_t3d_actor_manifest(Path(actor_file))
            return {"ok": actors["ok"], "checks": {"actors": actors}}
        return {"ok": False, "checks": {"actors": {"ok": False, "warnings": ["Actor manifest not found"]}}}

    def build_manifest(
        self,
        build_id: str,
        actor_file: Optional[Path] = None,
        scene_graph_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Creates a portable build manifest from current engine evidence."""
        manifest = {
            "schema": "uah.build_manifest.v1",
            "build_id": build_id,
            "engine_id": self.config_mgr.get_active_engine_id(),
            "system_dir": str(self.system_dir),
            "actor_file": str(actor_file) if actor_file else "",
            "scene_graph_path": str(scene_graph_path) if scene_graph_path else "",
            "preflight": self.run_map_preflight(actor_file),
            "created_at": time.time(),
        }
        manifest_dir = Path(__file__).resolve().parent.parent / "logs" / "build_manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        target = manifest_dir / f"{build_id}.json"
        target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        manifest["manifest_path"] = str(target)
        try:
            from .memory_engine import MemoryEngine
            MemoryEngine().record_build_manifest(manifest)
        except Exception as exc:
            logger.debug(f"Build manifest graph record unavailable: {exc}")
        return manifest

    # -----------------------------------------------------------------
    # DIALOG DISMISSAL & UTILITIES
    # -----------------------------------------------------------------
    def dismiss_dialogs(self) -> int:
        """Dismisses modal popups (e.g. Map Check, Rebuild complete) without freezing."""
        if not HAS_PYWIN32:
            return 0

        dismissed = 0
        dialog_hwnds: List[int] = []

        def _enum_dialogs(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            try:
                cls = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd).lower()
                if cls == "#32770" or any(kw in title for kw in ["check", "progress", "warning", "information", "notice", "map check"]):
                    if any(kw in title for kw in ["check", "progress", "warning", "information", "notice", "map check"]):
                        dialog_hwnds.append(hwnd)
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(_enum_dialogs, None)
        except Exception:
            pass

        for dhwnd in dialog_hwnds:
            try:
                win32gui.PostMessage(dhwnd, win32con.WM_CLOSE, 0, 0)
                dismissed += 1
            except Exception:
                pass

        return dismissed

    # -----------------------------------------------------------------
    # LOG TAILING
    # -----------------------------------------------------------------
    def get_log_deltas(self) -> List[str]:
        """Reads new log entries from the active engine's log files."""
        for log_name in self.log_filenames:
            log_path = self.system_dir / log_name
            if log_path.exists():
                try:
                    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                        f.seek(self._last_log_offset)
                        new_lines = f.readlines()
                        self._last_log_offset = f.tell()
                        return [l.strip() for l in new_lines if l.strip()]
                except Exception:
                    pass
        return []

    # -----------------------------------------------------------------
    # VIEWPORT CAPTURE
    # -----------------------------------------------------------------
    def capture_viewport_image(self) -> Optional[bytes]:
        """Captures the active UnrealEd viewport as PNG bytes.

        Uses DPI-aware coordinates (initialised by bootstrap.py) so that
        captures on 4K / multi-monitor setups return pixel-accurate images.
        """
        if not HAS_PIL or not HAS_PYWIN32:
            return None

        hwnd_main, _, _ = self.find_unrealed_window()
        if not hwnd_main:
            return None

        try:
            rect = win32gui.GetWindowRect(hwnd_main)
            # With DPI awareness active, GetWindowRect already returns
            # physical pixel coordinates; ImageGrab.grab also expects them.
            bbox = (rect[0], rect[1], rect[2], rect[3])
            img = ImageGrab.grab(bbox=bbox)
            dpi_scale = get_dpi_scale_factor(hwnd_main)
            logger.info(
                f"Viewport captured: {img.size[0]}x{img.size[1]}px "
                f"(DPI scale: {dpi_scale:.2f}x)"
            )
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Viewport capture error: {e}")
            return None

    def capture_viewport_quality(self) -> Dict[str, Any]:
        """Captures the editor viewport and runs the visual smoke gate."""
        image_bytes = self.capture_viewport_image()
        if not image_bytes:
            return {"ok": False, "reason": "Viewport capture unavailable"}
        try:
            from PIL import Image
            image = Image.open(io.BytesIO(image_bytes))
            from .vision_inspector import VisionInspector
            return VisionInspector().analyze_viewport_quality(image)
        except Exception as exc:
            return {"ok": False, "reason": str(exc)}

    # -----------------------------------------------------------------
    # STANDARD VIEWPORT CONFIGURATION (TOP, FRONT, SIDE + DYNAMIC LIGHT)
    # -----------------------------------------------------------------
    def configure_standard_viewports(self) -> Dict[str, Any]:
        """
        Configures UnrealEd to the standard 4-viewport layout:
        - Top row (1/3 width each, 1/2 height): Top (XY), Front (XZ), Side (YZ) scaled for complete view
        - Bottom row (full width, 1/2 height): Dynamic Light (3D perspective)
        Updates UnrealEd.ini and dispatches camera alignment/extents commands.
        """
        ini_path = self.system_dir / "UnrealEd.ini"
        ini_updated = False
        if ini_path.exists():
            try:
                content = ini_path.read_text(encoding="utf-8", errors="replace")
                # Ensure Config=3 in [Viewports] if present
                import re
                if "[Viewports]" in content:
                    content = re.sub(r"(?<=\[Viewports\][\r\n]{1,2})Config=\d+", "Config=3", content)
                ini_path.write_text(content, encoding="utf-8")
                ini_updated = True
                logger.info(f"Updated {ini_path.name} to standard 4-viewport layout (Config=3)")
            except Exception as e:
                logger.warning(f"Could not update UnrealEd.ini viewport config: {e}")

        # If connected to live editor, issue viewport alignment, centering, zoom, and redraw commands
        commands_dispatched = []
        if self.is_connected():
            setup_cmds = [
                # 1. Move camera/starting vantage position out to the adjacent foreground vantage location
                "CAMERA MOVETO X=-600 Y=1400 Z=400 PITCH=-3000 YAW=-16000 ROLL=0",
                # 2. Zoom out and center the Top (XY) orthographic grid view
                "VIEWPORT TOP ZOOM=100",
                # 3. Zoom out and center the Front (XZ) orthographic grid view
                "VIEWPORT FRONT ZOOM=100",
                # 4. Zoom out and center the Side (YZ) orthographic grid view
                "VIEWPORT SIDE ZOOM=100",
                # 5. Enable real-time Dynamic Lighting on perspective viewport and redraw all
                "MODE DYNAMICLIGHT",
                "CAMERA ALIGN",
                "VIEWPORT REDRAW",
            ]
            for cmd in setup_cmds:
                res = self.execute_command(cmd)
                commands_dispatched.append(res)


        # Record training and configuration telemetry in Graph Memory
        try:
            from .memory_engine import MemoryEngine
            mem = MemoryEngine()
            mem.record_graph_node(
                "viewport:standard_quad_layout",
                "config",
                "Standard 4-Viewport Setup (Top, Front, Side + Dynamic Light)",
                {
                    "layout": "3_top_ortho_1_bottom_dynamic_light",
                    "top_row": ["top_xy", "front_xz", "side_yz"],
                    "bottom_row": ["dynamic_light_3d"],
                    "ini_updated": ini_updated,
                    "active_engine": self.config_mgr.get_active_engine_id(),
                    "timestamp": time.time(),
                }
            )
            mem.record_wisdom(
                category="viewport_standard",
                title="Standard 4-Viewport Editor Setup (Top, Front, Side + Dynamic Light)",
                content=(
                    "The world-class default Unreal Editor layout splits the workspace into a top tri-view "
                    "(Top XY, Front XZ, Side YZ scaled to full extents) and a bottom panoramic Dynamic Light 3D viewport. "
                    "This ensures continuous multi-angle spatial awareness and real-time lighting evaluation."
                ),
                tags="viewport,unrealed,dynamic_light,ortho,standards",
                confidence=1.0,
            )
        except Exception as e:
            logger.debug(f"Memory recording for viewport setup deferred: {e}")

        return {
            "success": True,
            "ini_updated": ini_updated,
            "commands": commands_dispatched,
            "layout": "Top (XY) | Front (XZ) | Side (YZ) above Dynamic Light (3D)",
        }


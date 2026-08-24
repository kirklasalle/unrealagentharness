r"""
Multi-Engine UnrealEd Automation Controller for Standalone Agent Harness.
Supports Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e), UT2003 (UE2.0), and UT2004 (UE2.5).
Handles Win32 UI Handles, Command Bar injection, Log streaming, and Viewport Capture.
"""

import ctypes
import io
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

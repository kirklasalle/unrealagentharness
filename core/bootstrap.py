"""
Universal Bootstrap for Standalone Multi-Engine Agent Harness.
Ensures repository root is always in sys.path, aliases 'AgentHarness' dynamically in sys.modules,
installs early crash / trace logging hooks, and initialises Win32 DPI awareness for accurate
multi-monitor 4K viewport capture and coordinate mapping.
"""

import os
import sys
from pathlib import Path

# Identify repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# 1. Normalize sys.path so 'core', 'ui', 'server', 'config' are importable directly
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# 2. Alias AgentHarness in sys.modules so `from AgentHarness.core...` always works
try:
    import core
    import ui
    import server
    import version

    class _AgentHarnessNamespace:
        core = core
        ui = ui
        server = server
        version = version
        __path__ = [str(REPO_ROOT)]

    if "AgentHarness" not in sys.modules:
        sys.modules["AgentHarness"] = _AgentHarnessNamespace
        sys.modules["AgentHarness.core"] = core
        sys.modules["AgentHarness.ui"] = ui
        sys.modules["AgentHarness.server"] = server
        sys.modules["AgentHarness.version"] = version
except Exception:
    pass

# Ensure logs directory exists
LOGS_DIR = REPO_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 3. Win32 DPI Awareness Initialization
# ---------------------------------------------------------------------------
# Without this, GetWindowRect / ImageGrab.grab on 4K / multi-monitor setups
# return virtualised (scaled) coordinates, producing blurry or incorrectly-
# cropped viewport captures.  The harness calls this at import-time so every
# module that later uses Win32 screen coordinates gets true physical pixels.
#
# Fallback chain (newest → oldest API):
#   Win10 1703+  → SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)
#   Win8.1+      → SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
#   Win7+        → SetProcessDPIAware()   (system-level only, no per-monitor)
# ---------------------------------------------------------------------------

_DPI_AWARENESS_LEVEL = "unset"  # tracks which tier succeeded


def _init_dpi_awareness() -> str:
    """
    Attempts to set the highest available DPI awareness mode.
    Returns a string describing which tier was activated:
      'per_monitor_v2'  – Win10 1703+ (best: per-monitor V2 scaling)
      'per_monitor'     – Win8.1+     (per-monitor scaling)
      'system_aware'    – Win7+       (system-level DPI only)
      'unavailable'     – Non-Windows or all API calls failed
    """
    if sys.platform != "win32":
        return "unavailable"

    import ctypes

    # Tier 1: SetProcessDpiAwarenessContext  (Win10 1703+ / user32.dll)
    # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
    try:
        result = ctypes.windll.user32.SetProcessDpiAwarenessContext(
            ctypes.c_ssize_t(-4)
        )
        if result:
            return "per_monitor_v2"
    except (AttributeError, OSError):
        pass

    # Tier 2: SetProcessDpiAwareness  (Win8.1+ / shcore.dll)
    # PROCESS_PER_MONITOR_DPI_AWARE = 2
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return "per_monitor"
    except (AttributeError, OSError):
        pass

    # Tier 3: SetProcessDPIAware  (Win7+ / user32.dll, system-wide only)
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return "system_aware"
    except (AttributeError, OSError):
        pass

    return "unavailable"


# Run at import time so all downstream Win32 coordinate calls are accurate
_DPI_AWARENESS_LEVEL = _init_dpi_awareness()


def get_dpi_awareness_level() -> str:
    """Returns the DPI awareness tier that was activated at bootstrap.

    Possible values:
      'per_monitor_v2' | 'per_monitor' | 'system_aware' | 'unavailable'
    """
    return _DPI_AWARENESS_LEVEL


def get_dpi_scale_factor(hwnd: int = 0) -> float:
    """
    Returns the DPI scale factor for a given window handle (or the primary
    monitor if hwnd is 0).

    A 100% (96 DPI) display returns 1.0; a 150% (144 DPI) display returns 1.5;
    a 200% (192 DPI / 4K) display returns 2.0, etc.

    This factor is essential for converting between virtualised coordinates
    (returned by non-DPI-aware APIs) and true physical pixel coordinates
    needed by ImageGrab.grab().

    Args:
        hwnd: Win32 window handle. Pass 0 for primary monitor.

    Returns:
        DPI scale factor as a float (≥ 1.0). Falls back to 1.0 on failure.
    """
    if sys.platform != "win32":
        return 1.0

    import ctypes

    # Tier 1: GetDpiForWindow (Win10 1607+ / user32.dll)  — per-window DPI
    if hwnd:
        try:
            dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
            if dpi > 0:
                return dpi / 96.0
        except (AttributeError, OSError):
            pass

    # Tier 2: GetDpiForSystem (Win10 1607+ / user32.dll)  — system-wide DPI
    try:
        dpi = ctypes.windll.user32.GetDpiForSystem()
        if dpi > 0:
            return dpi / 96.0
    except (AttributeError, OSError):
        pass

    # Tier 3: GetDeviceCaps on the desktop DC  (Win7+ / gdi32.dll)
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        if hdc:
            LOGPIXELSX = 88
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            ctypes.windll.user32.ReleaseDC(0, hdc)
            if dpi > 0:
                return dpi / 96.0
    except (AttributeError, OSError):
        pass

    return 1.0

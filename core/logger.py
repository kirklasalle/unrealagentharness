"""
Centralized World-Class Logger & Diagnostics System for Standalone Multi-Engine Agent Harness.
Supports custom TRACE level (5), microsecond timestamp formatting, multi-destination rotating logs,
global uncaught exception crash capture, and environment diagnostics.
"""

import atexit
import datetime
import logging
import os
import platform
import sys
import threading
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Define custom TRACE log level (level 5, below DEBUG=10)
TRACE_LEVEL_NUM = 5
TRACE_LEVEL_NAME = "TRACE"

if not hasattr(logging, "TRACE"):
    logging.TRACE = TRACE_LEVEL_NUM
    logging.addLevelName(TRACE_LEVEL_NUM, TRACE_LEVEL_NAME)


def _logger_trace(self, message, *args, **kwargs):
    """Log 'msg % args' with severity 'TRACE'."""
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


if not hasattr(logging.Logger, "trace"):
    logging.Logger.trace = _logger_trace

# Directory paths
LOGS_DIR = REPO_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MASTER_LOG_FILE = LOGS_DIR / "agent_harness.log"
CRASH_LOG_FILE = LOGS_DIR / "agent_harness_crash.log"

# Default log level from environment
_DEFAULT_LEVEL_STR = os.getenv("AGENT_HARNESS_LOG_LEVEL", "DEBUG").strip().upper()
_LEVEL_MAP = {
    "TRACE": TRACE_LEVEL_NUM,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.CRITICAL,
}
_CURRENT_GLOBAL_LEVEL = _LEVEL_MAP.get(_DEFAULT_LEVEL_STR, logging.DEBUG)

# ANSI Color codes for console output
_COLORS = {
    "TRACE": "\033[36m",      # Cyan
    "DEBUG": "\033[34m",      # Blue
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "WARN": "\033[33m",
    "ERROR": "\033[31m",      # Red
    "CRITICAL": "\033[1;31m", # Bold Red
    "RESET": "\033[0m",
}


class ColoredConsoleFormatter(logging.Formatter):
    """Rich colorized formatter for terminal console output."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = sys.stdout.isatty() or os.name == "nt"

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        msg = super().format(record)
        if self.use_color and levelname in _COLORS:
            color = _COLORS[levelname]
            reset = _COLORS["RESET"]
            return f"{color}{msg}{reset}"
        return msg


# High-precision millisecond formatters
DETAILED_FORMAT = (
    "[%(asctime)s.%(msecs)03d] [%(levelname)-5s] [PID:%(process)d:%(threadName)s] "
    "[%(name)s] [%(filename)s:%(lineno)d] %(message)s"
)
CONSOLE_FORMAT = "[%(asctime)s.%(msecs)03d] [%(levelname)-5s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_file_formatter = logging.Formatter(fmt=DETAILED_FORMAT, datefmt=DATE_FORMAT)
_console_formatter = ColoredConsoleFormatter(fmt=CONSOLE_FORMAT, datefmt=DATE_FORMAT)

# Shared master file handler
_master_file_handler: Optional[RotatingFileHandler] = None
_master_handler_lock = threading.Lock()


def get_master_file_handler() -> RotatingFileHandler:
    """Returns a singleton rotating file handler for the consolidated master log."""
    global _master_file_handler
    with _master_handler_lock:
        if _master_file_handler is None:
            _master_file_handler = RotatingFileHandler(
                str(MASTER_LOG_FILE),
                maxBytes=10 * 1024 * 1024,  # 10 MB per file
                backupCount=5,
                encoding="utf-8",
                delay=True,
            )
            _master_file_handler.setLevel(TRACE_LEVEL_NUM)
            _master_file_handler.setFormatter(_file_formatter)
        return _master_file_handler


def get_logger(
    name: str = "AgentHarness",
    log_filename: Optional[str] = "agent_harness.log",
    level: Optional[int] = None,
) -> logging.Logger:
    """
    Factory function to retrieve or configure a logger with world-class trace logging.

    Args:
        name: Logger identifier (e.g. 'EngineController', 'NexusBridge')
        log_filename: Dedicated log file in logs/ (if different from master log)
        level: Minimum log level override (defaults to global level)
    """
    logger = logging.getLogger(name)
    target_level = level if level is not None else _CURRENT_GLOBAL_LEVEL
    logger.setLevel(target_level)

    # Check if handlers already configured
    if logger.handlers:
        return logger

    logger.propagate = False

    # 1. Console Stream Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(target_level)
    ch.setFormatter(_console_formatter)
    logger.addHandler(ch)

    # 2. Master Consolidated File Handler
    try:
        master_handler = get_master_file_handler()
        logger.addHandler(master_handler)
    except Exception as e:
        sys.stderr.write(f"[WARN] Failed to attach master log handler: {e}\n")

    # 3. Component-Specific File Handler (if requested and distinct from master)
    if log_filename and log_filename != "agent_harness.log":
        try:
            comp_log_path = LOGS_DIR / log_filename
            fh = RotatingFileHandler(
                str(comp_log_path),
                maxBytes=5 * 1024 * 1024,  # 5 MB per component file
                backupCount=3,
                encoding="utf-8",
                delay=True,
            )
            fh.setLevel(target_level)
            fh.setFormatter(_file_formatter)
            logger.addHandler(fh)
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to attach component log handler for {log_filename}: {e}\n")

    return logger


def set_global_log_level(level_name_or_int: str | int) -> None:
    """Sets log level globally across all active and future loggers."""
    global _CURRENT_GLOBAL_LEVEL
    if isinstance(level_name_or_int, str):
        _CURRENT_GLOBAL_LEVEL = _LEVEL_MAP.get(level_name_or_int.strip().upper(), logging.DEBUG)
    else:
        _CURRENT_GLOBAL_LEVEL = int(level_name_or_int)

    # Update root and active loggers
    root = logging.getLogger()
    root.setLevel(_CURRENT_GLOBAL_LEVEL)
    for name in list(logging.root.manager.loggerDict.keys()):
        log = logging.getLogger(name)
        log.setLevel(_CURRENT_GLOBAL_LEVEL)
        for h in log.handlers:
            h.setLevel(_CURRENT_GLOBAL_LEVEL)


def flush_all_logs() -> None:
    """Flushes all active log handlers to disk immediately."""
    for name in list(logging.root.manager.loggerDict.keys()):
        log = logging.getLogger(name)
        for h in getattr(log, "handlers", []):
            try:
                h.flush()
            except Exception:
                pass
    if _master_file_handler:
        try:
            _master_file_handler.flush()
        except Exception:
            pass


# Auto-flush at process exit
atexit.register(flush_all_logs)


def write_crash_report(
    exc_type,
    exc_value,
    exc_tb,
    context: str = "Unhandled Exception",
) -> Path:
    """
    Writes an exhaustive crash diagnostics report to logs/agent_harness_crash.log.
    Captures complete stack traces, hardware/OS metadata, environment, and sys info.
    """
    try:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        tb_text = "".join(tb_lines)

        # Redact sensitive environment variables
        safe_env = {}
        for k, v in os.environ.items():
            if any(s in k.upper() for s in ["KEY", "TOKEN", "SECRET", "PASS", "AUTH"]):
                safe_env[k] = "***REDACTED***"
            else:
                safe_env[k] = v

        report = [
            "=" * 80,
            f"AGENT HARNESS CRASH DIAGNOSTICS REPORT — {now_str}",
            "=" * 80,
            f"Context       : {context}",
            f"Exception     : {exc_type.__name__ if exc_type else 'Unknown'}: {exc_value}",
            f"Python Ver    : {sys.version}",
            f"Platform      : {platform.platform()} ({platform.machine()})",
            f"Executable    : {sys.executable}",
            f"Working Dir   : {os.getcwd()}",
            f"Arguments     : {sys.argv}",
            f"Thread        : {threading.current_thread().name} (ID: {threading.get_ident()})",
            f"Process PID   : {os.getpid()}",
            "-" * 80,
            "TRACEBACK:",
            tb_text.rstrip(),
            "-" * 80,
            "ENVIRONMENT DUMP (Sanitized):",
        ]

        for k, v in sorted(safe_env.items()):
            report.append(f"  {k} = {v}")

        report.append("=" * 80)
        report.append("\n")
        report_str = "\n".join(report)

        # Write to crash log file
        with open(CRASH_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(report_str)

        # Also write to master log
        master_logger = get_logger("CrashHandler")
        master_logger.critical(f"CRASH OCCURRED: {exc_type.__name__ if exc_type else 'Unknown'}: {exc_value}\n{tb_text}")
        flush_all_logs()

        return CRASH_LOG_FILE
    except Exception as e:
        sys.stderr.write(f"[FATAL] Failed to write crash report: {e}\n")
        return CRASH_LOG_FILE


def _global_excepthook(exc_type, exc_value, exc_tb):
    """Global uncaught exception handler for main thread."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    crash_file = write_crash_report(exc_type, exc_value, exc_tb, context="Main Thread Exception")
    sys.stderr.write(
        f"\n[FATAL ERROR] An unhandled exception crashed the Agent Harness!\n"
        f"Details have been written to: {crash_file}\n"
    )
    traceback.print_exception(exc_type, exc_value, exc_tb)


def _threading_excepthook(args):
    """Global uncaught exception handler for background threads."""
    if issubclass(args.exc_type, KeyboardInterrupt):
        return

    crash_file = write_crash_report(
        args.exc_type,
        args.exc_value,
        args.exc_traceback,
        context=f"Background Thread [{args.thread.name if args.thread else 'Unknown'}] Exception",
    )
    sys.stderr.write(
        f"\n[FATAL THREAD ERROR] Thread '{args.thread.name if args.thread else 'Unknown'}' crashed!\n"
        f"Details have been written to: {crash_file}\n"
    )


def setup_global_exception_handlers():
    """Installs process-wide unhandled exception hooks for bulletproof crash logging."""
    sys.excepthook = _global_excepthook
    if hasattr(threading, "excepthook"):
        threading.excepthook = _threading_excepthook


# Automatically install exception handlers on import
setup_global_exception_handlers()

# Default logger instance for direct import
logger = get_logger("AgentHarness")

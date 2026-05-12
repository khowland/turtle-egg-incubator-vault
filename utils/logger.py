"""
=============================================================================
Module:        utils/logger.py
Project:       WINC Incubator System v9.2.0
Requirement:   Enterprise Logging Standard [§35, §36]
Description:   Structured JSON logging with file rotation, automatic
               timestamp capture, correlation IDs, context injection,
               performance timing, and @log_exceptions decorator.
               
               Outputs:
               - logs/app.log      (INFO+, all messages)
               - logs/error.log    (ERROR+, exceptions + tracebacks)
               - stdout            (real-time terminal output)
               
               Usage:
                   from utils.logger import logger, log_context
                   log_context.set(session_id="...", observer_id="...", page="Dashboard")
                   logger.info("User logged in")
                   
                   from utils.logger import log_exceptions, log_timing
                   @log_timing
                   @log_exceptions
                   def risky_function():
                       ...

               Environment Variables:
                   LOG_LEVEL   - Set log level (DEBUG, INFO, WARNING, ERROR). Default: INFO
                   TEST_MODE   - Set to '1' or 'true' to suppress file logging during tests.
=============================================================================
"""

import logging
import logging.handlers
import sys
import os
import functools
import json
import time
import traceback
import contextvars
import threading
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Log Context (contextvars for cross-function correlation)
# ---------------------------------------------------------------------------
_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")
_session_id: contextvars.ContextVar[str] = contextvars.ContextVar("session_id", default="")
_observer_id: contextvars.ContextVar[str] = contextvars.ContextVar("observer_id", default="")
_page_name: contextvars.ContextVar[str] = contextvars.ContextVar("page_name", default="")

class LogContext:
    """Thread-safe log context manager for injecting session/observer/trace IDs."""
    
    @staticmethod
    def set(session_id: str = "", observer_id: str = "", page_name: str = "", trace_id: str = ""):
        """Set log context for the current request/rerun."""
        if not trace_id:
            trace_id = str(uuid.uuid4())[:8]
        _trace_id.set(trace_id)
        _session_id.set(session_id or "")
        _observer_id.set(observer_id or "")
        _page_name.set(page_name or "")
    
    @staticmethod
    def get() -> dict:
        """Get current log context as a dict."""
        return {
            "trace_id": _trace_id.get(),
            "session_id": _session_id.get(),
            "observer_id": _observer_id.get(),
            "page": _page_name.get(),
        }
    
    @staticmethod
    def clear():
        """Clear log context."""
        _trace_id.set("")
        _session_id.set("")
        _observer_id.set("")
        _page_name.set("")

log_context = LogContext()


# ---------------------------------------------------------------------------
# Silent failure tracking (alert on swallowed exceptions)
# ---------------------------------------------------------------------------
_silent_failure_count = 0
_silent_failure_lock = threading.Lock()

def get_silent_failure_count() -> int:
    """Return the count of silently swallowed exceptions since server start."""
    return _silent_failure_count


# ---------------------------------------------------------------------------
# Environment-based configuration
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    LOG_LEVEL = "INFO"

TEST_MODE = os.getenv("TEST_MODE", "").lower() in ("1", "true", "yes")


# ---------------------------------------------------------------------------
# Ensure logs directory exists
# ---------------------------------------------------------------------------
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Context Filter – injects trace/context into every log record
# ---------------------------------------------------------------------------
class ContextFilter(logging.Filter):
    """Inject correlation context (trace_id, session_id, observer_id, page) into each log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = _trace_id.get() or ""
        record.session_id = _session_id.get() or ""
        record.observer_id = _observer_id.get() or ""
        record.page = _page_name.get() or ""
        return True


# ---------------------------------------------------------------------------
# Structured JSON Formatter
# ---------------------------------------------------------------------------
class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter with automatic context injection."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        # Inject correlation context if present
        for key in ("trace_id", "session_id", "observer_id", "page"):
            val = getattr(record, key, "")
            if val:
                log_entry[key] = val
        # Include extra fields if present
        if hasattr(record, "extra_data") and record.extra_data:
            log_entry["extra"] = record.extra_data
        # Include exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        return json.dumps(log_entry)


# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------
logger = logging.getLogger("WINC-Vault")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logger.propagate = False

# Attach context filter
context_filter = ContextFilter()
logger.addFilter(context_filter)

# Clear any existing handlers (idempotent on reload)
if logger.handlers:
    logger.handlers.clear()

# --- Console Handler (stdout, human-readable) ---
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(module)-12s | %(trace_id)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(console_handler)

# --- File Handlers (disabled in TEST_MODE) ---
if not TEST_MODE:
    # App Log: INFO+, structured JSON
    app_log_path = os.path.join(LOG_DIR, "app.log")
    app_file_handler = logging.handlers.RotatingFileHandler(
        app_log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(app_file_handler)

    # Error Log: ERROR+, structured JSON
    error_log_path = os.path.join(LOG_DIR, "error.log")
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(error_file_handler)
else:
    logger.info("🧪 TEST_MODE active – file logging suppressed")


# ---------------------------------------------------------------------------
# @log_timing Decorator
# ---------------------------------------------------------------------------
def log_timing(func=None, *, threshold_ms: float = 0):
    """
    Decorator that logs function execution time.
    
    Args:
        threshold_ms: Only log if execution exceeds this many milliseconds (0 = always log).
    
    Usage:
        @log_timing
        def slow_func():
            ...
        
        @log_timing(threshold_ms=500)
        def sometimes_slow():
            ...
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = f(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                if elapsed_ms >= threshold_ms:
                    logger.debug(
                        f"[{f.__name__}] completed in {elapsed_ms:.2f}ms",
                        extra={"extra_data": {
                            "timing": {"function": f.__name__, "elapsed_ms": round(elapsed_ms, 2)}
                        }}
                    )
                return result
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.warning(
                    f"[{f.__name__}] failed after {elapsed_ms:.2f}ms",
                    extra={"extra_data": {
                        "timing": {"function": f.__name__, "elapsed_ms": round(elapsed_ms, 2), "status": "failed"}
                    }}
                )
                raise
        return wrapper
    
    if func is not None and callable(func):
        return decorator(func)
    return decorator


# ---------------------------------------------------------------------------
# @log_exceptions Decorator
# ---------------------------------------------------------------------------
def log_exceptions(func=None, *, reraise=True, log_args=False):
    """
    Decorator that automatically wraps a function in try/except,
    logging ALL exceptions with full traceback and timestamp.
    
    When reraise=False, a WARNING is logged and a global silent-failure counter
    is incremented for monitoring.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                extra = {
                    "decorator": "log_exceptions",
                    "reraise": reraise,
                    "function": f.__name__,
                    "module": f.__module__,
                }
                if log_args:
                    extra["args"] = str(args)
                    extra["kwargs"] = str({k: str(v)[:200] for k, v in kwargs.items()})
                
                logger.error(
                    f"[{f.__name__}] Unhandled exception: {type(e).__name__}: {e}",
                    exc_info=True,
                    extra={"extra_data": extra}
                )
                
                if reraise:
                    raise
                # Silent failure: increment counter and warn
                global _silent_failure_count
                with _silent_failure_lock:
                    _silent_failure_count += 1
                logger.warning(
                    f"[{f.__name__}] Swallowed exception (silent failure #{_silent_failure_count}). "
                    f"Caller received None."
                )
                return None
        return wrapper
    
    # Support both @log_exceptions and @log_exceptions(reraise=False)
    if func is not None and callable(func):
        return decorator(func)
    return decorator


# ---------------------------------------------------------------------------
# Convenience: audit logger for clinical audit trail
# ---------------------------------------------------------------------------
audit_logger = logging.getLogger("WINC-Audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False
audit_logger.addFilter(context_filter)

if not TEST_MODE:
    audit_log_path = os.path.join(LOG_DIR, "audit.log")
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8"
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(StructuredFormatter())
    audit_logger.addHandler(audit_handler)


# ---------------------------------------------------------------------------
# Helper: log a clinical audit event (writes to both app.log and audit.log)
# ---------------------------------------------------------------------------
def audit_event(event_type: str, message: str, **extra_kwargs):
    """
    Log a clinical audit event to both the main logger and the audit logger.
    
    Args:
        event_type: e.g. "INTAKE_CREATED", "OBSERVATION_SAVED", "STAGE_TRANSITION"
        message: Human-readable description
        **extra_kwargs: Additional context to include in the log entry
    """
    extra_data = {"audit_event": event_type, **extra_kwargs}
    trace_id = _trace_id.get()
    if trace_id:
        extra_data["trace_id"] = trace_id
    logger.info(f"AUDIT: [{event_type}] {message}", extra={"extra_data": extra_data})
    audit_logger.info(f"[{event_type}] {message}", extra={"extra_data": extra_data})


# ---------------------------------------------------------------------------
# Initialization message
# ---------------------------------------------------------------------------
logger.info("Logger initialized", extra={"extra_data": {
    "log_dir": LOG_DIR,
    "log_level": LOG_LEVEL,
    "test_mode": TEST_MODE,
}})

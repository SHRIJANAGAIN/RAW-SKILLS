# ============================================================
#                 SKT AI LABS PRIVATE LIMTED 
# ============================================================
# CHECK SKILL.MD FOR USING GUIDE OF FILESYSTEM
# ============================================================
# USED FOR MANAGE OF FILESYSTEM

from __future__ import annotations

import argparse
import difflib
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import uuid

from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple


VERSION = "SKT_TOOL"
SCHEMA_VERSION = "2.0"

DEFAULT_ENCODING = "utf-8"
DEFAULT_HASH = "sha256"

DEFAULT_MAX_READ_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_OUTPUT_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_RESULTS = 10_000
DEFAULT_MAX_DEPTH = 64
DEFAULT_MAX_ENTRIES = 50_000
DEFAULT_MAX_TOTAL_BYTES = 512 * 1024 * 1024


# ============================================================
# ERRORS
# ============================================================

class ToolError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        stage: str = "EXECUTION",
        retryable: bool = False,
        recoverable: bool = False,
        details: Optional[Dict[str, Any]] = None,
        exit_code: int = 1,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.stage = stage
        self.retryable = retryable
        self.recoverable = recoverable
        self.details = details or {}
        self.exit_code = exit_code


# ============================================================
# POLICY / CONTEXT
# ============================================================

@dataclass
class Policy:
    workspace_root: Optional[str] = None

    allow_outside_root: bool = False

    symlink_policy: str = "follow_within_root"
    hidden_policy: str = "exclude"

    allow_delete: bool = True
    allow_recursive_delete: bool = True

    max_read_bytes: int = DEFAULT_MAX_READ_BYTES
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES
    max_results: int = DEFAULT_MAX_RESULTS
    max_depth: int = DEFAULT_MAX_DEPTH
    max_entries: int = DEFAULT_MAX_ENTRIES
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES

    command_timeout: float = 30.0
    max_command_timeout: float = 300.0


@dataclass
class Context:
    operation_id: str
    started: float
    policy: Policy
    dry_run: bool = False
    attempt: int = 1


# ============================================================
# UTILITIES
# ============================================================

def op_id() -> str:
    return "op_" + uuid.uuid4().hex


def json_dump(obj: Any, pretty: bool = False) -> str:
    return json.dumps(
        obj,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        default=str,
    )


def success(
    ctx: Context,
    operation: str,
    result: Any,
    *,
    verified: bool = False,
    verification_level: int = 0,
    warnings: Optional[List[str]] = None,
    truncated: bool = False,
) -> Dict[str, Any]:

    return {
        "success": True,
        "tool": "filesystem",
        "operation": operation,
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "operation_id": ctx.operation_id,
        "stage": "COMPLETED",
        "execution": {
            "attempt": ctx.attempt,
            "duration_ms": int((time.time() - ctx.started) * 1000),
        },
        "verification": {
            "verified": verified,
            "level": verification_level,
        },
        "recovery": {
            "attempted": False,
            "performed": False,
        },
        "truncated": truncated,
        "warnings": warnings or [],
        "result": result,
    }


def failure(
    ctx: Context,
    operation: str,
    err: ToolError,
    *,
    recovery: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    return {
        "success": False,
        "tool": "filesystem",
        "operation": operation,
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "operation_id": ctx.operation_id,
        "stage": err.stage,
        "execution": {
            "attempt": ctx.attempt,
            "duration_ms": int((time.time() - ctx.started) * 1000),
        },
        "verification": {
            "verified": False,
            "level": 0,
        },
        "recovery": recovery or {
            "attempted": False,
            "performed": False,
        },
        "error": {
            "code": err.code,
            "message": err.message,
            "retryable": err.retryable,
            "recoverable": err.recoverable,
            "details": err.details,
        },
    }


def require_dict(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "request must be a JSON object",
            stage="SCHEMA",
        )
    return value


def require_string(
    args: Dict[str, Any],
    key: str,
    *,
    allow_empty: bool = False,
) -> str:

    value = args.get(key)

    if not isinstance(value, str):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be a string",
            stage="SCHEMA",
        )

    if not allow_empty and not value:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be a non-empty string",
            stage="SCHEMA",
        )

    return value


def optional_bool(
    args: Dict[str, Any],
    key: str,
    default: bool = False,
) -> bool:

    value = args.get(key, default)

    if not isinstance(value, bool):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be boolean",
            stage="SCHEMA",
        )

    return value


def optional_int(
    args: Dict[str, Any],
    key: str,
    default: Optional[int] = None,
    *,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> Optional[int]:

    value = args.get(key, default)

    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, int):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be integer",
            stage="SCHEMA",
        )

    if minimum is not None and value < minimum:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be >= {minimum}",
            stage="SCHEMA",
        )

    if maximum is not None and value > maximum:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be <= {maximum}",
            stage="SCHEMA",
        )

    return value


def optional_number(
    args: Dict[str, Any],
    key: str,
    default: Optional[float] = None,
    *,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
) -> Optional[float]:

    value = args.get(key, default)

    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be a number",
            stage="SCHEMA",
        )

    if minimum is not None and value < minimum:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be >= {minimum}",
            stage="SCHEMA",
        )

    if maximum is not None and value > maximum:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"{key} must be <= {maximum}",
            stage="SCHEMA",
        )

    return value


def check_unknown(
    args: Dict[str, Any],
    allowed: Sequence[str],
) -> None:

    unknown = set(args) - set(allowed)

    if unknown:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "unknown argument(s)",
            stage="SCHEMA",
            details={"unknown": sorted(unknown)},
        )


# ============================================================
# POLICY
# ============================================================

def policy_from_request(req: Dict[str, Any]) -> Policy:

    raw = req.get("policy", {})

    if raw is None:
        raw = {}

    if not isinstance(raw, dict):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "policy must be an object",
            stage="SCHEMA",
        )

    p = Policy()

    # Backwards-compatible top-level workspace_root.
    if "workspace_root" in req and "workspace_root" not in raw:
        raw = {
            **raw,
            "workspace_root": req["workspace_root"],
        }

    allowed = {
        "workspace_root",
        "allow_outside_root",
        "symlink_policy",
        "hidden_policy",
        "allow_delete",
        "allow_recursive_delete",
        "max_read_bytes",
        "max_output_bytes",
        "max_results",
        "max_depth",
        "max_entries",
        "max_total_bytes",
        "command_timeout",
        "max_command_timeout",
    }

    unknown = set(raw) - allowed

    if unknown:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "unknown policy field(s)",
            stage="SCHEMA",
            details={"unknown": sorted(unknown)},
        )

    for key, value in raw.items():
        setattr(p, key, value)

    if p.workspace_root is not None and not isinstance(
        p.workspace_root, str
    ):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "workspace_root must be string or null",
            stage="SCHEMA",
        )

    if p.symlink_policy not in {
        "deny",
        "follow",
        "follow_within_root",
        "explicit_only",
    }:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "invalid symlink_policy",
            stage="SCHEMA",
        )

    if p.hidden_policy not in {
        "include",
        "exclude",
        "explicit_only",
    }:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "invalid hidden_policy",
            stage="SCHEMA",
        )

    integer_limits = (
        "max_read_bytes",
        "max_output_bytes",
        "max_results",
        "max_depth",
        "max_entries",
        "max_total_bytes",
    )

    for name in integer_limits:
        value = getattr(p, name)

        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"invalid policy {name}",
                stage="SCHEMA",
            )

    if p.command_timeout <= 0:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "command_timeout must be > 0",
            stage="SCHEMA",
        )

    if p.max_command_timeout <= 0:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "max_command_timeout must be > 0",
            stage="SCHEMA",
        )

    if p.command_timeout > p.max_command_timeout:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "command_timeout cannot exceed max_command_timeout",
            stage="SCHEMA",
        )

    return p


# ============================================================
# PATH SAFETY
# ============================================================

def is_hidden_name(name: str) -> bool:
    return name.startswith(".") and name not in {".", ".."}


def is_within(path: str, root: str) -> bool:
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False


def resolve_path(
    raw: str,
    policy: Policy,
    *,
    must_exist: bool = False,
    for_create: bool = False,
) -> Tuple[str, Dict[str, Any]]:

    if "\x00" in raw:
        raise ToolError(
            "FS_INVALID_PATH",
            "path contains a null byte",
            stage="PRECONDITIONS",
        )

    requested = os.path.abspath(os.path.expanduser(raw))

    workspace_real = None

    if policy.workspace_root:
        workspace_real = os.path.realpath(
            os.path.abspath(os.path.expanduser(policy.workspace_root))
        )

    if os.path.exists(requested) or os.path.islink(requested):
        resolved = os.path.realpath(requested)
    else:
        parent = os.path.realpath(os.path.dirname(requested))
        resolved = os.path.join(parent, os.path.basename(requested))

    if workspace_real and not policy.allow_outside_root:
        if not is_within(resolved, workspace_real):
            raise ToolError(
                "FS_PATH_OUTSIDE_ROOT",
                "path resolves outside workspace root",
                stage="PRECONDITIONS",
                details={
                    "requested": requested,
                    "resolved": resolved,
                    "root": workspace_real,
                },
            )

    if os.path.islink(requested):

        if policy.symlink_policy in {
            "deny",
            "explicit_only",
        }:
            raise ToolError(
                "FS_SYMLINK_BLOCKED",
                "symlink is blocked by policy",
                stage="PRECONDITIONS",
            )

        if (
            policy.symlink_policy == "follow_within_root"
            and workspace_real
            and not is_within(
                os.path.realpath(requested),
                workspace_real,
            )
        ):
            raise ToolError(
                "FS_PATH_OUTSIDE_ROOT",
                "symlink target escapes workspace root",
                stage="PRECONDITIONS",
            )

    if must_exist and not (
        os.path.exists(requested) or os.path.islink(requested)
    ):
        raise ToolError(
            "FS_PATH_NOT_FOUND",
            "path does not exist",
            stage="PRECONDITIONS",
            details={"path": requested},
        )

    if for_create and not os.path.isdir(
        os.path.dirname(requested)
    ):
        raise ToolError(
            "FS_PATH_NOT_FOUND",
            "parent directory does not exist",
            stage="PRECONDITIONS",
            details={"parent": os.path.dirname(requested)},
        )

    return requested, {
        "resolved_path": resolved,
        "workspace_root": workspace_real,
    }


# ============================================================
# FILE UTILITIES
# ============================================================

def file_type(path: str) -> str:

    if os.path.islink(path):
        return "symlink"

    if os.path.isfile(path):
        return "file"

    if os.path.isdir(path):
        return "directory"

    if os.path.exists(path):
        return "other"

    return "missing"


def hash_file(
    path: str,
    algorithm: str = DEFAULT_HASH,
    chunk: int = 1024 * 1024,
) -> str:

    try:
        h = hashlib.new(algorithm)
    except ValueError:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"unsupported hash algorithm: {algorithm}",
            stage="SCHEMA",
        )

    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)

            if not data:
                break

            h.update(data)

    return h.hexdigest()


def detect_binary(
    path: str,
    sample: int = 8192,
) -> bool:

    try:
        with open(path, "rb") as f:
            return b"\x00" in f.read(sample)
    except OSError:
        return False


def read_text(
    path: str,
    encoding: str = DEFAULT_ENCODING,
    max_bytes: Optional[int] = None,
) -> str:

    try:
        size = os.path.getsize(path)

        if max_bytes is not None and size > max_bytes:
            raise ToolError(
                "FS_OUTPUT_LIMIT",
                "file exceeds read limit",
                stage="EXECUTION",
                details={
                    "size": size,
                    "limit": max_bytes,
                },
            )

        with open(
            path,
            "r",
            encoding=encoding,
            newline="",
        ) as f:
            return f.read()

    except UnicodeDecodeError as e:
        raise ToolError(
            "FS_ENCODING_ERROR",
            str(e),
            stage="EXECUTION",
        )

    except ToolError:
        raise

    except OSError as e:
        raise ToolError(
            "FS_READ_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
        )


def atomic_write(
    path: str,
    data: bytes,
    *,
    mode: Optional[int] = None,
) -> None:

    directory = os.path.dirname(path) or "."

    fd = None
    tmp = None

    try:
        fd, tmp = tempfile.mkstemp(
            prefix=".skt-filesystem-",
            dir=directory,
        )

        with os.fdopen(fd, "wb") as f:
            fd = None

            f.write(data)
            f.flush()
            os.fsync(f.fileno())

        if mode is not None:
            os.chmod(tmp, mode)

        os.replace(tmp, path)
        tmp = None

        try:
            dfd = os.open(directory, os.O_RDONLY)

            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)

        except OSError:
            pass

    except OSError as e:
        raise ToolError(
            "FS_WRITE_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
            recoverable=True,
        )

    finally:

        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass

        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def make_backup(path: str) -> Optional[str]:

    if not os.path.exists(path):
        return None

    directory = os.path.dirname(path) or "."

    fd, tmp = tempfile.mkstemp(
        prefix=".skt-backup-",
        dir=directory,
    )

    os.close(fd)

    try:
        shutil.copy2(path, tmp)
        return tmp

    except Exception:

        try:
            os.unlink(tmp)
        except OSError:
            pass

        raise


def restore_backup(
    path: str,
    backup: Optional[str],
) -> bool:

    if not backup or not os.path.exists(backup):
        return False

    try:
        os.replace(backup, path)
        return True
    except OSError:
        return False


# ============================================================
# DIRECTORY WALK
# ============================================================

def visible_entries(
    path: str,
    policy: Policy,
    include_hidden: Optional[bool] = None,
):

    include = (
        policy.hidden_policy == "include"
        if include_hidden is None
        else include_hidden
    )

    try:
        entries = os.scandir(path)
    except OSError as e:
        raise ToolError(
            "FS_READ_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
        )

    with entries:
        for entry in entries:

            if not include and is_hidden_name(entry.name):
                continue

            yield entry


def safe_walk(
    root: str,
    policy: Policy,
    *,
    max_depth: Optional[int] = None,
    max_entries: Optional[int] = None,
    include_hidden: Optional[bool] = None,
) -> Iterator[Tuple[str, os.DirEntry, int]]:

    max_depth = (
        policy.max_depth
        if max_depth is None
        else min(max_depth, policy.max_depth)
    )

    max_entries = (
        policy.max_entries
        if max_entries is None
        else min(max_entries, policy.max_entries)
    )

    count = 0
    seen_real_dirs = set()

    def walk(directory: str, depth: int):

        nonlocal count

        if depth > max_depth:
            return

        real_directory = os.path.realpath(directory)

        if real_directory in seen_real_dirs:
            raise ToolError(
                "FS_SYMLINK_LOOP",
                "directory traversal loop detected",
                stage="EXECUTION",
            )

        seen_real_dirs.add(real_directory)

        try:
            entries = list(
                visible_entries(
                    directory,
                    policy,
                    include_hidden,
                )
            )
        except ToolError:
            raise

        for entry in entries:

            count += 1

            if count > max_entries:
                raise ToolError(
                    "FS_LIMIT_REACHED",
                    "maximum entries reached",
                    stage="EXECUTION",
                    details={
                        "max_entries": max_entries,
                    },
                )

            yield directory, entry, depth

            try:
                is_dir = entry.is_dir(
                    follow_symlinks=False
                )
            except OSError:
                continue

            if not is_dir:
                continue

            if entry.is_symlink():

                if policy.symlink_policy in {
                    "deny",
                    "explicit_only",
                }:
                    continue

                target = os.path.realpath(entry.path)

                if (
                    policy.symlink_policy == "follow_within_root"
                    and policy.workspace_root
                    and not is_within(
                        target,
                        os.path.realpath(
                            policy.workspace_root
                        ),
                    )
                ):
                    continue

            yield from walk(
                entry.path,
                depth + 1,
            )

        seen_real_dirs.discard(real_directory)

    yield from walk(root, 0)


# ============================================================
# OUTPUT
# ============================================================

def output_limited(
    text: str,
    limit: int,
) -> Tuple[str, bool, int]:

    data = text.encode(
        DEFAULT_ENCODING,
        errors="replace",
    )

    if len(data) <= limit:
        return text, False, len(data)

    truncated = data[:limit].decode(
        DEFAULT_ENCODING,
        errors="ignore",
    )

    return truncated, True, len(data)


def line_slice(
    text: str,
    args: Dict[str, Any],
) -> Tuple[str, int, int]:

    lines = text.splitlines(keepends=True)

    start = optional_int(
        args,
        "start_line",
        None,
        minimum=1,
    )

    end = optional_int(
        args,
        "end_line",
        None,
        minimum=1,
    )

    offset = optional_int(
        args,
        "offset",
        None,
        minimum=0,
    )

    limit = optional_int(
        args,
        "limit",
        None,
        minimum=1,
    )

    if start is not None or end is not None:

        s = (start or 1) - 1
        e = end if end is not None else len(lines)

        selected = lines[s:e]

        actual_start = (
            s + 1
            if selected
            else min(s + 1, len(lines) + 1)
        )

        actual_end = (
            s + len(selected)
            if selected
            else actual_start
        )

    elif offset is not None or limit is not None:

        s = offset or 0
        e = (
            s + limit
            if limit is not None
            else len(lines)
        )

        selected = lines[s:e]

        actual_start = (
            s + 1
            if selected
            else min(s + 1, len(lines) + 1)
        )

        actual_end = (
            s + len(selected)
            if selected
            else actual_start
        )

    else:

        selected = lines
        actual_start = 1 if lines else 0
        actual_end = len(lines)

    if optional_bool(args, "line_numbers", False):

        output = "".join(
            f"{actual_start + i}\t{line}"
            for i, line in enumerate(selected)
        )

    else:
        output = "".join(selected)

    return output, actual_start, actual_end


# ============================================================
# EDITING
# ============================================================

def diff_text(
    old: str,
    new: str,
    path: str,
) -> str:

    return "".join(
        difflib.unified_diff(
            old.splitlines(True),
            new.splitlines(True),
            fromfile=path,
            tofile=path,
            lineterm="",
        )
    )


def write_content(
    path: str,
    content: str,
    encoding: str,
    overwrite: bool,
    backup: bool,
    dry_run: bool,
) -> Dict[str, Any]:

    exists = os.path.exists(path)

    if exists and not overwrite:
        raise ToolError(
            "FS_COLLISION",
            "target exists and overwrite=false",
            stage="PRECONDITIONS",
        )

    try:
        data = content.encode(encoding)
    except UnicodeEncodeError as e:
        raise ToolError(
            "FS_ENCODING_ERROR",
            str(e),
            stage="SCHEMA",
        )

    before = (
        hash_file(path)
        if os.path.isfile(path)
        else None
    )

    after_expected = hashlib.sha256(data).hexdigest()

    if dry_run:

        return {
            "path": path,
            "would_change": (
                before != after_expected
                if before is not None
                else True
            ),
            "bytes": len(data),
            "dry_run": True,
        }

    backup_path = (
        make_backup(path)
        if backup and os.path.isfile(path)
        else None
    )

    try:

        mode = (
            os.stat(path).st_mode & 0o7777
            if os.path.exists(path)
            else None
        )

        atomic_write(
            path,
            data,
            mode=mode,
        )

        after = hash_file(path)

        if after != after_expected:
            raise ToolError(
                "FS_VERIFICATION_FAILED",
                "written content hash mismatch",
                stage="VERIFICATION",
                recoverable=True,
            )

        if backup_path:

            try:
                os.unlink(backup_path)
            except OSError:
                pass

        return {
            "path": path,
            "bytes_written": len(data),
            "sha256": after,
            "backup_used": bool(backup_path),
        }

    except Exception:

        if backup_path:
            restore_backup(path, backup_path)

        raise


# ============================================================
# OPERATIONS
# ============================================================

def op_read(ctx: Context, args: Dict[str, Any]):

    check_unknown(
        args,
        [
            "path",
            "offset",
            "limit",
            "start_line",
            "end_line",
            "line_numbers",
            "encoding",
            "binary_ok",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isfile(path):
        raise ToolError(
            "FS_NOT_A_FILE",
            "target is not a regular file",
            stage="PRECONDITIONS",
        )

    binary_ok = optional_bool(
        args,
        "binary_ok",
        False,
    )

    if detect_binary(path) and not binary_ok:
        raise ToolError(
            "FS_BINARY_FILE",
            "file appears to be binary",
            stage="PRECONDITIONS",
        )

    encoding = args.get(
        "encoding",
        DEFAULT_ENCODING,
    )

    if not isinstance(encoding, str):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "encoding must be string",
            stage="SCHEMA",
        )

    text = read_text(
        path,
        encoding,
        ctx.policy.max_read_bytes,
    )

    selected, start, end = line_slice(
        text,
        args,
    )

    selected, truncated, total_bytes = output_limited(
        selected,
        ctx.policy.max_output_bytes,
    )

    return success(
        ctx,
        "read",
        {
            "path": path,
            "start_line": start,
            "end_line": end,
            "content": selected,
            "bytes_returned": len(
                selected.encode(
                    encoding,
                    errors="replace",
                )
            ),
            "bytes_total": total_bytes,
        },
        verified=True,
        verification_level=1,
        truncated=truncated,
    )


def op_write(ctx: Context, args: Dict[str, Any]):

    check_unknown(
        args,
        [
            "path",
            "content",
            "overwrite",
            "backup",
            "dry_run",
            "encoding",
            "create_parents",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        for_create=True,
    )

    content = args.get("content")

    if not isinstance(content, str):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "content must be string",
            stage="SCHEMA",
        )

    overwrite = optional_bool(
        args,
        "overwrite",
        True,
    )

    backup = optional_bool(
        args,
        "backup",
        True,
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    create_parents = optional_bool(
        args,
        "create_parents",
        False,
    )

    if create_parents and not dry:
        os.makedirs(
            os.path.dirname(path),
            exist_ok=True,
        )

    if not os.path.isdir(
        os.path.dirname(path)
    ):
        raise ToolError(
            "FS_PATH_NOT_FOUND",
            "parent directory does not exist",
            stage="PRECONDITIONS",
        )

    result = write_content(
        path,
        content,
        args.get("encoding", DEFAULT_ENCODING),
        overwrite,
        backup,
        dry,
    )

    return success(
        ctx,
        "write",
        result,
        verified=not dry,
        verification_level=2 if not dry else 0,
    )


def op_append(ctx: Context, args: Dict[str, Any]):

    check_unknown(
        args,
        [
            "path",
            "content",
            "encoding",
            "dry_run",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isfile(path):
        raise ToolError(
            "FS_NOT_A_FILE",
            "target is not a file",
            stage="PRECONDITIONS",
        )

    content = args.get("content")

    if not isinstance(content, str):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "content must be string",
            stage="SCHEMA",
        )

    encoding = args.get(
        "encoding",
        DEFAULT_ENCODING,
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    before = os.path.getsize(path)

    if dry:
        return success(
            ctx,
            "append",
            {
                "path": path,
                "before_bytes": before,
                "append_bytes": len(
                    content.encode(encoding)
                ),
                "dry_run": True,
            },
        )

    try:

        with open(
            path,
            "a",
            encoding=encoding,
            newline="",
        ) as f:

            f.write(content)
            f.flush()
            os.fsync(f.fileno())

    except Exception as e:
        raise ToolError(
            "FS_APPEND_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
        )

    after = os.path.getsize(path)

    if after < before:
        raise ToolError(
            "FS_VERIFICATION_FAILED",
            "file size decreased after append",
            stage="VERIFICATION",
        )

    return success(
        ctx,
        "append",
        {
            "path": path,
            "before_bytes": before,
            "after_bytes": after,
            "bytes_appended": after - before,
        },
        verified=True,
        verification_level=1,
    )


def perform_edit(
    ctx: Context,
    args: Dict[str, Any],
    mode: str,
):

    allowed = [
        "path",
        "old_text",
        "new_text",
        "expected_matches",
        "replace_all",
        "dry_run",
        "encoding",
        "pattern",
        "replacement",
        "flags",
        "backup",
    ]

    check_unknown(args, allowed)

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isfile(path):
        raise ToolError(
            "FS_NOT_A_FILE",
            "target is not a file",
            stage="PRECONDITIONS",
        )

    if detect_binary(path):
        raise ToolError(
            "FS_BINARY_FILE",
            "text editing on binary file is blocked",
            stage="PRECONDITIONS",
        )

    encoding = args.get(
        "encoding",
        DEFAULT_ENCODING,
    )

    text = read_text(
        path,
        encoding,
        ctx.policy.max_read_bytes,
    )

    expected = optional_int(
        args,
        "expected_matches",
        1,
        minimum=0,
    )

    replace_all = optional_bool(
        args,
        "replace_all",
        False,
    )

    if mode == "exact":

        old = args.get("old_text")
        new = args.get("new_text")

        if not isinstance(old, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "old_text is required",
                stage="SCHEMA",
            )

        if not isinstance(new, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "new_text is required",
                stage="SCHEMA",
            )

        count = text.count(old)

        if count == 0:
            raise ToolError(
                "FS_MATCH_NOT_FOUND",
                "old_text was not found",
                stage="PRECONDITIONS",
                details={
                    "found": 0,
                    "expected": expected,
                },
            )

        if replace_all:

            if (
                expected not in (None, 0)
                and count != expected
            ):
                raise ToolError(
                    "FS_AMBIGUOUS_MATCH",
                    "match count differs from expected_matches",
                    stage="PRECONDITIONS",
                    details={
                        "found": count,
                        "expected": expected,
                    },
                )

            new_text = text.replace(
                old,
                new,
            )

        else:

            if count != expected:
                raise ToolError(
                    "FS_AMBIGUOUS_MATCH",
                    "exact edit match count is not exactly expected",
                    stage="PRECONDITIONS",
                    details={
                        "found": count,
                        "expected": expected,
                    },
                )

            new_text = text.replace(
                old,
                new,
                1,
            )

        matches = count

    else:

        pattern = args.get("pattern")
        replacement = args.get(
            "replacement",
            "",
        )

        if not isinstance(pattern, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "pattern must be string",
                stage="SCHEMA",
            )

        if not isinstance(replacement, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "replacement must be string",
                stage="SCHEMA",
            )

        flags = 0

        for flag in args.get("flags", []) or []:

            if flag == "i":
                flags |= re.I
            elif flag == "m":
                flags |= re.M
            elif flag == "s":
                flags |= re.S
            else:
                raise ToolError(
                    "FS_INVALID_ARGUMENT",
                    f"unsupported regex flag: {flag}",
                    stage="SCHEMA",
                )

        try:
            rx = re.compile(
                pattern,
                flags,
            )
        except re.error as e:
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"invalid regex: {e}",
                stage="SCHEMA",
            )

        matches = len(
            list(rx.finditer(text))
        )

        if matches == 0:
            raise ToolError(
                "FS_MATCH_NOT_FOUND",
                "regex did not match",
                stage="PRECONDITIONS",
            )

        if (
            not replace_all
            and matches != expected
        ):
            raise ToolError(
                "FS_AMBIGUOUS_MATCH",
                "regex match count is not exactly expected",
                stage="PRECONDITIONS",
                details={
                    "found": matches,
                    "expected": expected,
                },
            )

        new_text = rx.sub(
            replacement,
            text,
            0 if replace_all else 1,
        )

    diff = diff_text(
        text,
        new_text,
        path,
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    if dry:
        return success(
            ctx,
            "edit" if mode == "exact" else "regex_edit",
            {
                "path": path,
                "mode": mode,
                "matches": matches,
                "changed": text != new_text,
                "diff": diff,
                "dry_run": True,
            },
        )

    backup = (
        make_backup(path)
        if optional_bool(args, "backup", True)
        else None
    )

    before = hashlib.sha256(
        text.encode(encoding)
    ).hexdigest()

    try:

        atomic_write(
            path,
            new_text.encode(encoding),
            mode=os.stat(path).st_mode & 0o7777,
        )

        verify = read_text(
            path,
            encoding,
            ctx.policy.max_read_bytes,
        )

        if verify != new_text:
            raise ToolError(
                "FS_VERIFICATION_FAILED",
                "edited content did not verify",
                stage="VERIFICATION",
                recoverable=True,
            )

        after = hashlib.sha256(
            verify.encode(encoding)
        ).hexdigest()

        if backup:
            try:
                os.unlink(backup)
            except OSError:
                pass

    except Exception as e:

        restored = restore_backup(
            path,
            backup,
        )

        if isinstance(e, ToolError):
            raise ToolError(
                e.code,
                e.message,
                stage=e.stage,
                retryable=e.retryable,
                recoverable=not restored,
                details=e.details,
            )

        raise

    return success(
        ctx,
        "edit" if mode == "exact" else "regex_edit",
        {
            "path": path,
            "mode": mode,
            "matches": matches,
            "changed": True,
            "diff": diff,
            "before_sha256": before,
            "after_sha256": after,
        },
        verified=True,
        verification_level=2,
    )


def op_edit(ctx, args):
    return perform_edit(
        ctx,
        args,
        "exact",
    )


def op_regex_edit(ctx, args):
    return perform_edit(
        ctx,
        args,
        "regex",
    )


# ============================================================
# PATCH
# ============================================================

def op_patch(ctx: Context, args: Dict[str, Any]):

    # FIXED CONTRACT:
    # patch expects edits[]
    check_unknown(
        args,
        [
            "path",
            "edits",
            "dry_run",
            "encoding",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isfile(path):
        raise ToolError(
            "FS_NOT_A_FILE",
            "target is not a file",
            stage="PRECONDITIONS",
        )

    edits = args.get("edits")

    if not isinstance(edits, list) or not edits:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "edits must be a non-empty list",
            stage="SCHEMA",
        )

    if len(edits) > 1000:
        raise ToolError(
            "FS_LIMIT_REACHED",
            "too many patch edits",
            stage="SCHEMA",
        )

    encoding = args.get(
        "encoding",
        DEFAULT_ENCODING,
    )

    text = read_text(
        path,
        encoding,
        ctx.policy.max_read_bytes,
    )

    new_text = text
    records = []

    for index, edit in enumerate(edits):

        if not isinstance(edit, dict):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"edit {index} must be object",
                stage="SCHEMA",
            )

        allowed = {
            "old_text",
            "new_text",
            "expected_matches",
            "replace_all",
        }

        unknown = set(edit) - allowed

        if unknown:
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"unknown patch field(s) in edit {index}",
                stage="SCHEMA",
                details={
                    "unknown": sorted(unknown),
                },
            )

        old = edit.get("old_text")
        replacement = edit.get("new_text")

        if not isinstance(old, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"edit {index} old_text must be string",
                stage="SCHEMA",
            )

        if not isinstance(replacement, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"edit {index} new_text must be string",
                stage="SCHEMA",
            )

        expected = edit.get(
            "expected_matches",
            1,
        )

        replace_all = edit.get(
            "replace_all",
            False,
        )

        if (
            isinstance(expected, bool)
            or not isinstance(expected, int)
            or expected < 0
        ):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"edit {index} expected_matches invalid",
                stage="SCHEMA",
            )

        if not isinstance(replace_all, bool):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"edit {index} replace_all must be boolean",
                stage="SCHEMA",
            )

        count = new_text.count(old)

        if count == 0:
            raise ToolError(
                "FS_MATCH_NOT_FOUND",
                f"patch edit {index} not found",
                stage="PRECONDITIONS",
                details={
                    "index": index,
                },
            )

        if replace_all:

            if expected not in (0, count):
                raise ToolError(
                    "FS_AMBIGUOUS_MATCH",
                    f"patch edit {index} count mismatch",
                    stage="PRECONDITIONS",
                    details={
                        "index": index,
                        "found": count,
                        "expected": expected,
                    },
                )

            new_text = new_text.replace(
                old,
                replacement,
            )

        else:

            if count != expected:
                raise ToolError(
                    "FS_AMBIGUOUS_MATCH",
                    f"patch edit {index} ambiguous",
                    stage="PRECONDITIONS",
                    details={
                        "index": index,
                        "found": count,
                        "expected": expected,
                    },
                )

            new_text = new_text.replace(
                old,
                replacement,
                1,
            )

        records.append(
            {
                "index": index,
                "matches": count,
            }
        )

    diff = diff_text(
        text,
        new_text,
        path,
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    if dry:
        return success(
            ctx,
            "patch",
            {
                "path": path,
                "edits": records,
                "diff": diff,
                "dry_run": True,
            },
        )

    backup = make_backup(path)

    before = hashlib.sha256(
        text.encode(encoding)
    ).hexdigest()

    try:

        atomic_write(
            path,
            new_text.encode(encoding),
            mode=os.stat(path).st_mode & 0o7777,
        )

        verify = read_text(
            path,
            encoding,
            ctx.policy.max_read_bytes,
        )

        if verify != new_text:
            raise ToolError(
                "FS_VERIFICATION_FAILED",
                "patch verification failed",
                stage="VERIFICATION",
                recoverable=True,
            )

        after = hashlib.sha256(
            verify.encode(encoding)
        ).hexdigest()

        try:
            os.unlink(backup)
        except OSError:
            pass

    except Exception as e:

        restored = restore_backup(
            path,
            backup,
        )

        if isinstance(e, ToolError):
            raise ToolError(
                e.code,
                e.message,
                stage=e.stage,
                retryable=e.retryable,
                recoverable=not restored,
                details=e.details,
            )

        raise

    return success(
        ctx,
        "patch",
        {
            "path": path,
            "edits": records,
            "diff": diff,
            "before_sha256": before,
            "after_sha256": after,
        },
        verified=True,
        verification_level=2,
    )


# ============================================================
# LIST / TREE / FIND / SEARCH
# ============================================================

def entry_info(
    entry: os.DirEntry,
) -> Dict[str, Any]:

    try:
        st = entry.stat(
            follow_symlinks=False
        )
    except OSError:
        st = None

    if entry.is_symlink():
        typ = "symlink"
    elif entry.is_dir(
        follow_symlinks=False
    ):
        typ = "directory"
    elif entry.is_file(
        follow_symlinks=False
    ):
        typ = "file"
    else:
        typ = "other"

    return {
        "name": entry.name,
        "path": entry.path,
        "type": typ,
        "size": st.st_size if st else None,
        "mtime": st.st_mtime if st else None,
        "mode": (
            oct(st.st_mode & 0o7777)
            if st
            else None
        ),
        "is_hidden": is_hidden_name(
            entry.name
        ),
        "is_symlink": entry.is_symlink(),
    }


def op_list(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "include_hidden",
            "sort",
            "max_results",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isdir(path):
        raise ToolError(
            "FS_NOT_A_DIRECTORY",
            "target is not a directory",
            stage="PRECONDITIONS",
        )

    include = optional_bool(
        args,
        "include_hidden",
        ctx.policy.hidden_policy == "include",
    )

    limit = optional_int(
        args,
        "max_results",
        ctx.policy.max_results,
        minimum=1,
        maximum=ctx.policy.max_results,
    )

    sort_key = args.get(
        "sort",
        "name",
    )

    if sort_key not in {
        "name",
        "size",
        "mtime",
        "type",
    }:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "sort must be name, size, mtime or type",
            stage="SCHEMA",
        )

    items = []

    try:

        with os.scandir(path) as entries:

            for entry in entries:

                if (
                    not include
                    and is_hidden_name(entry.name)
                ):
                    continue

                items.append(
                    entry_info(entry)
                )

    except OSError as e:
        raise ToolError(
            "FS_READ_FAILED",
            str(e),
            stage="EXECUTION",
        )

    items.sort(
        key=lambda item: (
            item.get(sort_key) is None,
            item.get(sort_key),
        )
    )

    truncated = len(items) > limit

    items = items[:limit]

    return success(
        ctx,
        "list",
        {
            "path": path,
            "entries": items,
            "count": len(items),
        },
        verified=True,
        verification_level=1,
        truncated=truncated,
    )


def op_tree(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "max_depth",
            "max_entries",
            "include_hidden",
        ],
    )

    root, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isdir(root):
        raise ToolError(
            "FS_NOT_A_DIRECTORY",
            "target is not directory",
            stage="PRECONDITIONS",
        )

    max_depth = optional_int(
        args,
        "max_depth",
        ctx.policy.max_depth,
        minimum=0,
        maximum=ctx.policy.max_depth,
    )

    max_entries = optional_int(
        args,
        "max_entries",
        ctx.policy.max_entries,
        minimum=1,
        maximum=ctx.policy.max_entries,
    )

    include = optional_bool(
        args,
        "include_hidden",
        ctx.policy.hidden_policy == "include",
    )

    output = []

    try:

        for directory, entry, depth in safe_walk(
            root,
            ctx.policy,
            max_depth=max_depth,
            max_entries=max_entries,
            include_hidden=include,
        ):

            info = entry_info(entry)
            info["depth"] = depth
            output.append(info)

    except ToolError as e:

        if e.code != "FS_LIMIT_REACHED":
            raise

    truncated = len(output) >= max_entries

    return success(
        ctx,
        "tree",
        {
            "root": root,
            "entries": output,
            "count": len(output),
        },
        verified=True,
        verification_level=1,
        truncated=truncated,
    )


def op_find(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "name",
            "glob",
            "extension",
            "type",
            "max_depth",
            "max_results",
            "include_hidden",
        ],
    )

    root, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    if not os.path.isdir(root):
        raise ToolError(
            "FS_NOT_A_DIRECTORY",
            "target is not directory",
            stage="PRECONDITIONS",
        )

    name = args.get("name")
    glob = args.get("glob")
    extension = args.get("extension")
    typ = args.get("type")

    if typ is not None and typ not in {
        "file",
        "directory",
        "symlink",
        "other",
    }:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "invalid type",
            stage="SCHEMA",
        )

    max_depth = optional_int(
        args,
        "max_depth",
        ctx.policy.max_depth,
        minimum=0,
        maximum=ctx.policy.max_depth,
    )

    limit = optional_int(
        args,
        "max_results",
        ctx.policy.max_results,
        minimum=1,
        maximum=ctx.policy.max_results,
    )

    include = optional_bool(
        args,
        "include_hidden",
        ctx.policy.hidden_policy == "include",
    )

    results = []

    try:

        iterator = safe_walk(
            root,
            ctx.policy,
            max_depth=max_depth,
            max_entries=ctx.policy.max_entries,
            include_hidden=include,
        )

        for _, entry, depth in iterator:

            typ_now = (
                "symlink"
                if entry.is_symlink()
                else "directory"
                if entry.is_dir(
                    follow_symlinks=False
                )
                else "file"
                if entry.is_file(
                    follow_symlinks=False
                )
                else "other"
            )

            if name is not None and entry.name != name:
                continue

            if (
                glob is not None
                and not fnmatch.fnmatch(
                    entry.name,
                    glob,
                )
            ):
                continue

            if (
                extension is not None
                and not entry.name.endswith(
                    extension
                )
            ):
                continue

            if typ is not None and typ_now != typ:
                continue

            results.append(
                {
                    "path": entry.path,
                    "name": entry.name,
                    "type": typ_now,
                    "depth": depth,
                }
            )

            if len(results) >= limit:
                break

    except ToolError as e:

        if e.code != "FS_LIMIT_REACHED":
            raise

    return success(
        ctx,
        "find",
        {
            "root": root,
            "results": results,
            "count": len(results),
        },
        verified=True,
        verification_level=1,
        truncated=len(results) >= limit,
    )


def op_search(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "query",
            "regex",
            "case_sensitive",
            "max_results",
            "max_depth",
            "include_hidden",
            "extensions",
            "context_lines",
            "file_glob",
        ],
    )

    root, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    query = args.get("query")

    if not isinstance(query, str) or not query:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "query must be non-empty",
            stage="SCHEMA",
        )

    use_regex = optional_bool(
        args,
        "regex",
        False,
    )

    case_sensitive = optional_bool(
        args,
        "case_sensitive",
        True,
    )

    max_results = optional_int(
        args,
        "max_results",
        ctx.policy.max_results,
        minimum=1,
        maximum=ctx.policy.max_results,
    )

    max_depth = optional_int(
        args,
        "max_depth",
        ctx.policy.max_depth,
        minimum=0,
        maximum=ctx.policy.max_depth,
    )

    context_lines = optional_int(
        args,
        "context_lines",
        0,
        minimum=0,
        maximum=20,
    )

    extensions = args.get("extensions")

    if extensions is not None:

        if (
            not isinstance(extensions, list)
            or not all(
                isinstance(x, str)
                for x in extensions
            )
        ):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "extensions must be list of strings",
                stage="SCHEMA",
            )

    file_glob = args.get("file_glob")

    if file_glob is not None and not isinstance(
        file_glob,
        str,
    ):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "file_glob must be string",
            stage="SCHEMA",
        )

    flags = 0 if case_sensitive else re.I

    rx = None

    if use_regex:

        try:
            rx = re.compile(
                query,
                flags,
            )
        except re.error as e:
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                f"invalid regex: {e}",
                stage="SCHEMA",
            )

    if os.path.isfile(root):

        files = [(root, 0)]

    else:

        files = []

        for _, entry, depth in safe_walk(
            root,
            ctx.policy,
            max_depth=max_depth,
            max_entries=ctx.policy.max_entries,
        ):

            if not entry.is_file(
                follow_symlinks=False
            ):
                continue

            if (
                not optional_bool(
                    args,
                    "include_hidden",
                    ctx.policy.hidden_policy == "include",
                )
                and is_hidden_name(entry.name)
            ):
                continue

            if (
                file_glob
                and not fnmatch.fnmatch(
                    entry.name,
                    file_glob,
                )
            ):
                continue

            if (
                extensions
                and not any(
                    entry.name.endswith(ext)
                    for ext in extensions
                )
            ):
                continue

            files.append(
                (entry.path, depth)
            )

    results = []

    for path, depth in files:

        if detect_binary(path):
            continue

        try:
            text = read_text(
                path,
                DEFAULT_ENCODING,
                ctx.policy.max_read_bytes,
            )
        except ToolError:
            continue

        lines = text.splitlines()

        for index, line in enumerate(lines):

            if rx:
                matched = bool(
                    rx.search(line)
                )
            elif case_sensitive:
                matched = query in line
            else:
                matched = (
                    query.lower()
                    in line.lower()
                )

            if not matched:
                continue

            item = {
                "path": path,
                "line": index + 1,
                "text": line,
                "depth": depth,
            }

            if context_lines:
                item["context_before"] = lines[
                    max(
                        0,
                        index - context_lines,
                    ):index
                ]

                item["context_after"] = lines[
                    index + 1:
                    min(
                        len(lines),
                        index + 1 + context_lines,
                    )
                ]

            results.append(item)

            if len(results) >= max_results:
                return success(
                    ctx,
                    "search",
                    {
                        "query": query,
                        "results": results,
                        "count": len(results),
                    },
                    verified=True,
                    verification_level=1,
                    truncated=True,
                )

    return success(
        ctx,
        "search",
        {
            "query": query,
            "results": results,
            "count": len(results),
        },
        verified=True,
        verification_level=1,
    )


# ============================================================
# METADATA
# ============================================================

def op_stat(ctx, args):

    check_unknown(
        args,
        ["path"],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    try:
        st = os.lstat(path)
    except OSError as e:
        raise ToolError(
            "FS_READ_FAILED",
            str(e),
            stage="EXECUTION",
        )

    return success(
        ctx,
        "stat",
        {
            "path": path,
            "resolved_path": os.path.realpath(path),
            "type": file_type(path),
            "size": st.st_size,
            "mode": oct(
                st.st_mode & 0o7777
            ),
            "uid": getattr(
                st,
                "st_uid",
                None,
            ),
            "gid": getattr(
                st,
                "st_gid",
                None,
            ),
            "created": getattr(
                st,
                "st_ctime",
                None,
            ),
            "modified": getattr(
                st,
                "st_mtime",
                None,
            ),
            "accessed": getattr(
                st,
                "st_atime",
                None,
            ),
            "is_symlink": os.path.islink(path),
            "symlink_target": (
                os.readlink(path)
                if os.path.islink(path)
                else None
            ),
            "readable": os.access(
                path,
                os.R_OK,
            ),
            "writable": os.access(
                path,
                os.W_OK,
            ),
            "executable": os.access(
                path,
                os.X_OK,
            ),
        },
        verified=True,
        verification_level=1,
    )


def op_exists(ctx, args):

    check_unknown(
        args,
        ["path"],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
    )

    return success(
        ctx,
        "exists",
        {
            "path": path,
            "exists": (
                os.path.exists(path)
                or os.path.islink(path)
            ),
            "type": file_type(path),
        },
        verified=True,
        verification_level=1,
    )


# ============================================================
# DIRECTORY CREATION
# ============================================================

def op_mkdir(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "parents",
            "exist_ok",
            "dry_run",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
    )

    parents = optional_bool(
        args,
        "parents",
        True,
    )

    exist_ok = optional_bool(
        args,
        "exist_ok",
        True,
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    if dry:
        return success(
            ctx,
            "mkdir",
            {
                "path": path,
                "would_change": not os.path.isdir(path),
                "dry_run": True,
            },
        )

    try:

        if parents:
            os.makedirs(
                path,
                exist_ok=exist_ok,
            )
        else:
            os.mkdir(path)

    except OSError as e:
        raise ToolError(
            "FS_WRITE_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
        )

    if not os.path.isdir(path):
        raise ToolError(
            "FS_VERIFICATION_FAILED",
            "directory creation did not verify",
            stage="VERIFICATION",
        )

    return success(
        ctx,
        "mkdir",
        {
            "path": path,
        },
        verified=True,
        verification_level=1,
    )


# ============================================================
# COPY / MOVE / DELETE
# ============================================================

def collision_target(
    dst: str,
    policy: str,
) -> bool:

    if policy not in {
        "fail",
        "skip",
        "replace",
        "merge",
    }:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "invalid collision policy",
            stage="SCHEMA",
        )

    exists = (
        os.path.exists(dst)
        or os.path.islink(dst)
    )

    if exists and policy == "fail":
        raise ToolError(
            "FS_COLLISION",
            "destination exists",
            stage="PRECONDITIONS",
        )

    return exists


def remove_existing(path: str):

    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.unlink(path)


def op_copy(ctx, args):

    check_unknown(
        args,
        [
            "src",
            "dst",
            "recursive",
            "collision",
            "dry_run",
            "preserve_metadata",
        ],
    )

    src, _ = resolve_path(
        require_string(args, "src"),
        ctx.policy,
        must_exist=True,
    )

    dst, _ = resolve_path(
        require_string(args, "dst"),
        ctx.policy,
    )

    recursive = optional_bool(
        args,
        "recursive",
        False,
    )

    collision = args.get(
        "collision",
        "fail",
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    preserve_metadata = optional_bool(
        args,
        "preserve_metadata",
        True,
    )

    exists = collision_target(
        dst,
        collision,
    )

    if (
        os.path.isdir(src)
        and not os.path.islink(src)
        and not recursive
    ):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "directory copy requires recursive=true",
            stage="SCHEMA",
        )

    if dry:
        return success(
            ctx,
            "copy",
            {
                "src": src,
                "dst": dst,
                "recursive": recursive,
                "would_change": True,
                "dry_run": True,
            },
        )

    if exists and collision == "skip":
        return success(
            ctx,
            "copy",
            {
                "src": src,
                "dst": dst,
                "skipped": True,
            },
            verified=True,
            verification_level=1,
        )

    try:

        if exists and collision == "replace":
            remove_existing(dst)

        if (
            os.path.isdir(src)
            and not os.path.islink(src)
        ):

            shutil.copytree(
                src,
                dst,
                copy_function=(
                    shutil.copy2
                    if preserve_metadata
                    else shutil.copyfile
                ),
            )

        else:

            if preserve_metadata:
                shutil.copy2(
                    src,
                    dst,
                    follow_symlinks=(
                        ctx.policy.symlink_policy
                        == "follow"
                    ),
                )
            else:
                shutil.copyfile(
                    src,
                    dst,
                )

    except OSError as e:
        raise ToolError(
            "FS_COPY_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
        )

    if not (
        os.path.exists(dst)
        or os.path.islink(dst)
    ):
        raise ToolError(
            "FS_VERIFICATION_FAILED",
            "copy destination missing",
            stage="VERIFICATION",
        )

    return success(
        ctx,
        "copy",
        {
            "src": src,
            "dst": dst,
        },
        verified=True,
        verification_level=1,
    )


def op_move(ctx, args):

    check_unknown(
        args,
        [
            "src",
            "dst",
            "collision",
            "dry_run",
        ],
    )

    src, _ = resolve_path(
        require_string(args, "src"),
        ctx.policy,
        must_exist=True,
    )

    dst, _ = resolve_path(
        require_string(args, "dst"),
        ctx.policy,
    )

    collision = args.get(
        "collision",
        "fail",
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    exists = collision_target(
        dst,
        collision,
    )

    if dry:
        return success(
            ctx,
            "move",
            {
                "src": src,
                "dst": dst,
                "would_change": True,
                "dry_run": True,
            },
        )

    if exists and collision == "skip":
        return success(
            ctx,
            "move",
            {
                "src": src,
                "dst": dst,
                "skipped": True,
            },
            verified=True,
            verification_level=1,
        )

    try:

        if exists and collision == "replace":
            remove_existing(dst)

        os.replace(
            src,
            dst,
        )

    except OSError as e:
        raise ToolError(
            "FS_MOVE_FAILED",
            str(e),
            stage="EXECUTION",
            retryable=True,
            recoverable=True,
        )

    if (
        os.path.exists(src)
        or os.path.islink(src)
        or not (
            os.path.exists(dst)
            or os.path.islink(dst)
        )
    ):
        raise ToolError(
            "FS_VERIFICATION_FAILED",
            "move verification failed",
            stage="VERIFICATION",
        )

    return success(
        ctx,
        "move",
        {
            "src": src,
            "dst": dst,
        },
        verified=True,
        verification_level=1,
    )


def op_delete(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "recursive",
            "dry_run",
            "confirm",
        ],
    )

    if not ctx.policy.allow_delete:
        raise ToolError(
            "FS_PERMISSION_DENIED",
            "delete is disabled by policy",
            stage="PERMISSIONS",
        )

    path, meta = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    recursive = optional_bool(
        args,
        "recursive",
        False,
    )

    dry = optional_bool(
        args,
        "dry_run",
        ctx.dry_run,
    )

    confirm = optional_bool(
        args,
        "confirm",
        False,
    )

    if (
        recursive
        and not ctx.policy.allow_recursive_delete
    ):
        raise ToolError(
            "FS_PERMISSION_DENIED",
            "recursive delete disabled by policy",
            stage="PERMISSIONS",
        )

    if (
        os.path.isdir(path)
        and not os.path.islink(path)
        and not recursive
    ):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "directory deletion requires recursive=true",
            stage="SCHEMA",
        )

    workspace = meta.get(
        "workspace_root"
    )

    if workspace and os.path.realpath(path) == workspace:
        raise ToolError(
            "FS_PERMISSION_DENIED",
            "workspace root cannot be deleted",
            stage="PERMISSIONS",
        )

    if recursive and not confirm and not dry:
        raise ToolError(
            "FS_PERMISSION_DENIED",
            "recursive delete requires confirm=true",
            stage="PERMISSIONS",
        )

    if dry:
        return success(
            ctx,
            "delete",
            {
                "path": path,
                "would_delete": True,
                "recursive": recursive,
                "dry_run": True,
            },
        )

    try:
        remove_existing(path)
    except OSError as e:
        raise ToolError(
            "FS_DELETE_FAILED",
            str(e),
            stage="EXECUTION",
        )

    if (
        os.path.exists(path)
        or os.path.islink(path)
    ):
        raise ToolError(
            "FS_VERIFICATION_FAILED",
            "target still exists after delete",
            stage="VERIFICATION",
        )

    return success(
        ctx,
        "delete",
        {
            "path": path,
            "deleted": True,
        },
        verified=True,
        verification_level=1,
    )


# ============================================================
# HASH / DIFF
# ============================================================

def op_hash(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "algorithm",
            "recursive",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    algorithm = args.get(
        "algorithm",
        DEFAULT_HASH,
    )

    recursive = optional_bool(
        args,
        "recursive",
        False,
    )

    if os.path.isfile(path):

        digest = hash_file(
            path,
            algorithm,
        )

        return success(
            ctx,
            "hash",
            {
                "path": path,
                "algorithm": algorithm,
                "digest": digest,
                "size": os.path.getsize(path),
            },
            verified=True,
            verification_level=1,
        )

    if not recursive:
        raise ToolError(
            "FS_NOT_A_FILE",
            "hash target is directory; use recursive=true",
            stage="SCHEMA",
        )

    entries = []

    for _, entry, _ in safe_walk(
        path,
        ctx.policy,
    ):

        if entry.is_file(
            follow_symlinks=False
        ):
            entries.append(
                (
                    os.path.relpath(
                        entry.path,
                        path,
                    ),
                    hash_file(
                        entry.path,
                        algorithm,
                    ),
                )
            )

    manifest = "\n".join(
        f"{digest}  {name}"
        for name, digest in sorted(entries)
    )

    digest = hashlib.new(
        algorithm,
        manifest.encode(),
    ).hexdigest()

    return success(
        ctx,
        "hash",
        {
            "path": path,
            "algorithm": algorithm,
            "digest": digest,
            "files": len(entries),
        },
        verified=True,
        verification_level=1,
    )


def op_diff(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "new_content",
            "other_path",
            "encoding",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    encoding = args.get(
        "encoding",
        DEFAULT_ENCODING,
    )

    old = read_text(
        path,
        encoding,
        ctx.policy.max_read_bytes,
    )

    if "new_content" in args:

        new = args["new_content"]

        if not isinstance(new, str):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "new_content must be string",
                stage="SCHEMA",
            )

    elif "other_path" in args:

        other, _ = resolve_path(
            require_string(
                args,
                "other_path",
            ),
            ctx.policy,
            must_exist=True,
        )

        new = read_text(
            other,
            encoding,
            ctx.policy.max_read_bytes,
        )

    else:

        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "new_content or other_path required",
            stage="SCHEMA",
        )

    diff = diff_text(
        old,
        new,
        path,
    )

    return success(
        ctx,
        "diff",
        {
            "path": path,
            "diff": diff,
            "changed": old != new,
        },
        verified=True,
        verification_level=1,
    )


# ============================================================
# WATCH
# ============================================================

def op_watch(ctx, args):

    check_unknown(
        args,
        [
            "path",
            "interval",
            "duration",
            "recursive",
            "max_events",
        ],
    )

    path, _ = resolve_path(
        require_string(args, "path"),
        ctx.policy,
        must_exist=True,
    )

    interval = optional_number(
        args,
        "interval",
        0.5,
        minimum=0.05,
        maximum=60,
    )

    duration = optional_number(
        args,
        "duration",
        5,
        minimum=0.05,
        maximum=ctx.policy.command_timeout,
    )

    max_events = optional_int(
        args,
        "max_events",
        100,
        minimum=1,
        maximum=ctx.policy.max_results,
    )

    recursive = optional_bool(
        args,
        "recursive",
        False,
    )

    def snapshot():

        snapshot_data = {}

        if os.path.isfile(path):

            st = os.stat(path)

            snapshot_data[path] = (
                st.st_mtime_ns,
                st.st_size,
            )

        elif os.path.isdir(path):

            if recursive:

                for _, entry, _ in safe_walk(
                    path,
                    ctx.policy,
                ):

                    try:
                        st = entry.stat(
                            follow_symlinks=False
                        )

                        snapshot_data[
                            entry.path
                        ] = (
                            st.st_mtime_ns,
                            st.st_size,
                        )

                    except OSError:
                        pass

            else:

                for entry in visible_entries(
                    path,
                    ctx.policy,
                ):

                    try:
                        st = entry.stat(
                            follow_symlinks=False
                        )

                        snapshot_data[
                            entry.path
                        ] = (
                            st.st_mtime_ns,
                            st.st_size,
                        )

                    except OSError:
                        pass

        return snapshot_data

    before = snapshot()

    events = []

    deadline = (
        time.time() + duration
    )

    while (
        time.time() < deadline
        and len(events) < max_events
    ):

        time.sleep(interval)

        after = snapshot()

        for changed_path in sorted(
            set(after) - set(before)
        ):
            events.append(
                {
                    "type": "create",
                    "path": changed_path,
                }
            )

        for changed_path in sorted(
            set(before) - set(after)
        ):
            events.append(
                {
                    "type": "delete",
                    "path": changed_path,
                }
            )

        for changed_path in sorted(
            set(before) & set(after)
        ):

            if (
                before[changed_path]
                != after[changed_path]
            ):
                events.append(
                    {
                        "type": "modify",
                        "path": changed_path,
                    }
                )

        before = after

    return success(
        ctx,
        "watch",
        {
            "path": path,
            "events": events,
            "duration": duration,
        },
        verified=True,
        verification_level=1,
        truncated=len(events) >= max_events,
    )


# ============================================================
# AI TOOL SCHEMA
# ============================================================

OPERATION_DESCRIPTIONS = {
    "read": "Read a text file with optional line and output limits.",
    "write": "Create or atomically replace a file.",
    "append": "Append text to a file.",
    "edit": "Perform an exact text replacement with match-count protection.",
    "regex_edit": "Perform a bounded regular-expression replacement.",
    "patch": "Apply multiple exact edits atomically with verification.",
    "list": "List directory entries.",
    "tree": "Recursively inspect a directory tree.",
    "search": "Search file contents recursively.",
    "find": "Find filesystem entries.",
    "stat": "Inspect filesystem metadata.",
    "exists": "Check whether a path exists.",
    "mkdir": "Create a directory.",
    "copy": "Copy a file or directory.",
    "move": "Move or rename a file or directory.",
    "delete": "Delete a file or directory.",
    "hash": "Calculate a cryptographic content hash.",
    "diff": "Generate a text diff without changing the target.",
    "watch": "Watch a path for bounded filesystem changes.",
    "batch": "Execute multiple filesystem operations.",
    "schema": "Return the complete machine-readable schema.",
    "help": "Return operation descriptions or an operation schema.",
    "describe": "Return the schema for one operation.",
}


COMMON = {
    "type": "object",
}


OPERATION_SCHEMAS = {

    "read": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "offset": {"type": "integer", "minimum": 0},
            "limit": {"type": "integer", "minimum": 1},
            "start_line": {"type": "integer", "minimum": 1},
            "end_line": {"type": "integer", "minimum": 1},
            "line_numbers": {"type": "boolean"},
            "encoding": {"type": "string"},
            "binary_ok": {"type": "boolean"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "write": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "overwrite": {"type": "boolean"},
            "backup": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
            "encoding": {"type": "string"},
            "create_parents": {"type": "boolean"},
        },
        "required": ["path", "content"],
        "additionalProperties": False,
    },

    "append": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "encoding": {"type": "string"},
            "dry_run": {"type": "boolean"},
        },
        "required": ["path", "content"],
        "additionalProperties": False,
    },

    "edit": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
            "expected_matches": {
                "type": "integer",
                "minimum": 0,
            },
            "replace_all": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
            "encoding": {"type": "string"},
            "backup": {"type": "boolean"},
        },
        "required": [
            "path",
            "old_text",
            "new_text",
        ],
        "additionalProperties": False,
    },

    "regex_edit": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "pattern": {"type": "string"},
            "replacement": {"type": "string"},
            "flags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "expected_matches": {
                "type": "integer",
                "minimum": 0,
            },
            "replace_all": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
            "encoding": {"type": "string"},
            "backup": {"type": "boolean"},
        },
        "required": [
            "path",
            "pattern",
            "replacement",
        ],
        "additionalProperties": False,
    },

    # FIXED PATCH SCHEMA
    "patch": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "edits": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1000,
                "items": {
                    "type": "object",
                    "properties": {
                        "old_text": {
                            "type": "string",
                        },
                        "new_text": {
                            "type": "string",
                        },
                        "expected_matches": {
                            "type": "integer",
                            "minimum": 0,
                        },
                        "replace_all": {
                            "type": "boolean",
                        },
                    },
                    "required": [
                        "old_text",
                        "new_text",
                    ],
                    "additionalProperties": False,
                },
            },
            "dry_run": {"type": "boolean"},
            "encoding": {"type": "string"},
        },
        "required": [
            "path",
            "edits",
        ],
        "additionalProperties": False,
    },

    "list": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "include_hidden": {"type": "boolean"},
            "sort": {
                "type": "string",
                "enum": [
                    "name",
                    "size",
                    "mtime",
                    "type",
                ],
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "tree": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "max_depth": {
                "type": "integer",
                "minimum": 0,
            },
            "max_entries": {
                "type": "integer",
                "minimum": 1,
            },
            "include_hidden": {
                "type": "boolean",
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "search": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "query": {"type": "string"},
            "regex": {"type": "boolean"},
            "case_sensitive": {"type": "boolean"},
            "max_results": {
                "type": "integer",
                "minimum": 1,
            },
            "max_depth": {
                "type": "integer",
                "minimum": 0,
            },
            "include_hidden": {
                "type": "boolean",
            },
            "extensions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "context_lines": {
                "type": "integer",
                "minimum": 0,
                "maximum": 20,
            },
            "file_glob": {
                "type": "string",
            },
        },
        "required": [
            "path",
            "query",
        ],
        "additionalProperties": False,
    },

    "find": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "name": {"type": "string"},
            "glob": {"type": "string"},
            "extension": {"type": "string"},
            "type": {
                "type": "string",
                "enum": [
                    "file",
                    "directory",
                    "symlink",
                    "other",
                ],
            },
            "max_depth": {
                "type": "integer",
                "minimum": 0,
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
            },
            "include_hidden": {
                "type": "boolean",
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "stat": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "exists": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "mkdir": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "parents": {"type": "boolean"},
            "exist_ok": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "copy": {
        "type": "object",
        "properties": {
            "src": {"type": "string"},
            "dst": {"type": "string"},
            "recursive": {"type": "boolean"},
            "collision": {
                "type": "string",
                "enum": [
                    "fail",
                    "skip",
                    "replace",
                    "merge",
                ],
            },
            "dry_run": {"type": "boolean"},
            "preserve_metadata": {
                "type": "boolean",
            },
        },
        "required": [
            "src",
            "dst",
        ],
        "additionalProperties": False,
    },

    "move": {
        "type": "object",
        "properties": {
            "src": {"type": "string"},
            "dst": {"type": "string"},
            "collision": {
                "type": "string",
                "enum": [
                    "fail",
                    "skip",
                    "replace",
                    "merge",
                ],
            },
            "dry_run": {"type": "boolean"},
        },
        "required": [
            "src",
            "dst",
        ],
        "additionalProperties": False,
    },

    "delete": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "recursive": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
            "confirm": {"type": "boolean"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "hash": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "algorithm": {
                "type": "string",
                "enum": [
                    "sha256",
                    "sha512",
                    "sha1",
                    "md5",
                ],
            },
            "recursive": {"type": "boolean"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "diff": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "new_content": {"type": "string"},
            "other_path": {"type": "string"},
            "encoding": {"type": "string"},
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "watch": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "interval": {
                "type": "number",
                "minimum": 0.05,
            },
            "duration": {
                "type": "number",
                "minimum": 0.05,
            },
            "recursive": {"type": "boolean"},
            "max_events": {
                "type": "integer",
                "minimum": 1,
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },

    "batch": {
        "type": "object",
        "properties": {
            "calls": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "items": {
                    "type": "object",
                },
            },
            "stop_on_error": {
                "type": "boolean",
            },
        },
        "required": ["calls"],
        "additionalProperties": False,
    },
}


# ============================================================
# TOOL DEFINITION
# ============================================================

def tool_definition():

    return {
        "name": "filesystem",
        "description": (
            "Production filesystem tool for AI agents. "
            "Supports safe reads, writes, edits, patches, "
            "search, copy, move, delete, hashing and inspection. "
            "Mutations are validated and verified."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": list(
                        OPERATION_DESCRIPTIONS
                    ),
                },
                "args": {
                    "type": "object",
                },
                "dry_run": {
                    "type": "boolean",
                },
                "policy": {
                    "type": "object",
                },
            },
            "required": [
                "operation",
            ],
            "additionalProperties": False,
        },
        "operations": {
            name: {
                "description": description,
                "input_schema": OPERATION_SCHEMAS.get(
                    name,
                    {},
                ),
            }
            for name, description
            in OPERATION_DESCRIPTIONS.items()
        },
    }


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_tool_call(
    raw: Any,
) -> Dict[str, Any]:

    if not isinstance(raw, dict):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "tool call must be JSON object",
            stage="SCHEMA",
        )

    # {"name":"filesystem","arguments":...}
    if "name" in raw:

        if raw["name"] != "filesystem":
            raise ToolError(
                "FS_WRONG_TOOL",
                "tool call is not for filesystem",
                stage="SCHEMA",
            )

        arguments = raw.get(
            "arguments",
            {},
        )

        if isinstance(arguments, str):

            try:
                arguments = json.loads(
                    arguments
                )
            except json.JSONDecodeError as e:
                raise ToolError(
                    "FS_INVALID_JSON",
                    str(e),
                    stage="SCHEMA",
                )

        if not isinstance(arguments, dict):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "arguments must be object",
                stage="SCHEMA",
            )

        raw = arguments

    # {"tool":"filesystem",...}
    if "tool" in raw:

        if raw["tool"] != "filesystem":
            raise ToolError(
                "FS_WRONG_TOOL",
                "request is not for filesystem",
                stage="SCHEMA",
            )

        raw = {
            key: value
            for key, value in raw.items()
            if key != "tool"
        }

    operation = raw.get("operation")

    if not isinstance(operation, str):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "operation is required",
            stage="SCHEMA",
        )

    if "args" in raw:

        if not isinstance(
            raw["args"],
            dict,
        ):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "args must be object",
                stage="SCHEMA",
            )

        return raw

    # Friendly flat form.
    args = {
        key: value
        for key, value in raw.items()
        if key not in {
            "operation",
            "dry_run",
            "policy",
            "workspace_root",
        }
    }

    normalized = {
        "operation": operation,
        "args": args,
    }

    for key in (
        "dry_run",
        "policy",
        "workspace_root",
    ):
        if key in raw:
            normalized[key] = raw[key]

    return normalized


# ============================================================
# HELP / SCHEMA
# ============================================================

def tool_schema_response():

    return {
        "success": True,
        "tool": "filesystem",
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "tool_definition": tool_definition(),
    }


def operation_help_response(
    operation: Optional[str] = None,
):

    if operation is None:

        return {
            "success": True,
            "tool": "filesystem",
            "version": VERSION,
            "schema_version": SCHEMA_VERSION,
            "operations": OPERATION_DESCRIPTIONS,
        }

    if operation not in OPERATION_DESCRIPTIONS:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"unknown operation: {operation}",
            stage="SCHEMA",
        )

    return {
        "success": True,
        "tool": "filesystem",
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "operation": operation,
        "description": OPERATION_DESCRIPTIONS[
            operation
        ],
        "input_schema": OPERATION_SCHEMAS.get(
            operation,
            {},
        ),
    }


# ============================================================
# DISPATCH
# ============================================================

def dispatch(
    req: Dict[str, Any],
    *,
    allow_batch: bool = True,
) -> Dict[str, Any]:

    req = require_dict(req)

    operation = req.get(
        "operation"
    )

    args = req.get(
        "args",
        {},
    )

    if not isinstance(operation, str) or not operation:
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "operation is required",
            stage="SCHEMA",
        )

    if not isinstance(args, dict):
        raise ToolError(
            "FS_INVALID_ARGUMENT",
            "args must be object",
            stage="SCHEMA",
        )

    policy = policy_from_request(req)

    dry = optional_bool(
        req,
        "dry_run",
        False,
    )

    ctx = Context(
        operation_id=op_id(),
        started=time.time(),
        policy=policy,
        dry_run=dry,
    )

    if operation == "schema":
        return tool_schema_response()

    if operation in {
        "help",
        "describe",
    }:

        requested = args.get(
            "operation"
        )

        return operation_help_response(
            requested
        )

    operations = {
        "read": op_read,
        "write": op_write,
        "append": op_append,
        "edit": op_edit,
        "regex_edit": op_regex_edit,
        "patch": op_patch,
        "list": op_list,
        "tree": op_tree,
        "search": op_search,
        "find": op_find,
        "stat": op_stat,
        "exists": op_exists,
        "mkdir": op_mkdir,
        "copy": op_copy,
        "move": op_move,
        "delete": op_delete,
        "hash": op_hash,
        "diff": op_diff,
        "watch": op_watch,
    }

    if operation == "batch":

        if not allow_batch:
            raise ToolError(
                "FS_BATCH_NESTING_BLOCKED",
                "nested batch operations are not allowed",
                stage="SCHEMA",
            )

        check_unknown(
            args,
            [
                "calls",
                "stop_on_error",
            ],
        )

        calls = args.get(
            "calls"
        )

        if (
            not isinstance(calls, list)
            or not calls
        ):
            raise ToolError(
                "FS_INVALID_ARGUMENT",
                "batch requires non-empty calls list",
                stage="SCHEMA",
            )

        if len(calls) > 100:
            raise ToolError(
                "FS_LIMIT_REACHED",
                "batch call limit exceeded",
                stage="SCHEMA",
            )

        stop_on_error = optional_bool(
            args,
            "stop_on_error",
            True,
        )

        results = []

        for index, call in enumerate(calls):

            try:

                normalized = normalize_tool_call(
                    call
                )

                # Explicitly block nested batch.
                if normalized.get(
                    "operation"
                ) == "batch":
                    raise ToolError(
                        "FS_BATCH_NESTING_BLOCKED",
                        "nested batch operations are not allowed",
                        stage="SCHEMA",
                    )

                child_request = {
                    **normalized,
                    "policy": req.get(
                        "policy",
                        {},
                    ),
                }

                if "workspace_root" in req:
                    child_request[
                        "workspace_root"
                    ] = req[
                        "workspace_root"
                    ]

                child_result = dispatch(
                    child_request,
                    allow_batch=False,
                )

                results.append(
                    {
                        "index": index,
                        "result": child_result,
                    }
                )

                if (
                    stop_on_error
                    and not child_result.get(
                        "success",
                        False,
                    )
                ):
                    break

            except Exception as e:

                result = {
                    "success": False,
                    "tool": "filesystem",
                    "operation": "batch_item",
                    "version": VERSION,
                    "schema_version": SCHEMA_VERSION,
                    "error": {
                        "code": getattr(
                            e,
                            "code",
                            "FS_INTERNAL_ERROR",
                        ),
                        "message": str(e),
                    },
                }

                results.append(
                    {
                        "index": index,
                        "result": result,
                    }
                )

                if stop_on_error:
                    break

        return success(
            ctx,
            "batch",
            {
                "results": results,
                "completed": len(results),
                "requested": len(calls),
            },
            verified=all(
                item["result"].get(
                    "success",
                    False,
                )
                for item in results
            ),
            verification_level=1,
        )

    if operation not in operations:

        raise ToolError(
            "FS_INVALID_ARGUMENT",
            f"unknown operation: {operation}",
            stage="SCHEMA",
            details={
                "available": sorted(
                    list(operations)
                    + [
                        "schema",
                        "help",
                        "describe",
                        "batch",
                    ]
                )
            },
        )

    return operations[operation](
        ctx,
        args,
    )


# ============================================================
# REQUEST RUNNER
# ============================================================

def run_request(
    req: Dict[str, Any],
) -> Dict[str, Any]:

    started = time.time()

    operation = (
        req.get(
            "operation",
            "unknown",
        )
        if isinstance(req, dict)
        else "unknown"
    )

    operation_id = op_id()

    try:

        result = dispatch(req)

        # Keep outer operation ID stable.
        if isinstance(result, dict):
            result.setdefault(
                "operation_id",
                operation_id,
            )

        return result

    except ToolError as e:

        try:
            policy = policy_from_request(
                req
                if isinstance(req, dict)
                else {}
            )
        except Exception:
            policy = Policy()

        ctx = Context(
            operation_id=operation_id,
            started=started,
            policy=policy,
        )

        return failure(
            ctx,
            operation,
            e,
        )

    except KeyboardInterrupt:

        ctx = Context(
            operation_id=operation_id,
            started=started,
            policy=Policy(),
        )

        return failure(
            ctx,
            operation,
            ToolError(
                "FS_CANCELLED",
                "operation cancelled",
                stage="EXECUTION",
                retryable=True,
            ),
        )

    except Exception as e:

        ctx = Context(
            operation_id=operation_id,
            started=started,
            policy=Policy(),
        )

        return failure(
            ctx,
            operation,
            ToolError(
                "FS_INTERNAL_ERROR",
                str(e),
                stage="EXECUTION",
                details={
                    "type": type(e).__name__,
                },
            ),
        )


# ============================================================
# CLI
# ============================================================

def main(
    argv: Optional[Sequence[str]] = None,
) -> int:

    parser = argparse.ArgumentParser(
        description=(
            "SKT AI LABS production filesystem tool"
        )
    )

    parser.add_argument(
        "request",
        nargs="?",
        help="JSON request",
    )

    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read one JSON request per line from stdin",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
    )

    parser.add_argument(
        "--schema",
        action="store_true",
        help="Print machine-readable schema",
    )

    parser.add_argument(
        "--describe",
        metavar="OPERATION",
        help="Print schema for an operation",
    )

    ns = parser.parse_args(argv)

    if ns.schema:

        print(
            json_dump(
                tool_schema_response(),
                ns.pretty,
            )
        )

        return 0

    if ns.describe:

        try:

            print(
                json_dump(
                    operation_help_response(
                        ns.describe
                    ),
                    ns.pretty,
                )
            )

            return 0

        except ToolError as e:

            print(
                json_dump(
                    {
                        "success": False,
                        "error": {
                            "code": e.code,
                            "message": e.message,
                        },
                    }
                )
            )

            return 1

    if ns.stdin:

        rc = 0

        for line in sys.stdin:

            if not line.strip():
                continue

            try:
                req = json.loads(line)

            except json.JSONDecodeError as e:

                out = {
                    "success": False,
                    "tool": "filesystem",
                    "operation": "unknown",
                    "version": VERSION,
                    "error": {
                        "code": "FS_INVALID_JSON",
                        "message": str(e),
                    },
                }

                print(
                    json_dump(
                        out,
                        ns.pretty,
                    )
                )

                rc = max(rc, 2)
                continue

            out = run_request(req)

            print(
                json_dump(
                    out,
                    ns.pretty,
                )
            )

            if not out.get(
                "success",
                False,
            ):
                rc = max(
                    rc,
                    1,
                )

        return rc

    if ns.request is None:
        parser.error(
            "provide request JSON or --stdin"
        )

    try:
        req = json.loads(
            ns.request
        )

    except json.JSONDecodeError as e:

        print(
            json_dump(
                {
                    "success": False,
                    "tool": "filesystem",
                    "operation": "unknown",
                    "version": VERSION,
                    "error": {
                        "code": "FS_INVALID_JSON",
                        "message": str(e),
                    },
                }
            )
        )

        return 2

    out = run_request(req)

    print(
        json_dump(
            out,
            ns.pretty,
        )
    )

    return (
        0
        if out.get(
            "success",
            False,
        )
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
---
name: filesystem-tool
version: 1.0.0
description: Production-grade SKT filesystem tool for safe file and directory operations via JSON requests. Use for reading, writing, editing, searching, hashing, patching, and batch filesystem work with policy enforcement and verification.
author: SKT AI LABS
---

# SKT TOOL (script.py) FILESYSTEM GUIDE

This document explains how to use the **SKT Filesystem Tool** – a production‑grade, AI‑friendly utility for safe file and directory operations. The tool is designed to be called via JSON requests and returns structured JSON responses, making it ideal for agentic workflows.

---

## 1. Purpose & Context

> **Why this tool?**  
> Many AI agents need to read, write, edit, and explore the filesystem. Shell commands are powerful but unsafe and hard to validate. This tool provides a controlled, auditable, and verifiable interface for all common filesystem operations, with built‑in limits, policy enforcement, and verification.

Use this tool whenever you need to:
- Inspect files and directories (including **metadata** like permissions, size, timestamps, ownership).
- Create, modify, or delete files.
- Search content or find files by pattern.
- Get cryptographic hashes to verify content.
- Prepare patches or batch operations.
- Preview changes before applying them (dry‑run).

---

## 2. General Request Format

All requests are JSON objects with the following structure:

```json
{
  "operation": "<operation>",
  "args": { ... },
  "dry_run": true|false,          // optional, global override
  "policy": { ... },              // optional, see Policy section
  "workspace_root": "/path"       // optional, shorthand for policy.workspace_root
}
```

| Field         | Type   | Description |
|---------------|--------|-------------|
| `operation`   | string | One of: `read`, `write`, `append`, `edit`, `regex_edit`, `patch`, `list`, `tree`, `search`, `find`, `stat`, `exists`, `mkdir`, `copy`, `move`, `delete`, `hash`, `diff`, `watch`, `batch`, `schema`, `help`, `describe`. |
| `args`        | object | Operation‑specific arguments (see schemas). |
| `dry_run`     | bool   | Preview a mutation without changing anything. |
| `policy`      | object | Security and limits (see below). |
| `workspace_root` | string | Root directory; all paths must stay inside it unless `allow_outside_root` is true. |

### Policy (optional, with defaults)

```json
{
  "workspace_root": null,
  "allow_outside_root": false,
  "symlink_policy": "follow_within_root",
  "hidden_policy": "exclude",
  "allow_delete": true,
  "allow_recursive_delete": true,
  "max_read_bytes": 8388608,
  "max_output_bytes": 2097152,
  "max_results": 10000,
  "max_depth": 64,
  "max_entries": 50000,
  "max_total_bytes": 536870912,
  "command_timeout": 30.0,
  "max_command_timeout": 300.0
}
```

**Important**: If `workspace_root` is set, all paths must resolve inside it (unless `allow_outside_root: true`). Symlinks are followed only if they stay within the root by default.

---

## 3. Basic Invocation

Run the script with a JSON request as a command‑line argument:

```bash
./script.py '{"operation":"read", "args":{"path":"file.txt"}}'
```

Or read from stdin (one JSON per line):

```bash
echo '{"operation":"read", "args":{"path":"file.txt"}}' | ./script.py --stdin
```

For pretty output, add `--pretty`.

---

## 4. Worked Examples (with Step‑by‑Step Reasoning)

### Example 1 – Reading a configuration file and editing a value

**Goal**:  
We have `config.json` with `"timeout": 30`. We need to change it to `60`.

**Step‑by‑step reasoning (what the agent does):**

1. **Check existence** → use `exists` to confirm the file is present.
2. **Read the file** → use `read` to get current content and locate the line.
3. **Dry‑run the edit** → use `edit` with `dry_run: true` to see what would change.
4. **Apply the edit** → use `edit` with appropriate `expected_matches` to avoid surprises.

**Request #1 – exists**

```json
{
  "operation": "exists",
  "args": { "path": "config.json" }
}
```

**Response #1** (success)

```json
{
  "success": true,
  "operation": "exists",
  "result": {
    "path": "/project/config.json",
    "exists": true,
    "type": "file"
  }
}
```

**Request #2 – read (with line numbers)**

```json
{
  "operation": "read",
  "args": {
    "path": "config.json",
    "line_numbers": true
  }
}
```

**Response #2** (excerpt)

```json
{
  "success": true,
  "operation": "read",
  "result": {
    "path": "/project/config.json",
    "start_line": 1,
    "end_line": 10,
    "content": "1\t{\n2\t  \"timeout\": 30,\n3\t  \"retries\": 3\n4\t}\n",
    "bytes_returned": 45,
    "bytes_total": 45
  }
}
```

We see `"timeout": 30` on line 2. Now we want to replace `"timeout": 30` with `"timeout": 60`.  
We know there is exactly one occurrence, so `expected_matches: 1`.

**Request #3 – dry‑run edit**

```json
{
  "operation": "edit",
  "args": {
    "path": "config.json",
    "old_text": "\"timeout\": 30",
    "new_text": "\"timeout\": 60",
    "expected_matches": 1,
    "dry_run": true
  }
}
```

**Response #3**

```json
{
  "success": true,
  "operation": "edit",
  "result": {
    "path": "/project/config.json",
    "mode": "exact",
    "matches": 1,
    "changed": true,
    "diff": "--- config.json\n+++ config.json\n@@ -1,4 +1,4 @@\n {\n-  \"timeout\": 30,\n+  \"timeout\": 60,\n   \"retries\": 3\n }",
    "dry_run": true
  }
}
```

The diff shows exactly what would change. Since it looks correct, we apply it **without** `dry_run`.

**Request #4 – apply edit**

```json
{
  "operation": "edit",
  "args": {
    "path": "config.json",
    "old_text": "\"timeout\": 30",
    "new_text": "\"timeout\": 60",
    "expected_matches": 1
  }
}
```

**Response #4**

```json
{
  "success": true,
  "operation": "edit",
  "result": {
    "path": "/project/config.json",
    "mode": "exact",
    "matches": 1,
    "changed": true,
    "diff": "...",
    "before_sha256": "a1b2c3...",
    "after_sha256": "d4e5f6..."
  }
}
```

The edit succeeded and the file was atomically replaced with verification.

---

### Example 2 – Batch patch (multiple edits atomically)

**Goal**:  
In `app.py`, replace two occurrences: `"DEBUG=False"` → `"DEBUG=True"` and `"PORT=5000"` → `"PORT=8080"`. We want both changes to happen together or not at all.

We use the `patch` operation with an `edits` array.

**Request**

```json
{
  "operation": "patch",
  "args": {
    "path": "app.py",
    "edits": [
      {
        "old_text": "DEBUG=False",
        "new_text": "DEBUG=True",
        "expected_matches": 1,
        "replace_all": false
      },
      {
        "old_text": "PORT=5000",
        "new_text": "PORT=8080",
        "expected_matches": 1,
        "replace_all": false
      }
    ]
  }
}
```

**Response (success)**

```json
{
  "success": true,
  "operation": "patch",
  "result": {
    "path": "/project/app.py",
    "edits": [
      { "index": 0, "matches": 1 },
      { "index": 1, "matches": 1 }
    ],
    "diff": "...",
    "before_sha256": "...",
    "after_sha256": "..."
  }
}
```

All edits are applied atomically – if any edit fails (e.g., one pattern not found), the entire patch is rolled back.

---

### Example 3 – Searching files recursively with context

**Goal**:  
Find all Python files (`*.py`) that contain the word `TODO` (case‑insensitive), show 2 lines of context.

**Request**

```json
{
  "operation": "search",
  "args": {
    "path": "src/",
    "query": "TODO",
    "case_sensitive": false,
    "file_glob": "*.py",
    "context_lines": 2,
    "max_results": 10
  }
}
```

**Response (excerpt)**

```json
{
  "success": true,
  "operation": "search",
  "result": {
    "query": "TODO",
    "results": [
      {
        "path": "src/main.py",
        "line": 42,
        "text": "    # TODO: implement error handling",
        "depth": 1,
        "context_before": ["    result = do_something()", "    if result is None:"],
        "context_after": ["    return result", ""]
      }
    ],
    "count": 1
  }
}
```

---

### Example 4 – Inspecting metadata before editing

**Goal**:  
Check if `important.log` is writable before attempting to append to it.

**Request**:
```json
{
  "operation": "stat",
  "args": { "path": "important.log" }
}
```

**Response**:
```json
{
  "success": true,
  "operation": "stat",
  "result": {
    "path": "/project/important.log",
    "size": 5120,
    "mode": "0600",
    "writable": true,
    "modified": 1700001000.0
  }
}
```

If `writable` is `false`, you know you need to change permissions or abort.

---

## 5. Negative Examples (Common Mistakes)

### ❌ Mistake 1 – Editing without `expected_matches` when multiple matches exist

Suppose `README.md` contains the word "version" three times. You want to replace the **first** occurrence with "release".

**Wrong request (no `expected_matches`)**

```json
{
  "operation": "edit",
  "args": {
    "path": "README.md",
    "old_text": "version",
    "new_text": "release"
  }
}
```

**Why it fails**  
By default, `expected_matches` is `1`. The tool finds **3** matches and throws `FS_AMBIGUOUS_MATCH` because the count differs. You **must** either set `expected_matches` to the exact number if you want a single replacement, or use `replace_all: true` if you want to replace all occurrences.

**Correct** (replace all occurrences):
```json
{
  "operation": "edit",
  "args": {
    "path": "README.md",
    "old_text": "version",
    "new_text": "release",
    "replace_all": true,
    "expected_matches": 3
  }
}
```

Or if you only want the first occurrence, make `old_text` more specific to avoid ambiguity.

---

### ❌ Mistake 2 – Deleting a directory without `recursive` and `confirm`

**Wrong**

```json
{
  "operation": "delete",
  "args": { "path": "old_backup/" }
}
```

This fails because deletion of a directory requires `recursive: true` **and** `confirm: true` (unless `dry_run`).

**Correct** (for non‑empty directory):

```json
{
  "operation": "delete",
  "args": {
    "path": "old_backup/",
    "recursive": true,
    "confirm": true
  }
}
```

---

### ❌ Mistake 3 – Writing a file outside `workspace_root`

If the policy has `workspace_root: "/home/user/project"` and you try:

```json
{
  "operation": "write",
  "args": {
    "path": "/tmp/outside.txt",
    "content": "hello"
  }
}
```

You get `FS_PATH_OUTSIDE_ROOT`. You must either set `allow_outside_root: true` in the policy or keep the path inside the root.

---

## 6. Clear Decision Rules

| Situation | Do this |
|-----------|---------|
| You need to **inspect metadata** (size, permissions, timestamps) | Use `stat`. |
| You need to **check if a path exists** without raising errors | Use `exists`. |
| You need a **content hash** for verification or change detection | Use `hash` (single file) or `hash` with `recursive: true` for directories. |
| You need to **replace a fixed string** exactly once | Use `edit` with `expected_matches: 1` (or the exact number you expect). |
| You need to **replace all occurrences** of a fixed string | Use `edit` with `replace_all: true` (and set `expected_matches` to the expected total count for safety). |
| You need to replace based on a **pattern** | Use `regex_edit`; test your regex with a dry‑run first. |
| You have **multiple independent replacements** that must be atomic | Use `patch` with an array of edits. |
| You want to **preview** changes | Set `dry_run: true` in the request. |
| You are **deleting a directory** | Always set `recursive: true` and `confirm: true` (unless `dry_run`). |
| You need to **copy a directory** | Set `recursive: true` and choose `collision` policy (`fail`/`skip`/`replace`/`merge`). |
| You are **reading a large file** | Use `offset`/`limit` or `start_line`/`end_line` to avoid hitting `max_output_bytes`. |
| You need to **find files** by name/extension | Use `find` with `glob` or `extension`. |
| You need to **search inside files** | Use `search` with `query`; enable `regex: true` for patterns. |
| You need to execute **many operations** in one go | Use `batch` – but remember nested batch is not allowed. |
| You are **unsure about the file’s text encoding** | Specify `encoding`; if binary, set `binary_ok: true` for `read`. |
| You need to **compare two files or a file with new content** | Use `diff`. |

---

## 7. Edge Cases and Tricky Situations

### 7.1 Binary files
- `read` will refuse to read a file that appears binary unless `binary_ok: true`.
- `edit`, `regex_edit`, `patch`, `search` block binary files by default (they skip binary files during search).
- Use `hash` or `stat` to inspect binary files safely.

### 7.2 Symlinks
- By default (`symlink_policy: "follow_within_root"`), symlinks are followed only if their target stays inside the workspace root.
- If you set `symlink_policy: "deny"`, any operation on a symlink fails.
- `list` and `tree` show symlinks with type `"symlink"` and their target path in `stat`.

### 7.3 Hidden files (dot‑files)
- By default (`hidden_policy: "exclude"`), hidden files (starting with `.`) are ignored in `list`, `tree`, `find`, and `search`.
- To include them, set `include_hidden: true` in the operation args or change the policy to `"include"`.

### 7.4 Large outputs
- `read` truncates content if it exceeds `max_output_bytes` (2 MB by default). The `truncated` flag in the response tells you if truncation occurred.
- Use `offset`/`limit` or `start_line`/`end_line` to read only the part you need.

### 7.5 File does not exist
- Operations that require `must_exist` (like `read`, `edit`, `stat`) will throw `FS_PATH_NOT_FOUND`.
- Use `exists` first to check if a path exists without raising an error.

### 7.6 Concurrent modifications
- The tool uses atomic writes (temporary file + rename) to ensure that writes are all‑or‑nothing and crash‑safe.
- However, it does not perform file locking. If another process writes concurrently, you might get a conflict. Use `backup: true` to retain the previous version.

### 7.7 Batch operations – stopping on error
- In a `batch` call, you can set `stop_on_error: true` (default) to stop processing further calls if one fails.
- If you want to continue despite errors, set `stop_on_error: false`.

### 7.8 Dry‑run and verification
- When `dry_run` is `true`, no actual changes are made, but the tool still performs all checks (existence, matches, etc.) and returns a diff or preview.
- After a real mutation, the tool verifies the change (e.g., hash comparison) and sets `verified: true` and `verification_level` (1 or 2). If verification fails, the operation is rolled back if a backup exists.

### 7.9 Metadata edge cases
- `stat` on a symlink returns metadata about the symlink itself, not its target (use `resolved_path` to get the target's real path).
- For large directories, `stat` may be slow – use `list` with limited results instead.
- `hash` on a directory with `recursive: true` will compute a tree‑hash of all files (sorted by path) – useful for detecting changes in a whole tree.

---

## 8. Output Format and Structure

All responses are JSON objects with these top‑level fields:

| Field            | Type    | Description |
|------------------|---------|-------------|
| `success`        | boolean | `true` if the operation completed without errors. |
| `tool`           | string  | Always `"filesystem"`. |
| `operation`      | string  | The requested operation name. |
| `version`        | string  | Tool version. |
| `schema_version` | string  | API schema version. |
| `operation_id`   | string  | Unique ID for this operation (for tracing). |
| `stage`          | string  | `"COMPLETED"` on success, or an error stage (e.g., `"PRECONDITIONS"`). |
| `execution`      | object  | `attempt` and `duration_ms`. |
| `verification`   | object  | `verified` and `level` (0–2). |
| `recovery`       | object  | `attempted` and `performed` (if a backup was used). |
| `truncated`      | boolean | Whether the result was truncated (e.g., output limit). |
| `warnings`       | array   | Any non‑fatal warnings. |
| `result`         | object  | Operation‑specific result data (present on success). |
| `error`          | object  | Present on failure with `code`, `message`, `retryable`, `recoverable`, and `details`. |

**Example error response**:

```json
{
  "success": false,
  "operation": "edit",
  "error": {
    "code": "FS_MATCH_NOT_FOUND",
    "message": "old_text was not found",
    "retryable": false,
    "recoverable": false,
    "details": { "found": 0, "expected": 1 }
  }
}
```

**Example success with metadata** (for `stat`):

```json
{
  "success": true,
  "operation": "stat",
  "operation_id": "op_a1b2c3d4",
  "execution": { "attempt": 1, "duration_ms": 12 },
  "verification": { "verified": true, "level": 1 },
  "result": {
    "path": "/project/config.json",
    "size": 1024,
    "mode": "0644",
    "uid": 1000,
    "gid": 1000,
    "modified": 1700000100.0,
    "writable": true
  }
}
```

---

## 9. Step‑by‑Step Process for an AI Agent

When you need to perform a complex operation, follow this structured approach:

1. **Define the goal** – What do you want to achieve (e.g., “change the timeout value”).
2. **Check prerequisites** – Use `exists` or `stat` to ensure the target exists and has the right permissions.
3. **Inspect current state** – Use `read` (with line numbers or offsets) to examine the content, or `stat` for metadata.
4. **Formulate the change** – Decide which operation (`edit`, `regex_edit`, `patch`) and precise text/pattern.
5. **Test with dry‑run** – Apply the operation with `dry_run: true` and inspect the diff.
6. **Verify the diff** – Confirm it matches your expectation.
7. **Apply the change** – Run the same request without `dry_run`.
8. **Validate the result** – Optionally re‑read the file or use `hash` to confirm the change.

---

## 10. Complete Example: Multi‑step Workflow with Metadata

**Scenario**: In a project, we need to rename all imports from `old_lib` to `new_lib` in all Python files under `src/`, but only for files that actually contain `old_lib`. Before editing, check that each file is writable.

**Workflow**:

1. **Search** for files containing `old_lib`:
   ```json
   {
     "operation": "search",
     "args": {
       "path": "src/",
       "query": "old_lib",
       "file_glob": "*.py",
       "max_results": 50
     }
   }
   ```
   Extract the list of file paths from the response.

2. For each path, run `stat` to check `writable`:
   ```json
   { "operation": "stat", "args": { "path": "src/module.py" } }
   ```
   If `writable: false`, skip or abort.

3. For each writable file, **dry‑run** a `regex_edit` to replace `old_lib` with `new_lib`:
   ```json
   {
     "operation": "regex_edit",
     "args": {
       "path": "src/module.py",
       "pattern": "old_lib",
       "replacement": "new_lib",
       "expected_matches": 3,   // from the search count in that file
       "replace_all": true,
       "dry_run": true
     }
   }
   ```
   Check the diff.

4. If all look good, apply them – either individually or **batch** them:
   ```json
   {
     "operation": "batch",
     "args": {
       "calls": [
         {
           "operation": "regex_edit",
           "args": { "path": "src/module.py", "pattern": "old_lib", "replacement": "new_lib", "replace_all": true, "expected_matches": 3 }
         },
         { ... } // more files
       ],
       "stop_on_error": true
     }
   }
   ```

5. Finally, run a `search` again to confirm no `old_lib` remains.

---

## 11. Quick Reference – Operation Schemas

For a full machine‑readable schema, run:

```bash
./script.py --schema --pretty
```

Or get help for a specific operation:

```bash
./script.py --describe read --pretty
```

---

## 12. Conclusion

This tool gives you a safe, predictable, and verifiable way to interact with the filesystem. By following the examples and rules above, you will avoid common pitfalls and produce robust agentic workflows.

**Remember**:  
- Always **dry‑run** before mutating.  
- Always **verify** your changes.  
- Use **batch** for atomic multi‑edits.  
- Respect the **policy** – it’s there to protect your system.
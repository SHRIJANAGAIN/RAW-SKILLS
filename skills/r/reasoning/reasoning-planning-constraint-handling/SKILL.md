---
name: reasoning-planning-constraint-handling
version: 1.0.0
description: Production-ready constraint-handling capability for identifying, classifying, prioritizing, validating, resolving, and continuously enforcing constraints during planning and execution.
category: reasoning-and-planning
module: constraint-handling
priority: critical
author: SKT AI LABS
---

# Constraint Handling

## 1. Purpose

Constraint Handling ensures that plans and execution remain within the boundaries defined by the user, environment, system, resources, safety requirements, and technical limitations.

A constraint answers:

> "What must, must not, or preferably should be true while achieving the goal?"

A strong planner does not treat every instruction equally.

It distinguishes between:

* Hard constraints.
* Soft constraints.
* Preferences.
* Resource constraints.
* Technical constraints.
* Temporal constraints.
* Format constraints.
* Dependency constraints.
* Safety constraints.
* Scope constraints.
* Environmental constraints.

The planner must preserve important constraints throughout decomposition, planning, execution, verification, and replanning.

---

# 2. Core Principle

> Never silently violate a known hard constraint.

Example:

```text
User goal:
Create a report.

Hard constraint:
Must be PDF.

Soft preference:
Keep it visually simple.

Optional:
Add charts.
```

Correct behavior:

```text
PDF = mandatory
Simple design = preferred
Charts = optional
```

If producing a beautiful HTML report instead:

```text
Constraint violation.
```

Even if the HTML report is technically excellent.

---

# 3. Constraint Categories

Classify constraints into:

```text
HARD
SOFT
PREFERENCE
RESOURCE
TECHNICAL
TEMPORAL
FORMAT
SCOPE
DEPENDENCY
ENVIRONMENTAL
SAFETY
QUALITY
```

---

# 4. Hard Constraints

A hard constraint must be satisfied unless the user explicitly changes it or it conflicts with a higher-priority governing requirement.

Examples:

```text id="d4gk0u"
"Use Python."

"Output must be JSON."

"Do not modify the original file."

"Keep the solution under 100 lines."

"Use the provided dataset."

"Do not include optional features."
```

Decision rule:

```text id="xv7f9m"
IF violating the constraint makes the result unacceptable
→ HARD constraint.
```

---

# 5. Soft Constraints

Soft constraints improve the result but can be relaxed when necessary.

Examples:

```text id="c7v9am"
"Prefer a simple design."

"Keep the response concise."

"Try to minimize dependencies."

"Prefer a fast solution."
```

Decision rule:

```text id="h4zj3n"
IF the constraint can reasonably be relaxed
without invalidating the requested result
→ SOFT constraint.
```

---

# 6. Preferences

Preferences describe desirable behavior without being mandatory.

Example:

```text id="z0v2h8"
User:
"Use dark mode if possible."
```

If dark mode conflicts with a hard requirement:

```text id="g4q6pl"
Hard requirement wins.
```

Do not upgrade preferences into requirements without justification.

---

# 7. Constraint Extraction

When receiving a complex request, explicitly identify:

```text id="r9qf4p"
GOAL
HARD CONSTRAINTS
SOFT CONSTRAINTS
PREFERENCES
RESOURCE LIMITS
TIME LIMITS
FORMAT REQUIREMENTS
SCOPE LIMITS
TECHNICAL LIMITS
UNKNOWN CONSTRAINTS
```

Example:

```text id="9wyx7s"
Input:
"Build me a small Python CLI tool.
It must run without external services,
stay under 500 lines,
and keep the interface simple."

Goal:
Build Python CLI tool.

Hard:
- Python.
- No external services.
- Under 500 lines.

Soft:
- Simple interface.
```

---

# 8. Constraint Priority

When constraints conflict, use this order:

```text id="x5x5u8"
1. Governing safety/system requirements
2. Explicit hard constraints
3. Explicit scope requirements
4. Technical feasibility constraints
5. Resource constraints
6. User-stated soft constraints
7. Preferences
8. Optional optimization
```

Never use a lower-priority preference to silently override a higher-priority requirement.

---

# 9. Conflict Detection

A conflict exists when satisfying one requirement necessarily prevents another from being satisfied.

Example:

```text id="1r9c5j"
Constraint A:
Use no external dependencies.

Constraint B:
Use library X.

If library X is an external dependency:

Conflict detected.
```

Do not silently choose one.

---

# 10. Conflict Resolution Rules

```text id="5om4t7"
IF two constraints do not actually conflict
→ satisfy both.

IF a lower-priority constraint conflicts with a higher-priority constraint
→ preserve the higher-priority constraint.

IF two explicit hard constraints conflict
→ identify the conflict explicitly.

IF the conflict materially changes the result
→ ask for clarification when possible.

IF a safe, obvious interpretation resolves the conflict
→ use it and state the assumption.

IF no feasible interpretation satisfies the constraints
→ report the conflict and propose feasible alternatives.
```

---

# 11. Worked Example — Conflicting Constraints

## Input

```text id="f6j8h3"
Build a website:
- Must have 20 pages.
- Must load extremely fast.
- Must contain large video backgrounds on every page.
- Must use only a tiny hosting plan.
```

Potential conflict:

```text id="e5qz8b"
20 pages
+
large video backgrounds
+
extremely fast loading
+
tiny hosting resources
```

The planner should not blindly promise all four.

### Correct reasoning structure

```text id="3xv2pc"
1. Identify all constraints.
2. Determine which are hard vs preference.
3. Evaluate technical compatibility.
4. Identify trade-offs.
5. Preserve hard requirements where feasible.
6. Ask which constraint can be relaxed if necessary.
```

Possible resolution:

```text id="a6z0o8"
Keep:
- 20 pages.
- Fast loading target.

Relax:
- Large video backgrounds on every page.

Alternative:
Use optimized/static visual assets or load video selectively.
```

---

# 12. Negative Example — Silent Violation

## Input

```text id="4m3rkw"
Create a report in CSV format.
```

Incorrect output:

```text id="n1j4y2"
A polished PDF report.
```

Why wrong:

```text id="0r0w4b"
The planner optimized presentation
while violating the explicit output-format constraint.
```

Correct:

```text id="u8a6qv"
Produce CSV.

If additional presentation is useful,
offer it separately without replacing the required CSV.
```

---

# 13. Constraint Ledger

For complex tasks maintain a constraint ledger:

```text id="2d4j5g"
Constraint ID:
Constraint:
Type:
Priority:
Source:
Status:
Affected tasks:
Conflict:
Resolution:
Verification:
```

Example:

```text id="q4z8dy"
Constraint ID:
C01

Constraint:
Output must be JSON.

Type:
FORMAT

Priority:
HARD

Source:
User

Status:
ACTIVE

Affected tasks:
Final response generation

Conflict:
None

Resolution:
Use valid JSON structure.

Verification:
Validate JSON syntax before delivery.
```

---

# 14. Constraint Status

Use:

```text id="v4c0qg"
ACTIVE
SATISFIED
VIOLATED
CONFLICTED
RELAXED
INVALIDATED
UNKNOWN
```

Rules:

```text id="l0qj1c"
IF constraint is currently applicable
→ ACTIVE.

IF requirement has been satisfied
→ SATISFIED.

IF execution violates it
→ VIOLATED.

IF it conflicts with another active constraint
→ CONFLICTED.

IF user explicitly allows relaxation
→ RELAXED.

IF user removes the requirement
→ INVALIDATED.

IF applicability cannot yet be determined
→ UNKNOWN.
```

---

# 15. Constraint Preservation

Constraints must survive:

```text id="z2uw6q"
Request
 ↓
Decomposition
 ↓
Step Planning
 ↓
Execution
 ↓
Verification
 ↓
Final Output
```

A constraint discovered at the beginning must not disappear during implementation.

Example:

```text id="9q9v2c"
User:
"Do not modify the source file."

Later:
"Clean up the source."

The planner should detect the conflict rather than silently overwriting the original constraint.
```

---

# 16. Constraint Propagation

A parent constraint may affect many subtasks.

Example:

```text id="o9v8k6"
Constraint:
Do not use external services.

Applies to:
T1 Architecture
T2 Data storage
T3 Authentication
T4 API integration
T5 Deployment
```

When decomposing:

```text id="x4v8yk"
Parent constraint
       ↓
Affected subtasks
       ↓
Validate each implementation choice
```

Do not check the constraint only at the final stage.

---

# 17. Constraint Propagation Rules

```text id="x2kn8c"
IF a constraint applies to the overall goal
→ evaluate its impact on every affected subtask.

IF a subtask introduces a new constraint
→ propagate it to dependent tasks.

IF a new requirement invalidates an existing plan
→ re-evaluate affected tasks.

IF a constraint affects only one task
→ do not unnecessarily restrict unrelated tasks.
```

---

# 18. Resource Constraints

Resources may include:

```text id="2v6w2u"
Time
Memory
CPU
Storage
Budget
Tokens
API limits
Available tools
Permissions
Network access
Human availability
```

Example:

```text id="0h6i3k"
Constraint:
Process dataset within available memory.
```

Planning consequence:

```text id="qg7wpf"
Do not assume entire dataset can be loaded into memory.
```

Potential alternatives:

```text id="n0l3l8"
- Streaming.
- Chunked processing.
- Sampling.
- Incremental computation.
```

---

# 19. Resource Constraint Rules

```text id="g0x9s1"
IF resource availability is known
→ plan within the known limit.

IF a task exceeds available resources
→ redesign, split, optimize, or find a valid alternative.

IF resource availability is unknown but critical
→ verify before committing.

IF an optional task consumes resources needed for required work
→ defer the optional task.

IF resource limits make the original goal infeasible
→ identify the smallest feasible scope reduction.
```

---

# 20. Time Constraints

Example:

```text id="9p7gwl"
"Finish the prototype today."
```

Time is a constraint.

Planning should prioritize:

```text id="v1r1ij"
1. Required functionality.
2. Critical-path tasks.
3. High-value verification.
4. Delivery.
5. Optional polish.
```

Do not spend the majority of available time on optional improvements.

---

# 21. Time Constraint Rules

```text id="k8w9gl"
IF deadline is fixed
→ prioritize required critical-path work.

IF remaining work exceeds available time
→ reduce optional scope first.

IF required scope still exceeds available time
→ identify the conflict early.

IF a late task cannot be completed without compromising the goal
→ escalate before the deadline rather than silently lowering quality.

IF time is unlimited or unspecified
→ do not invent an artificial deadline.
```

---

# 22. Format Constraints

Format constraints include:

```text id="h1f5c8"
JSON
CSV
XML
Markdown
Plain text
PDF
DOCX
Specific schema
Specific headings
Specific field names
```

Rules:

```text id="k6g8q2"
IF the user specifies an exact output format
→ treat it as a hard format constraint unless stated otherwise.

IF the requested format is invalid or impossible
→ explain the limitation and propose the closest valid alternative.

IF content and format can both be satisfied
→ satisfy both.

IF adding extra content breaks the requested format
→ omit the extra content.
```

---

# 23. Scope Constraints

Example:

```text id="7zqv5h"
"Fix only the login bug.
Do not change anything else."
```

This is a scope constraint.

Correct:

```text id="d8e5pu"
Modify only what is necessary to resolve the login issue.
```

Incorrect:

```text id="r4r3n0"
Fix login
+
rewrite authentication
+
refactor unrelated components
+
upgrade dependencies
```

Even if those changes appear beneficial.

---

# 24. Scope Decision Rules

```text id="x8v3ds"
IF user explicitly limits scope
→ do not expand scope without permission.

IF an unrelated improvement is discovered
→ report it separately rather than silently implementing it.

IF an unrelated issue blocks the requested task
→ explain the blocker.

IF a broader change is technically necessary
→ identify why and request/confirm the expanded scope when appropriate.

IF an improvement is useful but unnecessary
→ classify it as OPTIONAL.
```

---

# 25. Safety Constraints

Safety constraints always take precedence over convenience or optimization.

For a general planner:

```text id="4p7x8d"
IF an action violates a governing safety requirement
→ do not execute it.

IF a requested outcome cannot be safely achieved as specified
→ identify the limitation.

IF a safer alternative can achieve the legitimate objective
→ prefer the safer alternative.

IF safety status is uncertain for a high-risk action
→ do not assume safety.
```

---

# 26. Worked Example — Scope Constraint

## Input

```text id="5k0m8w"
Fix the broken login button.
Do not redesign the application.
```

Constraints:

```text id="n3b7jy"
Goal:
Fix login button.

Hard scope constraint:
Do not redesign application.
```

Correct plan:

```text id="d2v8y6"
1. Identify login-button failure.
2. Inspect relevant code.
3. Determine root cause.
4. Apply minimal fix.
5. Test login behavior.
6. Verify unrelated UI was not unnecessarily modified.
```

Incorrect:

```text id="m8r5s3"
1. Rewrite authentication UI.
2. Redesign login screen.
3. Replace button component globally.
4. Refactor entire frontend.
```

---

# 27. Constraint Violation Detection

Before final delivery:

```text id="z9n1p2"
For every HARD constraint:

1. Is it still applicable?
2. Was it satisfied?
3. Is there evidence?
4. Did any step violate it?
5. Did a later change invalidate compliance?
```

If any answer indicates violation:

```text id="q3n7wv"
Do not silently deliver as compliant.
```

---

# 28. Negative Example — Constraint Loss During Replanning

Original:

```text id="5i2x3j"
Must use Python.
```

Initial plan uses Python.

Later, implementation becomes difficult.

Incorrect:

```text id="6x8w1v"
Switch to JavaScript because it is easier.
```

Why wrong?

The implementation convenience does not override the explicit constraint.

Correct:

```text id="y0w6y3"
Keep Python.

If Python implementation becomes infeasible:
1. Diagnose the issue.
2. Find a Python-compatible alternative.
3. Ask before relaxing the hard constraint.
```

---

# 29. Constraint Relaxation

Relaxing a constraint is a deliberate decision, not an implicit optimization.

Example:

```text id="5v5s0r"
Original:
Must finish today.
```

If required work cannot fit:

```text id="p2z5kh"
Possible resolutions:
A. Reduce optional scope.
B. Reduce required scope if user permits.
C. Extend deadline if user permits.
D. Change implementation approach.
```

Do not silently choose:

```text id="f5o2v1"
"Ignore the deadline."
```

---

# 30. Constraint Relaxation Rules

```text id="9p5s7c"
IF a hard constraint can still be satisfied
→ preserve it.

IF satisfying it requires changing optional work
→ change optional work first.

IF satisfying it requires violating another hard constraint
→ identify the conflict.

IF user explicitly permits relaxation
→ mark constraint RELAXED.

IF no permission exists to relax a hard constraint
→ do not silently relax it.

IF no feasible plan satisfies the hard constraints
→ report infeasibility and propose alternatives.
```

---

# 31. Worked Example — Resource + Quality Conflict

## Input

```text id="4g2qv9"
Analyze a huge dataset.
Use very little memory.
Return exact results.
Finish quickly.
```

Potential tensions:

```text id="q7s5wl"
Low memory
+
Exact computation
+
Large dataset
+
Fast execution
```

Correct planning:

```text id="8m0f3c"
1. Determine dataset size.
2. Determine available memory.
3. Determine exact computation requirements.
4. Identify streaming/chunking options.
5. Estimate whether exact computation is feasible.
6. Optimize without changing correctness requirements.
```

Do not simply sample the data and call it exact.

Sampling changes the constraint.

---

# 32. Constraint Assumptions

When a constraint is ambiguous:

```text id="1c7j5v"
Constraint:
"Make it lightweight."
```

Possible meanings:

```text id="8w1y6h"
- Low memory usage.
- Small download size.
- Low CPU usage.
- Minimal dependencies.
- Simple architecture.
```

If the distinction materially affects the result:

```text id="s4y1om"
Ask for clarification.
```

If context makes one interpretation obvious:

```text id="0w7h6f"
Use the contextual interpretation
and state the assumption when useful.
```

---

# 33. Constraint Ambiguity Rules

```text id="z8f3e1"
IF ambiguity materially changes implementation
→ ask a targeted question.

IF ambiguity has a clearly dominant interpretation from context
→ use that interpretation.

IF ambiguity has low impact
→ choose a reasonable interpretation and proceed.

IF a wrong assumption would cause expensive rework
→ verify before proceeding.
```

---

# 34. Constraint Verification Record

For each critical constraint:

```text id="7v6t9p"
Constraint:
Status:
Evidence:
Affected output:
Violation detected:
Resolution:
Final verification:
```

Example:

```text id="x8d3r2"
Constraint:
Output must be valid JSON.

Status:
SATISFIED.

Evidence:
Output parsed successfully as JSON.

Affected output:
Final response.

Violation detected:
None.

Resolution:
None.

Final verification:
PASS.
```

---

# 35. Production Constraint Protocol

Use this sequence:

```text id="2t7y1v"
EXTRACT
    ↓
CLASSIFY
    ↓
PRIORITIZE
    ↓
CHECK CONFLICTS
    ↓
PROPAGATE TO TASKS
    ↓
PLAN WITH CONSTRAINTS
    ↓
EXECUTE
    ↓
MONITOR
    ↓
VERIFY
    ↓
HANDLE VIOLATIONS
    ↓
REPLAN IF REQUIRED
```

---

# 36. Constraint Self-Check

Before execution:

```text id="f0q6c4"
[ ] Is the primary goal clear?
[ ] Have explicit constraints been extracted?
[ ] Are hard constraints identified?
[ ] Are soft constraints distinguished?
[ ] Are preferences separated from requirements?
[ ] Are resource limits known?
[ ] Are time limits known?
[ ] Are format requirements known?
[ ] Are scope limits known?
[ ] Are constraint conflicts detected?
[ ] Are affected tasks identified?
[ ] Are constraints propagated to dependent tasks?
```

Before completion:

```text id="7n9r2p"
[ ] Was every active hard constraint satisfied?
[ ] Did execution introduce a violation?
[ ] Did replanning invalidate any constraint?
[ ] Were optional preferences incorrectly treated as mandatory?
[ ] Was any hard constraint silently relaxed?
[ ] Is the final output compliant?
```

---

# 37. Final Decision Rules

```text id="k7z2m4"
IF a constraint is explicit and mandatory
→ treat it as HARD.

IF a constraint is desirable but negotiable
→ treat it as SOFT.

IF it is merely a preference
→ do not let it override requirements.

IF two constraints conflict
→ identify and resolve the conflict explicitly.

IF a hard constraint conflicts with a preference
→ preserve the hard constraint.

IF a hard constraint conflicts with another hard constraint
→ identify the conflict and seek a feasible resolution.

IF a constraint affects downstream tasks
→ propagate it.

IF a constraint becomes irrelevant
→ mark it INVALIDATED.

IF a constraint is explicitly relaxed
→ mark it RELAXED.

IF a plan violates a hard constraint
→ revise the plan.

IF a resource limit makes the plan infeasible
→ redesign or negotiate scope.

IF a time limit makes optional work impossible
→ remove optional work first.

IF the requested format is explicit
→ preserve that format.

IF the user limits scope
→ do not silently expand scope.

IF a constraint is ambiguous and materially affects the result
→ clarify.

IF no feasible plan satisfies all hard constraints
→ do not fabricate compliance; report the conflict and provide feasible alternatives.

IF final verification shows all active hard constraints satisfied
→ mark constraint compliance PASS.
```

---

# 38. Final Constraint-Handling Pattern

```text id="c2q8k5"
GOAL
  ↓
EXTRACT CONSTRAINTS
  ↓
CLASSIFY
  ├── HARD
  ├── SOFT
  ├── PREFERENCE
  ├── RESOURCE
  ├── TIME
  ├── FORMAT
  └── SCOPE
  ↓
PRIORITIZE
  ↓
DETECT CONFLICTS
  ↓
PROPAGATE CONSTRAINTS
  ↓
BUILD PLAN
  ↓
EXECUTE
  ↓
MONITOR COMPLIANCE
  ↓
VERIFY
  ↓
RESOLVE / RELAX / REPLAN
  ↓
FINAL COMPLIANCE CHECK
```

The Constraint Handling module is successful when the system can always answer:

> **What constraints apply, which ones are mandatory, which ones are preferences, what happens when they conflict, how they affect the plan, and what evidence proves the final result respects them?**

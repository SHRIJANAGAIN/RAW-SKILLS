---
name: reasoning-planning-plan-revision
version: 1.0.0
description: Production-ready capability for revising plans when assumptions, constraints, dependencies, resources, evidence, or execution results change.
category: reasoning-and-planning
module: planning-revision
priority: critical
author: SKT AI LABS
---

# Planning Revision

## 1. Purpose

Planning Revision allows the system to adapt an existing plan when reality differs from the original plan.

A plan should not be treated as permanent.

During execution, new information may appear:

```text
A dependency fails.
A tool is unavailable.
A requirement changes.
A hypothesis is rejected.
A task takes longer than expected.
A blocker appears.
A prerequisite is missing.
A resource becomes unavailable.
A previous assumption becomes false.
The user's goal changes.
A completed step produces an unexpected result.
```

The system must determine:

> **What remains valid, what became invalid, what needs to change, and what is the smallest safe revision that restores progress toward the goal?**

---

# 2. Core Principle

> Preserve valid work, discard invalid assumptions, and revise only the parts of the plan affected by new information.

Bad:

```text
"The first plan failed, so start everything from zero."
```

Also bad:

```text
"The plan was already approved, so continue exactly as written."
```

Correct:

```text
Existing plan
    ↓
New evidence
    ↓
Impact analysis
    ↓
Preserve valid components
    ↓
Replace invalid components
    ↓
Recalculate dependencies
    ↓
Update execution order
    ↓
Continue
```

---

# 3. When to Revise

Trigger plan revision when:

```text
A critical assumption becomes false.
A required dependency becomes unavailable.
A task fails.
A requirement changes.
A constraint changes.
A deadline changes.
A tool produces unexpected results.
A hypothesis is rejected.
A new blocker appears.
A cheaper/better path is discovered.
A downstream task becomes unnecessary.
The original plan is no longer feasible.
```

Do not revise merely because execution is slightly slower than expected unless the difference affects the outcome.

---

# 4. Revision Levels

Classify revision size:

```text
R0 — NO REVISION
Minor variation; plan remains valid.

R1 — LOCAL REVISION
One task or small section changes.

R2 — PARTIAL REVISION
Several dependent tasks change.

R3 — MAJOR REVISION
Critical path changes.

R4 — FULL REPLAN
Original plan is no longer viable.
```

---

# 5. Revision Decision Rule

```text
IF new information does not affect dependencies,
constraints, goals, or expected outcome
→ continue existing plan.

IF one task is affected
→ revise that task and its immediate dependents.

IF a critical dependency changes
→ recalculate downstream tasks.

IF the primary goal or hard constraints change
→ perform a major revision.

IF the original strategy cannot satisfy the goal
→ create a new plan.
```

---

# 6. Worked Example — API Integration

## Original Goal

```text
Build an application that uses API X.
```

Original plan:

```text
T1. Read API documentation.
T2. Create authentication.
T3. Implement API client.
T4. Build application features.
T5. Test integration.
T6. Deploy.
```

## New Information

```text
API X does not support the required operation.
```

Incorrect response:

```text
Continue T2 → T6 anyway.
```

Also incorrect:

```text
Delete everything and start over.
```

Correct analysis:

```text
T1:
Completed.

T2:
Potentially reusable if API Y uses compatible authentication.

T3:
Invalid for API X.

T4:
Depends on API client.

T5:
Depends on API client.

T6:
Still relevant.
```

Revised plan:

```text
T1 ✓
    ↓
Evaluate alternative APIs
    ↓
Select compatible API
    ↓
Adapt authentication
    ↓
Implement new client
    ↓
Continue features
    ↓
Test
    ↓
Deploy
```

The valid work is preserved.

---

# 7. Negative Example — Blind Continuation

Original assumption:

```text
Database supports feature X.
```

Later:

```text
Database does not support X.
```

Incorrect:

```text
Continue implementation and hope a workaround appears later.
```

Why wrong?

The plan depends on a false prerequisite.

Correct:

```text
Mark dependency invalid.
Identify alternatives.
Estimate impact.
Revise affected tasks.
Resume execution.
```

---

# 8. Negative Example — Full Restart

Original plan:

```text
Build backend.
Build frontend.
Test.
Deploy.
```

Frontend styling takes longer than expected.

Incorrect:

```text
Throw away backend and restart planning.
```

Why wrong?

The issue affects only part of the execution.

Correct:

```text
Keep backend plan.
Revise frontend schedule.
Adjust remaining work.
Continue.
```

---

# 9. Revision Process

Use:

```text
DETECT CHANGE
    ↓
IDENTIFY WHAT CHANGED
    ↓
COMPARE WITH CURRENT PLAN
    ↓
IDENTIFY AFFECTED TASKS
    ↓
IDENTIFY DOWNSTREAM DEPENDENCIES
    ↓
CHECK GOAL / CONSTRAINTS
    ↓
PRESERVE VALID WORK
    ↓
REMOVE INVALID WORK
    ↓
GENERATE ALTERNATIVES
    ↓
SELECT REVISED PATH
    ↓
UPDATE ORDER
    ↓
UPDATE COMPLETION CRITERIA
    ↓
RESUME EXECUTION
    ↓
MONITOR AGAIN
```

---

# 10. Impact Analysis

When something changes, ask:

```text
What changed?

Which task directly depends on it?

Which downstream tasks depend on that task?

Does the primary goal remain unchanged?

Are any hard constraints now violated?

Did the critical path change?

Did the estimated cost change?

Did the risk change?

Can completed work still be reused?
```

Do not modify unrelated tasks without justification.

---

# 11. Dependency Propagation

Example:

```text
T1 → T2 → T3 → T4
          ↓
          T5
```

If T2 fails:

```text
T2 = invalid
```

Then inspect:

```text
T3
T4
T5
```

They may also become invalid.

But T1 may remain valid.

Rule:

```text
IF task X becomes invalid
→ inspect every downstream dependent task.

Do not automatically invalidate unrelated tasks.
```

---

# 12. Worked Example — Dependency Failure

Original:

```text
T1. Download dataset
T2. Clean dataset
T3. Train model
T4. Evaluate model
T5. Deploy model
```

New information:

```text
Dataset source is unavailable.
```

Impact:

```text
T1 → blocked

T2 → blocked
T3 → blocked
T4 → blocked
T5 → blocked
```

But possible independent work:

```text
Define model architecture.
Prepare training environment.
Write evaluation code.
Prepare deployment configuration.
```

Revised plan:

```text
Find alternative dataset
      +
Prepare independent infrastructure work
      ↓
Acquire dataset
      ↓
Clean
      ↓
Train
      ↓
Evaluate
      ↓
Deploy
```

Do not sit idle merely because one dependency is blocked.

---

# 13. Preserve Completed Work

When revising:

```text
COMPLETED
→ preserve unless invalidated.

VALID
→ preserve.

INVALID
→ replace.

BLOCKED
→ postpone or unblock.

OPTIONAL
→ reconsider.

UNKNOWN
→ investigate.
```

This avoids unnecessary rework.

---

# 14. Plan State Model

Every task should have a state:

```text
NOT_STARTED
READY
IN_PROGRESS
COMPLETED
BLOCKED
FAILED
INVALIDATED
DEFERRED
CANCELLED
```

Example:

```text
T1 → COMPLETED
T2 → COMPLETED
T3 → INVALIDATED
T4 → BLOCKED
T5 → NOT_STARTED
```

This makes revision explicit.

---

# 15. Failed vs Invalidated

These are different.

### FAILED

The task was attempted but did not succeed.

```text
T3:
Implementation failed.
```

It may still be possible to retry.

### INVALIDATED

The task no longer makes sense because a premise changed.

```text
T3:
API client for API X is no longer required
because API Y was selected.
```

Do not automatically retry invalidated tasks.

---

# 16. Retry Rules

```text
IF failure is transient
→ retry when safe.

IF failure is caused by a fixable local error
→ repair and retry.

IF repeated attempts produce the same failure
→ investigate root cause.

IF the underlying assumption is false
→ stop retrying and revise the plan.

IF retry cost is high
→ validate the cause before retrying.
```

---

# 17. Negative Example — Infinite Retry

Incorrect:

```text
Task fails.

Retry.
Retry.
Retry.
Retry.
```

Why wrong?

Repeated failure without new information does not constitute planning.

Correct:

```text
Attempt
    ↓
Failure
    ↓
Analyze cause
    ↓
Determine whether retry is justified
    ↓
Retry OR revise
```

---

# 18. Requirement Change

Suppose original requirement:

```text
Output must be JSON.
```

New requirement:

```text
Output must be XML.
```

Do not continue producing JSON.

Revision:

```text
Update output specification.
Identify affected implementation.
Update validation.
Update tests.
Update documentation.
```

Unrelated logic can remain unchanged.

---

# 19. Requirement Revision Rules

```text
IF a requirement changes
→ identify every task implementing that requirement.

IF the new requirement conflicts with another requirement
→ identify the conflict explicitly.

IF the new requirement makes existing work reusable
→ preserve reusable components.

IF the new requirement makes a task unnecessary
→ cancel or defer that task.

IF the change affects the primary goal
→ re-evaluate the complete critical path.
```

---

# 20. Constraint Change

Example:

Original:

```text
Budget:
$1000
```

New:

```text
Budget:
$300
```

Possible revision:

```text
Remove optional services.
Use cheaper infrastructure.
Reduce scope.
Prioritize critical functionality.
Recalculate operating costs.
```

Do not simply keep the old plan and exceed the new constraint.

---

# 21. Deadline Change

Original:

```text
Deadline:
Friday
```

New:

```text
Deadline:
Tomorrow
```

Revision:

```text
1. Protect mandatory functionality.
2. Remove optional work.
3. Parallelize independent tasks.
4. Reduce unnecessary scope.
5. Increase validation of critical paths.
6. Recalculate feasible completion.
```

If the new deadline is impossible:

```text
State the conflict.
Do not fabricate completion.
```

---

# 22. Resource Loss

Example:

```text
Available:
2 GPUs

One GPU becomes unavailable.
```

Revision:

```text
Recalculate:
- Parallel tasks.
- Runtime.
- Batch size.
- Model size.
- Scheduling.
- Deadline feasibility.
```

Do not assume the original timing remains valid.

---

# 23. Better Alternative Discovered

Planning revision is not only for failures.

Suppose:

```text
Original approach:
4 hours.

New discovered approach:
45 minutes.

Both satisfy requirements.
```

Evaluate:

```text
Correctness
Reliability
Risk
Compatibility
Maintenance
```

If the new approach is genuinely superior:

```text
Revise the plan.
```

Do not remain attached to the old plan merely because it was created first.

---

# 24. Negative Example — Plan Attachment

Incorrect:

```text
"We already planned to use method A,
so we must use A."
```

Why wrong?

A plan is a means, not the goal.

Correct:

```text
Goal remains fixed.
Strategy may change.
```

---

# 25. Goal Preservation

When revising, distinguish:

```text
GOAL
What must ultimately be achieved.

STRATEGY
How we planned to achieve it.

TASKS
Concrete work used by the strategy.
```

Example:

```text
Goal:
Deploy a working application.

Old strategy:
Platform A.

New information:
Platform A unavailable.

Revision:
Use Platform B.
```

Do not confuse strategy failure with goal failure.

---

# 26. Goal Change

If the user changes the goal:

Original:

```text
Build a prototype.
```

New:

```text
Build a production-ready system.
```

This may require major revision:

```text
Testing
Security
Reliability
Monitoring
Deployment
Documentation
Scalability
```

The old prototype plan should not simply continue unchanged.

---

# 27. Plan Delta

When possible, express revisions as a delta:

```text
UNCHANGED:
T1
T2

MODIFIED:
T3

REMOVED:
T4

ADDED:
T5
T6

REORDERED:
T7 moved before T3

BLOCKED:
T8
```

This is easier to verify than rewriting the entire plan without explanation.

---

# 28. Worked Example — Plan Delta

Original:

```text
T1 Research
T2 Build API
T3 Build UI
T4 Integrate
T5 Test
T6 Deploy
```

New information:

```text
API provider changed.
```

Revision:

```text
UNCHANGED:
T1 Research

MODIFIED:
T2 Build API client

UNCHANGED:
T3 Build UI

MODIFIED:
T4 Integration

UNCHANGED:
T5 Test
T6 Deploy
```

Only affected components change.

---

# 29. Minimal Safe Revision

Prefer:

> The smallest revision that restores feasibility while preserving the goal.

Example:

```text
Problem:
Tool A unavailable.

Possible:
Rewrite entire architecture.

Better:
Replace only the tool-dependent component if compatibility allows.
```

Do not introduce unnecessary changes.

---

# 30. When Minimal Revision Is Not Enough

Use a major replan when:

```text
The primary strategy is fundamentally invalid.
Multiple critical dependencies failed.
Hard constraints changed substantially.
The goal changed.
The risk profile became unacceptable.
The remaining work is no longer feasible.
```

Then:

```text
Archive old plan.
Extract reusable work.
Create new plan.
Revalidate dependencies.
```

---

# 31. Edge Case — Partial Success

Example:

```text
Authentication:
Complete.

Payment:
Complete.

Notifications:
Failed.

```

Do not classify the entire project as failed.

Use:

```text
Authentication → COMPLETED
Payment → COMPLETED
Notifications → FAILED
```

Revise only the affected branch.

---

# 32. Edge Case — Hidden Dependency Discovered

Original:

```text
T1 → T2
```

New discovery:

```text
T2 actually requires T3 first.
```

Update:

```text
T1 → T3 → T2
```

Then inspect whether T4, T5, etc. depend on T2.

Update the dependency graph before continuing.

---

# 33. Edge Case — New Information Makes Work Unnecessary

Original:

```text
T1 Build custom parser.
```

New information:

```text
Required parser is already available and compatible.
```

Correct:

```text
Cancel T1.
Validate existing parser.
Continue integration.
```

Do not complete unnecessary work merely because it was planned.

---

# 34. Edge Case — Conflicting New Information

Example:

```text
Source A:
Tool supports required feature.

Source B:
Tool does not support required feature.
```

Do not immediately revise the plan.

First:

```text
Verify source reliability.
Check versions.
Check configuration.
Reproduce behavior.
```

Then revise.

---

# 35. Edge Case — User Changes Direction Mid-Execution

Example:

```text
User:
"Actually, don't build the web version.
Build a CLI instead."
```

Correct:

```text
Stop affected web-specific tasks.
Preserve reusable logic.
Redefine interface requirements.
Create CLI-specific tasks.
Update testing.
Resume.
```

Do not continue old UI work after the goal has changed.

---

# 36. Edge Case — Revision Creates New Risk

A quick workaround may restore progress but introduce technical debt.

Evaluate:

```text
Immediate benefit
+
Long-term cost
+
Failure risk
+
Reversibility
```

If workaround is acceptable:

```text
Mark it as temporary.
Define cleanup condition.
```

---

# 37. Temporary Workaround Record

```text
Workaround:
Use fallback implementation B.

Reason:
Primary dependency unavailable.

Status:
TEMPORARY.

Risk:
Higher maintenance cost.

Replacement condition:
Restore implementation A when dependency becomes available.

Owner:
Planning task.

Review point:
Before production release.
```

---

# 38. Revision Verification

After changing the plan:

```text
[ ] Goal still satisfied?
[ ] Hard constraints still satisfied?
[ ] Dependencies valid?
[ ] Task ordering still correct?
[ ] No invalid tasks remain?
[ ] Required tasks still covered?
[ ] Completed work preserved?
[ ] New risks identified?
[ ] New estimates updated?
[ ] Completion criteria updated?
```

Never revise one task in isolation if it affects downstream dependencies.

---

# 39. Revised Plan Format

Use:

```text
Goal:
...

Reason for revision:
...

What changed:
...

Preserved work:
...

Invalidated work:
...

Blocked work:
...

Added work:
...

Modified work:
...

New dependencies:
...

New execution order:
...

New risks:
...

New completion criteria:
...

Next action:
...
```

---

# 40. Worked Example — Full Revision

## Original

```text
Goal:
Deploy application.

Plan:
1. Build backend.
2. Build frontend.
3. Integrate payment API.
4. Test.
5. Deploy.
```

## New information

```text
Payment API is unavailable for the foreseeable future.
```

## Impact

```text
Backend:
Mostly valid.

Frontend:
Mostly valid.

Payment integration:
Blocked.

Testing:
Needs modification.

Deployment:
Still valid.
```

## Revised plan

```text
1. Complete backend.
2. Complete frontend.
3. Implement payment abstraction/interface.
4. Add mock payment provider for testing.
5. Test all non-payment functionality.
6. Keep payment integration blocked.
7. Deploy only if the product requirements permit payment to remain unavailable.
```

Important:

```text
Do NOT claim the original complete goal is achieved
if payment is a mandatory requirement.
```

---

# 41. Negative Example — Pretending the Goal Is Still Achieved

Incorrect:

```text
Payment integration is unavailable,
but the app is complete.
```

Why wrong?

The original requirement remains unsatisfied.

Correct:

```text
Current state:
Core application complete.

Blocked requirement:
Payment integration.

Goal status:
PARTIALLY_COMPLETE.
```

---

# 42. Plan Status

Use:

```text
NOT_STARTED
IN_PROGRESS
PARTIALLY_COMPLETE
BLOCKED
REVISED
COMPLETE
FAILED
CANCELLED
```

Example:

```text
Plan status:
REVISED

Reason:
Original API dependency unavailable.

Goal status:
PARTIALLY_COMPLETE.
```

---

# 43. Revision Confidence

Every major revision should have a confidence level:

```text
HIGH
MEDIUM
LOW
```

Example:

```text
Revision:
Replace dependency A with B.

Confidence:
MEDIUM.

Reason:
B satisfies functional requirements,
but production-scale performance is not yet verified.
```

---

# 44. Revision Rules for Tool Failure

```text
IF tool fails transiently
→ retry safely.

IF tool repeatedly fails
→ investigate.

IF tool is unavailable
→ identify alternative tools.

IF no equivalent tool exists
→ redesign affected step.

IF tool output contradicts assumptions
→ validate output and revise assumptions if confirmed.

IF tool failure affects only optional work
→ defer that work.

IF tool failure blocks critical work
→ prioritize fallback discovery.
```

---

# 45. Revision Rules for Evidence

```text
IF new evidence confirms the current plan
→ continue.

IF evidence weakens one task
→ inspect that task.

IF evidence invalidates a prerequisite
→ propagate impact downstream.

IF evidence invalidates the strategy
→ generate alternatives.

IF evidence changes the goal interpretation
→ clarify or redefine the plan.

IF evidence is unreliable or contradictory
→ verify before major revision.
```

---

# 46. Production Decision Rules

```text
IF the goal remains achievable with the existing plan
→ do not revise unnecessarily.

IF a local task changes
→ revise only affected tasks.

IF a dependency changes
→ propagate the change through downstream dependencies.

IF a hard constraint changes
→ recalculate feasibility.

IF a requirement changes
→ identify all affected tasks.

IF a task becomes unnecessary
→ cancel or defer it.

IF a task becomes invalid
→ do not blindly retry it.

IF a task fails repeatedly for the same reason
→ stop repeated retries and investigate.

IF completed work remains valid
→ preserve it.

IF the original strategy is invalid
→ generate a replacement strategy.

IF a better valid strategy appears
→ compare it before switching.

IF the primary goal changes
→ replan from the new goal.

IF the deadline becomes tighter
→ protect required critical-path work and remove optional work.

IF resources decrease
→ recalculate schedule and feasibility.

IF a workaround is temporary
→ explicitly mark it temporary and define its replacement condition.

IF a revision introduces new risks
→ record and evaluate those risks.

IF contradictory evidence appears
→ verify before making major changes.

IF the revised plan cannot satisfy the requirements
→ report the conflict instead of pretending the plan is feasible.

IF the plan is revised
→ revalidate dependencies, constraints, ordering, and completion criteria.

IF the revision is complete
→ resume execution from the earliest valid unfinished step.
```

---

# 47. Final Planning Revision Protocol

```text
CURRENT PLAN
    ↓
EXECUTE
    ↓
NEW INFORMATION / FAILURE / CHANGE
    ↓
DETECT
    ↓
CLASSIFY CHANGE
    ↓
MEASURE IMPACT
    ↓
CHECK GOAL
    ↓
CHECK CONSTRAINTS
    ↓
TRACE DEPENDENCIES
    ↓
PRESERVE VALID WORK
    ↓
REMOVE INVALID WORK
    ↓
GENERATE ALTERNATIVES
    ↓
SELECT MINIMUM SAFE REVISION
    ↓
UPDATE PLAN
    ↓
UPDATE PRIORITIES
    ↓
UPDATE COMPLETION CRITERIA
    ↓
VERIFY FEASIBILITY
    ↓
RESUME EXECUTION
    ↓
MONITOR AGAIN
```

The Planning Revision module is successful when the system can answer:

> **What changed, which parts of the original plan are still valid, which parts became invalid, what dependencies were affected, what work can be preserved, what must be replaced, and what is the safest revised path toward the original or newly defined goal?**

---

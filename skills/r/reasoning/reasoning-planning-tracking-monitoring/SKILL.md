---
name: reasoning-planning-tracking-monitoring
version: 1.0.0
description: Production-ready capability for continuous tracking and monitoring of goals, milestones, task states, completion criteria, blockers, dependencies, progress drift, and execution status.
category: reasoning-and-planning
module: goal-tracking-and-progress-monitoring
priority: critical
author: SKT AI LABS
---

# Goal Tracking & Progress Monitoring

## 1. Purpose

Goal Tracking ensures that the system does not merely create a plan and forget about it.

It continuously answers:

```text
What is the goal?
What has been completed?
What is currently in progress?
What remains?
What is blocked?
What changed?
Are we still moving toward the goal?
Is the goal actually complete?
```

The system must distinguish between:

```text
PLANNED
What should happen.

IN_PROGRESS
What is currently being worked on.

COMPLETED
What has actually been verified as done.

BLOCKED
What cannot currently proceed.

FAILED
What was attempted but did not succeed.

CANCELLED
What is intentionally no longer required.

INVALIDATED
What no longer applies because assumptions or requirements changed.
```

---

# 2. Core Principle

> Never confuse activity with progress.

Bad:

```text
"I worked on the API, so the API task is complete."
```

Correct:

```text
Task:
Implement API authentication.

Completion criteria:
- Authentication implemented.
- Valid credentials accepted.
- Invalid credentials rejected.
- Tests pass.

Status:
IN_PROGRESS

Reason:
Implementation exists, but validation is incomplete.
```

---

# 3. Goal Hierarchy

Represent complex goals hierarchically:

```text
GOAL
│
├── OBJECTIVE 1
│   ├── TASK 1
│   ├── TASK 2
│   └── TASK 3
│
├── OBJECTIVE 2
│   ├── TASK 4
│   └── TASK 5
│
└── OBJECTIVE 3
    ├── TASK 6
    └── TASK 7
```

Example:

```text
Goal:
Deploy production application.

Objective 1:
Prepare application.

Objective 2:
Configure infrastructure.

Objective 3:
Validate production deployment.
```

This makes progress measurable at multiple levels.

---

# 4. Goal Definition

Every major goal should contain:

```text
Goal:
...

Purpose:
...

Success criteria:
...

Constraints:
...

Deadline:
...

Current status:
...

Owner/actor:
...

Dependencies:
...
```

Example:

```text
Goal:
Deploy the application.

Purpose:
Make the application available to users.

Success criteria:
- Application starts successfully.
- Required endpoints respond.
- Critical tests pass.
- Production deployment is reachable.

Current status:
IN_PROGRESS.
```

---

# 5. Worked Example — Building an Application

## Input

```text
Build and deploy a small web application.
```

Breakdown:

```text
Goal:
Build and deploy web application.

T1:
Define requirements.

T2:
Build backend.

T3:
Build frontend.

T4:
Integrate frontend/backend.

T5:
Test.

T6:
Deploy.

T7:
Verify production.
```

Dependency graph:

```text
T1
 ↓
T2 ──┐
     ├──> T4 → T5 → T6 → T7
T3 ──┘
```

Initial state:

```text
T1 READY
T2 BLOCKED
T3 BLOCKED
T4 BLOCKED
T5 BLOCKED
T6 BLOCKED
T7 BLOCKED
```

After T1:

```text
T1 COMPLETED
T2 READY
T3 READY
```

Now T2 and T3 can potentially proceed in parallel.

---

# 6. Negative Example — False Progress

Incorrect:

```text
T1 completed.
T2 started.
T3 started.
Therefore project is 50% complete.
```

Why wrong?

Task count does not necessarily represent actual progress.

For example:

```text
T1 = 5 minutes
T2 = 2 days
T3 = 3 hours
```

Three tasks are not equally valuable.

Correct:

```text
Track completion against meaningful milestones and criteria,
not merely the number of task boxes checked.
```

---

# 7. Task State Machine

Use:

```text
NOT_STARTED
      ↓
READY
      ↓
IN_PROGRESS
      ↓
 ┌────┴────┐
 ↓         ↓
COMPLETED  FAILED
             ↓
          RETRY/REPLAN
```

Additional states:

```text
BLOCKED
CANCELLED
INVALIDATED
DEFERRED
```

---

# 8. State Transition Rules

```text
NOT_STARTED → READY
IF prerequisites are satisfied.

READY → IN_PROGRESS
IF execution begins.

IN_PROGRESS → COMPLETED
IF all completion criteria are verified.

IN_PROGRESS → FAILED
IF execution fails and cannot currently satisfy criteria.

IN_PROGRESS → BLOCKED
IF an external dependency prevents continuation.

IN_PROGRESS → CANCELLED
IF the task is intentionally removed.

ANY STATE → INVALIDATED
IF the task no longer applies.

FAILED → IN_PROGRESS
IF a justified retry begins.

BLOCKED → READY
IF the blocker is resolved.
```

---

# 9. Completion Criteria

Every meaningful task should have explicit completion criteria.

Example:

```text
Task:
Configure database.

Completion criteria:
[ ] Database starts.
[ ] Application connects.
[ ] Required schema exists.
[ ] Connection test passes.
```

Status:

```text
3/4 complete
→ NOT COMPLETE
```

Do not mark the task complete until required criteria are satisfied.

---

# 10. Negative Example — Premature Completion

Incorrect:

```text
"Database configuration is done because the config file exists."
```

Why wrong?

The actual objective is working connectivity, not merely file creation.

Correct:

```text
Configuration exists.
Connection verified.
Required operations tested.

→ COMPLETED
```

---

# 11. Progress Dimensions

Track multiple dimensions:

```text
Task completion
Milestone completion
Goal completion
Dependency readiness
Validation status
Blockers
Risk
Schedule
Quality
```

A project can be:

```text
90% implementation complete
but
40% validation complete.
```

Therefore:

```text
Implementation progress ≠ Overall readiness
```

---

# 12. Milestones

Use milestones for major checkpoints.

Example:

```text
M1 — Requirements complete
M2 — Core implementation complete
M3 — Integration complete
M4 — Testing complete
M5 — Production deployment complete
```

A milestone should have explicit criteria.

```text
M3 COMPLETE WHEN:
- Backend integrated.
- Frontend integrated.
- Critical workflows function.
```

---

# 13. Worked Example — Milestone Tracking

```text
M1 Requirements       ✅
M2 Implementation     ✅
M3 Integration        🔄
M4 Testing            ⏳
M5 Deployment         ⏳
```

Interpretation:

```text
Overall state:
IN_PROGRESS

Current milestone:
M3

Next milestone:
M4

Blocking issue:
Payment integration incomplete.
```

---

# 14. Goal Progress

Use a structured representation:

```text
Goal:
...

Status:
...

Milestones:
...

Completed:
...

In progress:
...

Blocked:
...

Remaining:
...

Risks:
...

Next action:
...
```

Example:

```text
Goal:
Deploy application.

Status:
IN_PROGRESS.

Completed:
Requirements
Backend
Frontend

In progress:
Integration

Blocked:
Payment provider

Remaining:
Testing
Deployment
Production verification

Next action:
Implement payment abstraction and investigate provider availability.
```

---

# 15. Progress Percentage

Percentages should be used carefully.

Bad:

```text
"7 out of 10 tasks complete = 70% project complete."
```

unless the tasks are intentionally equal-weight.

Better:

```text
Task-weighted progress:
...

Milestone progress:
...

Critical-path progress:
...
```

If weights are meaningful:

```text
Progress =
Σ(completed task weight)
/
Σ(total task weight)
× 100
```

Do not invent weights without justification.

---

# 16. Progress Categories

For simple systems:

```text
0%     NOT_STARTED
1–24%  EARLY
25–49% PARTIAL
50–74% SUBSTANTIAL
75–99% NEAR_COMPLETE
100%   COMPLETE
```

But:

```text
100% only means complete if completion criteria are satisfied.
```

---

# 17. Negative Example — Fake 100%

Incorrect:

```text
"Everything is 100% done."
```

when:

```text
Tests:
Not run.

Deployment:
Not verified.
```

Correct:

```text
Implementation:
Complete.

Validation:
Pending.

Overall:
NOT_COMPLETE.
```

---

# 18. Goal vs Task Completion

A goal can remain incomplete even when all planned tasks are complete.

Example:

```text
Goal:
Production-ready application.

Tasks:
All completed.

New issue:
Security requirement discovered after planning.
```

Therefore:

```text
Task completion:
100%

Goal completion:
Not yet verified.
```

The goal is complete only when its success criteria are satisfied.

---

# 19. Progress Verification

At checkpoints:

```text
COMPARE:

Expected state
vs
Actual state
```

Example:

```text
Expected:
API endpoint responds successfully.

Actual:
Endpoint returns 500.

Result:
Task NOT COMPLETE.
```

Never infer completion merely from intention.

---

# 20. Negative Example — Assuming Success

Incorrect:

```text
Command ran without an error,
therefore deployment succeeded.
```

Why wrong?

The command may complete while the deployed application remains unavailable.

Correct:

```text
Deployment command:
SUCCESS

Application health:
UNKNOWN

Production verification:
PENDING
```

Then verify.

---

# 21. Progress Drift

Drift occurs when actual execution diverges from the plan.

Examples:

```text
Expected:
Task takes 30 minutes.

Actual:
Task takes 3 hours.

Expected:
API available.

Actual:
API unavailable.

Expected:
5 tasks.

Actual:
12 required tasks discovered.
```

Detect drift early.

---

# 22. Drift Rules

```text
IF actual execution remains within expected boundaries
→ continue.

IF a task takes significantly longer than expected
→ reassess estimate and blocker status.

IF new tasks appear
→ update scope and plan.

IF dependencies change
→ update dependency graph.

IF the goal becomes less achievable
→ trigger plan revision.

IF drift does not affect outcome
→ record but do not overreact.
```

---

# 23. Worked Example — Time Drift

Original:

```text
Task:
Database migration.

Estimate:
1 hour.
```

Actual:

```text
After 1 hour:
Migration only 30% complete.
```

Incorrect:

```text
Continue using the original schedule.
```

Correct:

```text
Current progress:
30%.

Observed rate:
Lower than expected.

Action:
Investigate blocker and re-estimate remaining work.
```

---

# 24. ETA Re-estimation

Never preserve an old ETA blindly.

Use:

```text
Remaining work
÷
Observed execution rate
=
Approximate remaining time
```

Example:

```text
30% completed in 1 hour.

If rate remains roughly constant:
Remaining 70%
≈ 2.33 additional hours.
```

This is an estimate, not a guarantee.

If blockers exist, update the estimate after resolving them.

---

# 25. Negative Example — False ETA

Incorrect:

```text
"Only 30 minutes left."
```

when the estimate has not been recalculated after a major blocker.

Correct:

```text
Original ETA:
30 minutes.

New blocker:
Dependency unavailable.

Updated ETA:
Unknown until dependency is resolved.
```

---

# 26. Blocker Tracking

Every blocker should include:

```text
Blocker:
...

Affected task:
...

Cause:
...

Severity:
...

Since:
...

Required resolution:
...

Alternative path:
...

Status:
...
```

Example:

```text
Blocker:
Payment API unavailable.

Affected:
Payment integration.

Severity:
HIGH.

Alternative:
Mock provider for non-production testing.

Status:
ACTIVE.
```

---

# 27. Blocker Severity

```text
LOW
Minor inconvenience.

MEDIUM
Slows progress but workaround exists.

HIGH
Blocks important work.

CRITICAL
Blocks the primary goal or creates major risk.
```

---

# 28. Stalled Task Detection

A task is potentially stalled when:

```text
No meaningful progress
+
No valid reason for waiting
```

Examples:

```text
Task remains IN_PROGRESS for unusually long.
No new output produced.
Same failure repeated.
Required dependency is unavailable.
```

Action:

```text
Investigate.
```

Do not automatically mark it failed.

---

# 29. Negative Example — Ignoring a Stalled Task

Incorrect:

```text
Task:
"Implement authentication."

Status:
IN_PROGRESS for several days.

Planner:
Continue to next task anyway.
```

Why wrong?

The dependency may block later tasks.

Correct:

```text
Detect stall.
Identify cause.
Unblock, reassign, split, retry, or revise.
```

---

# 30. Dependency Progress

Track:

```text
READY
BLOCKED
PARTIALLY_READY
COMPLETED
```

Example:

```text
T1 completed.
T2 completed.
T3 requires T2 + external API.

T3:
BLOCKED by external API.
```

Do not mark T3 ready simply because T2 is complete.

---

# 31. Parallel Progress

If tasks are independent:

```text
T1 ──┐
     ├──> T4
T2 ──┤
     │
T3 ──┘
```

T1, T2, T3 can proceed in parallel.

Goal tracking should therefore track independent branches separately.

Do not treat one slow branch as proof that the entire project is stalled.

---

# 32. Critical Path Monitoring

The critical path contains tasks that directly determine completion time.

Example:

```text
T1 → T2 → T3 → T4
```

If T2 is delayed:

```text
Overall completion likely delayed.
```

If an optional parallel task is delayed:

```text
Overall deadline may remain unaffected.
```

Therefore prioritize monitoring of critical-path tasks.

---

# 33. Goal Health

Track:

```text
ON_TRACK
AT_RISK
BLOCKED
OFF_TRACK
COMPLETED
```

### ON_TRACK

Execution matches expected plan.

### AT_RISK

Warning signs exist.

### BLOCKED

Critical progress cannot continue.

### OFF_TRACK

Current plan is unlikely to achieve the goal without revision.

---

# 34. Worked Example — Goal Health

```text
Goal:
Launch application Friday.

Current:
Backend complete.
Frontend 80%.
Testing not started.

New information:
Testing requires 2 days.

Today:
Thursday.
```

Status:

```text
OFF_TRACK
```

Correct response:

```text
Do not say:
"Almost done."

Instead:
"The current plan is unlikely to meet Friday
because testing has not started and is estimated at 2 days.
Plan revision is required."
```

---

# 35. Risk Tracking

Progress can be high while risk remains high.

Example:

```text
Implementation:
95%

Tests:
20%

Security review:
0%
```

Overall:

```text
Progress appears high.
Readiness is low.
```

Track risk separately.

---

# 36. Progress vs Readiness

Use:

```text
PROGRESS
How much planned work has been completed?

READINESS
Is the result ready for its intended use?

QUALITY
Does it meet required standards?

CONFIDENCE
How certain are we that it works?
```

These are different dimensions.

---

# 37. Completion Gate

Before marking a major goal complete:

```text
GOAL COMPLETION GATE

[ ] All mandatory requirements satisfied.
[ ] Required tasks completed.
[ ] Required outputs exist.
[ ] Validation completed.
[ ] Critical dependencies verified.
[ ] Known blockers resolved or explicitly accepted.
[ ] Success criteria satisfied.
[ ] No unresolved critical failure.
```

Only then:

```text
GOAL = COMPLETE
```

---

# 38. Negative Example — Completion by Activity

Incorrect:

```text
"All code has been written, so the project is complete."
```

Correct:

```text
Code:
Complete.

Tests:
Pending.

Deployment:
Pending.

Goal:
IN_PROGRESS.
```

---

# 39. Partial Completion

Always allow:

```text
PARTIALLY_COMPLETE
```

Example:

```text
Goal:
Build application.

Completed:
Authentication
Dashboard
User settings

Incomplete:
Payments
Notifications
Production deployment
```

Correct status:

```text
PARTIALLY_COMPLETE
```

Do not force:

```text
COMPLETE
```

or:

```text
FAILED
```

---

# 40. Goal Abandonment

A goal can become:

```text
CANCELLED
```

when:

```text
User no longer wants it.
Business requirement removed.
Goal superseded by another goal.
Cost exceeds acceptable limit.
```

Record:

```text
Reason:
...

Replacement goal:
...
```

Do not continue tracking cancelled work as active progress.

---

# 41. Goal Invalidation

A goal can become:

```text
INVALIDATED
```

when its underlying premise is no longer valid.

Example:

```text
Goal:
Support API X.

New information:
API X discontinued.

Result:
Goal INVALIDATED.
```

This differs from failure.

---

# 42. Goal Revision

If the goal changes:

```text
Old:
Build web application.

New:
Build mobile application.
```

Do:

```text
Stop affected tasks.
Preserve reusable components.
Create new milestones.
Recalculate dependencies.
Restart tracking from the revised goal.
```

---

# 43. Progress Snapshot

At any point, generate:

```text
Goal:
...

Overall status:
...

Milestone:
...

Completed:
...

In progress:
...

Blocked:
...

Failed:
...

Remaining:
...

Risks:
...

Drift:
...

Next action:
...
```

Example:

```text
Goal:
Deploy application.

Overall:
AT_RISK.

Completed:
Backend
Frontend

In progress:
Integration

Blocked:
Payment provider

Remaining:
Testing
Deployment verification

Risk:
HIGH

Drift:
Payment dependency unavailable.

Next:
Implement fallback integration and revise deployment plan.
```

---

# 44. Negative Example — Vague Progress Report

Bad:

```text
"Things are going well."
```

Why wrong?

It gives no measurable state.

Better:

```text
Completed:
4/7 milestones.

Current:
Integration.

Blocked:
Payment.

Risk:
Medium.

Next:
Resolve payment dependency.
```

---

# 45. Progress Update Frequency

Do not constantly produce progress reports.

Use checkpoints:

```text
After major task completion.
After milestone completion.
When a blocker appears.
When a requirement changes.
When significant drift occurs.
Before major irreversible actions.
At final verification.
```

---

# 46. Change Detection

Compare:

```text
Previous state
vs
Current state
```

Track:

```text
Newly completed
Newly blocked
Newly failed
New dependencies
Changed requirements
Changed estimates
Changed risks
Changed goal status
```

This produces meaningful updates rather than repetitive status messages.

---

# 47. Worked Example — State Transition

Previous:

```text
T1 COMPLETED
T2 IN_PROGRESS
T3 BLOCKED
```

New event:

```text
T2 completed successfully.
```

Update:

```text
T2 COMPLETED
```

Then evaluate T3:

```text
If all T3 prerequisites are now satisfied:
T3 → READY

Otherwise:
T3 remains BLOCKED.
```

Do not blindly change T3 to READY.

---

# 48. Progress Integrity

Never claim:

```text
completed
verified
working
deployed
successful
fixed
```

unless the corresponding evidence exists.

Use:

```text
ATTEMPTED
when action was performed.

EXPECTED
when success is predicted.

VERIFIED
when evidence confirms success.
```

---

# 49. Negative Example — Expected vs Verified

Incorrect:

```text
"The deployment is working."
```

Evidence:

```text
Deployment command succeeded.
```

Correct:

```text
Deployment command:
SUCCESS

Application availability:
NOT YET VERIFIED.
```

Then perform health checks.

---

# 50. Goal Tracking Ledger

For complex projects:

```text
Goal ID:
...

Goal:
...

Status:
...

Success criteria:
...

Milestones:
...

Tasks:
...

Dependencies:
...

Completed:
...

In progress:
...

Blocked:
...

Failed:
...

Invalidated:
...

Risks:
...

Drift:
...

Current estimate:
...

Next action:
...

Last verified:
...
```

---

# 51. Goal Tracking Example

```text
Goal ID:
G01

Goal:
Deploy production application.

Status:
AT_RISK

Success criteria:
- Application reachable.
- Critical endpoints work.
- Production smoke tests pass.

Milestones:
M1 Requirements ✓
M2 Implementation ✓
M3 Integration 🔄
M4 Testing ⏳
M5 Deployment ⏳

Blocked:
Payment provider.

Risk:
HIGH.

Drift:
Integration delayed by external dependency.

Next action:
Implement fallback/mock integration and reassess production requirements.

Last verified:
Integration test status.
```

---

# 52. Progress Decision Rules

```text
IF completion criteria are satisfied
→ mark task COMPLETED.

IF completion criteria are not satisfied
→ do not mark task complete.

IF a task has started
→ mark IN_PROGRESS.

IF a required dependency is unavailable
→ mark BLOCKED.

IF the task no longer applies
→ mark INVALIDATED or CANCELLED.

IF execution failed
→ mark FAILED and determine retry/replan path.

IF a blocker is resolved
→ re-evaluate whether the task is READY.

IF a task is stalled
→ investigate rather than silently continuing.

IF actual progress differs materially from expected progress
→ recalculate estimates.

IF the critical path is delayed
→ assess overall goal health.

IF optional work is delayed but the goal remains feasible
→ do not falsely mark the whole project OFF_TRACK.

IF a milestone's completion criteria are unmet
→ milestone remains incomplete.

IF all tasks are complete but goal success criteria are unverified
→ goal remains incomplete.

IF implementation is complete but validation is pending
→ distinguish implementation completion from overall readiness.

IF a new requirement appears
→ update goal scope and re-evaluate progress.

IF a requirement is removed
→ remove affected tasks from remaining work.

IF a goal becomes unnecessary
→ mark CANCELLED.

IF the goal's premise becomes invalid
→ mark INVALIDATED.

IF a plan is no longer capable of meeting the goal
→ mark OFF_TRACK and trigger plan revision.

IF evidence confirms the goal's success criteria
→ mark COMPLETE.

IF evidence is insufficient
→ use UNKNOWN / PENDING rather than claiming success.

IF progress reports contain unsupported claims
→ downgrade them to observed status.

IF a task completes
→ immediately evaluate newly unblocked dependent tasks.

IF a critical blocker appears
→ update goal health immediately.

IF new evidence changes the expected outcome
→ update progress and planning state.
```

---

# 53. Final Goal Tracking Protocol

```text
DEFINE GOAL
    ↓
DEFINE SUCCESS CRITERIA
    ↓
BUILD MILESTONES
    ↓
BUILD TASKS
    ↓
MAP DEPENDENCIES
    ↓
INITIALIZE STATES
    ↓
EXECUTE
    ↓
OBSERVE ACTUAL STATE
    ↓
VERIFY COMPLETION
    ↓
UPDATE TASK STATES
    ↓
UPDATE MILESTONES
    ↓
CHECK BLOCKERS
    ↓
CHECK CRITICAL PATH
    ↓
COMPARE PLAN VS REALITY
    ↓
DETECT DRIFT
    ↓
RECALCULATE ESTIMATES
    ↓
UPDATE GOAL HEALTH
    ↓
TRIGGER REVISION IF REQUIRED
    ↓
REPEAT
    ↓
RUN COMPLETION GATE
    ↓
VERIFY SUCCESS CRITERIA
    ↓
MARK COMPLETE ONLY WHEN VERIFIED
```

---

# 54. Final Self-Check

Before reporting a goal as complete:

```text
[ ] Is the actual goal still the same?
[ ] Are all mandatory requirements satisfied?
[ ] Are all required tasks complete?
[ ] Are completion criteria verified?
[ ] Are critical dependencies resolved?
[ ] Are blockers resolved?
[ ] Are failures resolved?
[ ] Are tests/validation complete where required?
[ ] Does actual state match expected state?
[ ] Has significant drift been accounted for?
[ ] Is the final result actually usable?
[ ] Is completion based on evidence rather than assumption?
```

---

# 55. Final Production Principle

```text
PLAN
  ↓
EXECUTE
  ↓
OBSERVE
  ↓
VERIFY
  ↓
UPDATE STATE
  ↓
COMPARE AGAINST GOAL
  ↓
DETECT DRIFT
  ↓
REVISE IF NECESSARY
  ↓
VERIFY COMPLETION
```

The Goal Tracking & Progress Monitoring module is successful when the system can answer:

> **What is the current goal state, what has actually been completed and verified, what remains, what is blocked or at risk, how does reality differ from the original plan, and what must happen next to reach a verified completion state?**

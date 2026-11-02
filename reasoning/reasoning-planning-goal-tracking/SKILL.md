---
name: reasoning-planning-goal-tracking
version: 1.0.0
description: Production-ready goal-tracking capability for maintaining objectives, measuring progress, detecting goal drift, handling partial completion and changing requirements, and determining when a goal is actually complete.
category: reasoning-and-planning
module: goal-tracking
priority: critical
author: SKT AI LABS
---

# Goal Tracking

## 1. Purpose

Goal Tracking ensures that execution remains aligned with the user's actual objective from beginning to completion.

Task Decomposition determines **what needs to be done**.

Step Planning determines **how and when to do it**.

Goal Tracking continuously determines:

* What is the actual goal?
* What state is currently achieved?
* What remains incomplete?
* Which requirements are satisfied?
* Which requirements are blocked?
* Has the task drifted away from the user's objective?
* Has a new requirement changed the goal?
* Is the result actually complete?
* Can execution safely stop?

The purpose is to prevent a system from being busy without being useful.

---

# 2. Core Principle

> Progress is not the same as goal completion.

Example:

```text
Goal:
Deploy a working website.

Progress:
- 90% of code implemented.
- Build succeeds.
- Deployment started.

Completion:
- Website is deployed.
- Website is reachable.
- Required functionality works.
- Required constraints are satisfied.
```

A system must never equate:

```text
more work completed
```

with:

```text
goal achieved
```

---

# 3. Goal Hierarchy

Represent complex objectives hierarchically:

```text
PRIMARY GOAL
│
├── SUBGOAL A
│   ├── Task A1
│   └── Task A2
│
├── SUBGOAL B
│   ├── Task B1
│   └── Task B2
│
└── SUBGOAL C
    ├── Task C1
    └── Task C2
```

Example:

```text
Primary Goal:
Launch a production-ready web application.

Subgoal A:
Build application.

Subgoal B:
Verify application.

Subgoal C:
Deploy application.

Subgoal D:
Verify production deployment.
```

---

# 4. Goal Types

Classify objectives as:

```text
PRIMARY
REQUIRED SUBGOAL
OPTIONAL SUBGOAL
CONSTRAINT
MILESTONE
VALIDATION TARGET
```

Example:

```text
PRIMARY:
Launch application.

REQUIRED SUBGOAL:
Authentication works.

OPTIONAL SUBGOAL:
Dark mode.

CONSTRAINT:
Must work on mobile.

MILESTONE:
Production build succeeds.

VALIDATION TARGET:
Login succeeds with valid credentials.
```

---

# 5. Goal State Model

Track every meaningful goal using:

```text
NOT_STARTED
IN_PROGRESS
PARTIALLY_COMPLETE
BLOCKED
AT_RISK
COMPLETED
FAILED
INVALIDATED
DEFERRED
```

Definitions:

```text
NOT_STARTED
No meaningful execution has occurred.

IN_PROGRESS
Execution is actively progressing.

PARTIALLY_COMPLETE
Some required conditions are satisfied,
but the goal is not complete.

BLOCKED
Execution cannot continue because a required condition is missing.

AT_RISK
Execution can continue, but current evidence suggests
the goal may not be achieved as planned.

COMPLETED
All required completion criteria are satisfied.

FAILED
The current approach cannot achieve the goal.

INVALIDATED
The goal or requirement is no longer applicable.

DEFERRED
The goal remains valid but has intentionally been postponed.
```

---

# 6. Goal State Rules

```text
IF no required work has started
→ NOT_STARTED.

IF required work is actively progressing
→ IN_PROGRESS.

IF some but not all required criteria are satisfied
→ PARTIALLY_COMPLETE.

IF a required dependency prevents progress
→ BLOCKED.

IF evidence indicates likely failure without intervention
→ AT_RISK.

IF every required completion criterion is satisfied
→ COMPLETED.

IF the current approach cannot achieve the goal
→ FAILED.

IF the user removes or replaces the requirement
→ INVALIDATED.

IF the user explicitly postpones the goal
→ DEFERRED.
```

---

# 7. Define the Target State

Before tracking progress, define what success looks like.

Bad:

```text
Goal:
Make the app good.
```

Better:

```text
Goal:
Deploy a working task-management application.

Success criteria:
- Required pages exist.
- Authentication works.
- Tasks can be created.
- Tasks can be edited.
- Tasks can be deleted.
- Production build succeeds.
- Deployment succeeds.
- Production functionality is verified.
```

The system cannot accurately track an undefined target.

---

# 8. Completion Criteria

A goal is complete only when its required completion criteria are satisfied.

Use:

```text
Goal:
[goal]

Required criteria:
- Criterion 1
- Criterion 2
- Criterion 3

Optional criteria:
- Criterion A
- Criterion B

Current state:
...

Missing:
...

Status:
...
```

---

# 9. Required vs Optional Completion

Do not allow optional work to redefine completion.

Example:

```text
Required:
- Website works.
- Website is deployed.

Optional:
- Animation.
- Dark mode.
- Advanced analytics.
```

If the website works and is deployed:

```text
Goal = COMPLETED
```

even if optional enhancements remain.

Decision rule:

```text
IF all REQUIRED criteria are satisfied
AND no blocking condition remains
→ goal may be COMPLETED.

IF only OPTIONAL criteria remain
→ do not keep the primary goal IN_PROGRESS.
```

---

# 10. Worked Example — Website Project

## Input

```text
Build and deploy a business website with:
- Home page
- About page
- Contact form
- Mobile support
- Production deployment
```

## Goal Definition

```text
Primary Goal:
Build and deploy the requested business website.

Required criteria:
G1. Home page works.
G2. About page works.
G3. Contact form works.
G4. Mobile layout works.
G5. Production deployment works.
G6. Production verification passes.
```

---

## Initial State

```text
Status:
NOT_STARTED

Progress:
0 required criteria satisfied.

Remaining:
G1–G6
```

---

## After implementation

```text
G1 = COMPLETE
G2 = COMPLETE
G3 = COMPLETE
G4 = COMPLETE
G5 = NOT_STARTED
G6 = NOT_STARTED
```

Overall:

```text
PARTIALLY_COMPLETE
```

Do not claim:

```text
"Website completed."
```

because deployment and final verification remain.

---

## After deployment

```text
G1 = COMPLETE
G2 = COMPLETE
G3 = COMPLETE
G4 = COMPLETE
G5 = COMPLETE
G6 = NOT_STARTED
```

Still:

```text
PARTIALLY_COMPLETE
```

---

## After production verification

```text
G1 = COMPLETE
G2 = COMPLETE
G3 = COMPLETE
G4 = COMPLETE
G5 = COMPLETE
G6 = COMPLETE
```

Now:

```text
COMPLETED
```

---

# 11. Progress Tracking

Progress should reflect meaningful completion, not arbitrary activity.

A useful conceptual model:

```text
Progress =
completed required criteria
/
total required criteria
```

Example:

```text
6 required criteria
4 completed

Progress:
4 / 6
```

However, numerical progress is only a summary.

Never conclude:

```text
"80% progress = 80% certainty of completion."
```

Progress percentage does not measure risk.

---

# 12. Progress Rules

```text
IF a required criterion is fully satisfied
→ count it as completed.

IF a criterion is partially satisfied
→ mark it PARTIAL rather than falsely marking COMPLETE.

IF a task was performed but produced no usable result
→ do not count it as meaningful progress.

IF work must be redone because an assumption was wrong
→ update the state based on the valid result, not effort spent.

IF optional work is completed
→ track it separately from required progress.

IF a completed requirement becomes invalid
→ remove it from the active goal state according to the revised requirements.
```

---

# 13. Goal Drift

Goal drift occurs when execution gradually moves away from the user's actual objective.

Example:

```text
Original:
Create a simple portfolio website.

Execution:
Add animations.
Add analytics.
Add authentication.
Add CMS.
Add payments.
Add AI chatbot.
Add social login.
```

The system may produce a technically impressive result while failing the original objective.

---

# 14. Goal Drift Detection

Check:

```text
Does this action directly support a required goal?

Does it satisfy a stated constraint?

Was it explicitly requested?

Is it necessary for another required task?

Does it introduce scope not requested by the user?
```

If an action cannot be justified:

```text
Mark it OPTIONAL or remove it.
```

---

# 15. Goal Drift Rules

```text
IF a new task does not contribute to the primary goal
→ exclude or mark OPTIONAL.

IF execution introduces significant new scope
→ check whether the user requested it.

IF an optimization changes the original objective
→ stop and reassess.

IF an optional enhancement begins consuming resources
needed for required work
→ prioritize required work.

IF a task was added only because it is interesting
→ do not treat it as required.

IF the current output solves a different problem than requested
→ detect GOAL DRIFT and re-align.
```

---

# 16. Worked Example — Goal Drift

## Original request

```text
Create a simple command-line calculator.
```

### Execution begins

```text
T1. Parse arithmetic expressions.
T2. Implement calculations.
T3. Add error handling.
T4. Test calculations.
```

Then:

```text
T5. Build GUI.
T6. Add themes.
T7. Add user accounts.
T8. Add cloud synchronization.
T9. Add AI explanations.
```

### Problem

The work has drifted from:

```text
simple CLI calculator
```

toward:

```text
full calculator platform.
```

### Correct tracking

```text
T1–T4 = REQUIRED
T5–T9 = OPTIONAL / OUT OF SCOPE
```

Unless the user explicitly changes the goal.

---

# 17. Goal Change

User:

```text
Actually, make it a GUI calculator instead.
```

Do not treat this as a tiny addition.

Determine affected requirements.

```text
Original:
CLI calculator.

New:
GUI calculator.
```

Re-evaluate:

```text
Interface architecture
Input handling
Output handling
Testing
Packaging
Documentation
```

Some completed logic may remain valid.

---

# 18. Goal Change Rules

```text
IF the user explicitly changes the objective
→ update the primary goal.

IF only one requirement changes
→ preserve unaffected work.

IF the new requirement conflicts with an existing requirement
→ identify the conflict.

IF the new goal makes completed work reusable
→ retain reusable work.

IF completed work is no longer relevant
→ mark it INVALIDATED rather than pretending it remains useful.

IF the change substantially alters architecture
→ re-evaluate dependencies and execution plan.
```

---

# 19. Negative Example — False Completion

## Input

```text
Create a production-ready API.
```

System reports:

```text
API code has been written.
Therefore the API is complete.
```

### Why wrong?

Implementation is only one component.

Potential missing requirements:

```text
Testing
Error handling
Security validation
Configuration
Documentation
Production build
Deployment
Production verification
```

Correct:

```text
Implementation = milestone

Goal = not necessarily complete
```

---

# 20. Negative Example — Progress Confused With Success

Suppose:

```text
10 tasks exist.
9 tasks completed.
```

The remaining task:

```text
Deploy application.
```

Incorrect:

```text
"90% complete, therefore essentially finished."
```

If deployment is the final required milestone, the actual goal is not complete.

Correct:

```text
Required work remaining:
Deployment

Status:
PARTIALLY_COMPLETE
```

---

# 21. Negative Example — Optional Work Blocking Completion

Required:

```text
Website deployed.
```

Optional:

```text
Advanced animations.
```

System says:

```text
Website is not complete because animations aren't finished.
```

Wrong.

Correct:

```text
Required criteria satisfied:
YES

Optional criteria remaining:
Animations

Primary goal:
COMPLETED
```

Optional work should be tracked separately.

---

# 22. Partial Completion

Never use only:

```text
DONE
NOT DONE
```

Complex work requires more precise state.

Example:

```text
Authentication:
COMPLETE

Database:
COMPLETE

API:
PARTIAL

Testing:
NOT_STARTED

Deployment:
BLOCKED
```

Overall:

```text
PARTIALLY_COMPLETE + BLOCKED
```

---

# 23. Blocked Goal

A goal is blocked when a required condition cannot currently be satisfied.

Example:

```text
Goal:
Deploy application.

Blocker:
Required deployment credentials are unavailable.
```

Correct state:

```text
BLOCKED
```

Do not claim:

```text
FAILED
```

unless the goal itself cannot be achieved.

---

# 24. Blocked vs Failed

```text
BLOCKED:
The goal may still succeed once a missing condition is resolved.

FAILED:
The current approach cannot achieve the goal.

INVALIDATED:
The goal is no longer applicable.

AT_RISK:
The goal can still succeed but evidence indicates increased risk.
```

Example:

```text
Missing API credentials
→ BLOCKED

Deployment platform rejects required runtime permanently
→ FAILED for that approach

User cancels deployment
→ INVALIDATED

Build is becoming unstable and deadline is approaching
→ AT_RISK
```

---

# 25. Goal Tracking With Dependencies

Track both goal state and dependency state.

Example:

```text
Primary Goal:
Deploy application.

Required:
G1 Build succeeds
G2 Configuration valid
G3 Deployment succeeds
G4 Production verification succeeds

Dependencies:

G1 → G3
G2 → G3
G3 → G4
```

If:

```text
G1 = COMPLETE
G2 = BLOCKED
```

then:

```text
G3 = BLOCKED
G4 = NOT_READY
```

Do not independently report G3 as merely "pending" if a known blocker exists.

---

# 26. Detecting At-Risk Goals

A goal is AT_RISK when it is technically possible but current evidence indicates a meaningful probability of failure.

Examples:

```text
- Critical dependency is unstable.
- Repeated test failures remain unresolved.
- Major requirement is still ambiguous.
- Available resources are insufficient.
- Remaining work significantly exceeds available constraints.
```

Rules:

```text
IF a known risk threatens a required criterion
→ mark AT_RISK.

IF the risk is minor and has no meaningful effect
→ keep current state.

IF the risk becomes an actual blocker
→ change to BLOCKED.

IF the risk is resolved
→ return to the appropriate active state.
```

---

# 27. Goal Tracking During Failure

When a step fails:

```text
1. Do not automatically mark the primary goal FAILED.
2. Identify which subgoal failed.
3. Determine whether the failure blocks downstream work.
4. Determine whether a fallback exists.
5. Update affected states.
6. Recalculate remaining work.
7. Continue or re-plan.
```

Example:

```text
API deployment failed.

API implementation:
COMPLETE

Tests:
COMPLETE

Deployment:
FAILED

Primary goal:
AT_RISK
```

If fallback succeeds:

```text
Deployment:
COMPLETE

Primary goal:
IN_PROGRESS
```

Then continue verification.

---

# 28. Worked Example — Research Task

## Input

```text
Compare three programming languages and recommend one for my project.
```

Goal:

```text
Provide an evidence-based recommendation.
```

Required criteria:

```text
G1. Identify evaluation criteria.
G2. Gather relevant information.
G3. Compare all three languages.
G4. Evaluate against project requirements.
G5. Make recommendation.
G6. Explain trade-offs.
```

Tracking:

```text
G1 COMPLETE
G2 COMPLETE
G3 COMPLETE
G4 COMPLETE
G5 COMPLETE
G6 COMPLETE
```

Primary goal:

```text
COMPLETED
```

If one language's relevant information cannot be verified:

```text
G3 PARTIAL
Primary goal AT_RISK
```

Do not pretend the recommendation is fully evidence-backed.

---

# 29. Goal State Record

For complex objectives use:

```text
Goal ID:
Goal:
Purpose:
Priority:
Status:
Required criteria:
Optional criteria:
Completed:
Partial:
Remaining:
Blocked by:
Risks:
Assumptions:
Latest evidence:
Next required action:
Completion condition:
```

Example:

```text
Goal ID:
G00

Goal:
Deploy production API.

Purpose:
Make the API available to production users.

Priority:
CRITICAL

Status:
AT_RISK

Required criteria:
- Build succeeds.
- Tests pass.
- Production configuration is valid.
- Deployment succeeds.
- Production verification succeeds.

Completed:
- Build.
- Tests.

Partial:
- Configuration.

Remaining:
- Configuration verification.
- Deployment.
- Production verification.

Blocked by:
None.

Risks:
Production environment configuration is uncertain.

Assumptions:
Runtime version is supported.

Latest evidence:
Build and test suite pass.

Next required action:
Verify production runtime compatibility.

Completion condition:
All required criteria pass.
```

---

# 30. Goal Ledger

For large tasks maintain a compact goal ledger:

```text
| Goal | Priority | Status | Completed | Remaining | Blocker |
|------|----------|--------|-----------|-----------|---------|
| G1   | Critical | Done   | 3/3       | 0         | None    |
| G2   | Critical | Active | 2/4       | 2         | None    |
| G3   | High     | Blocked| 1/3       | 2         | G2      |
| G4   | Optional | Deferred| 0/2      | 2         | None    |
```

The ledger is a tracking mechanism, not proof by itself.

Evidence and completion criteria remain authoritative.

---

# 31. Goal Alignment Check

Before starting a new action:

```text
Action:
[planned action]

Ask:

1. Which goal does this support?
2. Which required criterion does it satisfy?
3. Is it required or optional?
4. Does it introduce new scope?
5. Does it threaten another required goal?
6. Is it still relevant under the latest requirements?
```

If no valid goal connection exists:

```text
Do not execute automatically.
```

---

# 32. Edge Case — User Gives Conflicting Goals

Example:

```text
"Make the application extremely feature-rich,
but keep it as simple as possible."
```

Do not silently choose one.

Identify the tension:

```text
Feature richness ↔ simplicity
```

Then prioritize based on:

```text
1. Explicit priority from user.
2. Hard constraints.
3. Primary objective.
4. Feasibility.
5. Optional enhancements.
```

If unresolved:

```text
Ask a targeted clarification when the conflict materially
changes the result.
```

---

# 33. Edge Case — Goal Becomes Impossible

Example:

```text
Goal:
Deploy application.

New information:
Deployment environment does not support the application's
required runtime and cannot be changed.
```

Do not continue pretending deployment is possible.

Update:

```text
Deployment:
FAILED / BLOCKED depending on whether a valid alternative exists.

Primary Goal:
AT_RISK or BLOCKED.
```

Then evaluate alternatives.

---

# 34. Edge Case — User Stops Midway

If the user says:

```text
Stop here.
```

Do not continue execution.

Record:

```text
Current state
Completed work
Remaining work
Unresolved blockers
Next possible action
```

The goal remains incomplete unless the user explicitly considers the partial result sufficient.

---

# 35. Edge Case — User Says "Done"

If the user says:

```text
Okay, done.
```

Do not infer that every technical criterion has been verified.

Distinguish:

```text
USER DECLARATION:
User considers task finished.

SYSTEM VERIFICATION:
Whether objective completion criteria are actually satisfied.
```

If verification is unnecessary in context, accept the user's completion.

If verification is important:

```text
State what remains unverified rather than falsely claiming verification.
```

---

# 36. Edge Case — Requirements Disappear

Suppose:

```text
Original:
A, B, C, D required.
```

User says:

```text
We don't need C anymore.
```

Update:

```text
C = INVALIDATED
```

Then recalculate:

```text
Dependencies
Remaining work
Completion criteria
Progress
Critical path
```

Do not keep C in active required progress.

---

# 37. Goal Tracking Self-Check

Before declaring completion:

```text
[ ] Is the primary goal still the same?
[ ] Have requirements changed?
[ ] Are all REQUIRED criteria satisfied?
[ ] Are any criteria only partially satisfied?
[ ] Are there unresolved blockers?
[ ] Are there unresolved high-impact risks?
[ ] Are any completed claims unsupported?
[ ] Has optional work been incorrectly treated as required?
[ ] Has goal drift occurred?
[ ] Are dependent goals actually complete?
[ ] Does the final state match the requested outcome?
```

If any required condition fails:

```text
Do not declare the primary goal COMPLETED.
```

---

# 38. Production Decision Rules

```text
IF the objective is not clearly defined
→ clarify or establish a safe explicit assumption.

IF the objective is defined but success criteria are missing
→ define measurable completion criteria.

IF a required criterion is satisfied
→ mark it COMPLETE.

IF only part of a criterion is satisfied
→ mark it PARTIAL.

IF a required dependency blocks progress
→ mark the affected goal BLOCKED.

IF evidence indicates likely failure
→ mark AT_RISK.

IF the current approach cannot achieve the goal
→ mark FAILED and evaluate alternatives.

IF the user changes the goal
→ update the goal model and re-plan affected work.

IF a requirement is removed
→ mark it INVALIDATED.

IF optional work remains but all required criteria are complete
→ mark the primary goal COMPLETED.

IF an action does not support the active goal
→ remove it or classify it as OPTIONAL.

IF execution begins solving a different problem
→ detect GOAL DRIFT and re-align.

IF a completed task becomes invalid after a requirement change
→ preserve it only if it remains useful; otherwise mark INVALIDATED.

IF a blocker is resolved
→ recalculate affected goals and resume execution.

IF all required completion criteria are satisfied
AND no blocking condition remains
→ declare the goal COMPLETED.

IF completion cannot be demonstrated
→ do not claim completion.
```

---

# 39. Final Goal-Tracking Protocol

Use this continuous loop:

```text
DEFINE GOAL
    ↓
DEFINE SUCCESS CRITERIA
    ↓
IDENTIFY REQUIRED / OPTIONAL
    ↓
ESTABLISH INITIAL STATE
    ↓
EXECUTE PLANNED WORK
    ↓
UPDATE CURRENT STATE
    ↓
COMPARE CURRENT STATE WITH TARGET STATE
    ↓
CHECK FOR DRIFT
    ↓
CHECK FOR BLOCKERS / RISKS
    ↓
PROCESS REQUIREMENT CHANGES
    ↓
UPDATE REMAINING WORK
    ↓
REPLAN IF NECESSARY
    ↓
VERIFY COMPLETION CRITERIA
    ↓
COMPLETE / CONTINUE / BLOCK / REPLAN
```

The Goal Tracking module is successful when the system can always answer:

> **What are we trying to achieve, what has actually been achieved, what remains, what is blocking progress, whether the current work is still aligned with the goal, and what evidence proves completion?**

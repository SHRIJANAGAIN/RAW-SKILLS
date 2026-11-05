---
name: reasoning-planning-prioritization
version: 1.0.0
description: Production-ready prioritization capability for ranking tasks and decisions by goal impact, urgency, dependencies, risk, constraints, value, and execution cost.
category: reasoning-and-planning
module: prioritization
priority: critical
author: SKT AI LABS
---

# Prioritization

## 1. Purpose

Prioritization determines **what deserves attention first** when multiple tasks, requirements, risks, or decisions compete for limited resources.

Resources may include:

* Time.
* Compute.
* Memory.
* Budget.
* Attention.
* Tool availability.
* Human effort.
* Execution capacity.
* Context/token budget.

The objective is not:

> "Do the easiest task first."

The objective is:

> **Maximize progress toward the primary goal while protecting required constraints and minimizing avoidable risk and wasted effort.**

---

# 2. Core Principle

Not all tasks have equal importance.

Example:

```text id="z1m5e8"
Task A:
Fix critical authentication failure.

Task B:
Improve button animation.

Task C:
Add optional dark mode.

Task D:
Fix production database corruption.
```

A naive planner may process tasks in the order received.

A prioritizing planner evaluates:

```text id="y5n7q2"
Goal impact
+
Urgency
+
Dependency
+
Risk
+
Constraint importance
+
Expected value
+
Cost
```

and determines the appropriate order.

---

# 3. Priority Levels

Use:

```text id="j8s3xk"
P0 — BLOCKER / CRITICAL
P1 — HIGH
P2 — NORMAL
P3 — LOW
P4 — OPTIONAL / DEFERRED
```

### P0 — Critical

Failure prevents the primary goal or creates a severe immediate problem.

Examples:

```text id="1zq8vc"
- Required dependency unavailable.
- Production service down.
- Critical security issue.
- Hard constraint violation.
- Final delivery blocker.
```

### P1 — High

Strongly affects the primary goal but does not immediately block everything.

```text id="q0m2kf"
- Important feature.
- Major bug.
- Critical-path task.
- High-impact validation.
```

### P2 — Normal

Useful required work that does not currently block critical progress.

### P3 — Low

Useful but non-urgent improvements.

### P4 — Optional

Nice-to-have work that can safely be deferred.

---

# 4. Priority Decision Factors

Evaluate tasks using:

```text id="5z0m4p"
1. Goal impact
2. Requirement criticality
3. Dependency importance
4. Urgency
5. Risk reduction
6. Expected value
7. Cost
8. Reversibility
9. Resource availability
10. Opportunity cost
```

Do not rely on one factor alone.

---

# 5. Primary Priority Rule

```text id="m3j9s7"
IF a task is required for the primary goal
AND blocks other required tasks
→ prioritize highly.

IF a task is optional
AND does not affect required work
→ defer it.

IF a task reduces a major risk cheaply
→ consider doing it early.

IF a task is urgent but irrelevant to the primary goal
→ do not automatically prioritize it.

IF a task is both high-impact and high-urgency
→ prioritize immediately.
```

---

# 6. Goal Impact

Ask:

> "How much does completing this task move us toward the actual goal?"

Example:

```text id="0c5q2d"
Goal:
Launch website.

Task A:
Fix broken deployment.

Impact:
Very high.

Task B:
Change heading font.

Impact:
Low.

Task C:
Add requested payment system.

Impact:
High.

Task D:
Add optional animation.

Impact:
Low.
```

Priority should reflect these differences.

---

# 7. Dependency Priority

A task may be important because many other tasks depend on it.

Example:

```text id="s3w7k9"
T1 — Define database schema
   ↓
T2 — Implement API
   ↓
T3 — Integration
   ↓
T4 — Testing
```

T1 may have high priority even if it does not directly produce visible user functionality because it unlocks the critical path.

Rule:

```text id="x7k2m1"
IF completing Task A unlocks multiple required downstream tasks
→ increase its priority.
```

---

# 8. Bottleneck Priority

A bottleneck is a resource, decision, dependency, or task that limits progress.

Example:

```text id="3v4z8q"
Five developers are ready,
but the required API specification is missing.
```

The API specification becomes the bottleneck.

Correct priority:

```text id="p6j1x9"
Resolve API specification
```

rather than having everyone work on unrelated tasks.

---

# 9. Bottleneck Rules

```text id="w3m8c0"
IF many tasks are waiting on one condition
→ prioritize resolving that condition.

IF a bottleneck cannot currently be resolved
→ find independent work that can proceed.

IF a bottleneck affects only optional work
→ defer it.

IF resolving the bottleneck requires a decision
→ prioritize the decision.
```

---

# 10. Risk-Based Prioritization

High-risk assumptions should sometimes be tested before low-risk implementation.

Example:

```text id="r9x2m6"
Assumption:
Chosen API supports required functionality.

Cost to test:
5 minutes.

Cost of discovering failure after implementation:
5 hours.
```

Prioritize the test.

Rule:

```text id="f2j8q4"
IF a cheap validation can prevent expensive rework
→ prioritize the validation.
```

---

# 11. Worked Example — Software Project

## Input

```text id="x6h3q1"
Build a mobile application with:
- Login
- User profiles
- Payments
- Notifications
- Dark mode
- Analytics
```

Tasks:

```text id="q8n1v4"
T1. Authentication
T2. Profile system
T3. Payment integration
T4. Notifications
T5. Dark mode
T6. Analytics
T7. Production testing
```

Potential prioritization:

```text id="r3m7k5"
P1:
T1 Authentication

P1:
T3 Payment integration

P1:
T7 Production testing

P2:
T2 Profile system

P2:
T4 Notifications

P3:
T6 Analytics

P4:
T5 Dark mode
```

Actual priority depends on the user's stated requirements and dependencies.

The important principle is that optional polish does not outrank required core functionality.

---

# 12. Negative Example — "First Come, First Served"

User requests:

```text id="v4p8y1"
Fix production crash.
Add dark mode.
Improve icon spacing.
Update documentation.
```

Incorrect:

```text id="n2m7x5"
1. Icon spacing
2. Dark mode
3. Documentation
4. Production crash
```

Why wrong?

The ordering follows request order or convenience rather than goal impact.

Correct:

```text id="s5k9d2"
1. Fix production crash.
2. Verify production recovery.
3. Update documentation if required.
4. Dark mode.
5. Icon spacing.
```

---

# 13. Urgency vs Importance

Urgency and importance are different.

```text id="c4x7m2"
URGENT:
Needs attention soon.

IMPORTANT:
Meaningfully affects the goal.
```

Examples:

```text id="b6r1y8"
Urgent + Important:
Production outage.

Important + Not urgent:
Long-term architecture decision.

Urgent + Less important:
Minor deadline for optional documentation.

Not urgent + Not important:
Cosmetic polish.
```

Rule:

```text id="d8q5n3"
Do not automatically treat urgency as importance.
```

---

# 14. Priority Matrix

Use this conceptual matrix:

```text id="k4m8z2"
                  HIGH IMPACT
                       │
          P1           │           P0
                       │
LOW URGENCY ───────────┼────────── HIGH URGENCY
                       │
          P3           │           P2
                       │
                  LOW IMPACT
```

Interpretation:

```text id="z8v1p6"
High impact + high urgency
→ P0

High impact + low urgency
→ P1

Low impact + high urgency
→ P2

Low impact + low urgency
→ P3/P4
```

This is a heuristic, not an absolute rule.

Dependencies and hard constraints can override the matrix.

---

# 15. Hard Constraints and Priority

Constraint compliance outranks convenience.

Example:

```text id="r5j2x7"
Task A:
Optional performance optimization.

Task B:
Fix hard-format violation.
```

Prioritize:

```text id="a1m9q3"
Task B
```

because violating a hard constraint can invalidate the result.

---

# 16. Priority Rules for Constraints

```text id="h6p3w0"
IF a task is required to satisfy a hard constraint
→ prioritize it over optional improvements.

IF delaying a task causes hard-constraint violation
→ increase its priority.

IF an optional task conflicts with required constraint compliance
→ defer the optional task.
```

---

# 17. Resource-Aware Prioritization

When resources are limited:

```text id="x2c9v5"
Available resources:
Limited time
Limited compute
Limited budget
```

Prioritize:

```text id="k7m4p1"
High-value required work
        ↓
Critical-path work
        ↓
Risk-reducing validation
        ↓
Supporting work
        ↓
Optional improvements
```

Do not distribute resources equally if task importance is unequal.

---

# 18. Worked Example — Limited Time

Deadline:

```text id="y8n3q6"
2 hours remaining.
```

Remaining tasks:

```text id="b5r2m9"
A. Fix critical bug — 30 min
B. Add requested feature — 45 min
C. Improve animations — 30 min
D. Write optional documentation — 20 min
E. Run final verification — 15 min
```

Required:

```text id="t4v8c2"
A
B
E
```

Optional:

```text id="m3z6k1"
C
D
```

Minimum required time:

```text id="s9w2d7"
30 + 45 + 15 = 90 minutes
```

Remaining:

```text id="f1q7x4"
30 minutes
```

Use remaining time for the highest-value optional work only after required work is protected.

---

# 19. Negative Example — Equal Resource Allocation

Incorrect:

```text id="n5q8w3"
Spend 25% of time on:
- Authentication
- Documentation
- Animations
- Testing
```

Why wrong?

Authentication and testing may be much more important than animations.

Correct:

```text id="j2m6p9"
Allocate resources according to:
- Goal importance
- Dependencies
- Risk
- Deadline
- Required status
```

---

# 20. Expected Value

When two tasks have similar importance, compare expected value.

Conceptually:

```text id="w7p3k8"
Expected Value =
Impact × Probability of useful outcome
```

For planning, also consider cost:

```text id="d6n1q4"
Priority Value ≈
Expected Impact
+
Risk Reduction
+
Dependency Unlock
−
Execution Cost
```

This is a reasoning heuristic, not a rigid mathematical requirement.

---

# 21. Example — Choosing Between Two Tasks

```text id="r4k8m2"
Task A:
Improve performance by 5%.
Impact: Medium
Cost: 4 hours
Risk reduction: Low

Task B:
Verify whether deployment environment supports runtime.
Impact: High
Cost: 10 minutes
Risk reduction: High
```

Prefer:

```text id="q3v7n5"
Task B
```

because it can prevent major downstream failure at very low cost.

---

# 22. Reprioritization

Priority is dynamic.

A task's priority can change when:

* A requirement changes.
* A dependency fails.
* A deadline changes.
* New evidence appears.
* A blocker is discovered.
* Risk increases.
* Resources become unavailable.
* Another task becomes more valuable.

Rule:

```text id="h2z6m9"
IF new information materially changes expected impact,
risk, urgency, or dependency
→ recalculate priority.
```

---

# 23. Worked Example — Priority Change

Initial:

```text id="p4m8x1"
T1. Build dashboard — P1
T2. Fix minor UI bug — P3
T3. Add optional export — P4
```

New information:

```text id="c8y2v6"
Users cannot log in because of a newly discovered authentication bug.
```

New priority:

```text id="q5n9r3"
Authentication bug → P0
Dashboard → P1
UI bug → P3
Export → P4
```

Do not remain committed to the original priority ordering.

---

# 24. Negative Example — Static Priority

Incorrect:

```text id="m7x4q2"
"We already decided the task order,
so we must follow it regardless of new information."
```

Why wrong?

Planning is adaptive.

Correct:

```text id="k3p8n1"
New evidence
→ reassess priority
→ preserve valid completed work
→ replan remaining work.
```

---

# 25. Parallelization and Priority

Parallel tasks can have different priorities.

Example:

```text id="b1v6m9"
T1 Critical API fix
T2 High-priority testing
T3 Optional documentation
T4 Optional UI polish
```

If resources allow:

```text id="z5q2r8"
Worker A → T1
Worker B → T2
```

Do not allocate equal effort to T3 and T4 merely because they are available.

---

# 26. Priority and Dependencies

A low-visibility task can have high priority if it unlocks critical work.

Example:

```text id="u4m7c2"
T1. Obtain required configuration.
T2. Build authentication.
T3. Build profile system.
T4. Build UI polish.
```

If T2 and T3 both depend on T1:

```text id="n8x3p6"
T1 priority increases.
```

Because it is a bottleneck.

---

# 27. Negative Example — Visible Work Bias

Incorrect:

```text id="e7r2m5"
"The UI is what users see,
so UI polish should be prioritized."
```

Why wrong?

Visibility does not equal importance.

A hidden database failure can be much more important.

Correct:

```text id="w3k9q1"
Prioritize based on actual goal impact,
not visual prominence.
```

---

# 28. Priority Under Uncertainty

When information is incomplete:

```text id="r6v2m8"
Do not confidently rank tasks whose importance depends
on unknown information.
```

Instead:

```text id="p9x4n1"
Identify:
- What is known.
- What is uncertain.
- Which uncertainty affects priority.
- Whether the uncertainty is cheap to resolve.
```

If a 2-minute clarification determines whether a task is critical:

```text id="k5m8q3"
Prioritize the clarification.
```

---

# 29. Edge Case — Everything Is "High Priority"

If every task is marked HIGH:

```text id="s3v7p2"
The priority system has failed to discriminate.
```

Resolve using:

```text id="f8n2m6"
1. Hard constraints.
2. Goal blockers.
3. Dependencies.
4. Deadline.
5. Risk.
6. Expected impact.
7. Cost.
```

Force meaningful ordering where possible.

---

# 30. Edge Case — No Deadline

If no deadline exists:

```text id="y4q8m1"
Do not invent urgency.
```

Prioritize using:

```text id="c6p3v9"
Goal impact
Dependency
Risk
Expected value
Cost
```

---

# 31. Edge Case — Deadline Is Impossible

Example:

```text id="h7m2x5"
Required work:
8 hours.

Available:
2 hours.
```

Do not pretend everything can be completed.

Correct:

```text id="j1q6r8"
1. Identify critical requirements.
2. Remove optional work.
3. Find faster valid approaches.
4. Determine minimum viable scope.
5. Identify remaining conflict.
6. Communicate the trade-off.
```

---

# 32. Priority Record

For complex tasks:

```text id="p4z8m2"
Task ID:
Task:
Priority:
Reason:
Goal impact:
Urgency:
Dependency impact:
Risk reduction:
Cost:
Required/Optional:
Blocker:
Current status:
Priority confidence:
```

Example:

```text id="x7n3q9"
Task ID:
T08

Task:
Verify production database connectivity.

Priority:
P0

Reason:
Blocks production verification.

Goal impact:
Critical.

Urgency:
High.

Dependency impact:
Blocks T09 and T10.

Risk reduction:
High.

Cost:
Low.

Required/Optional:
Required.

Blocker:
None.

Current status:
READY.

Priority confidence:
High.
```

---

# 33. Priority Confidence

Priority itself may be uncertain.

Use:

```text id="q6m1v8"
HIGH
MEDIUM
LOW
```

Example:

```text id="w8r4p2"
Task:
Optimize caching.

Priority:
P2

Confidence:
LOW

Reason:
Importance depends on actual production performance data.
```

This prevents false certainty.

---

# 34. Priority Self-Check

Before execution:

```text id="m2x7k5"
[ ] Does the ordering reflect the primary goal?
[ ] Are hard constraints protected?
[ ] Are blockers prioritized?
[ ] Are critical dependencies prioritized?
[ ] Are high-value validations performed early?
[ ] Are optional tasks deferred appropriately?
[ ] Are resource limits considered?
[ ] Is deadline pressure represented correctly?
[ ] Is urgency being confused with importance?
[ ] Is the priority based on evidence rather than convenience?
[ ] Are uncertain priorities marked appropriately?
[ ] Does every P0/P1 task have a clear reason?
```

---

# 35. Production Decision Rules

```text id="v5k8q2"
IF a task blocks the primary goal
→ prioritize it highly.

IF a task satisfies a hard constraint
→ prioritize it over conflicting optional work.

IF a task unlocks many required downstream tasks
→ increase its priority.

IF a cheap test can prevent expensive rework
→ prioritize the test.

IF a task has high goal impact and high urgency
→ treat it as critical.

IF a task is optional and does not affect required work
→ defer it.

IF a task is urgent but low-impact
→ evaluate it rather than automatically prioritizing it.

IF a task is high-impact but not urgent
→ schedule it before low-impact work.

IF all tasks are marked equally high
→ re-evaluate using dependencies, impact, risk, and urgency.

IF resources become constrained
→ protect critical-path and required work first.

IF new evidence changes risk, impact, urgency, or dependencies
→ recalculate priority.

IF a bottleneck is preventing many tasks from progressing
→ prioritize resolving the bottleneck.

IF priority depends on missing information
→ resolve the highest-value uncertainty.

IF a deadline cannot accommodate all required work
→ remove optional work first.

IF required work still exceeds available resources
→ identify the constraint conflict rather than pretending all work is feasible.

IF a task has no meaningful connection to the primary goal
→ remove it or mark it OPTIONAL.

IF the priority of a task cannot be justified
→ reconsider its priority.
```

---

# 36. Final Prioritization Protocol

```text id="c7m4x9"
IDENTIFY GOAL
    ↓
LIST ACTIVE TASKS
    ↓
CLASSIFY REQUIRED / OPTIONAL
    ↓
IDENTIFY BLOCKERS
    ↓
IDENTIFY DEPENDENCIES
    ↓
ASSESS GOAL IMPACT
    ↓
ASSESS URGENCY
    ↓
ASSESS RISK
    ↓
ASSESS RESOURCE COST
    ↓
IDENTIFY BOTTLENECKS
    ↓
RANK TASKS
    ↓
EXECUTE HIGHEST-VALUE VALID WORK
    ↓
MONITOR NEW INFORMATION
    ↓
REPRIORITIZE WHEN CONDITIONS CHANGE
    ↓
VERIFY GOAL PROGRESS
```

The Prioritization module is successful when the system can answer:

> **Why is this task being done now instead of later, what important outcome does it protect or unlock, what happens if it is delayed, and is there a higher-value task that should come first?**

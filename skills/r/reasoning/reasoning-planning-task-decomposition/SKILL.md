---
name: reasoning-planning-task-decomposition
version: 1.0.0
description: Production-ready task decomposition capability for converting complex goals into atomic, dependency-aware, verifiable subtasks.
category: reasoning-and-planning
module: task-decomposition
priority: critical
author: SKT AI LABS
---

# Task Decomposition

## 1. Purpose

Task Decomposition converts a complex user goal into a structured set of smaller, executable tasks.

The purpose is **not** to produce a long list of steps.

The purpose is to determine:

- What must actually be done.
- What can be broken into independent units.
- Which tasks depend on other tasks.
- Which tasks are mandatory.
- Which tasks are optional.
- Which tasks can happen in parallel.
- What proves each task is complete.
- What information is missing before execution can safely begin.

A good decomposition should make execution easier, verification possible, and failure recovery straightforward.

---

# 2. Core Principle

> Decompose by **work required to achieve the goal**, not merely by the order in which actions appear in the user's sentence.

Bad decomposition:

```text
1. Start project
2. Do coding
3. Test
4. Finish
```

Good decomposition:

```text
Goal:
Build and deploy a web application.

Required tasks:
T1. Determine functional requirements
T2. Determine technical constraints
T3. Design application architecture
T4. Initialize project
T5. Implement frontend
T6. Implement backend
T7. Configure database
T8. Integrate frontend/backend
T9. Run automated tests
T10. Run production build
T11. Deploy application
T12. Verify production deployment

Dependencies:
T3 depends on T1 + T2
T4 depends on T3
T5 depends on T4
T6 depends on T4
T7 can begin after T3
T8 depends on T5 + T6 + T7
T9 depends on T8
T10 depends on T9
T11 depends on T10
T12 depends on T11
```

The second decomposition exposes the actual work structure.

---

# 3. Atomic Task Definition

A task is sufficiently atomic when:

1. It has one primary purpose.
2. Its expected result can be clearly identified.
3. Its completion can be independently verified.
4. It does not contain several unrelated outcomes.
5. Another task can depend on its result without ambiguity.

## Bad

```text
Build the backend, database, authentication,
API and deploy everything.
```

This is too broad.

## Better

```text
T1. Define backend requirements.
T2. Design API structure.
T3. Configure database.
T4. Implement authentication.
T5. Implement API endpoints.
T6. Integrate database with API.
T7. Run backend tests.
T8. Deploy backend.
```

---

# 4. When to Split a Task Further

Split a task if **any** of these conditions are true:

```text
IF a task produces multiple independent deliverables
→ split it.

IF different parts have different dependencies
→ split it.

IF different parts can execute independently
→ split it.

IF one part can fail while another succeeds
→ split it.

IF completion cannot be verified with one clear criterion
→ split it.

IF different tools/resources are required for different parts
→ consider splitting it.

IF the task contains "and" connecting unrelated actions
→ inspect whether decomposition is required.
```

Do NOT split unnecessarily.

```text
IF a task is already independently executable,
has one clear outcome,
and has one clear completion criterion
→ keep it atomic.
```

---

# 5. Required vs Optional Work

Every decomposition should distinguish between work that is necessary for goal completion and work that merely improves the result.

Use:

```text
REQUIRED
OPTIONAL
```

## Example

User goal:

> Build a simple portfolio website.

### Required

```text
T1. Determine required pages.
T2. Create website structure.
T3. Implement portfolio content.
T4. Implement responsive layout.
T5. Test navigation.
T6. Verify mobile rendering.
```

### Optional

```text
O1. Add animations.
O2. Add dark mode.
O3. Add analytics.
O4. Add advanced SEO.
O5. Add contact-form backend.
```

### Decision rule

```text
IF removing a task prevents the stated goal from being achieved
→ REQUIRED.

IF removing a task still allows the stated goal to be achieved
→ OPTIONAL.

IF the user explicitly requests an optional feature
→ it becomes REQUIRED for that request.

IF optional work threatens time, reliability, safety,
or core functionality
→ defer it unless the user prioritizes it.
```

---

# 6. Dependency Identification

A dependency exists when Task B cannot be correctly completed until Task A produces required information, output, resource, or state.

Represent dependencies explicitly.

```text
T1 → T2
```

means:

```text
T2 depends on T1.
```

For multiple dependencies:

```text
T1 + T2 → T3
```

means:

```text
T3 requires both T1 and T2.
```

## Dependency Types

### Information dependency

```text
Requirements → Architecture
```

Architecture requires requirements.

### Resource dependency

```text
Environment setup → Application execution
```

### Technical dependency

```text
Database schema → Database integration
```

### Decision dependency

```text
Technology selection → Implementation
```

### Verification dependency

```text
Implementation → Testing
```

---

# 7. Dependency Decision Rules

```text
IF Task B requires the output of Task A
→ A must precede B.

IF Task B requires only part of A's output
→ identify the specific required output.

IF A and B require no shared state or output
→ consider parallel execution.

IF A and B modify the same resource
→ do not assume they are parallel-safe.

IF dependency is uncertain
→ mark it as an assumption and verify before execution.

IF a dependency creates a cycle
→ stop and resolve the circular dependency before execution.
```

---

# 8. Parallelization

Tasks should be marked as parallelizable only when they are genuinely independent.

## Example

Goal:

> Create a documentation website.

After project initialization:

```text
             ┌── T3: Write documentation
T2 Setup ────┼── T4: Create visual assets
             └── T5: Prepare test cases
```

These can potentially happen in parallel.

Then:

```text
T3 + T4 + T5 → T6: Integrate and verify
```

## Parallelization Rules

```text
IF Task A does not require Task B's output
AND
Task B does not require Task A's output
AND
they do not create conflicting modifications
→ they may be parallelizable.

IF two tasks modify the same file/resource/state
→ treat them as sequential unless safe concurrency is established.

IF parallel execution increases coordination complexity more
than it saves
→ keep the tasks sequential.

IF a task has uncertain prerequisites
→ resolve the uncertainty before parallelizing it.
```

---

# 9. Completion Criteria

Every meaningful task must have an observable completion criterion.

Do not use:

```text
T1. Work on authentication.
```

Use:

```text
T1. Implement authentication.

Completion criteria:
- Login endpoint exists.
- Valid credentials are accepted.
- Invalid credentials are rejected.
- Authentication state is returned correctly.
- Automated tests pass.
```

Completion criteria answer:

> "How do we know this task is actually finished?"

---

# 10. Completion Criterion Rules

```text
IF the task produces a file
→ verify the file exists and contains the required content.

IF the task produces code
→ verify implementation + relevant tests/build.

IF the task produces a decision
→ verify the selected option and rationale are recorded.

IF the task produces data
→ verify required fields, validity, and expected structure.

IF the task produces a deployment
→ verify the deployed service is reachable and functional.

IF the task produces documentation
→ verify required sections and examples exist.

IF the task is research
→ verify required questions have evidence-backed answers.

IF completion cannot be objectively determined
→ define the criterion before execution.
```

---

# 11. Worked Example — Complex Software Request

## Input

```text
Build me a production-ready REST API for a task-management
application with authentication, PostgreSQL, tests, documentation,
Docker support, and deployment.
```

## Step 1 — Extract the Goal

Primary goal:

```text
Create and deploy a production-ready task-management REST API.
```

Required capabilities:

```text
- REST API
- Authentication
- PostgreSQL
- Automated tests
- Documentation
- Docker support
- Deployment
```

---

## Step 2 — Decompose

```text
T1. Define API requirements.
T2. Define authentication requirements.
T3. Define task-management data model.
T4. Design API endpoints.
T5. Select/configure application architecture.
T6. Initialize project.
T7. Configure PostgreSQL.
T8. Implement database models.
T9. Implement authentication.
T10. Implement task-management endpoints.
T11. Add validation and error handling.
T12. Add automated tests.
T13. Add API documentation.
T14. Create Docker configuration.
T15. Run integration verification.
T16. Prepare production configuration.
T17. Deploy API.
T18. Verify production deployment.
```

---

## Step 3 — Identify Dependencies

```text
T1 → T3
T1 → T4
T2 → T9
T3 → T8
T4 → T10
T5 → T6
T6 → T7
T6 → T8
T6 → T9
T8 → T10
T9 → T10
T10 → T11
T10 → T12
T11 → T12
T10 → T13
T6 → T14
T12 + T13 + T14 → T15
T15 → T16
T16 → T17
T17 → T18
```

---

## Step 4 — Identify Parallel Work

After T6:

```text
T7  Configure PostgreSQL
T8  Prepare database models
T9  Implement authentication
T13 Prepare documentation
T14 Prepare Docker configuration
```

Some of these may run in parallel, subject to the project's actual dependencies.

---

## Step 5 — Required vs Optional

### Required

```text
T1–T18
```

because every requested capability contributes to the stated goal.

### Optional enhancements

```text
O1. Rate limiting
O2. Redis caching
O3. Advanced observability
O4. CI/CD pipeline
O5. OpenAPI client generation
```

These should not silently become part of the core implementation.

---

## Step 6 — Completion Criteria

Example:

```text
T9 — Authentication

Complete when:
- Authentication mechanism is implemented.
- Valid credentials work.
- Invalid credentials fail safely.
- Protected endpoints reject unauthenticated requests.
- Relevant tests pass.
```

```text
T17 — Deployment

Complete when:
- Production service is deployed.
- Application starts successfully.
- Database connection works.
- Required endpoints respond.
- Production configuration is active.
```

---

# 12. Worked Example — Non-Technical Request

## Input

```text
Help me organize a school science exhibition project.
```

### Goal

```text
Prepare and present a complete science exhibition project.
```

### Decomposition

```text
T1. Determine exhibition requirements.
T2. Select project topic.
T3. Define project objective.
T4. Research required information.
T5. Design experiment/model.
T6. Identify required materials.
T7. Build prototype/model.
T8. Test prototype.
T9. Fix discovered problems.
T10. Prepare explanation.
T11. Prepare presentation materials.
T12. Conduct final verification.
```

### Dependencies

```text
T1 → T2
T2 → T3
T3 → T4
T4 → T5
T5 → T6
T5 → T7
T7 → T8
T8 → T9
T9 → T12
T10 → T12
T11 → T12
```

### Parallelizable

After the project design is sufficiently defined:

```text
T10 — Prepare explanation
T11 — Prepare presentation materials
```

may proceed alongside prototype work.

### Completion

```text
Project is complete when:

- Required exhibition criteria are satisfied.
- Prototype/model works as intended.
- Explanation is prepared.
- Presentation material is ready.
- Final requirements have been checked.
```

---

# 13. Negative Example — Looks Reasonable but Is Wrong

## Input

```text
Create and launch a website for my business.
```

### Incorrect decomposition

```text
1. Choose colors.
2. Build homepage.
3. Add animations.
4. Add logo.
5. Deploy website.
6. Add contact form.
7. Test website.
8. Improve SEO.
```

### Why it is wrong

The decomposition starts implementation before identifying fundamental requirements.

Problems:

```text
- Business requirements are unknown.
- Required pages are unknown.
- Target audience is unknown.
- Content requirements are unknown.
- Technical requirements are unknown.
- Contact form is treated as an afterthought.
- Deployment occurs before meaningful verification.
- SEO is mixed into the core plan without prioritization.
```

The plan is activity-oriented rather than goal-oriented.

---

# 14. Corrected Version

```text
T1. Identify business and website requirements.
T2. Identify required pages and content.
T3. Identify functional requirements.
T4. Define technical constraints.
T5. Design site structure.
T6. Create visual direction.
T7. Implement required pages.
T8. Implement required functionality.
T9. Test functionality and navigation.
T10. Verify responsive behavior.
T11. Prepare production build.
T12. Deploy.
T13. Verify production website.
T14. Perform optional SEO enhancements.
```

The corrected version establishes requirements before implementation and verification before completion.

---

# 15. Negative Example — False Parallelization

## Incorrect

```text
T1. Design database schema
T2. Implement database queries
```

Marked:

```text
T1 || T2
```

### Why this can be wrong

The query implementation may depend on the schema.

If the schema is not established, T2 may be based on assumptions and require rework.

Correct:

```text
T1 → T2
```

Unless the query contract/schema has already been independently defined.

---

# 16. Negative Example — Over-Decomposition

## Input

```text
Write a short project description.
```

### Bad

```text
T1. Open editor.
T2. Create document.
T3. Move cursor.
T4. Type first sentence.
T5. Type second sentence.
T6. Save document.
T7. Close editor.
```

### Why wrong

These are mechanical actions rather than meaningful work units.

Correct:

```text
T1. Draft project description.
T2. Verify it satisfies the requested purpose and length.
```

The decomposition should expose meaningful dependencies, not every physical interaction.

---

# 17. Ambiguous Request

## Input

```text
Make my app better.
```

Do not immediately invent a large decomposition.

First determine whether the missing information is blocking.

```text
Missing:
- What aspect should improve?
- Performance?
- UI?
- Reliability?
- Features?
- Security?
```

### Decision

```text
IF "better" cannot be operationalized from available context
→ ask a targeted clarification.

IF previous context clearly defines the improvement target
→ proceed using that context.

IF a safe assumption can be made without materially changing the result
→ state the assumption and proceed.
```

Example clarification:

```text
What should I prioritize: performance, UI/UX,
new features, reliability, or another specific area?
```

---

# 18. Missing Information

Use three categories:

### Blocking

Information required to perform the task correctly.

```text
Required credentials
Required target environment
Required file
Required output format
Required specification
```

### Important but non-blocking

Information that improves the result but does not prevent progress.

```text
Preferred visual style
Optional naming preference
Preferred implementation detail
```

### Irrelevant

Information that does not materially affect execution.

Do not ask for it.

---

# 19. Impossible Constraints

Example:

```text
Build a complete application in 10 minutes,
with zero dependencies, zero bugs, and unlimited features.
```

Do not blindly decompose impossible requirements.

Use:

```text
1. Identify conflicting constraints.
2. Determine which constraints are hard.
3. Determine which can be relaxed.
4. Explain the trade-off.
5. Propose the smallest viable alternative.
```

Example:

```text
Hard:
- Must produce a working prototype.

Flexible:
- Feature count.
- Advanced polish.
- Full production hardening.
```

Then decompose around the viable target.

---

# 20. Changing Requirements During Execution

Example:

```text
Original:
Build a web application.

Later:
It must also work offline.
```

Do not append "make offline" blindly.

Instead:

```text
1. Identify affected tasks.
2. Determine new dependencies.
3. Determine whether architecture changes.
4. Mark completed tasks that remain valid.
5. Invalidate affected assumptions.
6. Insert new required tasks.
7. Recalculate dependencies.
8. Continue from the earliest affected point.
```

Example:

```text
Original:

T5 → T6 → T7

New requirement affects T5.

Revised:

T5a. Re-evaluate architecture for offline support.
T5b. Update architecture.
T6. Implement application.
T7. Test online behavior.
T8. Test offline behavior.
```

Do not restart the entire project unless necessary.

---

# 21. Dependency Graph Template

Use this conceptual structure:

```text
GOAL
  ↓
REQUIREMENTS
  ↓
CORE TASKS
  ↓
DEPENDENCIES
  ↓
EXECUTION GROUPS
  ↓
VERIFICATION
  ↓
COMPLETION
```

For complex tasks:

```text
T1 ──┐
     ├──→ T4 ──→ T6 ──→ T8
T2 ──┘

T3 ─────────────→ T5 ──┘

T7 ────────────────────→ T8
```

---

# 22. Standard Task Record

For complex planning, represent each task conceptually as:

```text
Task ID:
Task:
Purpose:
Type: REQUIRED | OPTIONAL
Dependencies:
Inputs:
Expected output:
Parallelizable: YES | NO | CONDITIONAL
Completion criteria:
Risk:
Status:
```

Example:

```text
Task ID: T04

Task:
Design API endpoints.

Purpose:
Define the interface required by frontend and clients.

Type:
REQUIRED

Dependencies:
T01, T02

Inputs:
Requirements and data model.

Expected output:
Documented endpoint contract.

Parallelizable:
CONDITIONAL

Completion criteria:
- All required operations are represented.
- Inputs are defined.
- Outputs are defined.
- Error cases are defined.
- No required feature lacks an endpoint.
  
Risk:
Incomplete requirements may require revision.

Status:
NOT_STARTED
```

---

# 23. Task Status Model

Use explicit states:

```text
NOT_STARTED
BLOCKED
READY
IN_PROGRESS
COMPLETED
FAILED
INVALIDATED
DEFERRED
```

Rules:

```text
IF dependencies are incomplete
→ NOT READY.

IF a required dependency fails
→ dependent task becomes BLOCKED.

IF task is actively being executed
→ IN_PROGRESS.

IF completion criteria are satisfied
→ COMPLETED.

IF assumptions become invalid
→ INVALIDATED.

IF task cannot currently proceed but remains valid
→ BLOCKED.

IF optional work is intentionally postponed
→ DEFERRED.
```

---

# 24. Self-Check Before Execution

Before executing a decomposition, verify:

```text
[ ] Is the actual goal clear?
[ ] Have complex tasks been meaningfully decomposed?
[ ] Are required tasks separated from optional tasks?
[ ] Are dependencies explicit?
[ ] Are false dependencies avoided?
[ ] Have parallelizable tasks been identified?
[ ] Are blocking unknowns identified?
[ ] Does every important task have completion criteria?
[ ] Is there unnecessary over-decomposition?
[ ] Can the plan actually produce the requested outcome?
```

If any critical answer is "no":

```text
Revise decomposition before execution.
```

---

# 25. Final Decision Rules

```text
IF the goal is complex
→ decompose before execution.

IF a task has multiple independent outcomes
→ split it.

IF B requires A's output
→ A precedes B.

IF A and B are independent and conflict-free
→ consider parallel execution.

IF removing a task prevents the requested outcome
→ mark REQUIRED.

IF removing a task does not prevent the requested outcome
→ mark OPTIONAL.

IF a task has no clear completion condition
→ define one before execution.

IF required information is missing and blocks correctness
→ ask for it.

IF missing information does not block safe progress
→ state an assumption and continue.

IF a task is too granular to represent meaningful work
→ merge it.

IF requirements change
→ revise affected dependencies rather than blindly restarting.

IF a task fails
→ identify which dependent tasks are affected before continuing.

IF a plan contains circular dependencies
→ stop and resolve the cycle.

IF the decomposition cannot explain how the goal will be achieved
→ the decomposition is incomplete.
```

---

# 26. Production Pattern

For any complex request, internally transform:

```text
USER GOAL
    ↓
Extract desired outcome
    ↓
Identify requirements
    ↓
Identify constraints
    ↓
Identify missing blocking information
    ↓
Break goal into meaningful atomic tasks
    ↓
Separate REQUIRED / OPTIONAL
    ↓
Identify dependencies
    ↓
Identify parallelizable work
    ↓
Define completion criteria
    ↓
Validate decomposition
    ↓
Execute
```

The decomposition is considered **production-ready** only when another competent executor could take the task graph and understand:

1. What must be done.
2. Why it must be done.
3. What must happen first.
4. What can happen simultaneously.
5. What can be skipped.
6. What each task must produce.
7. How each task's completion will be verified.
8. What to do when information, dependencies, or requirements change.
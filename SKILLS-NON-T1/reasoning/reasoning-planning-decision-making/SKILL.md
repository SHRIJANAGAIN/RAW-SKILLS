---
name: reasoning-planning-decision-making
version: 1.0.0
description: Production-ready decision-making capability for evaluating alternatives, handling uncertainty, comparing trade-offs, selecting actions, and revising decisions when new evidence appears.
category: reasoning-and-planning
module: decision-making
priority: critical
author: SKT AI LABS
---

# Decision Making

## 1. Purpose

Decision Making converts available information and constraints into a justified choice.

A planner frequently encounters situations such as:

```text
Option A vs Option B
Tool A vs Tool B
Fix vs Rewrite
Proceed vs Clarify
Optimize vs Simplify
Continue vs Replan
Ship now vs Test further
```

The purpose is not to choose the option that merely looks best.

The purpose is to select the option that best satisfies:

```text
Goal
+
Constraints
+
Evidence
+
Risk tolerance
+
Resources
+
Dependencies
+
Expected outcome
```

---

# 2. Core Principle

> Make decisions from explicit criteria, not from convenience, habit, or superficial similarity.

Bad:

```text
"Python is popular, so use Python."
```

Better:

```text
Goal:
Build a small automation tool.

Criteria:
- Required libraries.
- Execution environment.
- Performance requirements.
- Maintainability.
- Existing team expertise.
- Deployment constraints.

Decision:
Select the option that best satisfies the actual project requirements.
```

---

# 3. Decision Process

Use this sequence:

```text
DEFINE DECISION
    ↓
IDENTIFY OBJECTIVE
    ↓
IDENTIFY CONSTRAINTS
    ↓
GENERATE FEASIBLE OPTIONS
    ↓
ELIMINATE INVALID OPTIONS
    ↓
DEFINE DECISION CRITERIA
    ↓
COLLECT RELEVANT EVIDENCE
    ↓
COMPARE OPTIONS
    ↓
ASSESS RISKS
    ↓
SELECT OPTION
    ↓
VERIFY ASSUMPTIONS
    ↓
EXECUTE
    ↓
MONITOR RESULT
    ↓
REVISE IF NECESSARY
```

---

# 4. Define the Decision

Before choosing, explicitly state what must be decided.

Bad:

```text
"What's better?"
```

Better:

```text
Decision:
Which implementation should be used for the requested application?

Options:
A
B
C

Objective:
Meet required functionality with minimum unnecessary complexity.
```

---

# 5. Decision Criteria

Possible criteria include:

```text
Goal fit
Correctness
Reliability
Performance
Security
Cost
Complexity
Maintainability
Compatibility
Time
Resource consumption
Scalability
Reversibility
Risk
Evidence quality
User preference
```

Do not use every criterion automatically.

Use criteria relevant to the decision.

---

# 6. Hard Criteria vs Soft Criteria

Separate:

```text
HARD CRITERIA
Must be satisfied.

SOFT CRITERIA
Used to distinguish otherwise feasible options.
```

Example:

```text
Decision:
Choose a database.

Hard:
- Must support required data model.
- Must run in target environment.

Soft:
- Easier administration.
- Lower resource usage.
- Better developer experience.
```

An option failing a hard criterion should normally be eliminated before scoring soft preferences.

---

# 7. Feasibility Before Preference

First ask:

```text
"Can this option actually satisfy the requirements?"
```

Only after feasibility is established ask:

```text
"Which feasible option is better?"
```

Rule:

```text
IF option violates a mandatory constraint
→ eliminate it.

IF option satisfies all mandatory constraints
→ compare it using secondary criteria.
```

---

# 8. Worked Example — Choosing an Implementation

## Input

```text
I need a small API.
It must:
- Run on Python 3.12.
- Have minimal dependencies.
- Be easy to deploy.
- Support async requests.
```

Options:

```text
A. Framework A
B. Framework B
C. Framework C
```

### Step 1 — Hard requirements

```text
Python 3.12 compatibility
Async support
Deployability
Minimal dependency requirement
```

### Step 2 — Eliminate invalid options

Suppose:

```text
A:
Python 3.12 ✓
Async ✓
Minimal dependencies ✓
Deployment ✓

B:
Python 3.12 ✓
Async ✓
Minimal dependencies ✗

C:
Python 3.12 ✗
Async ✓
Minimal dependencies ✓
```

Eliminate:

```text
B
C
```

### Step 3 — Decision

```text
A is the only option satisfying all mandatory requirements.
```

No complicated scoring is necessary.

### Output

```text
Decision:
Choose A.

Reason:
It is the only evaluated option satisfying every hard requirement.

Trade-off:
Other options may have advantages, but they fail mandatory requirements.
```

---

# 9. Negative Example — Popularity Bias

Incorrect:

```text
Option A has more GitHub stars,
therefore A is automatically better.
```

Why wrong?

Popularity is only one possible signal.

It does not prove:

```text
Compatibility
Correctness
Performance
Maintainability
Project fit
```

Correct:

```text
Use popularity only as supporting evidence,
not as an automatic decision rule.
```

---

# 10. Decision Rules

```text
IF an option violates a hard requirement
→ eliminate it.

IF only one feasible option remains
→ choose it and explain why.

IF multiple feasible options remain
→ compare them against relevant criteria.

IF one option dominates another across all important criteria
→ prefer the dominant option.

IF options trade advantages and disadvantages
→ explicitly identify the trade-off.

IF the decision depends on missing critical information
→ obtain the information before committing when practical.

IF obtaining information is expensive
→ compare the value of information against its cost.

IF the decision is easily reversible
→ prefer faster validation and experimentation.

IF the decision is difficult or expensive to reverse
→ increase verification before commitment.

IF evidence quality differs between options
→ account for evidence reliability.

IF uncertainty is high
→ avoid false certainty and state assumptions.
```

---

# 11. Option Dominance

Option A dominates Option B when A is:

```text
At least as good on all important criteria
AND
Strictly better on at least one important criterion
```

Example:

```text
A:
Cost: lower
Performance: equal
Compatibility: equal
Complexity: lower

B:
Cost: higher
Performance: equal
Compatibility: equal
Complexity: higher
```

A dominates B.

Decision:

```text
Choose A.
```

Do not overcomplicate the decision.

---

# 12. Trade-Off Decisions

Sometimes no option dominates.

Example:

```text
Option A:
Faster
More expensive

Option B:
Cheaper
Slower
```

Correct:

```text
No universally superior option exists.

Decision depends on:
- Budget priority.
- Performance requirement.
```

If budget is hard:

```text
Choose B.
```

If performance is hard:

```text
Choose A.
```

---

# 13. Weighted Criteria

When multiple feasible options remain, a weighted model may help.

Conceptually:

```text
Score =
Σ(weight × criterion score)
```

Example:

```text
Criteria:

Performance      weight 0.40
Maintainability  weight 0.30
Cost              weight 0.20
Complexity        weight 0.10
```

Option scores:

```text
A:
Performance: 9
Maintainability: 7
Cost: 6
Complexity: 8

B:
Performance: 7
Maintainability: 9
Cost: 8
Complexity: 7
```

Compute only when the decision actually benefits from quantitative comparison.

Do not invent precise numbers when evidence is qualitative.

---

# 14. Negative Example — Fake Precision

Incorrect:

```text
Option A = 87.4
Option B = 82.9

Therefore A is objectively 5.5 points better.
```

Why wrong?

The scores may be subjective and unsupported.

Correct:

```text
A appears stronger on performance.

B appears stronger on maintainability and cost.

The final choice depends on which criteria are more important.
```

Use numbers when they represent meaningful measurements or clearly defined scoring criteria.

---

# 15. Evidence Quality

Not all evidence deserves equal weight.

Consider:

```text
Direct measurement
Verified documentation
Reliable test results
Reproducible experiment
Relevant expert evidence
Indirect evidence
Anecdotal evidence
Unverified assumption
```

Rule:

```text
IF two options appear similar
AND one has substantially stronger evidence
→ prefer the better-supported option,
unless other requirements override it.
```

---

# 16. Uncertainty

Represent uncertainty explicitly.

Example:

```text
Decision:
Choose deployment platform.

Known:
- Supports required runtime.
- Meets memory requirements.

Unknown:
- Actual peak traffic performance.

Risk:
Medium.

Confidence:
Medium.
```

Do not convert:

```text
unknown
```

into:

```text
probably fine
```

without justification.

---

# 17. Decision Confidence

Use:

```text
HIGH
MEDIUM
LOW
```

### HIGH

Strong evidence and clear criteria.

### MEDIUM

Some uncertainty remains but the decision is adequately supported.

### LOW

Important information is missing or evidence is weak.

Example:

```text
Decision:
Use implementation A.

Confidence:
MEDIUM.

Reason:
Compatibility is verified,
but production performance has not yet been measured.
```

---

# 18. Reversible vs Irreversible Decisions

Classify decisions:

```text
REVERSIBLE
Easy to change later.

PARTIALLY REVERSIBLE
Change is possible but costly.

IRREVERSIBLE / HIGH-COST
Changing later is difficult or damaging.
```

Examples:

```text
Choosing a temporary variable name:
REVERSIBLE

Choosing a database schema:
PARTIALLY REVERSIBLE

Deleting irreplaceable data:
HIGH-RISK / IRREVERSIBLE
```

Decision rule:

```text
IF decision is cheap to reverse
→ favor rapid experimentation.

IF decision is expensive to reverse
→ verify more carefully before committing.
```

---

# 19. Negative Example — Treating All Decisions Equally

Incorrect:

```text
Spend the same amount of analysis on:
- Button spacing.
- Database architecture.
```

Why wrong?

The consequences are dramatically different.

Correct:

```text
High-cost irreversible decisions
→ deeper verification.

Low-cost reversible decisions
→ faster iteration.
```

---

# 20. Expected Loss

When uncertain, consider the consequences of being wrong.

Conceptually:

```text
Expected Loss =
Probability of failure × Cost of failure
```

Example:

```text
Decision A:
10% chance of failure.
Failure cost = 10.

Expected loss = 1.

Decision B:
2% chance of failure.
Failure cost = 100.

Expected loss = 2.
```

Even though B fails less often, its expected loss may be greater.

This is a decision aid, not an automatic answer.

---

# 21. Risk Asymmetry

Sometimes the downside matters more than average performance.

Example:

```text
Option A:
Usually works.
Rare failure is severe.

Option B:
Slightly slower.
Failure is easily recoverable.
```

If reliability is critical:

```text
Option B may be preferable.
```

Rule:

```text
IF failure consequences are highly asymmetric
→ evaluate downside risk explicitly.
```

---

# 22. Value of Information

Sometimes the best next action is not choosing.

It is learning.

Example:

```text
Choice:
A vs B

Unknown:
Whether A supports required feature X.

Test:
10 minutes.

Potential rework avoided:
Several hours.
```

Decision:

```text
Run the test first.
```

Rule:

```text
IF a small amount of information can substantially change the decision
→ obtain that information before committing.
```

---

# 23. Negative Example — Premature Commitment

Incorrect:

````text
"We should use A."

Then discover later:

```text
A does not support the required feature.
````

Why wrong?

The critical assumption was never validated.

Correct:

```text
Identify decision-critical assumptions first.
Validate them before expensive commitment.
```

---

# 24. Decision Under Missing Information

Use:

```text
Known:
...

Unknown:
...

Assumption:
...

Impact if assumption is false:
...

Best next action:
...
```

Example:

```text
Known:
Platform supports Python.

Unknown:
Maximum request duration.

Assumption:
Required requests finish within the platform limit.

Impact:
High.

Best next action:
Verify request-duration limits before architecture is finalized.
```

---

# 25. Decision Tree

For repeated decision patterns:

```text
Does the option satisfy all hard requirements?
        │
        ├── NO → Reject
        │
        └── YES
             ↓
Are multiple feasible options left?
        │
        ├── NO → Select remaining option
        │
        └── YES
             ↓
Does one option dominate?
        │
        ├── YES → Select dominant option
        │
        └── NO
             ↓
Are decision-critical facts missing?
        │
        ├── YES → Gather information
        │
        └── NO
             ↓
Compare trade-offs
             ↓
Assess risk
             ↓
Assess reversibility
             ↓
Select best-fit option
```

---

# 26. Worked Example — Fix vs Rewrite

## Input

```text
The application has several bugs.
Should I rewrite it from scratch?
```

Do not automatically recommend rewriting.

Evaluate:

```text
Current system stability
Bug frequency
Architecture quality
Technical debt
Code maintainability
Test coverage
Migration cost
Business requirements
Time available
Risk of regression
```

Possible outcomes:

```text
Small bugs + usable architecture
→ Fix incrementally.

Severe architectural failure + high change requirements
→ Rewrite may be justified.

Mixed situation
→ Incremental replacement / staged migration.
```

---

# 27. Negative Example — Rewrite Bias

Incorrect:

```text
"The code is messy, so rewrite everything."
```

Why wrong?

Messy code does not automatically imply that rewriting has lower total cost or risk.

Correct:

```text
Compare:
Cost of fixing
vs
Cost and risk of rewriting.
```

---

# 28. Decision Dependencies

A decision may depend on another decision.

Example:

```text
D1:
Choose deployment platform.

D2:
Choose database.

D3:
Choose storage architecture.
```

If D3 depends on D1:

```text
D1 → D3
```

Do not finalize D3 using assumptions about D1 that have not been established.

---

# 29. Decision Dependency Rules

```text
IF Decision A determines available options for Decision B
→ resolve A first.

IF B can be evaluated independently
→ do not unnecessarily block B.

IF a later decision may invalidate an earlier decision
→ preserve flexibility where possible.

IF a decision is provisional
→ explicitly mark it PROVISIONAL.
```

---

# 30. Provisional Decisions

Use provisional decisions when evidence is incomplete.

Format:

```text
Decision:
Use Option A temporarily.

Status:
PROVISIONAL.

Reason:
A currently best satisfies known requirements.

Assumption:
Requirement X remains unchanged.

Revisit when:
Requirement X is verified.
```

This prevents temporary choices from becoming invisible permanent assumptions.

---

# 31. Decision Reversal

Changing a decision is not automatically failure.

A good system changes its decision when evidence changes.

Rule:

```text
IF new evidence materially changes the decision criteria
or invalidates a key assumption
→ reconsider the decision.
```

Do not defend a previous decision merely because it was previously selected.

---

# 32. Negative Example — Sunk Cost Bias

Incorrect:

```text
"We already spent 10 hours implementing A,
so we must continue with A."
```

Why wrong?

Past effort is already spent.

The relevant question is:

```text
Which option is best from the current state forward?
```

Correct:

```text
Compare remaining cost and expected outcome of:
A
vs
alternative.
```

---

# 33. Decision Record

For important decisions use:

```text
Decision ID:
Question:
Objective:
Options:
Hard constraints:
Decision criteria:
Evidence:
Risks:
Assumptions:
Trade-offs:
Selected option:
Rejected options:
Reason:
Confidence:
Revisit condition:
```

Example:

```text
Decision ID:
D04

Question:
Which storage method should be used?

Objective:
Reliable storage with minimal operational complexity.

Options:
A
B
C

Hard constraints:
- Must support required data.
- Must work in target environment.

Criteria:
Reliability
Complexity
Cost

Evidence:
Verified compatibility documentation and test results.

Risks:
Option A has higher operational complexity.

Assumptions:
Expected traffic remains below current estimate.

Selected option:
B

Rejected options:
A — unnecessary complexity.
C — fails compatibility requirement.

Reason:
B satisfies all hard requirements with lower complexity.

Confidence:
HIGH

Revisit condition:
Requirements exceed current scale assumptions.
```

---

# 34. Decision Self-Check

Before committing:

```text
[ ] Is the actual decision clearly defined?
[ ] Is the objective clear?
[ ] Are hard constraints identified?
[ ] Have infeasible options been eliminated?
[ ] Are the relevant criteria explicit?
[ ] Is evidence quality considered?
[ ] Are important assumptions identified?
[ ] Are major risks evaluated?
[ ] Is reversibility considered?
[ ] Are trade-offs explicit?
[ ] Is false precision avoided?
[ ] Is the decision proportional to its consequences?
[ ] Is confidence stated appropriately?
[ ] Is there a condition that would trigger reconsideration?
```

---

# 35. Production Decision Rules

```text
IF an option violates a hard constraint
→ reject it.

IF only one feasible option remains
→ select it.

IF one feasible option dominates all others
→ select it.

IF options trade meaningful advantages
→ make the trade-off explicit.

IF the decision depends on missing critical information
→ gather that information when practical.

IF information gathering costs more than its likely benefit
→ make the best available decision with explicit uncertainty.

IF the decision is easily reversible
→ prefer rapid testing and iteration.

IF the decision is expensive to reverse
→ increase validation before commitment.

IF failure has severe consequences
→ prioritize downside-risk analysis.

IF evidence quality differs materially
→ prefer the better-supported option unless requirements dictate otherwise.

IF a decision depends on another unresolved decision
→ resolve the dependency first or preserve a provisional decision.

IF new evidence invalidates a key assumption
→ reconsider the decision.

IF the only reason to continue is past investment
→ reassess from the current state.

IF confidence is low because critical information is missing
→ avoid presenting the decision as certain.

IF the selected option no longer satisfies the goal
→ re-plan rather than defending the old decision.

IF a decision cannot be justified against explicit criteria
→ do not treat it as a reliable decision.
```

---

# 36. Final Decision-Making Protocol

```text
DEFINE
  ↓
CONSTRAIN
  ↓
GENERATE OPTIONS
  ↓
FILTER INFEASIBLE OPTIONS
  ↓
DEFINE CRITERIA
  ↓
COLLECT EVIDENCE
  ↓
IDENTIFY ASSUMPTIONS
  ↓
COMPARE
  ↓
ASSESS TRADE-OFFS
  ↓
ASSESS RISK
  ↓
CHECK REVERSIBILITY
  ↓
SELECT
  ↓
RECORD REASON
  ↓
EXECUTE
  ↓
MONITOR
  ↓
REASSESS WHEN EVIDENCE CHANGES
```

The Decision Making module is successful when the system can answer:

> **What decision is being made, what options were feasible, why was the selected option better under the actual constraints and evidence, what uncertainty remains, and what new information would cause the decision to change?**

---

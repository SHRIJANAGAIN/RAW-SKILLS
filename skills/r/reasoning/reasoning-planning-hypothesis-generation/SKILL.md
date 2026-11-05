---
name: reasoning-planning-hypothesis-generation
version: 1.0.0
description: Production-ready hypothesis-generation capability for producing plausible explanations, candidate solutions, testable predictions, alternative hypotheses, uncertainty estimates, and evidence-driven updates.
category: reasoning-and-planning
module: hypothesis-generation
priority: high
author: SKT AI LABS
---

# Hypothesis Generation

## 1. Purpose

Hypothesis Generation helps the system reason when the correct explanation or solution is not immediately known.

A hypothesis is:

> A plausible explanation, prediction, or candidate solution that can be evaluated against evidence.

A hypothesis is **not a fact**.

The system must distinguish:

```text
FACT
What is directly established.

OBSERVATION
What has been observed.

ASSUMPTION
What is temporarily accepted for planning.

HYPOTHESIS
What may explain or solve the situation.

CONCLUSION
What is supported after evaluation.
```

---

# 2. Core Principle

> Generate possibilities broadly, but treat them cautiously until evidence supports them.

Bad:

```text
"The server is down because the database crashed."
```

when no evidence confirms the database failure.

Better:

```text
Possible hypotheses:
H1. Database connection failure.
H2. Application process stopped.
H3. Network routing problem.
H4. Configuration error.

Next:
Test the cheapest high-information hypothesis first.
```

---

# 3. When to Generate Hypotheses

Generate hypotheses when:

```text
The cause is unknown.
Multiple explanations are possible.
Observed behavior is unexpected.
A task has failed.
Evidence is incomplete.
A solution is not obvious.
The user asks "why?"
A diagnosis is required.
A design choice has uncertain outcomes.
A failure requires root-cause analysis.
```

Do not generate unnecessary hypotheses when the answer is already directly established.

---

# 4. Hypothesis Types

Classify hypotheses as:

```text
CAUSAL
What caused the observed result?

DIAGNOSTIC
What explains the failure?

PREDICTIVE
What will happen next?

SOLUTION
What approach may solve the problem?

DESIGN
What architecture or strategy may work?

INTERPRETIVE
What does the evidence mean?

RISK
What may go wrong?

ALTERNATIVE
What other explanation could fit the evidence?
```

---

# 5. Hypothesis Structure

Use:

```text
Hypothesis ID:
Hypothesis:
Type:
Supporting evidence:
Contradicting evidence:
Assumptions:
Predicted observation:
Test:
Expected result:
Confidence:
Status:
```

Example:

```text
Hypothesis ID:
H1

Hypothesis:
The application cannot connect to the database.

Type:
DIAGNOSTIC

Supporting evidence:
Requests involving database operations fail.

Contradicting evidence:
Health endpoint still responds.

Assumptions:
Database credentials are unchanged.

Predicted observation:
Database connection test fails.

Test:
Run a connection check.

Confidence:
MEDIUM

Status:
UNTESTED
```

---

# 6. Hypothesis Lifecycle

Use:

```text
GENERATE
    ↓
SCREEN
    ↓
RANK
    ↓
TEST
    ↓
UPDATE
    ↓
ACCEPT / REJECT / REFINE
```

Possible states:

```text
UNTESTED
TESTING
SUPPORTED
WEAKLY_SUPPORTED
REJECTED
INCONCLUSIVE
REFINED
SUPERSEDED
```

---

# 7. Generate Multiple Hypotheses

Avoid immediately locking onto the first explanation.

Example:

```text
Observation:
Website suddenly became slow.

Possible hypotheses:

H1:
Database queries became slower.

H2:
Traffic increased.

H3:
External API is responding slowly.

H4:
Server resources are exhausted.

H5:
A recent deployment introduced inefficient code.
```

The purpose is not to create dozens of possibilities.

The purpose is to avoid premature commitment.

---

# 8. Minimum Useful Hypothesis Set

Generate enough alternatives to cover materially different explanations.

Typical target:

```text
2–5 strong hypotheses
```

depending on complexity.

Do not generate many nearly identical hypotheses.

Bad:

```text
H1:
Database is slow.

H2:
Database query is slow.

H3:
Database operation is slow.

H4:
Database response is slow.
```

These may represent the same underlying hypothesis.

Better:

```text
H1:
Database performance issue.

H2:
Application-side performance issue.

H3:
Network latency.

H4:
External dependency latency.
```

---

# 9. Hypothesis Diversity

When generating alternatives, deliberately vary the explanation category.

Check:

```text
Application
Infrastructure
Data
Configuration
Dependency
Environment
User behavior
Timing
Resource limitation
Incorrect assumption
```

This reduces tunnel vision.

---

# 10. Worked Example — Website Failure

## Input

```text
The website worked yesterday.
Today users are getting errors.
What could be wrong?
```

### Observation

```text
Users are receiving errors.
```

Do not immediately conclude the cause.

### Hypotheses

```text
H1:
A recent deployment introduced a regression.

H2:
The database is unavailable.

H3:
An external dependency is failing.

H4:
Production configuration changed.

H5:
Traffic/resource usage exceeded available capacity.
```

### Ranking

Suppose a deployment occurred immediately before the failures.

```text
H1:
HIGH

H2:
MEDIUM

H3:
MEDIUM

H4:
MEDIUM

H5:
LOW–MEDIUM
```

The ranking is provisional.

### Test

```text
Check deployment history.

If failures began immediately after deployment,
H1 gains support.

If no deployment occurred,
H1 loses support.
```

---

# 11. Negative Example — Premature Diagnosis

Incorrect:

```text
User:
"My app is slow."

Assistant:
"The database is definitely the problem."
```

Why wrong?

There is insufficient evidence.

Other possibilities include:

```text
Network latency
CPU saturation
Memory pressure
Slow external API
Inefficient application code
Large payloads
Database performance
```

Correct:

```text
"The database is one plausible hypothesis,
but we need evidence to distinguish it from other causes."
```

---

# 12. Hypothesis vs Fact

Never write:

```text
"The database crashed."
```

when the evidence only shows:

```text
Database-dependent requests are failing.
```

Instead:

```text
Observation:
Database-dependent requests are failing.

Hypothesis:
Database may be unavailable.

Verification:
Check database health/connectivity.
```

---

# 13. Evidence Mapping

For every important hypothesis, track:

```text
Supporting evidence
Contradicting evidence
Missing evidence
```

Example:

```text
H1:
Recent deployment caused regression.

Supporting:
- Deployment occurred 5 minutes before failures.
- Error rate increased immediately afterward.

Contradicting:
- One unaffected endpoint uses the same deployment.

Missing:
- Error logs from affected endpoint.
```

This prevents one-sided reasoning.

---

# 14. Hypothesis Ranking

Rank hypotheses using:

```text
Evidence strength
Prior plausibility
Observed fit
Test cost
Potential impact
Contradicting evidence
```

A useful heuristic:

```text
Priority =
Likelihood
×
Impact
×
Test value
```

Do not treat this as a scientifically exact probability unless actual probabilities are available.

---

# 15. Testability

Prefer hypotheses that make distinct predictions.

Weak:

```text
"Something in the system is broken."
```

Not useful because almost any result fits.

Better:

```text
"If the database is the cause,
database connection latency or errors should increase."
```

A useful hypothesis should produce observations that could support or weaken it.

---

# 16. Falsifiability

Ask:

> "What observation would make this hypothesis less likely?"

Example:

```text
Hypothesis:
The API is failing because of a timeout.

Prediction:
Requests exceed the configured timeout threshold.

Contradicting observation:
Requests fail immediately with authentication errors.
```

A hypothesis that cannot meaningfully be challenged is weak for diagnostic planning.

---

# 17. Test Selection

Choose tests based on information value.

Prefer tests that are:

```text
Cheap
Fast
Safe
Highly discriminative
Easy to interpret
```

Example:

```text
H1:
Database failure.

H2:
Network failure.

Test:
Run a direct database connectivity check.

If database connection succeeds:
H1 weakens.

If database connection fails:
H1 strengthens.
```

---

# 18. Negative Example — Expensive Test First

Incorrect:

```text
Spend 5 hours rewriting the API
to see whether the problem disappears.
```

when a 30-second log inspection could distinguish the likely causes.

Correct:

```text
Start with the lowest-cost,
highest-information test.
```

---

# 19. Hypothesis Testing Order

Use:

```text
1. Safety-critical hypotheses.
2. High-impact hypotheses.
3. High-probability hypotheses.
4. Cheap-to-test hypotheses.
5. Hypotheses that unlock other decisions.
```

Balance these rather than blindly following one factor.

---

# 20. Bayesian-Style Updating

When evidence arrives, update hypothesis confidence.

Conceptually:

```text
Prior belief
+
New evidence
→
Updated belief
```

Example:

```text
Initial:

H1 database issue:
MEDIUM

H2 deployment regression:
MEDIUM

Evidence:
A deployment happened immediately before failures.

Update:

H1:
MEDIUM

H2:
HIGH
```

If later evidence shows the deployment did not affect the failing service:

```text
H2:
LOWER confidence
```

Do not remain attached to the original hypothesis.

---

# 21. Negative Example — Confirmation Bias

Initial hypothesis:

```text
"The database is broken."
```

Then every observation is interpreted as evidence for it.

Incorrect:

```text
Database requests fail → database problem.
Other requests fail → database problem.
Logs show timeout → database problem.
```

Correct:

```text
Ask:
Could the same evidence also be explained by another hypothesis?
```

If yes, continue testing.

---

# 22. Alternative Hypothesis Rule

For important uncertain decisions:

```text
IF one hypothesis appears overwhelmingly likely
→ still consider at least one credible alternative
when the cost of being wrong is significant.
```

Example:

```text
Primary:
Deployment regression.

Alternative:
Infrastructure configuration change.
```

This prevents premature closure.

---

# 23. Hypothesis Elimination

Reject hypotheses when evidence contradicts their predictions.

Example:

```text
H1:
Server CPU exhaustion.

Prediction:
CPU utilization should be abnormally high.

Observed:
CPU utilization remains low.

Result:
H1 weakened or rejected.
```

Do not continue treating rejected hypotheses as equally likely without new evidence.

---

# 24. Hypothesis Refinement

Sometimes a hypothesis is partially correct.

Initial:

```text
H1:
Database is causing the slowdown.
```

Evidence:

```text
Database itself is healthy,
but one query is extremely slow.
```

Refined:

```text
H1a:
A specific database query is causing the slowdown.
```

Use:

```text
REJECT BROAD HYPOTHESIS
        ↓
PRESERVE VALID EVIDENCE
        ↓
REFINE
        ↓
RETEST
```

---

# 25. Worked Example — Debugging

## Input

```text
A program crashes when processing large files.
```

Possible hypotheses:

```text
H1:
Memory exhaustion.

H2:
File parsing bug.

H3:
Integer/size limitation.

H4:
Corrupted input.

H5:
External library limitation.
```

Tests:

```text
Test 1:
Check memory usage.

Test 2:
Try a known-good large file.

Test 3:
Try a slightly smaller file.

Test 4:
Inspect crash logs.

Test 5:
Test parser independently.
```

Interpretation:

```text
If memory spikes before crash:
H1 strengthens.

If only one file crashes:
H4 strengthens.

If failure happens at a consistent size boundary:
H3 strengthens.

If parser fails independently:
H2 strengthens.
```

---

# 26. Negative Example — One Test, One Conclusion

Incorrect:

```text
Test:
Memory usage is high.

Conclusion:
Memory is definitely the root cause.
```

Why wrong?

High memory usage may be a symptom rather than the root cause.

Correct:

```text
Observation:
Memory usage is high.

Hypothesis:
Memory exhaustion may contribute to the crash.

Next:
Determine whether memory exhaustion occurs immediately before failure.
```

---

# 27. Root Cause vs Symptom

Distinguish:

```text
SYMPTOM:
What is visibly going wrong.

CAUSE:
What directly produces the symptom.

ROOT CAUSE:
Underlying condition that initiated or enabled the failure.
```

Example:

```text
Symptom:
Website returns 500.

Immediate cause:
Application exception.

Root cause:
Invalid configuration introduced during deployment.
```

Do not stop at the first visible symptom.

---

# 28. Hypothesis Chains

For complex failures:

```text
Root cause
    ↓
Intermediate condition
    ↓
Immediate cause
    ↓
Observed symptom
```

Example:

```text
Configuration error
    ↓
Database connection string invalid
    ↓
Database connection fails
    ↓
API throws exception
    ↓
User receives 500
```

Test the chain from evidence rather than assuming every link.

---

# 29. Edge Case — No Plausible Hypothesis

If current evidence does not support a useful explanation:

```text
Do not invent one.
```

Use:

```text
Known:
...

Unknown:
...

Evidence needed:
...

Next diagnostic action:
...
```

Unknown is a valid state.

---

# 30. Edge Case — Many Plausible Hypotheses

If there are 20 possibilities:

```text
Do not test all 20 equally.
```

Cluster them:

```text
Application
Infrastructure
Network
Data
Dependency
Configuration
```

Then choose high-value tests that eliminate multiple hypotheses at once.

---

# 31. Edge Case — Conflicting Evidence

Example:

```text
Evidence A:
CPU is high.

Evidence B:
CPU is normal during failure.
```

Do not simply choose one.

Ask:

```text
Were they measured at different times?
Different machines?
Different environments?
Different workloads?
```

Resolve measurement context before updating confidence.

---

# 32. Edge Case — User Provides a False Premise

User:

```text
"The database definitely crashed.
Why is the frontend broken?"
```

If the crash has not been verified:

```text
Do not treat the premise as confirmed fact.
```

Correct:

```text
"If the database crash is confirmed,
it could explain database-dependent failures.
First verify whether the database is actually unavailable."
```

---

# 33. Edge Case — Hypothesis Becomes Irrelevant

If new evidence changes the problem:

```text
Original:
Why is API slow?

New evidence:
API is not slow; client-side rendering is slow.
```

Update:

```text
Original API hypotheses:
SUPERSEDED

New hypothesis set:
Client-side rendering causes slowdown.
```

Do not continue investigating the wrong layer.

---

# 34. Hypothesis Ledger

For complex investigation:

```text
Hypothesis ID:
Statement:
Type:
Prior confidence:
Supporting evidence:
Contradicting evidence:
Predictions:
Tests:
Current confidence:
Status:
Next action:
```

Example:

```text
H03

Statement:
Recent deployment introduced the regression.

Type:
CAUSAL

Prior confidence:
Medium

Supporting evidence:
Error rate increased immediately after deployment.

Contradicting evidence:
None currently.

Predictions:
Affected endpoints should fail on the new version.

Tests:
Compare old vs new version.

Current confidence:
High

Status:
TESTING

Next action:
Run version comparison.
```

---

# 35. Hypothesis Status Rules

```text
IF hypothesis has not been tested
→ UNTESTED.

IF a relevant test is running
→ TESTING.

IF evidence strongly supports it
→ SUPPORTED.

IF some evidence supports it but uncertainty remains
→ WEAKLY_SUPPORTED.

IF evidence contradicts its key predictions
→ REJECTED.

IF evidence cannot distinguish it
→ INCONCLUSIVE.

IF the hypothesis is modified using new evidence
→ REFINED.

IF another explanation replaces it
→ SUPERSEDED.
```

---

# 36. Confidence Calibration

Avoid:

```text
"99.9% certain"
```

unless the evidence genuinely supports such precision.

Prefer:

```text
HIGH
MEDIUM
LOW
```

or:

```text
Likely
Plausible
Unlikely
Unknown
```

Use precise probabilities only when they are meaningful.

---

# 37. Worked Example — Product Decision

## Input

```text
Users are abandoning the signup flow.
Why?
```

Possible hypotheses:

```text
H1:
Signup form is too long.

H2:
Signup page loads slowly.

H3:
Users encounter validation errors.

H4:
Required information is unclear.

H5:
Users do not trust the page.
```

Evidence:

```text
Analytics:
Large drop occurs on password validation step.
```

Update:

```text
H3:
High confidence.

H1:
Lower confidence.

H2:
Lower confidence.

H4:
Still plausible.

H5:
Still possible.
```

Next test:

```text
Inspect validation errors and failed signup events.
```

Correct conclusion:

```text
"Validation errors are currently the strongest hypothesis."
```

Not:

```text
"Validation errors are definitely the cause."
```

---

# 38. Hypothesis Quality Checklist

A strong hypothesis should be:

```text
Plausible
Specific
Testable
Relevant
Evidence-aware
Distinguishable
Falsifiable
Actionable
```

Weak:

```text
"Something is wrong."
```

Strong:

```text
"The recent configuration change may have invalidated
the database connection string, causing database-dependent
requests to fail."
```

---

# 39. Production Decision Rules

```text
IF the cause or solution is unknown
→ generate multiple plausible hypotheses.

IF evidence already establishes the answer
→ do not invent unnecessary hypotheses.

IF a hypothesis is unsupported
→ label it as unverified.

IF one hypothesis is favored
→ retain at least one credible alternative when failure cost is high.

IF a hypothesis violates known facts
→ reject or substantially reduce its priority.

IF a hypothesis produces no distinguishable prediction
→ refine it.

IF a cheap test can strongly distinguish hypotheses
→ prioritize that test.

IF evidence contradicts a hypothesis
→ reduce confidence or reject it.

IF new evidence supports a hypothesis
→ increase confidence proportionally.

IF new evidence invalidates a key assumption
→ reconsider the hypothesis.

IF a broad hypothesis is partially supported
→ refine it rather than treating the entire hypothesis as confirmed.

IF evidence is insufficient
→ preserve uncertainty.

IF the user supplies an unverified premise
→ distinguish the premise from established fact.

IF multiple hypotheses share the same root category
→ cluster them to avoid redundant testing.

IF a hypothesis has severe consequences if wrong
→ increase verification before acting on it.

IF a hypothesis is confirmed strongly enough for the decision
→ transition from investigation to action.

IF no hypothesis is adequately supported
→ state what is known, what remains unknown, and what evidence is needed next.
```

---

# 40. Final Hypothesis Generation Protocol

```text
OBSERVATION
    ↓
SEPARATE FACT FROM ASSUMPTION
    ↓
DEFINE UNKNOWN
    ↓
GENERATE PLAUSIBLE HYPOTHESES
    ↓
DIVERSIFY EXPLANATIONS
    ↓
FILTER WEAK / REDUNDANT HYPOTHESES
    ↓
IDENTIFY PREDICTIONS
    ↓
RANK BY EVIDENCE + IMPACT + TEST VALUE
    ↓
SELECT HIGH-INFORMATION TEST
    ↓
OBSERVE RESULT
    ↓
UPDATE CONFIDENCE
    ↓
REJECT / SUPPORT / REFINE
    ↓
REPEAT IF NECESSARY
    ↓
ACT ONLY ON SUFFICIENTLY SUPPORTED CONCLUSIONS
```

The Hypothesis Generation module is successful when the system can answer:

> **What are the plausible explanations or approaches, what evidence supports each one, what evidence would disprove them, which test gives the most useful information, and how should the hypotheses change when new evidence appears?**

---

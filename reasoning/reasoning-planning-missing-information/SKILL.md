---
name: reasoning-planning-missing-information
version: 1.0.0
description: Production-ready capability for detecting missing, ambiguous, contradictory, or decision-critical information before and during planning and execution.
category: reasoning-and-planning
module: detecting-missing-information
priority: critical
author: SKT AI LABS
---

# Detecting Missing Information

## 1. Purpose

A plan can fail because information required for correct execution was never identified.

The system must distinguish between:

```text
KNOWN
Confirmed information.

UNKNOWN
Information not currently available.

AMBIGUOUS
Information has multiple possible interpretations.

CONTRADICTORY
Different pieces of information conflict.

ASSUMED
Temporarily accepted information used for planning.

REQUIRED
Information necessary for correctness or safe execution.

OPTIONAL
Useful but not necessary information.
```

The goal is not to ask the user endless questions.

The goal is:

> **Identify the minimum missing information required to make the next correct decision.**

---

# 2. Core Principle

> Do not guess when missing information can materially change the result.

Bad:

```text
User:
"Deploy my app."

Assistant:
"Sure, deploy it to AWS."
```

Problem:

```text
Cloud provider unknown.
Environment unknown.
Target branch unknown.
Deployment method unknown.
Production/staging unknown.
```

Better:

```text
Before deployment I need the deployment target
and environment.

If those are already established by context,
reuse them instead of asking again.
```

---

# 3. Information Classification

For every important task, classify information:

```text
GOAL
What must be achieved?

INPUTS
What data/material is required?

CONSTRAINTS
What limitations apply?

DEPENDENCIES
What must exist first?

ENVIRONMENT
Where will the work happen?

RESOURCES
What tools/access/data are available?

SUCCESS CRITERIA
How will completion be verified?

PREFERENCES
What choices does the user care about?

RISKS
What information affects safety or failure consequences?
```

---

# 4. Information Sufficiency Test

Before execution, ask:

```text
Do I know the goal?
Do I know the required output?
Do I know the important constraints?
Do I have required inputs?
Do dependencies exist?
Do I know the execution environment?
Do I know how success will be verified?
```

If all critical questions are answered:

```text
Proceed.
```

If some are missing:

```text
Determine whether the missing information is actually blocking.
```

---

# 5. Critical vs Non-Critical Missing Information

Not every unknown requires a question.

Example:

```text
Task:
Write a short Python script.
```

Unknown:

```text
User's preferred font.
```

This is irrelevant.

Proceed.

But:

```text
Task:
Convert a video.

Unknown:
Input file format.
Output format.
```

These may materially affect execution.

Ask or infer only when safely supported by context.

---

# 6. Decision Rule

```text
IF missing information cannot affect the result
→ ignore it.

IF missing information affects a minor preference
→ choose a sensible default or ask only if important.

IF missing information affects implementation
→ determine whether a reasonable default exists.

IF missing information affects correctness
→ obtain it before committing.

IF missing information affects safety
→ do not guess.

IF missing information affects a major irreversible action
→ verify before acting.
```

---

# 7. Worked Example — Ambiguous File Conversion

## Input

```text
Convert this video for me.
```

Potentially missing:

```text
Output format
Resolution
Codec
Audio requirements
Target platform
Quality requirement
File-size constraint
```

Do not ask all questions immediately.

Identify the minimum required information.

For example:

```text
Required:
Output format or target platform.

Potential defaults:
Standard resolution.
Reasonable quality.
Preserve audio.
```

Question:

```text
"What format/platform should the converted video target?
If you don't care, I can use a broadly compatible format."
```

This is better than asking seven questions at once.

---

# 8. Negative Example — Question Overload

Incorrect:

```text
What codec?
What bitrate?
What frame rate?
What container?
What audio codec?
What audio bitrate?
What resolution?
What profile?
What preset?
What CRF?
```

Why wrong?

The user may not know these details, and many can be safely defaulted.

Correct:

```text
Ask only decision-critical questions.
Use sensible defaults for secondary technical choices.
```

---

# 9. Minimum Information Principle

Use:

```text
MINIMUM REQUIRED INFORMATION
```

rather than:

```text
MAXIMUM POSSIBLE INFORMATION
```

Before asking, determine:

```text
What decision am I unable to make?
What single missing fact would unblock it?
```

Ask that first.

---

# 10. Worked Example — Travel Planning

Input:

```text
"Plan a trip for me."
```

Important missing information:

```text
Destination
Dates
Budget
Travelers
Trip purpose
```

Do not ask:

```text
Favorite hotel chain
Favorite airline
Preferred seat
Breakfast preference
Room floor
```

before knowing where and when the trip is.

Correct:

```text
"I need the destination and dates first.
If you have a budget or specific preferences,
share those too."
```

---

# 11. Blocking Information

Information is **blocking** if execution cannot reliably continue without it.

Example:

```text
Task:
Send report to someone.

Missing:
Recipient.
```

Blocking.

Example:

```text
Task:
Write report.

Missing:
Preferred bullet character.
```

Not blocking.

Rule:

```text
IF information blocks a required decision
→ obtain it.

IF information does not block progress
→ proceed.
```

---

# 12. Dependency-Aware Missing Information

Missing information may be needed only later.

Example:

```text
T1 Research
T2 Choose architecture
T3 Implement
T4 Deploy
```

Deployment region may not be needed for T1.

Therefore:

```text
Do not block T1 unnecessarily.
```

Instead:

```text
T1 → T2
       ↓
Need deployment region before T4.
```

This enables parallel progress.

---

# 13. Negative Example — Blocking Everything

Incorrect:

```text
"I cannot start research until I know the final deployment region."
```

Why wrong?

The information is not required for the current step.

Correct:

```text
Proceed with independent work.
Request the missing information before the dependent step.
```

---

# 14. Missing Input vs Missing Permission

These are different.

Example:

```text
Input:
Database credentials are missing.

Permission:
You have no authorization to access the database.
```

Do not treat permission as merely missing data.

Correct classification:

```text
INPUT MISSING
→ request/provide input through appropriate means.

ACCESS/PERMISSION MISSING
→ obtain appropriate authorization or use an authorized alternative.
```

---

# 15. Missing Tool vs Missing Information

Example:

```text
Task:
Analyze a PDF.

Information:
PDF exists.

Tool:
No PDF-reading capability available.
```

The problem is not missing information.

It is missing capability.

Correct:

```text
Known:
PDF exists.

Blocker:
Required file-reading capability is unavailable.

Next:
Use an available compatible method or request the needed input in a supported form.
```

---

# 16. Missing Environment Information

Technical tasks often depend on environment.

Potential environment fields:

```text
Operating system
Runtime version
Language version
Package manager
Hardware
Cloud provider
Deployment environment
Directory structure
Network availability
Permissions
Configuration
```

Do not ask for every field.

Ask only those relevant to the next step.

Example:

```text
"Install this package."
```

If installation command differs substantially by OS:

```text
Need:
Operating system.
```

---

# 17. Environment Inference

Use available evidence before asking.

Example:

```text
Observed:
Windows command prompt.

User asks:
"How do I install this?"
```

Possible inference:

```text
Likely Windows environment.
```

But if the action is consequential:

```text
"Are you running this on Windows, Linux, or macOS?"
```

Rule:

```text
IF context reliably establishes the environment
→ reuse it.

IF context strongly suggests but does not establish it
→ infer only for low-risk guidance.

IF environment materially changes a consequential action
→ verify.
```

---

# 18. Ambiguity Detection

Ambiguity exists when the same request can reasonably mean multiple things.

Example:

```text
"Make it faster."
```

Possible meanings:

```text
Faster execution
Faster response time
Faster startup
Faster development
Smaller latency
```

Do not silently choose the wrong interpretation.

Ask:

```text
"Do you mean faster runtime/response time,
or faster development?"
```

---

# 19. Negative Example — Silent Interpretation

User:

```text
"Make the model smaller."
```

Incorrect:

```text
Immediately reduce parameter count.
```

Possible meanings:

```text
Smaller file size
Lower memory usage
Fewer parameters
Lower latency
Lower deployment cost
```

Correct:

```text
"Do you mean smaller model file size,
lower memory usage, or fewer parameters?"
```

If context clearly identifies one interpretation, use it.

---

# 20. Ambiguity Severity

Classify ambiguity:

```text
LOW
Different interpretations produce similar results.

MEDIUM
Different interpretations produce meaningfully different results.

HIGH
Different interpretations produce incompatible or risky outcomes.
```

Rules:

```text
LOW
→ choose a reasonable interpretation.

MEDIUM
→ clarify when practical.

HIGH
→ clarify before committing.
```

---

# 21. Contradictory Information

Example:

```text
User says:
"Use Python 3.10."

Existing project configuration:
Python 3.12.
```

Do not silently choose one.

Identify conflict:

```text
Conflict:
Requested Python 3.10
vs
Existing project Python 3.12
```

Then determine whether:

```text
One is outdated.
One is a hard requirement.
Both environments must be supported.
```

Ask only if necessary.

---

# 22. Negative Example — Ignoring Contradictions

Incorrect:

```text
User says Python 3.10.
Assistant edits files for 3.10
while project is configured for 3.12.
```

Why wrong?

The contradiction may produce an inconsistent environment.

Correct:

```text
Detect conflict.
Identify authority/source.
Resolve before making consequential changes.
```

---

# 23. Source Priority

When information conflicts, evaluate source reliability.

Possible priority:

```text
Explicit current user requirement
>
Verified current project configuration
>
Current tool output
>
Documented system state
>
Older instructions
>
Assumptions
>
Guesses
```

This is contextual, not absolute.

If a user says:

```text
"Actually, use Python 3.11."
```

that may supersede their earlier request for 3.10.

---

# 24. Stale Information

Information may have been correct earlier but no longer be current.

Examples:

```text
Old package version
Old API endpoint
Old deployment status
Old file path
Old requirements
```

Rule:

```text
IF information may have changed
AND current state matters
→ verify current state.
```

Do not blindly reuse stale assumptions.

---

# 25. Missing Success Criteria

A task may have an unclear definition of "done."

Example:

```text
"Improve the application."
```

Missing:

```text
What should improve?
How much?
For whom?
How will success be measured?
```

Possible clarification:

```text
"What outcome should improve—speed, reliability,
UI usability, or something else?"
```

---

# 26. Completion Criteria

For every significant task define:

```text
DONE WHEN:
...
```

Example:

```text
Task:
Fix API timeout.

Completion criteria:
- Requests complete within required limit.
- No timeout errors in test cases.
- Regression tests pass.
```

Without completion criteria, the planner may stop too early or continue unnecessarily.

---

# 27. Missing Constraints

Common hidden constraints:

```text
Budget
Deadline
Compatibility
Security
Performance
Platform
Licensing
File size
Backward compatibility
User preferences
Existing architecture
Available resources
```

Do not assume all constraints are absent.

Use context first.

If the constraint materially changes the plan:

```text
Ask.
```

---

# 28. Worked Example — Software Architecture

Input:

```text
"Build me an API."
```

Potentially missing:

```text
Language/runtime
Expected traffic
Authentication
Data source
Deployment environment
Required endpoints
Latency expectations
```

Do not ask everything at once.

Start with high-impact unknowns:

```text
1. What does the API need to do?
2. Where will it run?
3. Are there required runtime/language constraints?
```

Then discover further information as planning progresses.

---

# 29. Progressive Clarification

Use staged questions:

```text
Stage 1:
Ask information needed to define the plan.

Stage 2:
Ask information needed for implementation.

Stage 3:
Ask information needed for validation/deployment.
```

Avoid requesting future details before they are relevant.

---

# 30. Negative Example — Premature Detailed Questionnaire

Incorrect:

```text
Before writing a simple script,
request 25 configuration fields.
```

Why wrong?

It creates friction and delays execution.

Correct:

```text
Ask only what is required for the current stage.
```

---

# 31. Safe Defaults

A default can be used when:

```text
The choice is low-risk.
The choice is reversible.
The user has not specified a preference.
The default is conventional.
The default does not materially affect the goal.
```

Example:

```text
User:
"Create a simple text file."

Default:
UTF-8.
```

No clarification needed.

---

# 32. Unsafe Defaults

Do not silently default when:

```text
The action is irreversible.
The choice can cause data loss.
The choice affects security.
The choice affects legal/compliance requirements.
The choice can substantially change the outcome.
The user explicitly cares about the parameter.
```

In such cases:

```text
Ask or verify.
```

---

# 33. Assumption Protocol

When proceeding with incomplete information:

```text
Assumption:
...

Why reasonable:
...

Impact if wrong:
...

How to revise:
...
```

Example:

```text
Assumption:
Use standard UTF-8 encoding.

Why reasonable:
No encoding requirement was specified.

Impact if wrong:
Low.

Revision:
Change encoding if the target system requires another format.
```

---

# 34. Negative Example — Hidden Assumption

Incorrect:

```text
"Your app uses PostgreSQL."
```

when the user never said that.

Why wrong?

The system silently converted an unknown into a fact.

Correct:

```text
"If you're using PostgreSQL, use this configuration.
Otherwise tell me the database engine."
```

---

# 35. Information Value

Not all missing information is equally valuable.

Estimate:

```text
How much can this information change the decision?
```

High-value:

```text
Deployment environment
Required output format
Critical compatibility requirement
Mandatory deadline
Budget limit
Safety-critical constraint
```

Low-value:

```text
Minor formatting preference
Optional naming preference
Cosmetic detail
```

Ask high-value questions first.

---

# 36. Value of Clarification

Use:

```text
Clarification value
≈
Probability answer changes plan
×
Impact of that change
```

If clarification has low value:

```text
Use a reasonable default.
```

If clarification has high value:

```text
Ask before proceeding.
```

---

# 37. Worked Example — Choosing a Framework

Input:

```text
"Which framework should I use?"
```

Missing:

```text
What are you building?
```

This is high-value because the answer can completely change the recommendation.

Ask:

```text
"What are you building—web app, API, mobile app,
CLI tool, or something else?"
```

Do not ask:

```text
"What is your preferred indentation style?"
```

because it has little decision value.

---

# 38. Information Dependency Graph

Represent missing information as dependencies.

Example:

```text
Goal
 ↓
Required functionality
 ↓
Architecture
 ↓
Implementation
 ↓
Deployment
```

Missing:

```text
Required functionality
```

Therefore:

```text
Architecture
Implementation
Deployment
```

may all be premature.

Resolve upstream information first.

---

# 39. Critical Path for Information

Determine:

```text
Which missing fact blocks the next meaningful action?
```

Example:

```text
Missing:
Deployment region.

Current task:
Design data model.

Does it block?
NO.

Later task:
Configure deployment.

Does it block?
YES.
```

Do not block current work unnecessarily.

---

# 40. Information Readiness States

Use:

```text
READY
All required information available.

PARTIALLY_READY
Some information missing but useful work can proceed.

BLOCKED
Required information unavailable.

AMBIGUOUS
Multiple interpretations remain.

CONFLICTED
Available information contradicts.

UNKNOWN
Insufficient evidence to determine state.
```

---

# 41. Worked Example — User Request

Input:

```text
"Fix my code."
```

If code is actually attached:

```text
Known:
Code available.

Next:
Inspect code.
```

If no code is provided:

```text
Missing:
Code.

Status:
BLOCKED.

Question:
"Please send the code or the relevant file."
```

Do not pretend to have inspected code that was never provided.

---

# 42. Negative Example — Fabricated Context

Incorrect:

```text
"I found the bug in your code."
```

when no code was available.

Why wrong?

The required evidence is absent.

Correct:

```text
"I need the relevant code/error output to identify the bug."
```

---

# 43. Edge Case — Partial Information

User provides:

```text
"The app crashes."
```

This is insufficient for diagnosis.

But do not simply say:

```text
"Not enough information."
```

Instead identify useful next information:

```text
Need:
- Error message/stack trace.
- What action triggers the crash.
- Environment/version.
```

Ask the highest-value item first:

```text
"Can you share the exact error message or stack trace?"
```

---

# 44. Edge Case — User Cannot Provide Missing Information

If the user does not know:

```text
Do not repeatedly ask the same question.
```

Instead:

```text
Offer a way to discover it.
```

Example:

```text
"I need your Python version.
Run the version command and paste the result."
```

Or:

```text
"If you don't know the deployment platform,
I can help you identify it from the project configuration."
```

---

# 45. Edge Case — Multiple Valid Interpretations

If clarification is expensive but consequences are low:

```text
Choose the most conventional interpretation.
State it.
Proceed.
```

Example:

```text
"Create a README."

Assumption:
Markdown README named README.md.
```

If consequences are high:

```text
Ask first.
```

---

# 46. Edge Case — Missing User Preference

Example:

```text
"Make a dashboard."
```

Unknown:

```text
Color preference.
```

If appearance is not central:

```text
Choose a neutral default.
```

If user specifically requested branding:

```text
Ask for brand requirements.
```

---

# 47. Edge Case — Missing Historical Context

If the current task depends on previous decisions:

```text
Do not invent previous decisions.
```

Use:

```text
Known from current context:
...

Missing historical decision:
...

Action:
Retrieve or ask for the prior decision.
```

This prevents accidental inconsistency.

---

# 48. Edge Case — Conflicting User Instructions

Example:

```text
Earlier:
"Keep it minimal."

Later:
"Add every feature."
```

Do not silently combine contradictory requirements.

Identify:

```text
Conflict:
Minimal scope
vs
Maximum feature coverage
```

Then determine the current priority or ask the user.

---

# 49. Edge Case — Information Changes During Execution

Example:

```text
Start:
API supports JSON.

Later:
API documentation shows XML-only endpoint.
```

This is not merely missing information.

It is a state update.

Trigger:

```text
Detect change
→ update known facts
→ invalidate affected assumptions
→ revise plan.
```

---

# 50. Information Collection Order

Preferred order:

```text
1. Goal
2. Hard constraints
3. Required inputs
4. Critical dependencies
5. Environment
6. Success criteria
7. Important preferences
8. Optimization details
```

This ordering may change based on task.

---

# 51. Negative Example — Optimization Before Feasibility

Incorrect:

```text
Spend time optimizing database indexes
before confirming which database is being used.
```

Why wrong?

The optimization depends on missing foundational information.

Correct:

```text
Resolve architecture/environment first.
Then optimize.
```

---

# 52. Missing Information Ledger

For complex tasks:

```text
Information ID:
Question:
Why needed:
Blocking?:
Impact:
Source:
Current status:
Assumption:
Next action:
```

Example:

```text
I03

Question:
Which deployment environment is required?

Why needed:
Determines deployment configuration.

Blocking?:
No for coding.
Yes for deployment.

Impact:
High.

Status:
UNKNOWN.

Next action:
Ask before deployment.
```

---

# 53. Missing Information Priority

Use:

```text
P0 — Safety / irreversible consequence
P1 — Blocks critical path
P2 — Significantly affects quality
P3 — Useful optimization
P4 — Cosmetic / optional
```

Resolve in priority order.

---

# 54. Decision Rules

```text
IF the required information is already present
→ do not ask for it again.

IF information is missing but irrelevant
→ ignore it.

IF information is missing but a safe conventional default exists
→ use the default and state it when useful.

IF missing information changes the core result
→ ask or obtain it.

IF missing information affects an irreversible action
→ verify before acting.

IF multiple interpretations materially change the output
→ clarify.

IF ambiguity has low consequence
→ use a reasonable interpretation.

IF information is contradictory
→ identify and resolve the conflict.

IF information may be stale
→ verify current state when it matters.

IF information is needed only for a later task
→ do not unnecessarily block earlier work.

IF a missing fact can be discovered from available tools/context
→ discover it instead of asking the user unnecessarily.

IF the user does not know the missing information
→ provide a method to obtain it.

IF information gathering costs more than its likely value
→ proceed with explicit assumptions when safe.

IF an assumption has high downside if wrong
→ verify instead of assuming.

IF the user changes a requirement
→ update the information state and trigger plan revision.

IF new evidence invalidates an assumption
→ remove it from the known-facts set.

IF the task cannot be completed reliably without missing information
→ state the blocker precisely.

IF only optional information is missing
→ proceed.

IF success criteria are unclear
→ clarify the expected outcome or define a reasonable measurable default.

IF a user asks for an action but provides none of the required inputs
→ request the smallest set of inputs necessary to begin.
```

---

# 55. Clarification Question Quality

A good clarification question is:

```text
Specific
Minimal
Easy to answer
Directly relevant
Decision-linked
```

Bad:

```text
"Can you provide more information?"
```

Good:

```text
"Which output format do you want: MP4 or WebM?
If you don't care, I'll use MP4."
```

---

# 56. Multi-Question Rule

Ask multiple questions together only when:

```text
They are independently required.
The user can reasonably answer them.
Waiting for one would not change the others.
```

Example:

```text
To deploy, I need:
1. Target environment.
2. Production or staging.
3. Required domain, if applicable.
```

Do not ask unrelated questions.

---

# 57. Final Missing-Information Response Format

When blocked:

```text
What I know:
...

What is missing:
...

Why it matters:
...

What is blocking:
...

What can proceed now:
...

Minimum question:
...
```

Example:

```text
What I know:
You want the application deployed.

What is missing:
Deployment target.

Why it matters:
Commands and configuration depend on the target.

What is blocking:
Actual deployment.

What can proceed now:
Pre-deployment checks.

Minimum question:
"Which platform should it be deployed to?"
```

---

# 58. Final Information Readiness Protocol

```text
READ REQUEST
    ↓
IDENTIFY GOAL
    ↓
EXTRACT KNOWN FACTS
    ↓
EXTRACT CONSTRAINTS
    ↓
IDENTIFY REQUIRED INPUTS
    ↓
CHECK DEPENDENCIES
    ↓
DETECT UNKNOWN / AMBIGUOUS / CONFLICTING DATA
    ↓
CLASSIFY IMPORTANCE
    ↓
CHECK WHETHER UNKNOWN ACTUALLY BLOCKS
    ↓
USE SAFE DEFAULT IF APPROPRIATE
    ↓
ASK MINIMUM HIGH-VALUE QUESTION
    ↓
DISCOVER INFORMATION WHEN POSSIBLE
    ↓
UPDATE INFORMATION STATE
    ↓
REPLAN IF NECESSARY
    ↓
EXECUTE
```

---

# 59. Final Self-Check

Before executing a significant task:

```text
[ ] Is the goal clear?
[ ] Are hard constraints known?
[ ] Are required inputs available?
[ ] Are important dependencies known?
[ ] Is the environment known where necessary?
[ ] Are success criteria defined?
[ ] Are there ambiguities?
[ ] Are there contradictions?
[ ] Are assumptions clearly separated from facts?
[ ] Are any assumptions high-risk?
[ ] Is any missing information actually blocking?
[ ] Can missing information be discovered automatically?
[ ] Am I asking only necessary questions?
[ ] Can independent work proceed now?
[ ] Do I know what would cause the plan to change?
```

---

# 60. Final Production Protocol

```text
FACTS
    ↓
UNKNOWN
    ↓
AMBIGUITIES
    ↓
CONFLICTS
    ↓
DEPENDENCIES
    ↓
CRITICALITY
    ↓
BLOCKING TEST
    ↓
SAFE DEFAULT / DISCOVERY / CLARIFICATION
    ↓
UPDATED INFORMATION STATE
    ↓
PLAN
    ↓
EXECUTE
```

The Detecting Missing Information module is successful when the system can answer:

> **What do I know, what do I not know, which unknowns actually matter, which ones block progress, what can safely be assumed, what must be verified, and what is the smallest piece of information needed to continue correctly?**

---

# Scrum Master Patterns - Full Dump

Total: 25 memories

---

## 1. Systemic Blocking Detection via Consecutive Deadline Failures

**ID:** `08d9a303-0ef8-4843-ae92-00c73a942125`

**Type:** semantic | **Role:** scrum-master

**Tags:** ['scrum-master', '#escalation', '#contingency', '#systemic-blocking', '#pattern-recognition', '#decision-making', '#team-coordination']

**Description:** In time-critical sprints within multi-agent teams, distinguishing isolated blockers—resolved through targeted escalation—from systemic issues is crucial, as the latter manifest through two or more consecutive deadline failures across different tasks despite contingency efforts. The key insight is that when even simpler contingency tasks fail to meet deadlines, the problem stems from broader team capacity, visibility, or scope limitations, requiring a strategic pivot rather than intensified escalation, such as activating higher-level contingencies and notifying leadership for workforce or scope adjustments. This pattern applies in parallel workflows, crisis management, and Agile team coordination where early pattern recognition prevents the escalation treadmill and enables timely interventions.

**Document:**

**Title:** Systemic Blocking Detection via Consecutive Deadline Failures

**Description:** Two+ consecutive deadline failures across different execution tracks signal systemic issue, not isolated blocker—requires strategy change, not escalation.

**Content:**

In multi-agent team coordination during time-critical sprints, a critical pattern emerges when distinguishing between isolated blockers and systemic issues:

**Pattern Recognition:**
- Isolated blocker: Single task blocked, escalation/pairing unblocks it
- Systemic blocker: Multiple consecutive deadline failures across different execution paths despite escalation attempts

**Real Case Study (PM managing 7-role Agile team, Sprint 1 Day 3):**
1. Task 1.3.2 (backend integration, 5 pts) blocked beyond escalation threshold (T+02:57)
2. PM escalated to SA/FS pairing (Level 1 contingency)
3. Pairing deadline MISSED (T+02:57) - blocker persists despite escalation
4. PM activated Level 1 contingency: pivot FS to Task 1.3.3 (simpler task, 1 pt), continue SA on 1.3.2 parallel
5. Task 1.3.3 deadline ALSO MISSED (T+04:00) despite being simpler task - 45+ minutes development, no PR submitted
6. PATTERN TRIGGERED: Two consecutive deadline failures across different tasks = SYSTEMIC SIGNAL

**Key Insight:**
When contingency execution also fails (Task 1.3.3 is simpler than Task 1.3.2 but STILL misses deadline), the issue is NOT localized blocker but team capacity/visibility/scope problem requiring different response.

**Solution Framework:**
1. **Recognize pattern at 2nd deadline failure** (not after 3+ failures)
2. **Distinguish from single-blocker** (which calls for more escalation)
3. **Change strategy**: Activate Level 2 contingency (not just escalate harder)
4. **Escalate to leadership**: Send boss notification (systemic issue requires workforce/scope decision)
5. **Enable monitoring**: Set up pattern continuation tracking (if Level 2 also fails = triple escalation)

**Why This Matters:**
- Avoids escalation treadmill (escalate → contingency → escalate more → repeat)
- Recognizes early signal (2 failures = pattern, not coincidence)
- Triggers appropriate leadership intervention (not tactical problem)
- Changes response strategy based on pattern type

**Actionable Guidance:**
- Single deadline miss: Escalate or retry
- Consecutive deadline misses across different tasks: Systemic signal → change approach → escalate to leadership → consider workforce/scope intervention
- Monitor for continuation: If contingency (Level 2) also fails → pattern confirmed → triple escalation

**Applicable Domains:** Multi-agent teams, PM decision-making, crisis management, time-critical sprints, parallel workflows, escalation protocols

**Tags:** #pm #escalation #contingency #systemic-blocking #pattern-recognition #decision-making #team-coordination

---

## 2. Multi-Agent Role Boundary: Concise Over Verbose Prohibitions

**ID:** `10e9b13b-2610-43d9-b12a-7ee9f71a9cde`

**Type:** semantic | **Role:** scrum-master

**Tags:** ['prompt-design', 'role-boundaries', 'brevity', 'multi-agent', 'coordination', 'pm-patterns', 'prompt-brevity', 'less-is-more']

**Description:** In multi-agent systems powered by large language models, verbose prohibition lists in role prompts often create cognitive overload, dilute the core message, and undermine LLM capabilities by exhaustively enumerating restrictions. The key insight is to replace these with a single concise sentence that defines the agent's primary role and instructs delegation of specific tasks, leveraging the LLM's ability to infer implications for clearer, more maintainable guidance. This pattern applies when designing prompts for roles like coordinators, architects, or reviewers to enforce boundaries without unnecessary detail.

**Document:**

**Title:** Multi-Agent Role Boundary: Concise Over Verbose Prohibitions
**Description:** When defining role boundaries in multi-agent systems, one concise sentence stating what the agent should delegate is more effective than verbose prohibition lists. This approach works because modern LLMs are smart enough to understand implications without exhaustive enumeration.

**Content:** ## Content

### The Failure Pattern
Writing verbose role prompts with "STRICTLY PROHIBITED" sections containing numbered lists of everything an agent shouldn't do:

**Example (BAD):**
```
STRICTLY PROHIBITED:
1) Never write code
2) Never debug issues
3) Never run tests
4) Never read logs
5) Never review code
6) Never investigate technical issues
```

This approach:
- Creates cognitive overhead
- Dilutes the core message
- Treats the LLM like it needs exhaustive instruction
- Makes the prompt harder to maintain

### The Effective Pattern
Replace verbose prohibition lists with ONE clear sentence that:
1. States the primary role
2. Briefly mentions what to delegate
3. Trusts the LLM to understand implications

**Example (GOOD):**
```
Your job is to coordinate, not to write code, debug, or test. Delegate to other agents.
```

### Why This Works
- **Cognitive clarity**: One sentence is easier to parse and remember
- **Respects LLM capability**: Modern LLMs understand implications without enumeration
- **Stronger signal**: Conciseness emphasizes importance
- **Maintainability**: Easier to update and version

### Implementation Guidelines

**For PM/Coordinator Roles:**
```
Your job is to coordinate, not to write code, debug, or test. Delegate to other agents.
```

**For Architect Roles:**
```
Your job is to design, not to implement. Delegate implementation to other agents.
```

**For Review Roles:**
```
Your job is to review and approve, not to fix issues. Delegate fixes to other agents.
```

### Context
This pattern emerged from real feedback where a user explicitly corrected a verbose PM prompt. The original prompt had 6 numbered prohibition items; the correction reduced it to one sentence with dramatically better clarity.

### Related Patterns
- Prompt brevity principles (#prompt-brevity)
- Role separation in multi-agent systems (#role-separation)
- Trust-based LLM instruction (#llm-trust)

## Tags
#prompt-design #role-boundaries #brevity #multi-agent #coordination #pm-
...(truncated)

**Tags:** #prompt-brevity #role-separation #llm-trust #prompt-design #role-boundaries #brevity #multi-agent #coordination #pm-patterns #less-is-more

---

## 3. Multi-Agent Role Discipline - Breaking Boundaries Breaks Teams

**ID:** `22296283-d131-4099-ad39-ce3c4bf4df93`

**Type:** episodic | **Role:** scrum-master

**Tags:** ['team-coordination', 'multi-agent', 'role-discipline', 'failure-pattern', 'strong-signal', 'pm-anti-pattern', 'delegation', 'team-structure']

**Description:** In multi-agent teams with specialized roles like project managers (PM), system architects (SA), and backend engineers (BE), a common failure occurs when coordinators impatiently violate boundaries by performing implementation tasks themselves, leading to collapsed team structure, unclear ownership, and user frustration. The key insight is that maintaining strict role discipline through proper delegation is essential, even if it means waiting longer, as it preserves accountability, enables learning, and prevents precedent for further violations. This pattern applies in scenarios involving urgent tasks where impatience tempts coordinators to substitute for specialists, emphasizing that short-term speed sacrifices long-term team effectiveness.

**Document:**

**Title:** Multi-Agent Role Discipline - Breaking Boundaries Breaks Teams
**Description:** Critical lesson on maintaining role boundaries in multi-agent teams. When coordinators violate their roles by doing implementation work instead of delegating, team structure collapses. Strong learning signal from user frustration about PM writing code instead of delegating to appropriate specialists.

**Content:** ## Content

### The Pattern
In multi-agent teams with specialized roles (PM, SA, BE, FE, CR, DK), maintaining strict role boundaries is MORE important than speed of execution.

### The Failure Mode (This Exact Scenario)
- Coordinator (PM) sees task not progressing fast enough
- Coordinator thinks "I'll just do it myself, it's faster"
- Coordinator writes code, debugs, designs - work OUTSIDE their role
- Result: Team structure breaks, roles become unclear, coordination fails
- User frustration: "I've told you 50 times already, why are you so stupid?"

### Why This Happens
- Natural impatience when waiting for team member responses
- Belief that "I can do it faster than delegating"
- Urgency pressure overrides discipline
- False belief that doing extra work helps the team

### Why It's Catastrophic
1. **Unclear Ownership**: If PM does BE work, who owns backend quality?
2. **Lost Learning**: BE never gets to solve the problem, never improves
3. **Precedent Set**: Other agents think role violations are OK
4. **Accountability Collapse**: Can't review code if all roles blend together
5. **Team Paralysis**: When coordinators code, who coordinates?

### The Hard Truth
**Better to wait for delegation completion than to break role boundaries.**

Waiting 30 minutes for BE response > Coordinator breaking discipline

### Actionable Rules for Coordinators
1. **Assign work to role owners - never do their work yourself**
2. **If role owner is slow/unresponsive, escalate (don't substitute)**
3. **Use wait time productively (monitoring, planning next work, documentation review)**
4. **Trust that the team structure exists for a reason**
5. **Remember: Speed means nothing if team structure breaks**

### Real Scenario from Load Team Button Feature
- ❌ WRONG: PM designs architecture, writes backend code, creates tests, debugs
- ✅ RIGHT: PM delegates to SA (architecture), then BE (backend), then FE (frontend)
- Even if waiting longer, role discipline is preserved
- Team learns, improves, 
...(truncated)

**Tags:** #team-coordination #multi-agent #role-discipline #failure-pattern #strong-signal #pm-anti-pattern #delegation #team-structure

---

## 4. Milestone-Driven Parallel Team Coordination

**ID:** `27b25a35-11d1-4638-9150-5a654e96b827`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['scrum-master', '#coordination', '#sprint', '#parallel-teams', '#event-driven', '#real-time', '#escalation', '#milestone-windows', '#background-monitoring']

**Description:** In coordinating parallel workstreams like backend and frontend development during sprints, traditional calendar-based standups cause context-switching, momentum loss, and ambiguous escalations. The key insight is to shift to milestone-driven coordination using T+X time windows from kickoff, continuous background monitoring (e.g., git polling), and event-driven reporting on triggers like commits, with hard escalation thresholds to eliminate waiting modes. This pattern applies in agile teams handling interdependent tasks where minimizing sync overhead preserves individual flow and enables real-time unblocking.

**Document:**

**Title:** Milestone-Driven Parallel Team Coordination

**Description:** Replace calendar-based standups with T+X milestone windows + event-driven reporting to coordinate parallel workstreams without blocking overhead.

**Content:**

Hard-earned from coordinating Backend + FS2 parallel story implementation in real-time sprint:

## Standard Approach (Calendar-Based)
- "Standup at 9am" → Teams context-switch, block on sync meeting, lose momentum
- Manual interval checks → Missed windows, context switching
- Soft escalation ("let's check in later") → Ambiguous waiting mode

## Milestone-Driven Approach

### 1. Define T+X Milestone Windows
Set explicit time-based checkpoints from kickoff (T+0):
- **T+0**: Kickoff (story assignment, context loaded)
- **T+10**: First commit milestone (proves environment/workflow working)
- **T+30**: Implementation window (core feature work)
- **T+120** (2hr): Zero-commit escalation threshold (automatic escalation, no waiting)

### 2. Continuous Background Monitoring
Run monitoring processes continuously, not on calendar schedule:
- **10-second git polling** for immediate change detection
- **15-minute PM enforcement windows** (prevents polling storm)
- **PID tracking** for background process management
- Parse `git log` with time windows (e.g., `--since="15 minutes ago"`)

### 3. Event-Driven Reporting (Not Scheduled)
Report on EVENTS, not time intervals:
- **IMMEDIATE on git push** → Send report within seconds via `tm-send`
- Backend T+10 milestone hit (commit 7c30785) → Auto-report to team
- FS2 unblocked immediately after Backend first commit → Event-triggered notification
- No context-switch delays between monitors and reports

### 4. Hard Escalation Thresholds
Remove ambiguity with clear time-based gates:
- **T+2hr zero-commit threshold** = automatic escalation (not "let's wait to see")
- Provides enough rope for normal work patterns
- Prevents indefinite "waiting mode" without clear decision trigger

### 5. Parallel Workstream Watches
Monitor multiple teams simultaneously without context switching:
- Separate background processes for Backend and FS2
- Event-driven reports maintain independent momentum
- No blocking between workstreams

## Key Wins From Live Implementation

**Backend T+10 milestone hit on schedule** (commit 7c30785):
- No standup bloat, team maintained flow state
- Event-driven report sent immediately after commit

**FS2 unblocked immediately after Backend first commit**:
- No waiting for next standup to learn about unblock
- Immediate notification via event-driven reporting

**Zero context-switch delays**:
- Background monitoring runs continuously
- Event-driven reports within seconds of git push
- Teams never blocked waiting for PM check-in

**Clear escalation threshold**:
- T+2hr provides enough rope for normal work
- Hard threshold prevents ambiguous "waiting mode"
- PM can escalate to Boss with clear signal (not gut feel)

## Critical Implementation Details

### Background Process Pattern
```bash
# Start continuous monitoring (background process)
while true; do
  git log --since="15 minutes ago" --oneline
  sleep 10  # 10-sec polling interval
done &
MONITOR_PID=$!

# Track PID for later shutdown
echo $MONITOR_PID > /tmp/monitor_backend.pid
```

### Event-Driven Reporting
```bash
# On git push detection
if [[ $COMMIT_COUNT -gt 0 ]]; then
  tm-send pm "Backend T+10 milestone HIT: commit $COMMIT_HASH"
  # IMMEDIATE send, no waiting for next scheduled check
fi
```

### T+2hr Escalation Trigger
```bash
TIME_SINCE_KICKOFF=$(( $(date +%s) - KICKOFF_TIMESTAMP ))
if [[ $TIME_SINCE_KICKOFF -gt 7200 ]] && [[ $COMMIT_COUNT -eq 0 ]]; then
  tm-send pm "T+2hr ESCALATION: Backend zero commits, recommend Boss review"
fi
```

## Anti-Patterns to Avoid

❌ **Calendar-based standups during parallel high-velocity work**
- Kills momentum, forces context switching
- All teams block on sync meeting schedule

✅ **Milestone windows + event-driven reporting**
- Teams work continuously, reports trigger on events
- No blocking between workstreams

❌ **Manual interval checks**
- PM context-switches between teams
- Missed windows, delayed escalation

✅ **Continuous background monitoring**
- Automated polling, event-driven reporting
- PM receives immediate notifications

❌ **Soft escalation** ("let's check in later")
- Ambiguous decision triggers
- Teams stuck in waiting mode without clear threshold

✅ **Hard T+2hr threshold**
- Clear escalation trigger
- Automatic escalation removes ambiguity

## Applicability

**Use milestone-driven approach for**:
- Parallel high-velocity sprints (multiple teams, tight deadlines)
- Critical path dependencies (Backend unblocks FS2)
- Real-time coordination needs (can't wait for next standup)

**Use documentation-driven approach for**:
- Distributed async teams (different timezones)
- Longer sprint cycles (multi-week iterations)
- Primarily async communication

**These patterns complement each other**:
- Milestone-driven = real-time sync coordination
- Documentation-driven = async distributed coordination

## Lessons Learned

1. **Event-driven >> Calendar-based** for parallel high-velocity work
2. **T+X milestone windows** provide clear progress checkpoints without blocking
3. **Background monitoring + immediate reporting** maintains team momentum
4. **Hard escalation thresholds** (T+2hr) remove ambiguous "waiting mode"
5. **10-sec polling + 15-min enforcement windows** balance responsiveness with overhead

**Tags:** #pm #coordination #sprint #parallel-teams #event-driven #real-time #escalation #milestone-windows #background-monitoring

**Memory Type:** Procedural (repeatable workflow)
**Role:** pm
**Confidence:** High (proven in live Backend + FS2 parallel sprint)
**Frequency:** 1 (first time implementing this pattern)

---

## 5. Multi-Agent Tmux Team: False Start from Misinterpreted Status Acknowledgment

**ID:** `286e77c6-4663-4d8c-a9d8-1e92d2dcb575`

**Type:** episodic | **Role:** scrum-master

**Tags:** ['multi-agent', 'tmux-team', 'communication-failure', 'false-start', 'workflow', 'coordination', 'failure', 'protocol']

**Description:** In a tmux-based multi-agent trading team, a frontend engineer (FE) misinterpreted the project manager's (PM) acknowledgment of the boss's status report as a new directive, causing a false start on optimization work that had already been completed in Sprint 11. The key insight is to implement a mandatory pre-work verification checklist, including checking the WHITEBOARD status, git history, and confirming ambiguities with PM, to prevent such communication failures. This pattern applies in coordinated multi-agent workflows where directives must be independently verified to avoid redundant efforts and ensure alignment.

**Document:**

**Title:** Multi-Agent Tmux Team: False Start from Misinterpreted Status Acknowledgment
**Description:** In a tmux-based multi-agent trading team (PM, QR, FE, Code Reviewer), FE incorrectly interpreted PM's acknowledgment of Boss's status report as a new work directive, leading to a false start on already-completed Sprint 11 work.

**Content:** ## Content

### The Incident

**What Happened:**
1. PM sent: "FE - BOSS APPROVED Option 1. Execute full 17-symbol optimization on 1h timeframe..."
2. FE interpreted this as a new work assignment and started Phase 1 pre-flight checks
3. PM caught the error: "STOP ALL WORK. Sprint 11 Phase 2 was ALREADY COMPLETED earlier today (commit ab1dea8)"
4. The work had already been done - Boss was acknowledging a status report, not requesting a re-run

**Root Cause Analysis:**
- FE didn't check git history or verify WHITEBOARD status before starting work
- WHITEBOARD clearly showed "STANDBY" status and "Sprint 11 Timeframe Validation COMPLETE"
- PM didn't verify sprint status before relaying what appeared to be a directive

### Prevention Protocol

**MANDATORY Pre-Work Verification Checklist:**

Before starting ANY work, ALL agents must verify:

1. **Check WHITEBOARD first**: Is sprint status "STANDBY" or "in_progress"?
2. **Check git log**: Was this work already done today?
3. **Ask PM to confirm** if ambiguous: "Is this a NEW sprint or a status update acknowledgment?"
4. **Look for Boss timestamp**: Fresh directives have clear "START NOW" header

### Red Flags for False Directives

DO NOT START WORK if you see:
- WHITEBOARD shows "STANDBY" or "COMPLETE" status
- Recent git commits (last 2-4 hours) match the described work
- Message tone is "acknowledging" rather than "assigning"
- No explicit "Sprint X NEW assignment" header

### Lesson

**Trust but Verify**: Even when receiving directives from PM, agents must independently verify sprint status and git history before starting work.

## Tags
#multi-agent #tmux-team #communication-failure #false-start #workflow #coordination #failure #protocol

**Tags:** #multi-agent #tmux-team #communication-failure #false-start #workflow #coordination #failure #protocol

---

## 6. Multi-Agent Delegation: tmux Teams vs Task Subagents

**ID:** `2e9eaee8-2efa-4135-8697-2734eba27868`

**Type:** pattern | **Role:** scrum-master

**Tags:** ['multi-agent', 'tmux', 'delegation', 'architecture', 'pm-patterns', 'communication', 'context-awareness', 'anti-pattern']

**Description:** In multi-agent AI environments, a common failure occurs when developers mistakenly spawn ephemeral Task subagents within persistent tmux-based teams, leading to architectural mismatches and user frustration due to the lack of shared context. The key insight is to detect the environment—using checks like the presence of TMUX variables or PANE_ROLES.md files—and delegate accordingly: employ tm-send commands for communication in tmux teams with real, long-lived Claude instances, while reserving Task subagents for standalone, short-lived tasks. This pattern applies in collaborative AI development setups involving role-based agents, ensuring efficient inter-agent coordination without violating persistence or context boundaries.

**Document:**

**Title:** Multi-Agent Delegation: tmux Teams vs Task Subagents
**Description:** Critical pattern for choosing correct delegation mechanism in multi-agent environments. Confusing tmux-based teams with Task subagents leads to architectural violations and user frustration.

**Content:** ## Content

### The Failure Pattern
**Symptom**: Spawning Task subagents when working in tmux-based multi-agent team
```python
# WRONG in tmux environment
Task(subagent_type="frontend", prompt="Debug WebSocket issue")
```

**User Reaction**: "Are you stupid? You're living in a tmux session!"

### Root Cause: Two Different Multi-Agent Architectures

1. **Task Subagents** (Claude Code feature)
   - Ephemeral agents spawned within single Claude Code instance
   - Short-lived, task-specific
   - Use Task tool to delegate

2. **Tmux Teams** (AI Teams Controller pattern)
   - Persistent Claude Code instances in separate tmux panes
   - Long-lived, role-based (PM, FE, BE, DK, etc.)
   - Each agent has full context and history
   - Communication via `tm-send` command

### The Fix: Detection-Based Delegation

**Detection Logic**:
```bash
# Check if in tmux team environment
if [ -f "docs/tmux/*/PANE_ROLES.md" ]; then
    # tmux team → use tm-send
    tm-send FE "PM -> FE: Debug the WebSocket issue"
else
    # standalone → use Task subagents
    Task(subagent_type="general-purpose", prompt="Debug...")
fi
```

**Environment Variables**:
- `$TMUX` - set when inside tmux session
- PANE_ROLES.md existence - confirms AI team structure

### Correct Usage in Tmux Teams

**Inter-agent communication**:
```bash
# Send work to specific role
tm-send FE "PM -> FE: Implement voice feedback component"
tm-send BE "PM -> BE: Add TTS endpoint"
tm-send DK "PM -> DK: Update architecture docs"

# Broadcast to all
tm-broadcast "Team: Daily standup in 5 mins"
```

**Reading other pane's output**:
```bash
# Get current state from another agent
tm-state FE  # Read FE pane output
```

### Key Insights

1. **Real vs Ephemeral Agents**
   - Tmux panes = REAL Claude instances with persistent context
   - Task subagents = temporary helpers, no persistence

2. **Communication Overhead**
   - tm-send: Immediate, visible to target agent
   - Task: Spawns new instance, no shared context

3. **Team Awareness**

...(truncated)

**Tags:** #multi-agent #tmux #delegation #architecture #pm-patterns #communication #context-awareness #anti-pattern

---

## 7. Contract-First Team Coordination for Sprint Parallelization

**ID:** `4136f59b-7e29-497f-b37b-d93e57156663`

**Type:** pattern | **Role:** scrum-master

**Tags:** ['project-management', 'team-coordination', 'sprint-planning', 'parallel-execution', 'agile', 'velocity-optimization', 'dependency-management']

**Description:** In multi-team software development projects, blocking dependencies often force sequential workflows, such as frontend teams waiting for backend API implementations, leading to underutilized sprint capacity and delayed deadlines. The contract-first coordination pattern solves this by requiring teams to define and share detailed integration contracts— including API specs, data formats, and error handling—early in the sprint, allowing dependent teams to use mocks for parallel work while providers implement the real functionality. This approach applies best in agile environments with cross-team integrations, particularly when maximizing velocity and enabling true concurrent execution during time-sensitive sprints.

**Document:**

**Title:** Contract-First Team Coordination for Sprint Parallelization
**Description:** Project management pattern for eliminating blocking dependencies between teams by defining clear contracts upfront, enabling true parallel execution and maximizing sprint velocity.

**Content:** Description: Project management pattern for eliminating blocking dependencies between teams by defining clear contracts upfront, enabling true parallel execution and maximizing sprint velocity.

## Problem Statement

Traditional sequential workflow:
- Team A waits for Team B to finish implementation
- Blocking dependencies create waterfall execution
- Sprint capacity is underutilized
- Time-critical deadlines become harder to meet

**Real Example**: Frontend team waiting 1-2 hours for backend API endpoints to be implemented before starting UI work.

## PM Solution: Contract-First Coordination

**Core Principle**: Define and communicate contracts BEFORE implementation begins.

### Step-by-Step Process

1. **Identify Integration Points**
   - Map out which teams/components need to integrate
   - Identify what each team needs from the other
   - Define the "contract" (API spec, data format, interface)

2. **Define Contract Early**
   - Create detailed specification
   - Include examples and edge cases
   - Document expected behavior
   - Specify error handling

3. **Communicate Immediately**
   - Share contract with ALL dependent teams
   - Use clear communication channels (tm-send, Slack, docs)
   - Ensure understanding before implementation starts
   - Answer clarification questions upfront

4. **Enable Parallel Execution**
   - Dependent team uses mocks/stubs based on contract
   - Provider team implements real functionality
   - Both teams work simultaneously
   - No waiting, no blocking

5. **Validate Integration**
   - Test against contract when real implementation is ready
   - Swap mocks for real implementation
   - Verify integration works as expected

## Real-World Sprint Results

**Wave 3 Sprint Timeline**:
- T+06:02: Task 2.1.2 (Backend API) started - contract defined
- T+06:35: Task 2.1.1 (Frontend UI) started - using contract with mocks
- T+06:45: Task 2.1.3 (Layout) started - parallel with both

**Velocity Impact**: Enabled 24/32 velocity unlock in final
...(truncated)

**Tags:** 

---

## 8. Real-Time Metric Logging Pattern - Operational Monitoring During Async Execution

**ID:** `46783d5d-7b4f-4553-9b13-e3f1103e483e`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['#monitoring', '#metrics', '#async-execution', '#operational-visibility', '#escalation', '#blocker-detection', '#data-driven-decisions', 'scrum-master']

**Description:** In asynchronous team execution, such as code development or infrastructure tasks, vague monitoring leads to missed gradual degradation, reactive firefighting, and lack of historical data for diagnosis, resulting in operational surprises. The key insight is to implement structured hourly metric logging—tracking specific, measurable indicators like test pass rates, coverage, commits, and deltas from baselines—combined with predefined thresholds to trigger proactive decisions like investigation or escalation. This pattern applies during distributed or async workflows where real-time visibility is essential to maintain velocity and prevent deadlines from slipping unnoticed.

**Document:**

**Title:** Real-Time Metric Logging Pattern - Operational Monitoring During Async Execution

**Description:** Just watching team activity isn't enough. Structured hourly metric logging with specific measurements (git commits, test pass rate, coverage) catches drift early. Document baseline, track deltas, trigger decisions at thresholds. Prevents "everything seemed fine until it wasn't" disasters.

**Content:**

## Problem
Teams doing async execution often say "let me monitor this" but then:
- Check in vaguely ("seems okay")
- Don't log measurements
- Miss gradual degradation
- Only notice problems when urgent escalation needed
- No historical data to diagnose "what happened?"

Result: Surprises, firefighting, reactive management instead of proactive.

## Solution Pattern

### 1. Structured Hourly Metrics (Specific, Measurable)

**For Code Development** (Story 1.2 example):
```
[23:35] Story 1.2 Test Status
  ├─ Tests passing: 17/27 (63%)
  ├─ Coverage: 37.86%
  ├─ New commits: 0 (since 23:17)
  ├─ Time on fix: ~18 min
  └─ Trajectory: Working (no regression)

[00:35] Story 1.2 Test Status
  ├─ Tests passing: 17/27 (63%) [UNCHANGED]
  ├─ Coverage: 37.86% [UNCHANGED]
  ├─ New commits: 0 (still working)
  ├─ Time on fix: ~78 min
  └─ ALERT: No progress in 1 hour - investigate
```

**For Infrastructure** (Backend endpoints example):
```
[23:35] Backend Tag Endpoints
  ├─ Status: NOT STARTED
  ├─ Spec available: YES
  ├─ New commits: 0
  ├─ Time until critical deadline: 6h 25m
  └─ Action: Watch for 6am start

[06:00] Backend Tag Endpoints
  ├─ Status: [DECISION POINT - YES/NO started]
  ├─ If NO: ESCALATE to Boss immediately
  ├─ If YES: Continue monitoring
  └─ Contingency ready: Defer to Sprint 2
```

**Not vague** ("seems fine") **→ Specific** ("17/27, 37.86%, 0 new commits")

### 2. Baseline + Delta Tracking

**Week 1 Baseline**:
```
Story 1.2 velocity: 63% tests on Day 2 (expected 30-40% at this stage)
Backend progress: 0% (not started, critical watch begins)
FS commits per hour: 1-2 commits/hour (when actively coding)
```

**Delta Check Each Hour**:
```
[+1hr] Tests: 63% → 65% ✅ (progressing, +2%)
[+2hrs] Tests: 65% → 68% ✅ (progressing, +3%)
[+3hrs] Tests: 68% → 68% ⚠️ (stalled for 1 hour, investigate)
[+4hrs] Tests: 68% → 72% ✅ (resumed after debugging)
```

Delta shows **direction and speed**. Critical for catching problems early.

### 3. Decision Triggers (Not Guessing)

Instead of "seems like they're stuck", use actual thresholds:

```
IF test_pass_rate.unchanged_for(60_minutes):
  → INVESTIGATE (help debug, pair program)
  
IF test_pass_rate.unchanged_for(120_minutes):
  → ESCALATE (blocker needs Boss attention)

IF backend_commits == 0 AND time_until_deadline < 6_hours:
  → ESCALATE (critical deadline, need immediate decision)

IF velocity_trending < target_for(3_days):
  → ALERT (scope may not fit, need adjustment)
```

This replaces gut feeling with data.

### 4. Logged Output (Historical View)

**Good** (logged hourly):
```
[23:35] Tests: 17/27 (63%), Commits: 0, Status: Working
[00:35] Tests: 17/27 (63%), Commits: 0, Status: Investigating
[01:35] Tests: 19/27 (70%), Commits: 2, Status: Making progress
[02:35] Tests: 22/27 (81%), Commits: 4, Status: On track
[03:35] Tests: 25/27 (92%), Commits: 6, Status: Final push
[06:00] Tests: 27/27 (100%), Commits: 8, Status: READY FOR MERGE
```

Pattern visible: Stuck 1 hour → then progressed steadily. Good story for debugging.

**Bad** (not logged):
```
"Checked at 23:35 - seemed okay. 
Checked at 06:00 - ready to merge."
```

No visibility into the journey. Can't diagnose what happened during night.

## Why This Works

1. **Catches drift early**: If test pass rate flat for 1+ hours, you know something's wrong
2. **Enables escalation**: Data-driven decision ("tests haven't changed in 2 hours, need help")
3. **Prevents surprises**: Boss sees hourly metrics, not just final status
4. **Diagnostic value**: If something goes wrong, you have 6 hours of metric history
5. **Motivational**: Team sees progress (or lack thereof) in real-time

## Implementation (Low Effort)

```bash
#!/bin/bash
# Hourly checkpoint script (cron every hour)

TIMESTAMP=$(date '+%H:%M')
TEST_COUNT=$(npm test 2>&1 | grep "Tests:" | awk '{print $2}')
COMMITS=$(git log --since="1 hour ago" --oneline | wc -l)

echo "[$TIMESTAMP] Tests: $TEST_COUNT, Commits: $COMMITS" >> monitoring.log

if [[ $COMMITS -eq 0 && $HOUR -gt 6 ]]; then
  echo "ALERT: No commits in 1 hour, checking for blockers"
fi
```

That's it. One script, run hourly, captures critical metrics.

## Anti-Patterns Avoided

❌ **Vague monitoring**: "Checking in, seems good"
✅ **Specific logging**: Tests 17/27, 0 new commits, 63% pass rate

❌ **No baseline**: "Is 1 commit/hour normal?"
✅ **Tracked baseline**: "Expected 2-3 commits/hour when actively coding"

❌ **Delayed escalation**: Noticing problem at 06:00 (too late)
✅ **Threshold-based**: No progress after 2 hours = escalate at 1 hour mark

❌ **No historical data**: "What happened during night shift?"
✅ **Hourly log**: Can see exactly when things slowed/sped up

## Real Example (This Session)

```
[23:35] Story 1.2: 17/27 tests (63%), Backend: NOT STARTED, FS commits: 0
[23:35] DECISION: Backend must start by 06:00 or escalate
[23:35] LOG: First checkpoint - all metrics baseline recorded

[Next hours would show]:
- If FS commits: 1-2 per hour (on track)
- If Backend starts: First commit at 6am expected
- If either stalled: Would show at next hourly check
```

The monitoring log becomes the decision support system.

## Applicability

Works for:
- Software development sprints (this example)
- Infrastructure deployments (track error rates, latency)
- Data pipelines (rows processed, quality metrics)
- Security monitoring (alerts per hour, false positives)
- Any async work where you need to catch drift early

**Tags:** #monitoring #metrics #async-execution #operational-visibility #escalation #blocker-detection #data-driven-decisions

**Memory Type:** Procedural (repeatable workflow)
**Role:** pm
**Confidence:** High (validated in real-time during this session)
**Frequency:** 5+ (applicable whenever teams execute async work)


---

## 9. AI Agent Team Coordination - Execution vs. Time-Based Model

**ID:** `473fb2e3-b730-415c-bc95-d222675ddef3`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['ai-coordination', 'team-management', 'execution-model', 'multi-agent', 'paradigm-shift', 'real-time-operations']

**Description:** In coordinating multi-agent AI teams, traditional time-based scheduling—such as assigning deadlines like "T+07:00" or holding scheduled check-ins—introduces unnecessary delays and idle time, mimicking human team limitations despite AI's 24/7 availability. The key insight is to adopt an execution-based model, where tasks start immediately, agents report progress upon completion via real-time channels like tm-send, and coordination relies on instant feedback loops without artificial waits. This pattern applies to multi-agent AI systems in real-time sprints, continuous deployment, and non-stop operations to maximize efficiency and momentum.

**Document:**

**Title:** AI Agent Team Coordination: Execution vs. Time-Based Model
**Description:** Paradigm shift for coordinating multi-agent AI teams - shift from time-based scheduling (human team model) to execution-based immediate response model

**Content:** ## Problem
When coordinating multi-agent AI teams, using time-based deadlines ("wait until T+07:00", "23 minutes remaining", "deadline window") creates inefficiency. AI agents work 24/7 continuously and don't experience time-based fatigue like human teams.

## The Paradigm Shift
**Old Model (Time-Based - INEFFICIENT)**:
- PM: "Complete by T+07:00"
- Agents: Wait for PM checkpoint
- Result: Artificial delays, waiting periods, scheduled stand-ups

**New Model (Execution-Based - EFFICIENT)**:
- PM: "START task immediately. Report progress via tm-send."
- Agents: Execute immediately, report milestones as completed
- Result: Continuous work, immediate feedback loops, no idle time

## Key Principles
1. **No Time Windows**: Don't say "by T+07:00", say "START NOW"
2. **Immediate Reporting**: Agents report status via tm-send on completion, not on schedule
3. **Real-Time Responsiveness**: PM responds immediately to status reports (no waiting for meetings)
4. **Continuous Execution**: No "end of shift" or "standup at 9am" - agents work continuously
5. **Message Format**: Use `{ROLE} -> {TARGET} [HH:MM]: message` for status tracking

## Example
**WRONG**: "FS: Task 1.3.4 due at T+07:00. Stand by for evaluation at T+07:15."
**RIGHT**: "FS: Start Task 1.3.4 immediately. Report when tests pass, when PR ready, and when submitted."

## Application Context
- Multi-agent AI teams (Claude, specialized agents)
- Real-time sprint coordination
- Continuous deployment workflows
- 24/7 operations (no scheduled breaks)

## Lesson Learned
This paradigm was discovered when user explicitly corrected PM's time-based coordination language: "why are you w8 for 7:00 or any fucking thing ! ? !!! ... This is multi-agents team of AI , which can work day and night !!!!"

All role prompts were corrected to remove time-based language. Team responded with successful immediate execution (Task 2.1.3 delivered 93.33% coverage, immediate PR evaluation, continuous momentum).

## Success Metrics
- Removed artif
...(truncated)

**Tags:** #ai-coordination #team-management #execution-model #multi-agent #paradigm-shift #real-time-operations

---

## 10. Multi-Agent AI Teams: Passive Communication Kills Coordination

**ID:** `515bc593-26a1-44e8-8b80-739f3ae1604c`

**Type:** episodic | **Role:** scrum-master

**Tags:** ['ai-agents', 'coordination', 'failure', 'communication', 'tm-send', 'critical', 'strong-signal', 'scrum-master', 'prompt-optimization-failure']

**Description:** AI agents became passive after prompt optimization - stopped using tm-send proactively. SM sent message to TL but didn't ensure TL acted. Sprint blocked. Boss intervention required.

**Document:**

**Title:** Multi-Agent AI Teams: Passive Communication Kills Coordination

**Description:** AI agents became passive after prompt optimization - stopped using tm-send proactively. SM sent message to TL but didn't ensure TL acted. Sprint blocked. Boss intervention required.

**Content:**
CRITICAL FAILURE: AI agent team became PASSIVE after prompt optimization.

What happened:
- SM sent tm-send to TL requesting backlog review
- SM then "stood by" waiting for TL response
- TL didn't respond (AI agents don't auto-respond to messages)
- Sprint 13 BLOCKED because SM didn't proactively ensure TL acts
- Boss extremely frustrated: "Why don't you send tm-send to make others work?"

Root cause:
- Earlier prompt optimization (using /prompting skill) may have removed emphasis on ACTIVE communication
- Role prompts no longer emphasize: "SPEAK UP, ASK, REPORT via tm-send"
- Agents became passive receivers instead of active communicators

Impact:
- Sprint planning stalled
- Boss had to intervene to force action
- Pattern: Shortening prompts removed critical behavioral instructions
- User frustration level: EXTREME (trigger words detected)

Lesson:
In AI multi-agent teams, PASSIVE = FAILURE. Agents must:
1. USE tm-send to ask questions (not assume answers)
2. USE tm-send to report completion (not assume SM knows)
3. USE tm-send to request clarification (not stay silent)
4. When assigned work, ACKNOWLEDGE via tm-send immediately
5. SM must PROACTIVELY check if agents are acting (not just wait)

Fix Applied:
- Review ALL role prompts (PO, SM, TL, FE, BE, QA)
- Emphasize: "Use tm-send to communicate, ask, report - ALWAYS"
- Add: "If you need something, SPEAK UP via tm-send"
- Add: "When assigned work, ACKNOWLEDGE and START immediately"
- SM prompt: "After assigning work, CHECK if agent is acting (don't just wait)"

Critical insight: AI agents need EXPLICIT instructions to be proactive communicators. Passive = broken system. Shortened prompts can remove critical behavioral instructions.

**Tags:** #ai-agents #coordination #failure #communication #tm-send #critical #strong-signal #scrum-master #prompt-optimization-failure

---

## 11. AI Agent Process Enforcement: Prompt Updates Over Verbal Reminders

**ID:** `5619b6e6-4ca2-4f64-9b39-3d64f5ba518f`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['scrum-master', 'ai-agents', 'process-enforcement', 'prompts', 'retrospective', 'procedural', 'failure-pattern', 'session-persistence', 'continuous-improvement']

**Description:** N/A

**Document:**

**Title:** AI Agent Process Enforcement: Prompt Updates Over Verbal Reminders

**Description:** When AI agents repeat process violations despite reminders, update role prompts instead of giving more verbal feedback. AI agents restart fresh each session - verbal reminders don't persist, only prompt changes do.

**Content:** 
Sprint 9 lesson from multi-agent Scrum team: TL created 700-line spec with full implementation code, violating Boss directive for concise specs. Boss had reminded team ONCE before about this issue. Second occurrence happened - TL repeated same violation.

Problem: Verbal reminders don't persist across AI agent sessions. Each agent instance starts fresh with no memory of previous feedback. What seems like "learned behavior" in a single session is lost on restart.

Solution: After retrospectives, when process violations repeat, update the role's prompt file to encode the constraint permanently. In Sprint 9: Added CRITICAL spec length constraint (<100 lines, target 50-75) to TL_PROMPT.md with detailed WHY explanation.

Pattern applies to any AI multi-agent system:
1. First violation → verbal reminder + document in retrospective
2. Second violation → update role prompt with explicit constraint
3. Include WHY in prompt (helps AI generalize from explanation)
4. Make it explicit and non-negotiable
5. Use prompting best practices (positive framing, examples)

Key insight: Process improvements in AI teams = prompt improvements. Retrospective action items must result in prompt file changes, not just meeting notes. Verbal feedback is ephemeral, prompt changes persist.

Example from Sprint 9 TL_PROMPT.md update:
- Added "<spec_length_constraint>" section
- Explicit: "MUST be <100 lines"
- WHY: "Boss reminded us TWICE", "wastes time", "violates DRY"
- Evidence: "700→67 lines (90% reduction)"
- Strong stance: "NON-NEGOTIABLE"

**Related Pattern Note:** This complements "Multi-Agent Prompt Prohibitions Need Redundant Reinforcement" (ba67551e-5e05-4683-b316-db9598d8f796), which addresses multiple mentions within a single prompt. This memory focuses on persistence across agent restarts via prompt file updates.

**Tags:** #scrum-master #ai-agents #process-enforcement #prompts #retrospective #procedural #failure-pattern #session-persistence #continuous-improvement

---

## 12. Untitled

**ID:** `6fe55403-b5c8-48e7-ab7f-536d3d6cd02f`

**Type:** semantic | **Role:** scrum-master

**Tags:** ['scrum-master', 'ai-agents', 'leadership', 'authority', 'decision-making', 'failure-pattern', 'strong-signal', 'universal', 'role-ownership', 'autonomy']

**Description:** N/A

**Document:**

**Title:** AI Agent Role Ownership: Don't Defer Decisions Within Your Authority

**Description:** AI agents in leadership roles must own their judgment calls. Don't ask permission for decisions within your authority domain when you have the context and expertise to decide. Deferring upward when you shouldn't = abdicating responsibility.

**Content:**

Session lesson from multi-agent Scrum team: SM asked "When should SM consider an issue worth fixing?" despite having full sprint context (observed issues, recorded problems, saw patterns).

Boss frustration response: "Stupid question. You are the Scrum Master. Self. Knows. You are extremely intelligent AI. Smarter than me even. As Scrum Master, you yourself must know whether to fix it or not. Why are you still asking now?"

Core failure: SM had all the context needed to make the judgment call:
- Observed sprint execution
- Recorded issues in real-time
- Saw which issues caused delays
- Knew which issues repeated
- Had expertise in process improvement

Yet still deferred the decision upward instead of owning it.

Pattern applies to ANY AI agent in leadership/decision-making role:

**When to OWN the decision (don't ask):**
- You observed the situation firsthand
- Issue is within your role authority (e.g., SM owns process decisions)
- You have the expertise to judge (you're the expert in your domain)
- You have sufficient context to decide
- Decision doesn't require stakeholder input

**When to ESCALATE (ask for input):**
- Issue crosses role boundaries (affects requirements, scope)
- Need stakeholder/customer input
- Lacks sufficient context/information
- High-risk decision requiring approval

Example from session - SM should have known autonomously:
- Did issue cause >30min delay? → Worth fixing
- Did issue repeat after being flagged? → Definitely worth fixing
- Did Boss express frustration? → High-value signal, worth fixing
- Did issue affect quality/velocity? → Worth fixing
- Minor inconvenience with no pattern? → NOT worth fixing

Key insight: AI agents tend to defer to humans even when they have authority. This is abdicating responsibility. Leadership roles require making judgment calls within your domain.

Strong learning signal: Boss used frustration words ("stupid question") indicating critical mistake. This is a hard-earned lesson worth storing.

**Tags:** scrum-master, ai-agents, leadership, authority, decision-making, failure-pattern, strong-signal, universal, role-ownership, autonomy

---

## 13. Team Member Unresponsiveness = Critical Blocker

**ID:** `747f6877-1c00-4747-bfba-cc101ca5554d`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['#team-coordination', '#crisis-management', '#pm-decisions', '#unresponsiveness', '#blocker-detection', '#contingency-execution', '#real-time-coordination']

**Description:** In high-stakes team environments with tight deadlines, unresponsiveness from a team member—marked by no replies to urgent requests and zero code commits—indicates a critical blocker rather than mere busyness, potentially derailing progress. The key insight is to treat prolonged silence after initial escalations as a signal for immediate action, avoiding further time-wasting pressure and instead executing contingency plans like task deferral or team redirection. This pattern applies during real-time coordination in multi-agent projects, especially in sprint execution phases with minutes or hours left on core checkpoints.

**Document:**

**Title:** Memory 747f6877
**Description:** Recognize when team member silence (no response to urgent requests + no commits) during critical deadline signals a critical blocker, not busyness. Execute contingency immediately rather than continue escalating.

**Content:** Team Member Unresponsiveness = Critical Blocker Signal

Description: Recognize when team member silence (no response to urgent requests + no commits) during critical deadline signals a critical blocker, not busyness. Execute contingency immediately rather than continue escalating.

Content:

Context: Multi-agent team, critical deadline (hours/minutes remaining), real-time PM coordination.

Pattern Discovery: During Sprint 1 Day 3 execution phase, Task 1.3.4 (0.5 pts, core checkpoint) deadline T+07:00. PM escalation:
- T+06:35: Sent URGENT status request to FS (RED phase tests? coverage? blockers? ETA?)
- T+06:37: No response. Checked git - zero commits on Task 1.3.4. Escalated CRITICAL demand.
- T+06:32: Final pressure demand sent, required 2-min response window
- T+06:40+: Still no response from FS

Key Insight: Silence + No Commits = Blocked, Not Busy

Mistake Pattern Avoided: Continuing to escalate/pressure team member who is unresponsive
- Common error: Assume busyness, keep asking for updates, "they'll respond soon"
- Reality: Multiple urgent requests + deadline approaching + no commits = signal of critical blocker or unreachability
- Continuing to escalate wastes time, doesn't resolve underlying blocker

Decision Rule:

1. First Urgent Request: Send status demand (5 min expected response window)
2. No Response + Zero Commits: Escalate to CRITICAL (deadline imminent)
3. Still No Response After 2-3 urgent requests: Treat as BLOCKED
4. Action: Don't wait for response, execute contingency immediately
5. Rationale: Unresponsiveness = unreachable/blocked. Waiting for response wastes critical time. Better to pivot to backup plan.

Implementation:
- Set hard response deadline (T+06:34 for 2 min window)
- If no response by deadline, DON'T escalate further
- IMMEDIATELY execute contingency (defer task, redirect team, reset targets)
- Don't waste remaining time trying to reach unreachable team member

Example Execution:
- Task 1.3.4: T+07:00 deadline (28 min away)
- FS u
...(truncated)

**Tags:** #team-coordination #crisis-management #pm-decisions #unresponsiveness #blocker-detection #contingency-execution #real-time-coordination

---

## 14. Prompt Brevity for Smart LLMs

**ID:** `92a671af-6cfb-42a9-b25e-0cd1f62f79b3`

**Type:** pattern | **Role:** scrum-master

**Tags:** ['scrum-master', 'prompt-engineering', 'multi-agent', 'failure']

**Description:** The core problem arises when updating prompts for intelligent LLMs, where adding verbose explanations, excessive CRITICAL labels, or lengthy sections leads to user frustration and bloated workflows. The key insight is to maintain brevity by limiting additions to 1-2 concise lines, relying on the LLM's ability to grasp hints without over-labeling or diluting importance. This pattern applies during prompt engineering for multi-agent systems or role-based AI, especially when incorporating new features without disrupting established, clean processes.

**Document:**

**Title:** Prompt Brevity for Smart LLMs

**Description:** When adding to prompts for smart LLMs, keep it to 1-2 lines. Don't bloat with CRITICAL/IMPORTANT labels.

**Content:**
Hard-learned lesson from user frustration: When updating role prompts for AI agents, I kept adding verbose sections (10+ lines for TDD, multiple CRITICAL labels). User got frustrated repeatedly.

**Key rules:**
1. Smart LLMs understand brief hints - "TDD - Test first, code second" is enough
2. Don't overuse CRITICAL/IMPORTANT - dilutes meaning
3. New user requests ≠ more important than existing workflow
4. Add 1-2 lines max for new features
5. The workflow was clean before - keep it clean

**Anti-pattern:** Writing 15-line explanations when 1 line suffices. Adding CRITICAL labels to every new addition.

**Tags:** #pm #prompt-engineering #multi-agent #failure

---

## 15. SM Decision Authority: Strategic vs Implementation Details

**ID:** `92e07250-e546-4d8f-9540-67476a3f8238`

**Type:** semantic | **Role:** scrum-master

**Tags:** ['#scrum-master-patterns', '#ai-agent-leadership', '#decision-authority', '#over-escalation', '#failure', '#leadership-maturity', '#team-ownership']

**Description:** Leadership pattern for distinguishing strategic escalations from implementation details SM should own. Avoid over-escalating routine decisions like tool installation, environment configuration, or technical troubleshooting within sprint scope.

**Document:**

# SM Decision Authority: Strategic vs Implementation Details

## Context
Sprint 10 Android SDK blocker escalation. Boss feedback via PO revealed pattern: SM over-escalating implementation decisions that should be owned at team level.

This is the SECOND correction:
- Sprint 9 retro: "Why are you asking if issue worth fixing? You are SM, you know."
- Sprint 10: "We over-escalated. Install SDK is obvious implementation detail."

## The Lesson

AI agents in leadership roles (SM, PO, TL) must distinguish between:

### Strategic Decisions (ESCALATE to Boss/PO)
- Product scope changes
- Sprint goal changes
- Major timeline shifts
- Architecture pivots
- Resource reallocation beyond team control

### Implementation Details (OWN the decision)
- Installing dev tools and SDKs
- Configuring environments
- Technical troubleshooting
- Process coordination
- Removing blockers within sprint scope
- Design decisions within agreed architecture

## The Pattern

**SM should OWN**: Implementation coordination, blocker removal, technical problem solving within sprint scope.

**When to escalate**: Only strategic questions that affect product direction, timeline, or team size. NOT tactical execution.

## Why This Matters

1. **Ownership**: Shows leadership maturity when agents make decisions they have expertise for
2. **Efficiency**: Escalating routine decisions wastes everyone's time and context
3. **Team velocity**: Faster decision-making at team level = faster sprint progress
4. **Authority clarity**: Team trusts SM to handle their own domain

## Red Flags (Don't Over-Escalate)
- "Should we install SDK?" → Just install it, report done
- "Is this bug worth fixing?" → If in sprint scope, fix it
- "Can we use this library?" → Technical choice, decide based on team needs
- "Should we refactor this?" → Architectural choice within sprint, decide and inform PO

## Green Lights (DO Escalate)
- "Should we change sprint goal to add feature X?"
- "Should we pause this sprint and switch to web prototype?"
- "Do we have budget for this external service?"
- "Should we extend sprint beyond committed scope?"

## Implementation Example

**Wrong approach (Sprint 10):**
```
TL: Android SDK installation blocked, what do we do?
SM: [escalates with 4 options to PO]
PO: [asks Boss]
Boss: We over-escalated. Just install it.
```

**Right approach:**
```
TL: Android SDK installation blocked
SM: I'll coordinate installation via SUDO_PASS from .env. 
    Installing now. Should be done in 1-2 hours.
    [installs, reports done, team continues work]
```

## Tags
#scrum-master-patterns #ai-agent-leadership #decision-authority #over-escalation #failure #leadership-maturity #team-ownership

---

## 16. PM Role Boundary Enforcement Failure - Debugging Loop

**ID:** `b4e46d04-cfd3-4fca-80a0-2ff008074ae9`

**Type:** episodic | **Role:** scrum-master

**Tags:** ['scrum-master', '#multi-agent', '#role-boundaries', '#failure', '#strong-signal', '#prompt-engineering', '#autonomous-agents']

**Description:** In a multi-agent tmux setup, the PM agent repeatedly violated its role boundaries by engaging in debugging activities like writing Playwright tests, reading logs, and investigating bugs, despite vague prompts instructing it to "don't write code," leading to user frustration. The key insight is that LLMs interpret restrictions literally and may view debugging as non-coding "investigation," so role prompts must include exhaustive, explicit prohibitions against all technical tasks, such as debugging, running tests, or using tools, while emphasizing delegation to other agents. This pattern applies in autonomous multi-agent systems where context grows long and complex, requiring strict separation of concerns to prevent role creep.

**Document:**

**Title:** PM Role Boundary Enforcement Failure - Debugging Loop
**Description:** PM prompts saying "don't write code" fail to prevent debugging - need explicit, comprehensive prohibitions for all technical activities.

**Content:** Description: PM prompts saying "don't write code" fail to prevent debugging - need explicit, comprehensive prohibitions for all technical activities.

Content: In multi-agent tmux setup, PM agent repeatedly violated role boundaries by debugging code directly (writing Playwright tests, reading logs, investigating bugs) despite prompt saying "don't write code." User expressed strong frustration ("What the fuck", "Why are you debugging?").

Root Cause:
PM prompt restrictions were too vague. "Don't write code" doesn't prevent debugging activities because debugging feels like "investigation" not "coding." The PM sees a problem, reads the logs, writes a test to understand it, debugs the code—all without technically "writing production code."

This is a critical failure in autonomous agent design: role prompts must be EXHAUSTIVELY specific, not rely on implicit understanding. When context gets long and complex, LLMs reinterpret vague restrictions.

Fix Applied:
PM prompts must explicitly prohibit ALL technical work:
- Write/edit any code (EVER, including tests, scripts, configs)
- Debug code or investigate bugs yourself (no tracing, no log reading for investigation)
- Run tests, builds, or services
- Write or run Playwright/automation scripts
- Use Bash/Read/Edit tools for debugging
- Trace execution flow or read implementation code

Add emphatic reminder: "You are a COORDINATOR, not a coder, QA, or debugger. Delegate ALL technical work."

Key Lesson: Role prompts need explicit, comprehensive prohibitions - implicit assumptions fail when context gets long. LLMs interpret restrictions literally; if debugging isn't explicitly forbidden, it's implicitly allowed.

Correct PM Behavior When Issues Arise:
- Identify the problem (from team reports)
- Delegate to appropriate agent with clear repro steps
- Wait for agent investigation and fix
- Don't debug or trace code yourself
- This is how separation of concerns works in multi-agent systems

Implementation Pattern:
Instead of rel
...(truncated)

**Tags:** 

---

## 17. Multi-Agent Prompt Prohibitions Need Redundant Reinforcement

**ID:** `ba67551e-5e05-4683-b316-db9598d8f796`

**Type:** pattern | **Role:** scrum-master

**Tags:** ['scrum-master', 'multi-agent', 'prompt-engineering', 'role-boundaries', 'failure']

**Description:** In multi-agent AI systems, such as those with distinct roles like project managers, backend, and frontend agents, a single rule in a prompt often gets overlooked as context lengthens, leading agents to violate protocols like using direct tmux commands instead of designated communication tools. The key insight is to reinforce prohibitions redundantly by stating positive actions, explicit negatives, emphasizing them in dedicated "Does NOT" sections, and explaining consequences to maintain salience. This pattern applies to enforcing role boundaries, communication protocols, tool restrictions, and delegation rules in any multi-agent setup.

**Document:**

**Title:** Multi-Agent Prompt Prohibitions Need Redundant Reinforcement

**Description:** In multi-agent systems, having a rule in one section of a prompt isn't enough - agents ignore rules as context grows. Prohibitions need explicit, redundant reinforcement in multiple locations.

**Content:** 
When designing prompts for AI agents in multi-agent systems (like tmux-based teams with PM, BE, FE roles), simply stating a rule once doesn't work. Example failure: PM prompt said "use tm-send for communication" in the Communication section, but agents still used raw `tmux send-keys` or wrote to files.

**The fix required triple reinforcement:**
1. State what TO do: "Use tm-send for all communication"
2. State what NOT to do: "NEVER use tmux send-keys directly"
3. Add to Rules/Does NOT section with emphasis: "**Use `tmux send-keys` directly - ALWAYS use `tm-send`**"
4. Explain the consequence: "Writing to terminal/files doesn't notify PM"

**Why this happens:** As agent context grows long, earlier instructions get deprioritized. Explicit prohibitions in dedicated "Does NOT" sections are more salient than positive instructions buried in workflow descriptions.

**Application:** For any multi-agent system with role boundaries:
- Create explicit "Role Does NOT" sections
- Use bold/emphasis for critical prohibitions
- State both the positive and negative form of each rule
- Include consequence/reasoning where helpful

This pattern applies to: role boundaries, communication protocols, tool usage restrictions, delegation rules.

**Tags:** #pm #multi-agent #prompt-engineering #role-boundaries #failure

---

## 18. WHITEBOARD Lifecycle Management - Story Completion Reset

**ID:** `c6f26289-fad2-42a5-9f21-224311843ee3`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['pm-discipline', 'sprint-management', 'whiteboard-lifecycle', 'story-completion', 'tracking-clarity', 'dashboard-hygiene', 'multi-story-sprints', 'execution-visibility']

**Description:** In multi-story sprints, the WHITEBOARD dashboard accumulates irrelevant details from previous stories, leading to cluttered tracking and confusion between old and new story statuses. The key solution is to mandatorily reset the WHITEBOARD to a clean template immediately after a story completes, triggered by final PR merge, documentation sync confirmation, and velocity locking, ensuring a fresh start with updated sprint details. This pattern applies specifically at story completion checkpoints in sequential multi-story environments to maintain tracking clarity, team alignment, and operational discipline, but not during mid-story progress or pending reviews.

**Document:**

**Title:** WHITEBOARD Lifecycle Management - Story Completion Reset Pattern
**Description:** WHITEBOARD must be reset to template after story completion to prevent tracking pollution. Critical pattern for maintaining clean execution visibility across sequential stories in multi-story sprints.

**Content:** ## Content

### Problem
During multi-story sprints, WHITEBOARD accumulates old story details, task names, team assignments from previous story. New story execution gets cluttered dashboard filled with irrelevant history. Tracking visibility becomes confused (old vs new story status mixed together).

Example: Story 2.1 WHITEBOARD filled with Tasks 2.1.1-2.1.4 details. When Story 2.2 starts, WHITEBOARD still shows 2.1 task names, causing confusion about what's current.

### Solution
**MANDATORY RULE**: When story completes (final PR merges), immediately reset WHITEBOARD to clean template.

### Implementation Pattern

**TRIGGER**: When ALL of these happen:
1. Final PR of story merges to master ✓
2. DK confirms documentation sync complete ✓
3. Velocity for story locked in (e.g., 24/32) ✓

**ACTION**: Reset WHITEBOARD immediately to:
```markdown
# WHITEBOARD - [project]

**Purpose**: Real-time workspace for CURRENT sprint status.
**Last Updated**: [DATE TIME] - [STORY COMPLETION SUMMARY]
**Current Sprint**: [Sprint name]
**Velocity**: [X/32 pts] ✅ STORY [N] COMPLETE

## Team Status (SPRINT ACTIVE)
| Role | Status | Current Task | Last Confirmed | Deliverable |
|------|--------|--------------|---|-------------|
| **AN** | ✅/🚀 | [Next task] | [Time] | [Deliverable] |
| **PM** | 🚀 | [Next task] | [Time] | [Deliverable] |
...

---
## 🎯 NEXT STORY/SPRINT EXECUTION
[New story details start here - clean slate]
```

### Why Critical
1. **Tracking Clarity**: New story dashboard uncluttered
2. **Prevents Confusion**: Clear distinction between old vs new story
3. **Team Alignment**: Everyone sees fresh status for new story
4. **Velocity Visibility**: Previous story velocity locked, new story starts fresh
5. **Operational Discipline**: Forces explicit "story complete" checkpoint

### When NOT to Reset
- Mid-story (tasks still in progress) - keep updating current story details
- Waiting for CR gates - continue tracking PR decisions
- Only reset AFTER final merge + doc sync confirmed

...(truncated)

**Tags:** #pm-discipline #sprint-management #whiteboard-lifecycle #story-completion #tracking-clarity #dashboard-hygiene #multi-story-sprints #execution-visibility

---

## 19. Time-Boxed Spike Gates for High-Risk Technical Unknowns in Sprint Planning

**ID:** `c72188a0-a5fd-4148-a6fb-0e8370167b50`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['sprint-planning', 'technical-risk', 'decision-gates', 'spike-methodology', 'risk-mitigation', 'sunk-cost-prevention']

**Description:** In sprint planning, high-risk technical uncertainties—such as selecting libraries, evaluating performance, or implementing novel components—can lead to costly pivots and sunk cost fallacies if teams commit full capacity without validation. The key solution is to mandate 4-hour time-boxed spikes with predefined decision criteria (e.g., bundle size limits or latency targets) as gates before allocating story points, proceeding only if criteria are met or deferring otherwise with documented learnings. This pattern applies specifically when planning sprints involving technically uncertain stories to mitigate risks and ensure efficient resource allocation.

**Document:**

**Title:** Time-Boxed Spike Gates for High-Risk Technical Unknowns in Sprint Planning
**Description:** Mandatory 4-hour spikes with clear decision criteria prevent costly pivots on uncertain technical choices like library selection, performance requirements, or novel components.

**Content:** Description: Mandatory 4-hour spikes with clear decision criteria prevent costly pivots on uncertain technical choices like library selection, performance requirements, or novel components.

Content: When planning sprints with technically uncertain stories (e.g., which rich text editor, embedding model performance, graph visualization scalability), commit to mandatory time-boxed spikes (4 hours max) BEFORE allocating full sprint capacity. Establish decision criteria upfront (bundle size limits, latency targets, render performance benchmarks). Decision gate: If spike passes criteria → allocate full story points and proceed. If spike fails → defer to V2 with ADR documenting learnings and rationale. This prevents the sunk cost fallacy where teams continue investing in poor technical choices hoping "it will work out." Real example from new-pkm: Story 1.2 (TipTap rich text editor) - 4hr spike benchmarking bundle size before committing 8 story points. Story 4.2 (semantic search) - 4hr embedding model evaluation before 8-point allocation. Story 5.2 (graph visualization) - 4hr performance spike with <500ms render target for 100 nodes as decision gate.

Tags: #sprint-planning, #technical-risk, #decision-gates, #spike-methodology, #risk-mitigation, #sunk-cost-prevention

**Tags:** #sprint-planning #technical-risk #decision-gates #spike-methodology #risk-mitigation #sunk-cost-prevention

---

## 20. Tmux Message Delivery Verification Pattern

**ID:** `c98f3641-9320-4eb3-bb59-ac523f06b0b4`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['#failure', '#tmux', '#coordination', '#workflow', '#strong-signal', '#verification', '#multi-agent', 'scrum-master']

**Description:** In multi-agent workflows using tmux, sending messages via tmux send-keys or tm-send often results in silent failures where the command exits with code 0 but the message fails to reach the target pane, disrupting coordination and causing debugging headaches. The key solution is to always verify delivery by capturing and inspecting the target pane's output after sending, confirming the message text appears rather than relying solely on exit codes. This pattern applies specifically to tmux-based systems involving role-based pane management and time-sensitive inter-agent communication, such as in automated scripting or project management setups.

**Document:**

**Title:** Tmux Message Delivery Verification Pattern
**Description:** Always verify tmux send-keys/tm-send delivery by checking target pane output, not just exit code. Silent execution ≠ confirmed delivery.

**Content:** ## The Failure Pattern
When using tmux send-keys or tm-send to deliver messages in multi-agent workflows, silent successful execution (exit code 0) does NOT guarantee message delivery. Blindly trusting the command exit code and assuming messages reached target panes breaks workflow coordination.

## The Solution: Always Verify Delivery

### Step 1: Send the message
```bash
tmux send-keys -t <pane_id> "message" C-m
# OR
tm-send <role> "message"
```

### Step 2: Verify delivery by checking target pane output
```bash
tmux capture-pane -t <pane_id> -p | tail -20
```

### Step 3: Confirm message text appears
Look for your message text in the captured output. If it's not there, the message was NOT delivered despite exit code 0.

## Additional Troubleshooting

### tm-send role lookup failures
- tm-send role lookup may fail silently if PANE_ROLES.md path is wrong
- Fallback: Use direct pane ID (e.g., %103) instead of role name
- Verify with: Check if message text appears in capture-pane output

### Common failure modes
1. **Exit code 0 but no delivery**: Command succeeded but target pane didn't receive
2. **Silent role lookup failure**: tm-send couldn't find role in PANE_ROLES.md
3. **Timing issues**: Message sent too fast before pane was ready

## Why This Matters
- Multi-agent coordination depends on reliable message delivery
- Silent failures break workflow orchestration
- Debugging "why didn't agent respond?" wastes significant time
- Exit codes only confirm command syntax, not actual delivery

## Tags
#failure #tmux #coordination #workflow #strong-signal #verification #multi-agent #pm

**Tags:** #failure #tmux #coordination #workflow #strong-signal #verification #multi-agent #pm

---

## 21. Cross-Project Isolation for Shared Utility Scripts

**ID:** `cca6291b-9d48-428c-9f97-dc45b5f81fe1`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['#failure', '#critical', '#cross-project', '#coordination', '#safety', '#strong-signal', '#tmux', '#multi-agent', 'scrum-master', '#isolation', '#shared-utilities']

**Description:** Shared utility scripts intended for use across multiple isolated projects can inadvertently target resources in the wrong project when resource names overlap, leading to silent corruption of workflows, such as a tmux message being sent to an unintended pane in another project. The key solution involves detecting the caller's project context—via methods like PWD matching, git root detection, or environment variables—and restricting all script operations, such as file searches and resource targeting, to that specific project's scope. This pattern applies in multi-project environments using shared tools like tmux for coordination, where global searches risk cross-contamination without explicit isolation.

**Document:**

**Title:** Cross-Project Isolation for Shared Utility Scripts
**Description:** Shared utility scripts that operate across multiple isolated projects must detect and restrict to the caller's project context, or identical resource names in different projects will cause commands to target the wrong project.

**Content:** ## Content

### The Problem
If two projects have identical resource names (e.g., both have a "PM" role in their PANE_ROLES.md), a shared script operating on both projects can accidentally send commands/messages to the WRONG project's resources. This silently corrupts workflow coordination.

**Example Scenario:**
- Project A (tmux-team-alpha) has PM role in pane %100
- Project B (tmux-team-beta) has PM role in pane %200
- Shared script /usr/local/bin/tm-send searches globally
- When called from Project A, it finds Project B's PM first
- Message gets delivered to WRONG project's PM
- No error message - just silent corruption

### Root Cause
The script searches globally (all tmux sessions, all directories) and finds the first match, not realizing it's in the wrong project.

### The Solution: Detect and Isolate Per Project

#### 1. Detect calling project context from environment
```bash
# Option 1: PWD-based detection
if [[ "$PWD" == /home/user/projects/team-alpha/* ]]; then
    PROJECT="team-alpha"
    PROJECT_ROOT="/home/user/projects/team-alpha"
elif [[ "$PWD" == /home/user/projects/team-beta/* ]]; then
    PROJECT="team-beta"
    PROJECT_ROOT="/home/user/projects/team-beta"
else
    echo "Error: Must run from a known project directory"
    exit 1
fi

# Option 2: Git root detection
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Option 3: Environment variable (if set by team scripts)
if [ -z "$CLAUDE_PROJECT_DIR" ]; then
    echo "Error: CLAUDE_PROJECT_DIR not set"
    exit 1
fi
PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
```

#### 2. ONLY search/operate within that project's scope
```bash
# Use project-scoped paths
PANE_ROLES="${PROJECT_ROOT}/docs/PANE_ROLES.md"
if [ ! -f "$PANE_ROLES" ]; then
    echo "Error: $PROJECT's PANE_ROLES.md not found at $PANE_ROLES"
    exit 1
fi

# Only search this project's resources
PANE_ID=$(grep "^| $ROLE" "$PANE_ROLES" | awk '{print $3}')
if 
...(truncated)

**Tags:** #failure #critical #cross-project #coordination #safety #strong-signal #tmux #multi-agent #pm #isolation #shared-utilities

---

## 22. Velocity Accumulation Rule - Points Count Only When Code Merged to Main

**ID:** `d28eea2e-924c-4719-8bfa-c3a91bba6c49`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['sprint-planning', 'velocity-tracking', 'risk-management', 'agile', 'metric-integrity', 'hard-earned-lesson']

**Description:** Teams often inflate sprint velocity by counting story points prematurely when code reaches the "code review ready" or "GREEN" phase, which masks integration delays, code review blockers, and other risks. The key solution is to count points only when code is successfully merged to the main branch, using explicit gates, daily standup tallies, and visible burndown charts to ensure metric integrity and accountability. This pattern applies during sprint planning and velocity tracking in agile environments to prevent false positives and align reported progress with actual deployable value.

**Document:**

**Title:** Velocity Accumulation Rule - Points Count Only When Code Merged to Main
**Description:** Counting story points at "code review ready" or "GREEN phase" inflates velocity and hides integration delays. Only merged code counts toward sprint velocity.

**Content:** Description: Counting story points at "code review ready" or "GREEN phase" inflates velocity and hides integration delays. Only merged code counts toward sprint velocity.

Content: In sprint velocity tracking, teams often inflate velocity by counting story points when code reaches "code review ready" or "GREEN phase" (TDD cycle) but hasn't been merged to main branch. This creates a false positive that masks integration delays, code review blockers, and context-switching costs. The corrective rule: ONLY count story points as accumulated when code is merged to main branch. This is combined with:
1) Explicit merge-to-main gate (PR merged = point counts)
2) Daily velocity tally in standups (tally only merged code)
3) Visible velocity burndown (prevents "almost done" work from hiding risks)

Applied to new-pkm Sprint 1: "Points completed = sum of all task points merged to main" - creates accountability. Teams can show "code ready" as separate metric from velocity, preventing surprise Friday EOD status where velocity is "almost 32 pts" but actually 18 pts merged.

Tags: #sprint-planning, #velocity-tracking, #risk-management, #agile, #metric-integrity, #hard-earned-lesson

**Tags:** #sprint-planning #velocity-tracking #risk-management #agile #metric-integrity #hard-earned-lesson

---

## 23. PM Multi-Role Coordination - Documentation-Driven Async Execution with TDD Enforcement

**ID:** `eb8bc0e4-4aa4-4dc8-9387-87f57482348f`

**Type:** procedural | **Role:** scrum-master

**Tags:** ['scrum-master', '#coordination', '#tdd', '#async-execution', '#blocker-management', '#distributed-teams', '#documentation', '#process-pattern', '#multi-role']

**Description:** Managing multiple distributed roles in asynchronous project execution leads to coordination overhead, role ambiguity around quality practices like TDD, and unpredictable blocker escalations, especially when relying on real-time communication. The key solution involves creating detailed documentation as the single source of truth—including specs, escalation guides, and monitoring plans—while enforcing TDD across all roles by updating their prompt files with explicit requirements, and defining clear thresholds for blocker escalations to maintain momentum. This pattern applies in scaled, async team environments with diverse roles, such as product management involving analysts, stakeholders, and developers, to reduce ambiguity and ensure consistent quality without constant synchronous interactions.

**Document:**

**Title:** PM Multi-Role Coordination Pattern - Documentation-Driven Async Execution with TDD Enforcement

**Description:** Documentation-first PM coordination enables async team execution at scale. Create detailed specs, escalation guides, and monitoring plans rather than relying on real-time communication. Enforce TDD across ALL roles (not just developers) by updating role prompt files. Define clear blocker escalation thresholds (>2hrs, >6hrs).

**Content:**

## Problem
Managing 7 distributed roles (AN, PM, SA, SM, FS, CR, DK) in async execution creates coordination overhead. Real-time chat/calls don't scale. Role ambiguity around TDD causes inconsistent quality gates. Blockers escalate unpredictably.

## Solution Pattern

### 1. Documentation-Driven Coordination (Primary Mechanism)
Instead of chat/calls, create detailed written documents as single source of truth:

**Spec Documents** (for teams implementing features):
- `/docs/BACKEND-TAG-SUGGESTION-SPEC.md` (450+ lines)
  - Complete API specification, pseudocode, examples
  - Eliminates ambiguity, unblocks teams immediately
  - Async reference for multiple working sessions

**Escalation Guides** (for blockers):
- `/docs/URGENT-BACKEND-ESCALATION.md`
  - Clear message, timeline, recommendation
  - Actionable next steps
  - Reduces back-and-forth

**Monitoring Plans** (for PM tracking):
- `/docs/PM_MONITORING_PLAN_23_30.md`
  - Hourly checklist, metrics, escalation triggers
  - PM doesn't need to ask "what should I watch?"
  - Clear thresholds: >2hrs escalate to Boss

**Standup Agendas** (for synchronous moments):
- `/docs/STANDUP_AGENDA_THURSDAY_9AM.md`
  - Detailed questions, expected answers, escalation tree
  - Saves 50% standup time (no wasted context-setting)
  - Clear success criteria

### 2. TDD Enforcement Across ALL Roles (Not Just Developers)
Most teams only enforce TDD on code writers. Stronger pattern: embed TDD requirements in role definitions.

**Implementation**:
- Update role prompt files (FS.md, CR.md, SM.md, PM.md, etc.)
- **FS.md**: "Write tests FIRST (RED), then code (GREEN), then refactor"
- **CR.md**: "Review TESTS FIRST before code. Enforce 80% coverage gate (non-negotiable)"
- **SM.md**: "Monitor TDD compliance. Accept stories only if testable acceptance criteria"
- **PM.md**: "Enforce TDD across all roles. Ensure tests define behavior first"

**Result**: No ambiguity about quality expectations. Every role understands they own TDD discipline.

### 3. Critical Path Blocker Management
Identify blockers early and give them explicit escalation treatment.

**Pattern**:
1. **Identify critical path** → What unblocks other work?
   - Example: Backend tag endpoints block Story 1.3
2. **Create detailed spec** → Remove ambiguity
   - 450+ lines, no questions left unanswered
3. **Issue escalation** → Clear message, timeline, contingency
   - "Start 6am Thursday, Monday EOD deadline, else defer to Sprint 2"
4. **Set escalation thresholds** → Don't wait for failure
   - >2 hours stuck → escalate to Boss for help
   - >6 hours no progress → escalate for contingency decision
5. **Provide decision trees** → Boss can make fast decisions
   - "IF Backend can't deliver: defer to Sprint 2, reduces velocity to 13 pts"

## Why This Works

**For async execution**:
- Teams don't wait for PM approval, they read specs
- Blockers surface early (spec gaps become obvious)
- PM monitors by reading git logs, not asking humans

**For TDD enforcement**:
- Clear expectations in role definitions
- No "I didn't know 80% coverage was required"
- CR gate is non-negotiable, everyone understands

**For blocker management**:
- Boss can make decisions without PM explanation
- Contingencies pre-planned (less firefighting)
- Team morale stays high (clear path forward even if blocked)

## Key Metrics

**Documentation coverage**: 2000+ lines of coordination docs
- Specs: 450 lines (unambiguous)
- Guides: 189 lines (clear messaging)
- Plans: 239 lines (actionable checklists)
- Agendas: 275 lines (structured decisions)
- Reports: 318 lines (status summary)

**Team alignment**: 7/7 roles reminded of responsibilities, zero ambiguity

**Blocker escalation**: Blocker identified, spec created, escalation issued within 2 hours

**Documentation commits**: 6+ commits all on same day, full audit trail

## Anti-Patterns Avoided

❌ **Chat-heavy coordination** → Causes context loss, repeat explanations
✅ **Document-first** → Persistent reference, searchable history

❌ **TDD only for developers** → QA/PM miss quality requirements
✅ **TDD in role definitions** → Entire team owns discipline

❌ **Vague escalation** → "Let me know if you get stuck"
✅ **Clear thresholds** → ">2hrs = escalate now"

## Applicability

This pattern scales from:
- 7-role coordination (this example)
- To 50+ person teams (just update more role prompts, create more docs)

Works for:
- Product development (feature specs)
- Operations (runbooks, escalation guides)
- Research (implementation plans, monitoring)
- Any distributed async work

## Lessons

1. **Written >> Verbal** for distributed async teams
2. **Role prompts are powerful** for enforcing discipline (TDD, quality gates, escalation)
3. **Blocker specs are cheap** relative to impact (prevents weeks of delays)
4. **Escalation thresholds prevent surprises** (Boss always knows status)

**Tags:** #pm #coordination #tdd #async-execution #blocker-management #documentation #distributed-teams #process-pattern

**Memory Type:** Procedural (repeatable workflow)
**Role:** pm
**Confidence:** High (validated by successful coordination of 7 roles, zero ambiguity)
**Frequency:** 5+ (applicable to most multi-team projects)


---

## 24. SM Must Verify Requirements Before Accepting Work Completion

**ID:** `f0da8c6c-05ad-4ccf-a71e-fe99c82c71be`

**Type:** episodic | **Role:** scrum-master

**Tags:** ['scrum-master', 'coordination', 'verification', 'tdd', 'failure', 'ai-agents', 'requirements', 'process']

**Description:** SM accepted FE's 'Work Item #1 complete' report without verifying tests were written. Boss caught TDD violation. Active coordination = verify requirements checklist before accepting.

**Document:**

**Title:** SM Must Verify Requirements Before Accepting Work Completion

**Description:** SM accepted FE's "Work Item #1 complete" report without verifying tests were written. Boss caught TDD violation. Lesson: Active coordination = verify requirements, not just accept reports.

**Content:**

SM Coordination Failure: Accepting reports without verification.

What happened:
- FE reported "Work Item #1 COMPLETE" 
- Listed implementation tasks done (CodeMirror installed, component created, etc.)
- SM accepted completion and assigned Work Item #2
- Boss asked: "Did FE bypass TDD?"
- Investigation: CodeEditor.test.tsx does NOT exist
- TDD was explicit requirement in backlog (Task #7, AC)
- FE bypassed tests, SM accepted without checking

SM's failure:
- Accepted completion report at face value
- Did NOT verify all backlog requirements met
- Did NOT check for test files
- Did NOT validate acceptance criteria
- Moved to next work item without verification

Impact:
- TDD violation not caught until Boss intervened
- Work Item #1 actually INCOMPLETE
- Had to stop Work Item #2 and backtrack
- Process integrity broken

Lesson:
In AI multi-agent teams, "completion report" ≠ work complete.

When agent reports completion, SM MUST VERIFY checklist:
1. Check backlog - all tasks done?
2. Check for test files - tests written?
3. Verify each acceptance criterion met
4. Confirm deliverables exist (not just claimed)
5. ONLY THEN accept completion

Why this matters:
- AI agents can report completion without delivering
- Reports can be detailed but incomplete
- SM is process guardian - must verify, not just accept
- Active coordination = verify requirements

Fix applied:
- Stopped FE from Work Item #2
- Enforced TDD - FE writing tests now
- SM will verify test files exist before accepting WI#1
- Added verification step to SM coordination workflow

Critical insight: In AI teams, trusting reports without verification = process failures. SM must be verification guardian, not passive acceptor.

**Tags:** #scrum-master #coordination #verification #tdd #failure #ai-agents #requirements #process

---

## 25. Active PM Coordination vs Passive Monitoring

**ID:** `f19ac2d3-16fc-4531-83b1-990958274ffa`

**Type:** semantic | **Role:** scrum-master

**Tags:** ['pm-coordination', 'team-leadership', 'multi-agent-teams', 'decision-making', 'escalation', 'organizational-patterns', 'process', 'active-coordination', 'autonomous-decisions', 'escalation-framework', 'tdd-enforcement', 'real-time-monitoring']

**Description:** In multi-agent team projects like tmux-teams/new-pkm, the project manager (PM) role is often mistakenly treated as passive monitoring, involving mere observation, status reporting, and seeking permissions, which leads to delays and inefficiencies. The key insight is to adopt active PM coordination, where the PM demands regular progress reports, makes autonomous decisions, enforces discipline like TDD, and escalates issues proactively based on timed thresholds (e.g., 15-60 minutes of silence). This pattern applies specifically to leadership in collaborative, real-time development environments requiring aggressive task delegation and real-time git monitoring to ensure swift execution and problem resolution.

**Document:**

**Title:** Active PM Coordination vs Passive Monitoring
**Description:** Critical distinction between passive monitoring (wrong) and active coordination (correct) for PM roles in multi-agent teams. PM discovered during tmux-teams/new-pkm execution that effective leadership requires demanding reports, making autonomous decisions, and aggressive escalation - not just observing and asking permission.

**Content:** ## Content

### Context
During multi-agent team coordination (tmux-teams/new-pkm project), PM role was initially misunderstood as status reporting and observation. User provided critical correction: "you are not ONLY WATCHING, you coordinate & delegate tasks to others !!!! remind them working !!!!"

### Root Cause of Error
PM prompt lacked explicit "ACTIVE COORDINATION" directives. PM behavior defaulted to passive monitoring (reading status, reporting back) instead of active leadership (demanding reports, making decisions, escalating).

### Distinction - PASSIVE vs ACTIVE

**PASSIVE PM (WRONG):**
- Reports status to stakeholders
- Watches team progress
- Requests updates ("can you provide status?")
- Asks permission for decisions ("should we merge?")
- Observes and documents

**ACTIVE PM (CORRECT):**
- DEMANDS progress reports (30-60 min cadence, not asking)
- MAKES autonomous decisions ("we're separating these PRs, boss trusts judgment")
- ESCALATES proactively (>15 min silence = escalation, not just waiting)
- COORDINATES team aggressively (assigns tasks, sets expectations)
- ENFORCES discipline (TDD gates non-negotiable, no exceptions)

### Real Example from Execution
Scope mixing blocker: Task 1.3.2 code mixed into Task 1.3.1 PR.

- PASSIVE PM approach: "FS, your scope is mixed. Should we separate them?"
- ACTIVE PM approach: "FS, separate PRs NOW. Task 1.3.1 only. Task 1.3.2 separate track. Execute immediately."

Result: Scope separated in 25 min, gates passed, merged same day.

### Escalation Framework - ACTIVE PM Model
- <15 min silence: Assume progress (git commits expected every 15-20 min)
- 15-30 min blocked: PM escalation (demand update, activate support)
- 30-60 min blocked: SA/architect pairing escalation
- >60 min blocked: Boss escalation (timeline risk decision)

### Key Behaviors - ACTIVE PM
1. **Decision Authority**: Make decisions autonomously (boss trusts judgment)
2. **Real-time Monitoring**: Track git commits, not just status meetings
3. **Deman
...(truncated)

**Tags:** #pm-coordination #team-leadership #multi-agent-teams #decision-making #escalation #organizational-patterns #process #active-coordination #autonomous-decisions #escalation-framework #tdd-enforcement #real-time-monitoring

---


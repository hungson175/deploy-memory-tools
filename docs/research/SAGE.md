# SAGE: Reinforcement Learning for Self-Improving Agent with Skill Library

**Authors:** Jiongxiao Wang¹*, Qiaojing Yan², Yawei Wang², Yijun Tian², Soumya Smruti Mishra², Zhichao Xu², Megha Gandhi², Panpan Xu²†, Lin Lee Cheong²

¹University of Wisconsin–Madison; ²AWS Agentic AI

*Work was done during an internship at AWS Agentic AI.
†Corresponding author: Panpan Xu

**arXiv:2512.17102v1 [cs.AI] 18 Dec 2025**

---

## Abstract

Large Language Model (LLM)-based agents have demonstrated remarkable capabilities in complex reasoning and multi-turn interactions but struggle to continuously improve and adapt when deployed in new environments. One promising approach is implementing skill libraries that allow agents to learn, validate, and apply new skills. However, current skill library approaches rely primarily on LLM prompting, making consistent skill library implementation challenging.

To overcome these challenges, we propose a Reinforcement Learning (RL)-based approach to enhance agents' self-improvement capabilities with a skill library. Specifically, we introduce **Skill Augmented GRPO for self-Evolution (SAGE)**, a novel RL framework that systematically incorporates skills into learning. The framework's key component, **Sequential Rollout**, iteratively deploys agents across a chain of similar tasks for each rollout. As agents navigate through the task chain, skills generated from previous tasks accumulate in the library and become available for subsequent tasks. Additionally, the framework enhances skill generation and utilization through a **Skill-integrated Reward** that complements the original outcome-based rewards.

Experimental results on AppWorld demonstrate that SAGE, when applied to supervised-finetuned model with expert experience, achieves **8.9% higher Scenario Goal Completion** while requiring **26% fewer interaction steps** and generating **59% fewer tokens**, substantially outperforming existing approaches in both accuracy and efficiency.

---

## 1. Introduction

Large language model (LLM)-based agents have been widely applied to automate complex tasks through active environmental interactions, including:
- Coding agents (Yang et al., 2024; Novikov et al., 2025)
- Deep research (OpenAI, 2025)
- Assistant agents (Yao et al., 2024; Chen et al., 2025)
- Web browsing (Yao et al., 2022; Zhou et al., 2024)

To enhance the performance of these multi-turn interactive agents, researchers have successfully integrated reinforcement learning (RL) techniques into their frameworks. Recent advances, particularly in **reinforcement learning with verifiable rewards (RLVR)** (Shao et al., 2024; Guo et al., 2025), have enabled effective end-to-end agent training for improved performance.

### Key Challenges

Despite RL's effectiveness, significant limitations persist:
- RL-trained agents are often limited to specific training scenarios
- When deployed in new environments, they struggle to demonstrate continual learning capabilities
- Difficulty in effectively utilizing valuable on-going experiences for future tasks

### Skill Library Solution

One potential solution is enabling agents to transform their previous interaction experiences into **reusable skills**, which can be stored in a skill library for future reference. Benefits include:

1. **Experience Replay**: When agents encounter similar tasks, previously acquired skills can be leveraged to improve task success rates
2. **Enhanced Efficiency**: Since each skill is composed of a list of actions, utilization of these skills can enhance agent efficiency by condensing complex action sequences into reusable operations

### Contributions

This paper explores enhancing agents' self-improvement capabilities through RL with a skill library. Key contributions:

1. **Unified Format**: Implement a unified format for both task solving and skill generation (following DynaSaur approach)
2. **Sequential Rollout**: Train agents with chains of similar tasks where skills generated in previous tasks are preserved and made available for subsequent ones
3. **Skill-integrated Reward**: Computed as the sum of verifiable outcome-based reward and extra reward for high-quality skill generation and utilization
4. **SAGE Framework**: Skill Augmented GRPO for self-Evolution - a novel RL framework

---

## 2. Related Work

### LLM-based Agents

Recent advancements in instruction-tuned LLMs have enabled them to follow user instructions for interacting with external environments as autonomous agents. Various frameworks have been developed:

- **ReAct** (Yao et al., 2023): Pioneered "reason-then-act" pipeline
- **Plan-and-Act** (Erdogan et al., 2025): Extended with additional planning phase
- **CodeAct** (Wang et al., 2024b): Demonstrated that generating executable Python code significantly improves agent performance

Training approaches include:
- Supervised fine-tuning (Schick et al., 2023; Chen et al., 2023; Zeng et al., 2024)
- Reinforcement learning (Song et al., 2024; Bai et al., 2024; Wang et al., 2025a; Chen et al., 2025)

### Self-Improving Agent with Skill Library

Key works in skill library research:

| Work | Domain | Approach |
|------|--------|----------|
| Voyager (Wang et al., 2024a) | Minecraft exploration | Pioneered skill library for recording successful behaviors |
| Agent Workflow Memory (Wang et al., 2024c) | Web exploration | Skill library for web tasks |
| SkillWeaver (Zheng et al., 2025) | Web agents | Self-improvement through skill discovery |
| Agent Skill Induction (Wang et al., 2025b) | Web browsing | Inducing high-level skills from trajectories |
| Synapse (Zheng et al., 2024b) | Computer control | Trajectory-as-exemplar prompting |
| DynaSaur (Nguyen et al., 2024) | Math problems | Executable skills |

Skills can take two forms:
1. **Natural language experience memories** serving as a reference
2. **Executable skills** that can be directly implemented in the environment

---

## 3. Method

### 3.1 Skill Library Agent

The framework extends the CodeAct framework, enabling agents to compose code by combining multiple APIs with basic programming constructs to solve complex tasks.

**Key Design Decisions:**

Unlike previous frameworks (Agent Skill Induction, Voyager) that define reusable skills only after task completion, SAGE implements a **unified format for both task solving and skill generation**. This addresses two limitations:

1. In long-horizon tasks, additional skill generation process extends context length beyond model limitations
2. Separation between task execution and skill generation creates inconsistency affecting learning

**Agent Actions with Skill Library:**

Given a task set Q, the agent performs online learning with skill library M:

1. **Skill Usage**: Perform skill aᵢ ∈ [a₁, ..., aₖ] to process the task
2. **Skill Generation**: Define a skill function â composed of multiple actions and immediately call it
3. **Skill Update**: If a skill fails to execute, update it and recall
4. **Skill Save**: If skill executes without error, add/update in skill library M

Direct API calls are also allowed when defining a function skill is unnecessary.

### 3.2 SAGE for Skill Library Agent

#### 3.2.1 Preliminary: GRPO

SAGE builds on Group Relative Policy Optimization (GRPO). For each query q, GRPO:
1. Samples a group of outputs {o₁, ..., oG} from old policy πθold
2. Optimizes by maximizing:

```
J_GRPO(θ) = E[q~Q, {oᵢ}ᴳᵢ₌₁~πθold(O|q)]
            (1/G) Σᵢ (1/|oᵢ|) Σₜ {min[sᵢ,ₜÂᵢ,ₜ, clip(sᵢ,ₜ, 1-ε, 1+ε)Âᵢ,ₜ] - βD_KL}
```

Where:
- sᵢ,ₜ = πθ(oᵢ,ₜ|q,oᵢ,<ₜ) / πθold(oᵢ,ₜ|q,oᵢ,<ₜ)
- Âᵢ,ₜ = (rᵢ - mean(r)) / std(r)

#### 3.2.2 Sequential Rollout

**Key Insight**: Skill generation and usage processes often need multiple tasks to reveal quality.

**Solution**: Instead of one task, give the agent a chain of tasks with sequential rollout:
- Skills learned in earlier tasks can be used in subsequent tasks
- Reward signals from successful skill usage in later tasks back-propagate to skill generation in previous tasks
- Task chains constructed with examples under the same scenario (similar instructions)

For simplicity, the paper focuses on task chains containing **two examples**.

#### 3.2.3 Skill-integrated Reward

Beyond outcome-based rewards, additional rewards encourage:
1. **Skill generation** in the first example
2. **Skill utilization** in the second example

**Formulation:**

Let r¹, r² ∈ [0, 1] denote verifiable outcome-based rewards:

```
R¹ = r¹ + 1[r¹ = 1] * 1[r² = 1] * 1_skill(q²|q¹)
R² = r² + 1[r² = 1] * 1_skill(q²|q¹)
```

Where:
- 1_skill(q²|q¹) indicates whether q² uses skills generated by q¹
- 1[r = 1] indicates successful task completion
- A -1.0 penalty is applied when agent provides no code and terminates

#### 3.2.4 SAGE Algorithm

**Key modifications from standard GRPO:**

1. No KL divergence penalty
2. Advantage not normalized by standard deviation
3. Expectation computed across task chain
4. Within same group, generations o²ᵢ derive from different skill libraries M²ᵢ

**Objective Function:**

```
J_Agent(θ) = E[(q¹,q²)~Q, {τᵢ}ᴳᵢ₌₁~πθold(·|(q¹,q²))]
             (1/G) Σᵢ Σₖ (1/|oᵏᵢ|) Σₜ {min[sᵏᵢ,ₜÂᵏᵢ, clip(sᵏᵢ,ₜ, 1-ε, 1+ε)Âᵏᵢ]}
```

Where:
- τᵢ = Sequential Rollout trajectory
- oᵏᵢ = i-th output for qᵏ in the group
- Mᵏᵢ = skill library for query qᵏᵢ (M¹ᵢ is empty, M²ᵢ includes skills from q¹ᵢ)

---

## 4. Experiments

### 4.1 Experimental Settings

**Dataset**: AppWorld (Trivedi et al., 2024)
- 750 tasks from 250 task scenarios
- Each scenario: 3 tasks with similar instructions
- Splits: Train (105), Dev (60), Test-Normal (168), Test-Challenge (417)
- Well-suited for Sequential Rollout due to scenario-based structure

**Base Model**: Qwen2.5-32B-Instruct

**Metrics**:
- **TGC (Task Goal Completion)**: Accuracy of individual tasks
- **SGC (Scenario Goal Completion)**: Proportion of scenarios where all 3 tasks succeed
- **Avg. Steps**: Average interaction steps
- **Avg. Tokens**: Average generated tokens

**Training Pipeline**:
1. Expert experience dataset generated using Claude 3.5 Sonnet V2
2. Supervised fine-tuning (SFT) on expert data
3. SAGE training with Sequential Rollout and Skill-integrated Reward

### 4.2 Main Results

| Base Model | Method | Test Normal ||| Test Challenge |||
|------------|--------|-----|-----|-----|-----|-----|-----|
| | | TGC | SGC | Avg. Steps | TGC | SGC | Avg. Steps |
| **Training Free** |
| GPT-4o | ReAct | 48.8 | 32.1 | -- | 30.2 | 13.0 | -- |
| OpenAI o1 | ReAct | 61.9 | 41.1 | -- | 36.7 | 19.4 | -- |
| Claude Sonnet 3.5 V2 | ReAct | 57.1 | 41.1 | 15.7 | 49.2 | 28.8 | 21.8 |
| Qwen2.5 32B Instruct | ReAct | 39.2 | 18.6 | -- | 21.0 | 7.5 | -- |
| **RL without Skill Library** |
| Qwen2.5 32B Instruct | LOOP | 71.3 | 53.6 | -- | 45.7 | 26.6 | -- |
| | GRPO | 69.2 | 51.8 | 16.4 | 40.7 | 26.9 | 21.9 |
| **Our Approach** |
| Qwen2.5 32B Instruct | Skill Library Agent | 30.7 | 19.6 | 13.4 | 15.3 | 7.0 | 18.7 |
| | + SFT | 55.2 | 41.7 | **11.4** | 37.2 | 20.9 | **16.2** |
| | + SAGE | **72.0** | **60.7** | 12.1 | **50.1** | **32.4** | 17.3 |

**Key Findings:**
- SAGE achieves **8.9% higher SGC** on Test Normal compared to baseline GRPO
- **59% fewer tokens** compared to baseline GRPO
- RL approach with skill library enables open-source models to **surpass expert performance**
- Prompt-based skill library agent shows limitations; SFT alone is insufficient
- SAGE further enhances SFT-trained model to achieve superior performance

### 4.3 Skill Library Usage Analysis

**Metrics:**
1. **Skill Usage Rate**: Proportion that use skills (among examples with skill library)
2. **Success Skill Usage Rate**: Proportion reaching successful completion (among skill users)
3. **Skill Library Size**: Total generated skills
4. **Used Skill Num**: Number of skills being used

**Results (relative to Base Model):**

| Metric | Base Model | SFT | SAGE |
|--------|------------|-----|------|
| Skill Usage Rate | 1.0 | 0.63 | 0.88 |
| Success Skill Usage Rate | 0.31 | 0.51 | 0.72 |
| Skill Library Size | 439 | 336 | 361 |
| Used Skill Num | 101 | 205 | 230 |

**Key Observations:**
- SAGE significantly improves both Skill Usage Rate and Success Skill Usage Rate
- Base Model generates more skills but with lower quality and utilization effectiveness
- SFT improves Success Skill Usage Rate but insufficient for self-improvement capabilities

### 4.4 Ablation Studies

#### Evaluation without Skills

| Step | With Skill | TGC | SGC | Avg. Steps | Avg. Tokens |
|------|------------|-----|-----|------------|-------------|
| Skill Library Agent | ✓ | 30.7 | 19.6 | 13.4 | 2,988 |
| | ✗ | 34.7 | 14.9 | 16.4 | 3,704 |
| SFT | ✓ | 55.2 | 41.7 | **11.4** | **1,340** |
| | ✗ | 54.8 | 39.9 | 13.5 | 1,611 |
| SAGE | ✓ | **72.0** | **60.7** | 12.1 | 1,475 |
| | ✗ | 71.4 | 54.8 | 16.0 | 1,937 |

**Finding**: All models achieve improved SGC with reduced steps/tokens when using skills.

#### Skill Retrieval Methods

| Retrieval Method | TGC | SGC | Avg. Steps | Avg. Tokens |
|------------------|-----|-----|------------|-------------|
| Same Scenario | **72.0** | **60.7** | 12.1 | 1,475 |
| Query N-gram | **72.0** | 60.1 | 12.7 | 1,466 |
| Query Embedding | 69.6 | 59.5 | **11.8** | **1,335** |
| Skill Embedding | 66.3 | 56.0 | 14.5 | 1,692 |

**Finding**: Query N-gram achieves performance closest to ideal Same Scenario case.

#### Reward Design

| Reward Design | TGC | SGC | Avg. Steps | Avg. Tokens |
|---------------|-----|-----|------------|-------------|
| Skill-integrated | **72.0** | **60.7** | **12.1** | 1,475 |
| Outcome-based | 69.8 | 55.4 | 13.1 | 1,469 |
| Chain-based | 67.9 | 56.6 | 15.7 | **1,361** |

**Finding**: Skill-integrated Reward achieves superior TGC and SGC scores.

#### RL Initialization

| Initialization | Extra Data | TGC | SGC | Avg. Steps | Avg. Tokens |
|----------------|------------|-----|-----|------------|-------------|
| Base Model | ✗ | 40.7 | 25.6 | **11.9** | 2,532 |
| Self Distillation | ✗ | 66.5 | 53.6 | 13.1 | 2,321 |
| RL Warm-Up | ✗ | 68.3 | 55.3 | 16.0 | 2,556 |
| SFT | ✓ | **72.0** | **60.7** | 12.1 | **1,475** |

**Finding**: SFT initialization with expert data is crucial for state-of-the-art performance.

---

## 5. Conclusion

This paper presents pioneering work in exploring RL for self-improving agents with skill libraries. Key contributions:

1. **SAGE Framework**: Novel RL framework incorporating GRPO with Sequential Rollout and Skill-integrated Reward
2. **Significant Improvements**: On AppWorld, SAGE enables skill library agents to significantly outperform baselines in both performance and efficiency
3. **Path Forward**: Paves the way for enhanced self-improvement capabilities with skill libraries through RL

---

## Limitations

- Experiments conducted exclusively on AppWorld dataset
- Different scenarios may require different agent designs
- Future work: Extend evaluation to other tool-using agent datasets

---

## Key Concepts Summary

### Skill Library Agent Components

```
┌─────────────────────────────────────────────────────────┐
│                   Skill Library Agent                    │
├─────────────────────────────────────────────────────────┤
│  1. Skill Usage      - Use existing skills from library │
│  2. Skill Generation - Create new function skills       │
│  3. Skill Update     - Fix and retry failed skills      │
│  4. Skill Save       - Store successful skills          │
└─────────────────────────────────────────────────────────┘
```

### Sequential Rollout with Skill-integrated Reward

```
┌──────────────┐    Skills    ┌──────────────┐
│   Task q¹    │ ───────────► │   Task q²    │
│              │   transfer   │              │
└──────┬───────┘              └──────┬───────┘
       │                             │
       ▼                             ▼
┌──────────────┐              ┌──────────────┐
│ Task Success │              │ Task Success │
│    Reward    │              │    Reward    │
└──────────────┘              └──────────────┘
       │                             │
       └─────────┬───────────────────┘
                 ▼
         ┌──────────────┐
         │    Extra     │
         │   Rewards:   │
         │ - Skill Gen  │
         │ - Skill Use  │
         └──────────────┘
```

---

## References

Key references from the paper:

- Chen et al., 2025. Reinforcement learning for long-horizon interactive LLM agents.
- Nguyen et al., 2024. DynaSaur: Large language agents beyond predefined actions.
- Shao et al., 2024. DeepSeekMath: Pushing the limits of mathematical reasoning in open language models.
- Trivedi et al., 2024. AppWorld: A controllable world of apps and people for benchmarking interactive coding agents.
- Wang et al., 2024a. Voyager: An open-ended embodied agent with large language models.
- Wang et al., 2024b. Executable code actions elicit better LLM agents (CodeAct).
- Wang et al., 2025b. Inducing programmatic skills for agentic tasks.
- Yao et al., 2023. ReAct: Synergizing reasoning and acting in language models.

---

*Document converted from PDF: SAGE.pdf*
*arXiv:2512.17102v1 [cs.AI] 18 Dec 2025*

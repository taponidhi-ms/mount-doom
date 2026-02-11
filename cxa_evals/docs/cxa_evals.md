# CXA Evals Package – Overview & Metrics

The **CXA Evals** package is a comprehensive **response evaluation framework** designed to assess open-ended AI outputs using **LLM-as-a-judge** evaluation metrics. It enables you to evaluate your AI-generated responses against well-defined (out of the box, OOB) or custom evaluation metrics.

---

## 1.  What This Package Offers

- **Reusable Evaluation Framework** – Works across domains, data types, and scenarios.
- **Multiple Evaluator Types** – Choose from default or custom evaluation metrics.
- **Actionable Insights** – Identify strengths, weaknesses, and improvement areas in your outputs.

---

## 2. Supported Evaluators 

| **Evaluator Name** | **Key** | **Purpose** |
|--------------------|---------|-------------|
| **DefaultEvaluator** | `default` | Runs the standard set of metrics for general quality checks. |
| **CustomEvaluator** | `custom` | Allows tailored metric sets or weighting for specific use cases. |
| **GroundnessEvaluator** | `groundness` | Focuses on verifying that responses are grounded in authoritative source material. |
| **SBSEvaluator** | `sbs` | Focuses on comparing two model outputs for same prompt. |

---
## 3. Goals for Writing Metrics

The purpose of defining evaluation metrics in **CXA Evals** is to establish a **clear, shared standard** for what “good” looks like, so quality can be measured, compared, and improved consistently across teams, domains, and use cases.

### 3.1 Define Quality in Measurable Terms
- Translate abstract ideas like “helpful” or “clear” into **specific, observable criteria**.
- Example: Instead of “The answer should be professional, ” define *Tone* metric as:  
  *Matches professional tone used for qualified sales representatives.*

### 3.2 Ensure Consistency Across Evaluators
- Different evaluators, human or automated (LLM as a judge), should align at the **same score** for the same output.
- Metrics provide a "_common scoring language_".

### 3.4 Support Continuous Improvement
- Tracking scores over time highlights **patterns and weak spots**.
- Enables continuous monitoring and progress tracking over time..

### 3.5 Enable Transparency and Accountability
- Stakeholders can see **why** an output scored the way it did.
- Builds trust in the evaluation process.

### 3.6 Balance Multiple Dimensions of Quality
- An output can be partially correct but incomplete, or complete but irrelevant.
- Metrics ensure all critical aspects: **Accuracy, Completeness, Relevance, Usefulness, Conversationality, Groundedness, Safety** are considered.

---

## 4. Summary

The **CXA Evals package** gives partner teams:
- A **consistent and reusable framework** for evaluating the quality of open-ended AI outputs.
- **Clear, measurable metrics** that work across domains.
- A **scoring system** that supports transparency, comparability, and improvement.

By applying these principles, teams can ensure their outputs are **reliable, relevant, and valuable**, no matter the data source or use case.
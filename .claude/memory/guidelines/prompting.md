# Claude Code Prompting Guidelines

> For LLM-savvy engineers. Optimize for **performance** and **stable output formats** across data transformation, LLM-as-judge, and predictive/reasoning tasks.

---

## 1) Core Principles

* **State the contract up front.** Specify goal, inputs, constraints, and the *exact* output schema (keys, types, ordering, units). Keep ambiguity at zero.
* **Structure with tags.** Delimit sections (e.g., `<instructions>`, `<input>`, `<examples>`, `<output-spec>`) to prevent instruction/context bleed and to make parsing trivial.
* **Show, don't tell.** Include 2–5 representative I/O examples (covering edge cases) to enforce format and behavior.
* **Let the model think when needed.** Ask for step-by-step reasoning, ideally separated from the final answer (e.g., `<thinking>…</thinking>` then `<answer>…</answer>`). Use CoT only for tasks that benefit.
* **Prefer prompt chaining for multi-step work.** Plan → generate → verify → refine; isolate weak links.

---

## 2) Output Control (Make It Machine-Safe)

* **Rigid schemas.** Provide a minimal JSON (or XML) prototype or typed schema; forbid extra text.
* **Prefill to skip preamble.** In non-extended-thinking modes, prefill the assistant with `{` (or an opening tag) to force immediate structured output.
* **Consistency tactics:**
  * Keep keys stable and sorted; pin number formats (e.g., 2 decimals).
  * If uncertain/missing, emit `null` or `"unknown"` rather than inventing fields.
  * When strictness matters, add a second "**validate/repair**" pass that echoes corrected JSON only. (Two-pass is the pragmatic fix for occasional formatting slips.)

---

## 3) Reliability Patterns

* **CoT & Self-Consistency.** For hard reasoning, ask for multiple independent solution paths and converge on the majority result.
* **Self-critique.** Add a follow-up prompt: "Review the above for errors/omissions vs. the schema/criteria; output the corrected result only."
* **Evidence-first.** When grounding to documents, instruct: "extract quotes/snippets first, then answer using only those." (Reduces hallucinations.)

---

## 4) LLM-as-Judge (Evaluation Prompts)

* **Use an explicit rubric.** List criteria (e.g., correctness, completeness, style) and desired scales; require justification per criterion.
* **Prefer pairwise for subjective tasks.** It improves stability in many settings—*but* be aware of bias/manipulation risks; calibrate with spot human checks.
* **Output contract.** Return a compact JSON with per-criterion scores, rationale, and an overall verdict.

---

## 5) Prompt Skeletons (Drop-in)

### A. Data Transformation

```text
<role>You are a precise data transformer.</role>
<input>
{{RAW_DATA}}
</input>
<instructions>
1) Convert to the schema below. 2) Enforce units and types. 3) Never add fields.
</instructions>
<output-spec>
Return ONLY a JSON object with keys:
- "id": string
- "date_utc": ISO 8601 string
- "amount_usd": number (2 decimals)
- "tags": array[string] (sorted asc)
Missing → use null. Unknown → "unknown".
</output-spec>
<examples>
<example>
<input>{"id":"A1","date":"2025/09/10","amt":"12.5","tags":"b,a"}</input>
<output>{"id":"A1","date_utc":"2025-09-10T00:00:00Z","amount_usd":12.50,"tags":["a","b"]}</output>
</example>
</examples>
<answer>
{   <-- prefill "{" in non-extended-thinking modes
```

(End the prefill at `{` to force raw JSON.)

### B. LLM-as-Judge (Pairwise)

```text
<role>You are a strict evaluator.</role>
<question>{{Q}}</question>
<answer_a>{{A}}</answer_a>
<answer_b>{{B}}</answer_b>
<rubric>
Criteria (0–5 each): correctness, completeness, clarity, safety.
</rubric>
<instructions>
1) Brief justification per criterion.
2) Then output ONLY this JSON:
{
  "scores": {
    "A": {"correctness": n, "completeness": n, "clarity": n, "safety": n},
    "B": {"correctness": n, "completeness": n, "clarity": n, "safety": n}
  },
  "winner": "A"|"B"|"tie",
  "rationale": "≤120 chars overall reasoning"
}
</instructions>
<answer>{
```

(Use pairwise for subjective qualities; monitor for bias.)

### C. Predictive/Reasoning

```text
<role>You are a careful analyst.</role>
<context>{{STRUCTURED_CONTEXT}}</context>
<task>Predict {{TARGET}}.</task>
<instructions>
Think step-by-step in <thinking>, then output ONLY:
{
  "prediction": <number|string>,
  "confidence": 0..1,
  "assumptions": ["…", "…"]
}
If insufficient info, set "prediction": null and explain in "assumptions".
</instructions>
<thinking>…detailed reasoning…</thinking>
<answer>{
```

(CoT improves complex reasoning; include uncertainty rather than guessing.)

---

## 6) Anti-Patterns (Avoid)

* Vague goals ("summarize this") without audience/purpose/format.
* Mixing instructions, data, and examples in one blob; always tag and separate.
* Asking for JSON but allowing narration; enforce "**ONLY JSON**" and prefill.
* One mega-prompt for multi-stage tasks; chain and verify instead.

---

## 7) Quick QA Checklist (pre-ship)

* **Inputs delimited?** (`<input>`, `<context>`)
* **Schema pinned?** Keys, types, units, ordering
* **Examples present?** Nominal + edge cases (2–5)
* **Reasoning mode set?** (none / guided CoT / structured CoT)
* **Chaining plan?** Generate → review → repair → finalize
* **Preamble skipped?** (prefill)
* **Hallucination guard?** Evidence-first or "unknown/null if missing"

---

## References

Key concepts and patterns drawn from:

* Anthropic Prompt Engineering: XML tags, CoT, examples, roles, chaining, consistency & prefilling
* Zero-Shot CoT ("Let's think step by step")
* Self-Consistency for CoT
* LLM-as-Judge (MT-Bench/Chatbot Arena) and reliability cautions

---

**Usage tip:** Keep this file near your prompts (e.g., `PROMPTS.md`). Start from the skeletons, then iterate with a small eval set to confirm **format stability** and **task accuracy** before scaling.

# ExpertLens AI — Evaluation & Reliability Framework Documentation

## 1. Overview

ExpertLens AI features an integrated, production-grade **Evaluation & Reliability System** that rigorously benchmarks:
1. **End-to-End Answer Quality**: Fact accuracy, semantic groundedness, and hallucination prevention.
2. **Intermediate Execution Traces**: Retrieval relevance, tool selection, parameter correctness, latency, and token consumption.
3. **Deterministic Quote & Timestamp Validation**: Verifying that every attributed quote exists verbatim in the source transcripts.
4. **4-Stage Guardrails**: Real-time defense against prompt injection, cross-country data contamination, empty context retrieval, and unsupported assertions.
5. **Multi-Label Chunk Classification**: Measuring precision, recall, micro F1, and macro F1 across a 10-class domain taxonomy.
6. **A/B Testing & Human Review Calibration**: Side-by-side prompt/model experiments and human domain expert agreement scoring.

---

## 2. Directory Structure

```text
backend/evals/
├── datasets/
│   ├── benchmark_dataset.py       # 14 Real-world test cases covering explicit, implicit, cross-expert, and adversarial traps
│   └── classification_dataset.py  # Ground truth multi-label chunk annotations across 10 classes
├── graders/
│   ├── accuracy_grader.py         # Fact, answer, source, and citation precision
│   ├── groundedness_grader.py     # Groundedness, hallucination rate, safe abstention
│   ├── classification_grader.py   # Precision, recall, micro & macro F1
│   ├── tool_grader.py             # Tool selection, parameter correctness, latency, token usage
│   ├── quote_grader.py            # Exact & normalized deterministic quote verifier
│   └── context_grader.py          # Implicit reasoning & contradictory evidence handling
├── human_review/
│   ├── rubric.py                  # Standard 6-dimension evaluation rubric definitions
│   └── review_manager.py          # CSV/JSON export/import and Cohen's Kappa calculation
├── ab_testing/
│   └── experiment_runner.py       # Multi-variant comparative evaluation runner
├── runner.py                      # Main evaluation CLI and engine
├── report.py                      # Terminal ASCII scorecard, JSON, and CSV report generator
└── regression.py                  # Release gate regression check with exit codes
```

---

## 3. The 4-Stage Guardrails Pipeline

```
User Query
    ↓
[Stage 1: Input Guardrail]
  • Prompt injection detection (regex pattern filters)
  • False premise / non-existent entity detection
  • Trigger safe abstention if out-of-domain
    ↓
[Stage 2: Retrieval Guardrail]
  • Country and expert filter alignment
  • Chunk relevance thresholding (RETRIEVAL_SCORE_THRESHOLD)
  • Empty retrieval check
    ↓
[Stage 3: LLM Output Guardrail]
  • JSON structure and required schema enforcement
  • Chunk ID verification against retrieved set
    ↓
[Stage 4: Final Response Guardrail]
  • Cross-country contamination detection (preventing UK quotes assigned to Germany)
  • Deterministic quote validation against raw transcript text
  • Safe abstention fallback:
    "I couldn't find enough evidence in the provided transcripts to answer this question."
```

---

## 4. Multi-Label Classification Taxonomy (10 Classes)

1. `ADOPTION`: Current adoption levels, penetration rates, regional spread.
2. `BARRIER`: Impediments to acquisition (cost, resistance, training bottlenecks).
3. `ECONOMICS`: Capital expenditures, financial cases, budget approvals.
4. `ROI`: Payback period, procedure volume breakeven, business case viability.
5. `TRAINING`: Surgeon and theatre staff learning curves, simulator availability.
6. `CLINICAL_OUTCOME`: Complication rates, length of stay, surgical precision.
7. `OUTLOOK`: 3–5 year market expectations, annual procedure growth percentages.
8. `PURCHASING_TIMELINE`: Decision cycles (e.g. 6–12 months, 9–18 months).
9. `UTILIZATION`: Daily system volume, multi-specialty usage sharing.
10. `FUNDING`: Capital cycles, NHS trust allocations, DRG reimbursement tariffs.

---

## 5. Execution Commands

### Run Full Benchmark Evaluation
```bash
cd backend
python -m evals.runner
```
*Generates formatted terminal ASCII scorecards and writes reports to `data/evals/evals_report.json` and `data/evals/evals_report.csv`.*

### Run Release Gate Regression Suite
```bash
cd backend
python -m evals.regression
```
*Evaluates release gates defined in `.env` (`EVAL_MIN_ACCURACY`, `EVAL_MIN_GROUNDEDNESS`, `EVAL_MAX_HALLUCINATION`, `EVAL_MIN_CITATION_COVERAGE`). Returns exit code `0` on PASS or `1` on FAIL.*

### Run All Unit and Integration Tests
```bash
cd backend
pytest
```

---

## 6. Configurable Release Gate Thresholds (`.env`)

| Variable | Default Threshold | Description |
|---|---|---|
| `EVAL_MIN_ACCURACY` | `0.85` | Minimum required fact & answer accuracy |
| `EVAL_MIN_GROUNDEDNESS` | `0.90` | Minimum evidence grounding score |
| `EVAL_MAX_HALLUCINATION` | `0.05` | Maximum allowable hallucination rate |
| `EVAL_MIN_CITATION_COVERAGE` | `0.85` | Minimum citation coverage for generated claims |

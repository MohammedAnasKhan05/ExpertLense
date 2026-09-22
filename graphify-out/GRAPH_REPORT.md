# Graph Report - Hasamex_Project  (2026-09-23)

## Corpus Check
- 98 files · ~38,095 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 700 nodes · 1447 edges · 38 communities (31 shown, 7 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- services/comparison.py
- themes.py
- api.ts
- LLMProvider
- compilerOptions
- runner.py
- run_evaluation
- package.json
- transcripts.py
- validate_quote
- HumanReviewItem
- ingestion.py
- get_llm_provider
- counter.ts
- api/evidence.py
- analyze_all_questions
- GuardrailPipeline
- config.py
- api/chat.py
- FallbackStore
- Hasamex AI Engineer – Technical Case
- api/analysis.py
- main.py
- ExpertLens AI — Evaluation & Reliability Framework Documentation
- rules/graphify.md
- workflows/graphify.md
- services/analysis.py
- LocalProvider
- GroqProvider
- database.py
- HuggingFaceProvider

## God Nodes (most connected - your core abstractions)
1. `run_single_test_case()` - 26 edges
2. `validate_quote()` - 23 edges
3. `EvalTestCase` - 23 edges
4. `GuardrailPipeline` - 21 edges
5. `LLMProvider` - 21 edges
6. `get_llm_provider()` - 21 edges
7. `Document` - 20 edges
8. `extract_themes()` - 20 edges
9. `ToolTracer` - 18 edges
10. `analyze_all_questions()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `list_transcripts()` --uses--> `Document`  [INFERRED]
  backend/app/api/transcripts.py → backend/app/models/document.py
- `list_transcripts()` --uses--> `TranscriptChunk`  [INFERRED]
  backend/app/api/transcripts.py → backend/app/models/transcript_chunk.py
- `get_transcript()` --uses--> `Document`  [INFERRED]
  backend/app/api/transcripts.py → backend/app/models/document.py
- `get_transcript()` --uses--> `TranscriptChunk`  [INFERRED]
  backend/app/api/transcripts.py → backend/app/models/transcript_chunk.py
- `ABExperimentRunner` --uses--> `GuardrailPipeline`  [INFERRED]
  backend/evals/ab_testing/experiment_runner.py → backend/app/guardrails/pipeline.py

## Import Cycles
- None detected.

## Communities (38 total, 7 thin omitted)

### Community 0 - "services/comparison.py"
Cohesion: 0.21
Nodes (13): ComparisonCell, ComparisonResponse, ComparisonRow, BaseModel, ExpertLens AI — Comparison Schemas Pydantic models for cross-market comparison…, A single cell in the comparison table., A row comparing all markets on one topic., Full comparison table response. (+5 more)

### Community 1 - "themes.py"
Cohesion: 0.09
Nodes (32): get_analysis(), get_comparison_view(), get_themes(), list_interview_questions(), AsyncSession, get, Get existing analysis results (does not trigger new analysis)., Get the cross-market comparison table. (+24 more)

### Community 2 - "api.ts"
Cohesion: 0.07
Nodes (59): App(), EvidenceCard(), EvidenceCardProps, EvidenceLabel(), EvidenceDrawer(), EvidenceDrawerProps, navItems, Sidebar() (+51 more)

### Community 3 - "LLMProvider"
Cohesion: 0.13
Nodes (11): ABC, LLMProvider, ExpertLens AI — LLM Provider Base Abstract base class for all LLM providers.…, Abstract LLM provider interface., Generate a text response from the LLM. Args: prompt: The user/task prompt…, Generate a structured (JSON) response from the LLM. Args: prompt: The user/task…, Return the name of this provider., Alias for provider_name. (+3 more)

### Community 4 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+13 more)

### Community 5 - "runner.py"
Cohesion: 0.05
Nodes (65): ExecutionTrace, Retrieve grounded evidence chunks for a question with optional filters., Full execution trace for an agent or retrieval pipeline run., Context manager and recorder for tool execution traces., tool_retrieve_evidence(), ToolTracer, ABExperimentComparison, ABExperimentRunner (+57 more)

### Community 6 - "run_evaluation"
Cohesion: 0.08
Nodes (34): LabeledChunk, BaseModel, A transcript chunk with ground truth topic labels., ClassificationGrader, ClassificationResult, classify_chunk(), ClassMetric, BaseModel (+26 more)

### Community 7 - "package.json"
Cohesion: 0.07
Nodes (26): dependencies, react, react-dom, react-router-dom, devDependencies, @types/react, @types/react-dom, typescript (+18 more)

### Community 8 - "transcripts.py"
Cohesion: 0.07
Nodes (50): create_transcript(), CreateTranscriptRequest, get_transcript(), list_transcripts(), AsyncSession, BaseModel, get, post (+42 more)

### Community 9 - "validate_quote"
Cohesion: 0.09
Nodes (30): find_best_matching_quote(), normalize_text(), ExpertLens AI — Quote Validator Verifies that quotes attributed to transcript…, Normalize text for comparison by: - lowercasing - collapsing whitespace -…, Validate that a quote exists in the source text. Args: quote: The quote to…, Given an approximate quote, find the best matching segment in the source. This…, validate_quote(), Any (+22 more)

### Community 10 - "HumanReviewItem"
Cohesion: 0.15
Nodes (15): AgreementReport, HumanReviewItem, BaseModel, ExpertLens AI — Human Review Manager Handles: - Exporting evaluation cases to…, Calculate agreement rate and Cohen's Kappa between human labels and automated…, A single evaluation case formatted for human review., Agreement statistics between human reviews and automated graders., Manages human review export, import, and agreement scoring. (+7 more)

### Community 11 - "ingestion.py"
Cohesion: 0.08
Nodes (38): Application settings loaded from environment variables., Return CORS origins as a list., Settings, Chunk, chunk_transcript(), create_context_text(), ExpertLens AI — Transcript Chunking Creates timestamp-aware chunks from parsed…, A metadata-rich transcript chunk ready for embedding and storage. (+30 more)

### Community 12 - "get_llm_provider"
Cohesion: 0.38
Nodes (5): get_llm_provider(), Factory function that returns the configured LLM provider. Reads LLM_PROVIDER…, ExpertLens AI — LLM Package, main(), ExpertLens AI — Analysis Runner Script Runs the analysis pipeline for all…

### Community 15 - "api/evidence.py"
Cohesion: 0.18
Nodes (12): get_evidence_detail(), AsyncSession, get, ExpertLens AI — Evidence API Endpoint Provides evidence detail views for the…, Get detailed evidence for the evidence drawer. Returns the chunk with…, EvidenceDetailSchema, BaseModel, ExpertLens AI — Evidence Schemas Pydantic models for evidence inspection. (+4 more)

### Community 16 - "analyze_all_questions"
Cohesion: 0.16
Nodes (19): AnalysisResponse, AnalysisResponse, GroundedAnswer, BaseModel, QuestionAnalysis, QuestionAnalysisGroup, ExpertLens AI — Analysis Schemas Pydantic models for structured AI output…, An answer grounded in transcript evidence. (+11 more)

### Community 22 - "GuardrailPipeline"
Cohesion: 0.14
Nodes (21): GuardrailCheckResult, GuardrailPipeline, Any, BaseModel, ExpertLens AI — 4-Stage Guardrails Pipeline Implements strict validation across…, Stage 2: Retrieval Validation - Verify chunks exist - Ensure retrieved chunks…, Stage 3: LLM Output Validation - Parse valid structured JSON - Check required…, Stage 4: Final Response Guardrail - Validate citations against retrieved chunk… (+13 more)

### Community 24 - "api/chat.py"
Cohesion: 0.15
Nodes (19): _build_fallback_answer(), AsyncSession, post, ExpertLens AI — Chat API Endpoint Research AI interface for asking questions…, Build a structured answer from chunks when external LLM fails., Ask a research question across all transcripts. Returns a grounded answer with…, research_chat(), A verified source citation from a transcript. (+11 more)

### Community 26 - "Hasamex AI Engineer – Technical Case"
Cohesion: 0.29
Nodes (6): Demo, Hasamex AI Engineer – Technical Case, Important, Objective, Submit, Your app should:

### Community 27 - "api/analysis.py"
Cohesion: 0.22
Nodes (9): post, ExpertLens AI — Analysis API Endpoints Handles interview question analysis,…, Trigger or retrieve interview question analysis. Analyzes all 6 interview…, run_analysis(), get_db(), AsyncSession, Dependency that yields a database session., AnalyzeRequest (+1 more)

### Community 28 - "main.py"
Cohesion: 0.16
Nodes (12): init_db(), Create all tables. Called on application startup., health_check(), lifespan(), get, ExpertLens AI — FastAPI Application Evidence-Grounded Expert Interview…, Application startup and shutdown events., Health check endpoint. (+4 more)

### Community 29 - "ExpertLens AI — Evaluation & Reliability Framework Documentation"
Cohesion: 0.18
Nodes (10): 1. Overview, 2. Directory Structure, 3. The 4-Stage Guardrails Pipeline, 4. Multi-Label Classification Taxonomy (10 Classes), 5. Execution Commands, 6. Configurable Release Gate Thresholds (`.env`), ExpertLens AI — Evaluation & Reliability Framework Documentation, Run All Unit and Integration Tests (+2 more)

### Community 33 - "services/analysis.py"
Cohesion: 0.20
Nodes (11): Document, ExpertLens AI — Document Model Represents an uploaded expert interview…, An expert interview transcript document., ExpertLens AI — Analysis Service Generates grounded answers for the six…, format_context_for_llm(), ExpertLens AI — Retrieval Service Orchestrates semantic retrieval from ChromaDB…, Retrieve relevant transcript chunks for an interview question. Combines…, Format retrieved chunks into a context string for the LLM prompt. Uses the… (+3 more)

### Community 34 - "LocalProvider"
Cohesion: 0.24
Nodes (6): LocalProvider, Extract structured context sections from the prompt. The retrieval service…, Deterministic local provider that extracts answers directly from transcript…, Generate a text response by extracting key content from the prompt context., Generate a structured JSON response with Synthesized Analysis and Transcript…, Constructs an executive synthesis across retrieved expert statements.

### Community 36 - "database.py"
Cohesion: 0.14
Nodes (14): Base, ExpertLens AI — Database Setup SQLAlchemy async engine and session factory.…, Base class for all SQLAlchemy ORM models., Evidence, ExpertLens AI — Evidence Model Links an answer to its supporting transcript…, A verified piece of evidence linking an answer to a transcript chunk., ExpertLens AI — Database Models Package Imports all SQLAlchemy ORM models so…, InterviewAnswer (+6 more)

## Knowledge Gaps
- **58 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm_provider()` connect `get_llm_provider` to `themes.py`, `LocalProvider`, `LLMProvider`, `GroqProvider`, `HuggingFaceProvider`, `runner.py`, `run_evaluation`, `config.py`, `api/chat.py`, `api/analysis.py`, `main.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Document` connect `services/analysis.py` to `services/comparison.py`, `themes.py`, `database.py`, `transcripts.py`, `ingestion.py`, `api/evidence.py`, `analyze_all_questions`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `validate_quote()` connect `validate_quote` to `services/analysis.py`, `themes.py`, `runner.py`, `analyze_all_questions`, `GuardrailPipeline`, `api/chat.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `run_single_test_case()` (e.g. with `GuardrailPipeline` and `EvalTestCase`) actually correct?**
  _`run_single_test_case()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `EvalTestCase` (e.g. with `ABExperimentRunner` and `AccuracyGrader`) actually correct?**
  _`EvalTestCase` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `GuardrailPipeline` (e.g. with `ABExperimentRunner` and `run_single_test_case()`) actually correct?**
  _`GuardrailPipeline` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `LLMProvider` (e.g. with `get_llm_provider()` and `analyze_all_questions()`) actually correct?**
  _`LLMProvider` has 4 INFERRED edges - model-reasoned connections that need verification._
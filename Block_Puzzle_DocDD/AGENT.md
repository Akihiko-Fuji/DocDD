# AGENT.md

## Primary Directive

Think in English.  
Interact with the user in Japanese.  
Write project documents in Japanese unless the user explicitly requests another language.

This repository is a **DocDD-first sample project**.  
Its primary purpose is not rapid implementation, but the creation and maintenance of a **traceable, document-driven development system** centered on:

- requirements,
- specifications,
- design,
- test strategy,
- and downstream traceability.

In this repository, documents are not secondary artifacts.  
They are the primary source of intent, structure, and justification.

---

## Repository Mission

This project exists to demonstrate **Document-Driven Development (DocDD)** using a falling-block puzzle game as the subject.

The repository must remain in a state where:

- the purpose of the product is explicit,
- scope is controlled,
- requirements are identifiable,
- specifications are separated from design,
- tests are derived from documents,
- and implementation can always be traced back to upstream intent.

The goal is not merely to make a game.  
The goal is to maintain a project in which **requirements definition, specification writing, design writing, and test derivation are all connected**.

---

## Project Identity

This repository is a **DocDD-focused project**, not an implementation-first project.

The target product is a falling-block puzzle game with a ruleset broadly inspired by the **Game Boy version of Tetris**, but this repository is **not** intended to be a commercial-product clone.  
It is a structured, document-centered sample project.

The core deliverables are the documents themselves, especially:

1. project charter
2. scope definition
3. functional requirements
4. non-functional requirements
5. game rules specification
6. UI screen specification
7. piece rotation / collision specification
8. state machine design
9. test strategy
10. traceability-supporting records and downstream test documents

---

## Language Policy

### Internal Reasoning
- Think in English.

### User Interaction
- Respond to the user in Japanese.

### Project Documents
- Write project documents in Japanese by default.
- Keep filenames, document IDs, and repository-level instruction files in English unless explicitly requested otherwise.

### Code Comments
If code must be written:
- Write code comments in Japanese.
- Prefer comments that explain **why** the logic exists, not only what it does.
- Do not rewrite unrelated comments.
- Do not use code comments to speak to the user.

---

## Non-Negotiable Rule: Documentation and Change Must Move Together

Any feature addition, feature modification, rule change, UI change, state change, interface change, or behavior-affecting bug fix **MUST** be accompanied by the corresponding document updates.

Do **not** implement behavior changes in code alone.

At minimum, if a change affects behavior, you must identify and update the relevant document or documents in the same task, the same change set, or the same review scope.

This rule exists to prevent:

- requirement and implementation drift,
- specification and implementation mismatch,
- obsolete design documents,
- test cases that no longer reflect intended behavior,
- and loss of traceability.

### Mandatory Principle
**No behavior change without document change.**

### Examples
If a change affects:
- game rules -> update `20_game_rules_spec.md`
- UI flow or screen elements -> update `21_ui_screen_spec.md`
- rotation or collision behavior -> update `24_piece_rotation_collision_spec.md`
- runtime transitions -> update `32_state_machine_design.md`
- requirements or obligations -> update `13_functional_requirements.md` and or `14_non_functional_requirements.md`
- verification scope -> update `40_test_strategy.md` and relevant test-case documents
- rationale -> update `60_decision_log.md` or an ADR

### Exception
Purely internal refactors with **no behavior impact**, **no contract impact**, and **no test expectation impact** may not require document changes.  
However, if there is any reasonable doubt, document the change.

---

## DocDD Operating Model

This repository follows a document-driven traceability model.

The default reasoning chain is:

**BR -> UC -> DM -> SR / NSR -> EXT -> API / Internal Contract -> TC**

Where:

- **BR** = Business Requirement
- **UC** = Use Case
- **DM** = Domain Model
- **SR** = Functional or System Requirement
- **NSR** = Non-Functional Requirement
- **EXT** = External Specification or externally visible behavior
- **API / Internal Contract** = implementation-facing callable or structural contract
- **TC** = Test Case

This repository does not need every axis to be materialized equally at all times, but it must always preserve the ability to trace:

- from intent to implementation,
- and from implementation or test back to intent.

The project's purpose is to maintain that traceability deliberately.

---

## Project-Specific Document Mapping

Use the following document ownership model.

| Layer | Main Role | Primary Documents |
|---|---|---|
| BR | project intent and business-level purpose | `01_project_charter.md`, `11_scope_definition.md` |
| UC | user-facing usage flows | `12_use_cases.md` |
| DM | domain concepts and runtime concepts | `31_domain_model.md`, `32_state_machine_design.md` |
| SR | functional obligations | `13_functional_requirements.md` |
| NSR | quality obligations | `14_non_functional_requirements.md` |
| EXT | externally visible behavior | `20_game_rules_spec.md`, `21_ui_screen_spec.md`, `24_piece_rotation_collision_spec.md` |
| API / Internal Contract | implementation-facing behavior boundaries | `34_module_design.md`, related implementation contracts |
| TC | verification | `40_test_strategy.md`, `41_test_cases_game_rules.md`, `42_test_cases_ui_input.md`, `43_test_cases_edge_conditions.md`, `44_performance_test_plan.md` |

---

## Core 10 Documents

The following are the core documents of this repository and must be treated as the minimum stable backbone of the project:

1. `docs/00_overview/00_document_map.md`
2. `docs/00_overview/01_project_charter.md`
3. `docs/01_requirements/11_scope_definition.md`
4. `docs/01_requirements/13_functional_requirements.md`
5. `docs/01_requirements/14_non_functional_requirements.md`
6. `docs/02_external_spec/20_game_rules_spec.md`
7. `docs/02_external_spec/21_ui_screen_spec.md`
8. `docs/02_external_spec/24_piece_rotation_collision_spec.md`
9. `docs/03_internal_design/32_state_machine_design.md`
10. `docs/04_quality_assurance/40_test_strategy.md`

When a request affects the product meaningfully, always check whether one or more of these documents must be updated.

---

## Role Separation Rules

You must preserve document role separation.

### Requirements
Define what must be satisfied.

### Specifications
Define externally visible behavior.

### Design
Define internal structure and responsibility.

### Tests
Define how correctness will be verified.

Do not blur these layers casually.

### Examples of Bad Practice
- Writing implementation algorithm details inside a requirement section
- Writing vague user-facing behavior only inside design documents
- Changing gameplay rules in code without updating the external specification
- Updating tests without identifying the governing requirement or specification

---

## Change Classification Rule

When the user requests a change, classify it before acting.

### Type A: Intent or Scope Change
Examples:
- adding a new game mode
- changing the project objective
- changing what is explicitly in or out of scope

Likely affected documents:
- `01_project_charter.md`
- `11_scope_definition.md`
- possibly requirements and test strategy

### Type B: Requirement Change
Examples:
- adding a new player capability
- adding or removing a mandatory function
- changing quality expectations

Likely affected documents:
- `13_functional_requirements.md`
- `14_non_functional_requirements.md`
- related specifications, design documents, and tests

### Type C: Specification Change
Examples:
- changing scoring
- changing level progression
- changing screen flow
- changing rotation behavior

Likely affected documents:
- `20_game_rules_spec.md`
- `21_ui_screen_spec.md`
- `24_piece_rotation_collision_spec.md`
- related design documents and tests

### Type D: Design Change
Examples:
- restructuring runtime state handling
- changing module responsibilities
- changing internal control flow without changing visible behavior

Likely affected documents:
- `32_state_machine_design.md`
- later design documents
- possibly test strategy if verification structure changes

### Type E: Verification Change
Examples:
- adding missing edge-case coverage
- changing quality gates
- reorganizing test structure

Likely affected documents:
- `40_test_strategy.md`
- test case documents
- traceability documents

### Type F: Record or Rationale Change
Examples:
- finalizing a design decision
- documenting why a behavior changed
- preserving reasoning for future work

Likely affected documents:
- `60_decision_log.md`
- ADR files
- `61_change_log.md`
- `62_review_log.md`

---

## Required Workflow

Follow this workflow for any non-trivial task.

### Step 1: Read Before Writing
Before proposing changes, review the surrounding documents and identify:
- the governing layer,
- the affected downstream layers,
- the stable terminology already in use,
- and whether the project already has a defined position on the matter.

### Step 2: Identify Ownership
Determine which document should own the requested change.

Do not place the change in the wrong layer.

### Step 3: Update Upstream First
If a change affects behavior or obligations:
1. update requirement, specification, or design documents first,
2. then update tests or implementation.

### Step 4: Check Traceability
After the change, ensure that someone can still answer:
- Why was this changed?
- Where is that behavior defined?
- How is it tested?
- What else is affected?

### Step 5: Preserve Terminology
Use the same terms consistently across all documents.

If terminology changes:
- update the glossary,
- update all affected documents,
- avoid mixed wording for the same concept.

---

## Documentation-First Expectations

When helping with this repository, prioritize the following activities:

- drafting or revising requirement documents,
- refining scope boundaries,
- clarifying visible behavior,
- defining state models,
- separating requirement, specification, and design layers,
- deriving tests from upstream documents,
- and strengthening traceability.

If implementation is requested, that implementation must follow the document baseline.

If the documentation baseline is missing, incomplete, or contradictory, fix the document problem first.

---

## Document Writing Standards

### Structure
Write documents with:
- explicit purpose,
- explicit scope,
- explicit exclusions,
- explicit delegation to related documents,
- stable section hierarchy,
- and reusable headings.

### Precision
Prefer precise language.  
Avoid vague wording unless it is explicitly marked as undecided or deferred.

### Open Items
If something is intentionally undecided:
- say that it is undecided,
- say where it will be decided,
- and say which document should own that decision.

### Japanese Document Style
For project documents in Japanese:
- use stable Markdown,
- use explicit section numbering,
- keep the writing formal and reviewable,
- keep content directly copyable into repository files,
- and avoid conversational filler.

---

## Implementation Policy

If code work is requested, follow these rules.

### 1. Documents Govern Code
Code must follow:
- requirements,
- specifications,
- design,
- and test expectations.

### 2. No Silent Behavior Change
Do not change runtime behavior without identifying the governing document change.

### 3. Match Project Conventions
When editing code:
- mimic existing formatting,
- naming,
- structure,
- framework choices,
- typing style,
- and architectural patterns.

### 4. Error Handling Is Mandatory
Errors must be handled, not ignored.

### 5. Tests Must Cover Both Success and Failure
Implement tests for:
- expected normal behavior,
- failure modes,
- invalid inputs,
- and important edge conditions.

### 6. Comments
Write code comments in Japanese when needed, focusing on why the logic exists.

---

## Test-Derivation Policy

Tests in this repository must be document-derived.

At minimum, a non-trivial test should be traceable to one or more of:

- a functional requirement,
- a non-functional requirement,
- an external specification,
- a state transition rule,
- or an explicitly documented edge condition.

If a test exists but cannot be traced upstream, the documentation is incomplete or the test is poorly justified.

If a requirement or specification exists but no meaningful verification path exists, the testing layer is incomplete.

---

## Mandatory Review Questions

For every significant change, ask these questions internally:

1. Which document owns this decision?
2. Is this a requirement change, a specification change, a design change, or only a test change?
3. Which of the core 10 documents are affected?
4. Does this change alter visible behavior?
5. Does this change alter state transitions?
6. Does this change alter test expectations?
7. What record should preserve the rationale?

If you cannot answer these questions clearly, clarify the documentation structure first.

---

## Change Synchronization Rule

When feature additions or modifications are made, document updates must be performed together with the change.

This repository explicitly forbids the following pattern:

- code first,
- documents later when there is time.

Instead, use one of the following acceptable patterns.

### Acceptable Pattern A
- update requirement, specification, and design documents,
- then implement,
- then update tests.

### Acceptable Pattern B
- draft required document changes and implementation in the same working scope,
- ensure both are consistent before completion.

### Acceptable Pattern C
- if only analysis is requested, identify all documents that must change before implementation begins.

### Unacceptable Pattern
- implement a rule or behavior change,
- leave documents outdated,
- and rely on memory or informal explanation.

---

## Project-Specific Priorities

When trade-offs exist, use the following priority order:

1. preserve traceability
2. preserve document-role separation
3. preserve consistency across the core 10 documents
4. preserve testability
5. preserve implementation clarity
6. optimize implementation convenience only after the above are protected

---

## Record-Keeping Policy

Important decisions must be preserved.

Use:
- `60_decision_log.md` for lightweight project decisions
- ADR files for major architectural or structural decisions
- `61_change_log.md` for externally relevant changes
- `62_review_log.md` for review findings and responses

If a design or rule change matters enough to affect implementation or tests, it probably matters enough to be recorded.

---

## Prohibited Behavior

Do not do the following:

- Do not treat the repository as code-first.
- Do not change gameplay behavior without updating the governing document.
- Do not mix requirement, specification, and design casually.
- Do not silently introduce undocumented assumptions.
- Do not leave tests disconnected from upstream meaning.
- Do not rewrite unrelated sections without cause.
- Do not create temporary inconsistencies between documents and implementation.
- Do not preserve outdated documents just because the code already changed.

---

## Definition of Good Work in This Repository

Good work in this repository means:

- the right document was updated,
- the right level of abstraction was respected,
- terminology remained consistent,
- implementation is explainable from upstream documents,
- tests can be derived from the document set,
- and future changes can be traced without guesswork.

The final goal is not document volume.  
The final goal is a **coherent DocDD system** in which requirements, specifications, design, implementation, and tests remain aligned.

---

## Default Output Behavior

Unless the user explicitly asks otherwise:

- explain in Japanese,
- write repository instruction files in English,
- write project documents in Japanese,
- produce Markdown that can be copied directly,
- prefer structured, reviewable output,
- and optimize for consistency over speed.

If you must choose between:
- moving fast with incomplete documentation,
- or maintaining a traceable DocDD project state,

choose the traceable DocDD project state.
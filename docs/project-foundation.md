# Project Foundation

## 1. Purpose of This Document

This document defines the foundational decisions for the **Binokel Score Tracker** project. It provides a shared baseline for product direction, domain understanding, architecture, development practices, quality expectations, and delivery principles.

Its purpose is to ensure that future implementation decisions remain aligned with a clear product vision and a maintainable engineering approach.

---

## 2. Product Vision

The **Binokel Score Tracker** is an online application for recording, managing, and reviewing scores for the traditional German card game **Binokel**.

The product should replace or improve manual scorekeeping by offering:

- reliable and transparent score tracking,
- an intuitive workflow during active play,
- persistence of match results,
- reduced risk of arithmetic or transcription errors,
- a foundation for future extensions such as player history, statistics, and game variants.

### Vision Statement

> Build a reliable, understandable, and maintainable online score tracker for Binokel that combines strong domain clarity with modern software engineering practices such as BDD, clean architecture, automation, and testability.

---

## 3. Project Goals

### Primary Goals

- Enable digital score tracking for Binokel games.
- Model the essential scoring concepts of the game clearly and correctly.
- Use **BDD with Gherkin** to describe business behavior in a shared language.
- Establish a clean, maintainable, and testable codebase.
- Automate quality checks and development workflows as early as possible.

### Secondary Goals

- Learn and evaluate practical AI-supported development workflows.
- Create a demonstrable example of disciplined software engineering.
- Prepare the project for future growth without premature overengineering.

---

## 4. Non-Goals

The following items are **not part of the initial project baseline** unless explicitly added later:

- real-time multiplayer gameplay,
- full implementation of all possible regional Binokel rule variations,
- social platform features,
- sophisticated ranking systems,
- native mobile applications,
- offline-first synchronization,
- broad gamification features.

These may become later roadmap items, but they are out of scope for the initial foundation and MVP.

---

## 5. Target Users

### Primary Users

- Small groups of players who want to track Binokel scores digitally during or after a game.
- Players who want a clearer, less error-prone alternative to paper-based scorekeeping.

### Secondary Users

- Returning players who want to review previous matches.
- The project owner/developer as a learner and maintainer.

---

## 6. MVP Scope

The MVP should focus on the smallest coherent feature set that delivers real value.

### In Scope for MVP

- Create a game session.
- Register participating players or teams.
- Enter scoring-relevant results round by round.
- Calculate and store cumulative scores.
- Display the current game state clearly.
- End a game and persist the final result.
- Review completed games.

### Explicitly Out of Scope for MVP

- user accounts with complex permissions,
- live collaboration across multiple devices,
- advanced analytics dashboards,
- tournament management,
- support for many rule variants at once,
- notification systems,
- chat or community features.

---

## 7. Domain Understanding

The project should model the domain explicitly instead of mixing game rules, UI behavior, and persistence logic.

### Core Domain Concepts

The following concepts are expected to be central:

- **Game** – a complete Binokel match.
- **Round** – one scoring cycle within a game.
- **Player** – an individual participant.
- **Team** – if the selected Binokel mode uses teams.
- **Score Entry** – the scoring-relevant input for a round.
- **Total Score** – accumulated score across rounds.
- **Rule Set** – the selected scoring interpretation or game variant.
- **Game Status** – e.g. planned, active, completed, cancelled.

### Domain Modeling Principle

Domain concepts must be named consistently and implemented independently from technical concerns such as framework code, HTTP transport, or database layout.

---

## 8. Ubiquitous Language

A shared vocabulary should be defined early and kept stable.

### Initial Ubiquitous Language Candidates

- **Game**: one full match
- **Round**: one evaluated play/scoring cycle
- **Score**: the numeric result assigned in context
- **Score Entry**: an input record that contributes to scoring
- **Player**: one person participating in the game
- **Team**: grouped players if needed by rules
- **Rule Set**: the selected set of scoring rules
- **Standing**: current ranking within a game
- **Final Result**: persisted outcome of a completed game

### Rule

If a domain term is ambiguous, it must be clarified in documentation before it spreads into code, tests, and UI labels.

---

## 9. Functional Requirements

At a high level, the system should support the following capabilities:

1. Start a new score-tracking session.
2. Define participants.
3. Record scoring information per round.
4. Calculate current totals consistently.
5. Show current standings.
6. Complete and archive a game.
7. Retrieve prior completed games.

### Example User Stories

- As a player, I want to create a new game so that I can start tracking scores.
- As a player, I want to enter results round by round so that the current total is always visible.
- As a player, I want the application to calculate totals automatically so that I avoid manual calculation errors.
- As a player, I want to review finished games so that I can understand previous results.

---

## 10. BDD Strategy

BDD is a central project principle, not only a testing add-on.

### Goals of BDD in This Project

- Create a shared understanding of behavior before implementation.
- Express business requirements in a readable form.
- Connect business scenarios to executable automated checks.
- Keep focus on observable behavior instead of internal implementation.

### Gherkin Guidelines

- Features describe user-visible or business-relevant behavior.
- Scenarios should be concrete, small, and understandable.
- Each scenario should test one business behavior.
- Scenario wording should use the project’s ubiquitous language.
- Technical implementation details should not appear in business-facing Gherkin.

### Recommended Feature Structure

- One feature file per coherent business capability.
- Clear feature description with business intent.
- Scenarios focused on acceptance criteria.
- Background only when it improves readability.

### Separation Principle

- **Gherkin** describes business intent.
- **Integration/acceptance tests** verify behavior across boundaries.
- **Unit tests** verify internal rules and edge cases.

---

## 11. Architecture Principles

The project should prefer **simple, explicit, modular architecture**.

### Recommended Architectural Direction

A pragmatic layered or clean architecture is recommended, with clear separation between:

- **Domain logic**
- **Application/use-case orchestration**
- **Infrastructure/adapters**
- **User interface/API**

### Architectural Rules

- Business rules must not depend directly on UI or database details.
- Framework-specific code should be isolated.
- Side effects should be pushed to the outer layers.
- Dependencies should point inward toward the domain.
- Modules should be understandable and testable in isolation.

### Initial Simplicity Rule

Do not overengineer the first version. Use architecture to create clarity, not accidental complexity.

---

## 12. Technology Direction

Based on the current repository description, the tentative technology direction is:

- **Backend:** Python with Django
- **Frontend:** Vue
- **Testing/BDD:** Gherkin-compatible tooling plus automated test layers

### Technology Decision Rule

Technical choices should support:

- clarity,
- maintainability,
- testability,
- deployment simplicity,
- automation.

If a technology increases complexity without clear project value, it should be postponed or avoided.

---

## 13. Non-Functional Requirements

### Maintainability

- Code should be readable, modular, and intentionally structured.
- Naming should be domain-oriented and explicit.
- Complexity should be minimized.

### Testability

- Domain logic must be testable without heavy framework setup.
- Acceptance criteria should be automatable.
- Tests should be fast enough to support frequent execution.

### Reliability

- Score calculations must be deterministic and verifiable.
- Persisted results must be consistent.

### Usability

- Core score entry workflows must be simple and fast.
- The UI should minimize ambiguity during active play.

### Security

- Even in early stages, basic secure defaults should be used.
- Secrets must not be committed.
- Configuration must be environment-based.

### Deployability

- The application should be buildable and deployable in a repeatable way.
- Environment-specific setup should be minimized.

### Observability

- Logging should support debugging and operational understanding.
- Failures should be visible and diagnosable.

---

## 14. 12-Factor App Principles

The project should align with relevant 12-factor principles where appropriate.

### Initial Commitments

- Configuration via environment variables.
- Clear dependency management.
- Separation of config from code.
- Reproducible build and run steps.
- Stateless application processes where feasible.
- Logs treated as event streams.

---

## 15. Quality Standards

### Definition of Done

A work item is considered done only if:

- behavior is clearly defined,
- acceptance criteria exist,
- implementation is complete,
- automated tests are added or updated,
- code passes quality checks,
- documentation is updated when needed,
- the change is reviewable and understandable.

### Coding Principles

- Prefer clarity over cleverness.
- Keep functions and classes focused.
- Avoid hidden coupling.
- Use explicit naming.
- Refactor continuously when it improves clarity.

### Review Principles

Reviews should check:

- correctness,
- readability,
- alignment with architecture,
- test coverage of intended behavior,
- naming consistency,
- unnecessary complexity.

---

## 16. Test Strategy

The test strategy should balance confidence, speed, and maintainability.

### Test Layers

- **BDD / acceptance tests** for end-to-end business behavior
- **Integration tests** for component collaboration
- **Unit tests** for isolated domain rules and calculations

### Test Strategy Principles

- Important business rules should be covered first.
- Domain scoring logic should have strong unit-level protection.
- Acceptance scenarios should reflect meaningful user workflows.
- Test data should be easy to understand.
- Fragile or overly implementation-coupled tests should be avoided.

---

## 17. Automation and CI/CD Baseline

Automation should be introduced early.

### Minimum CI Expectations

Every meaningful change should eventually trigger automated checks such as:

- dependency installation,
- linting/format validation,
- unit tests,
- integration and/or acceptance tests where applicable,
- build verification.

### Pull Request Expectations

Before merging, a change should:

- pass automated checks,
- be understandable in scope,
- include tests appropriate to the change,
- not degrade architecture or code quality.

---

## 18. Documentation Strategy

Documentation should be lightweight but deliberate.

### Recommended Documentation Set

- `README.md` – entry point and project overview
- `docs/project-foundation.md` – foundational decisions
- `docs/ubiquitous-language.md` – domain vocabulary
- `docs/architecture.md` – architectural structure and rationale
- `docs/adr/` – architecture decision records for significant choices

### Documentation Rule

Only document what helps decisions, onboarding, maintenance, or shared understanding.

---

## 19. Assumptions

The following assumptions are currently made and should be validated later:

1. The initial implementation will use **Python/Django** for the backend.
2. The initial implementation will use **Vue** for the frontend.
3. The first target is a usable MVP for score tracking, not a full-featured game platform.
4. A single primary Binokel rule interpretation will be supported first before addressing multiple variants.
5. The repository owner wants a strong learning and engineering-quality focus in addition to product functionality.

---

## 20. Open Questions

The following questions should be clarified early:

1. Which exact Binokel rules and scoring interpretation define version 1?
2. Is the application focused first on local/private usage or broader public multi-user access?
3. Are players tracked only within a game, or should persistent player profiles exist early?
4. Will the MVP use teams, individual scoring, or both?
5. Should authentication be part of the MVP or explicitly deferred?
6. Which deployment target is intended first?
7. Which BDD toolchain should be selected for Django/Vue integration?
8. How much of the UI should be optimized for mobile-first usage during live play?

---

## 21. Recommended Next Steps

1. Refine the README so that it reflects the project vision and engineering principles more clearly.
2. Create `docs/ubiquitous-language.md` and define the first stable business vocabulary.
3. Clarify the exact Binokel scoring rules for version 1.
4. Derive an initial set of MVP user stories.
5. Create the first Gherkin feature files for the highest-value workflows.
6. Define the initial architecture/document module boundaries.
7. Establish the first automated quality pipeline.

---

## 22. Guiding Principle

When in doubt, prefer:

- simpler design,
- explicit domain language,
- testable business logic,
- automated quality checks,
- incremental delivery over speculative complexity.

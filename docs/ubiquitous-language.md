# Ubiquitous Language

## 1. Purpose

This document defines the shared domain vocabulary for the **Binokel Score Tracker** project.

Its goal is to ensure that product discussions, documentation, Gherkin scenarios, domain models, UI labels, and code all use the same terms with the same meanings.

A term that is unclear in the domain should be clarified here before it is introduced into implementation.

---

## 2. Scope

This vocabulary applies to:

- product and rules discussions,
- functional requirements,
- BDD and Gherkin specifications,
- backend domain models,
- frontend UI terminology,
- persistence naming where appropriate.

The document is intentionally domain-oriented and should avoid framework-specific or technical wording where a domain term exists.

---

## 3. Core Modeling Principles

1. Prefer **domain words** over technical shortcuts.
2. Use **one term for one concept** wherever possible.
3. Avoid synonyms in code, tests, and documentation if they refer to the same concept.
4. If a term has multiple meanings in everyday speech, define the project-specific meaning explicitly.
5. If local Binokel terminology and generic software terminology differ, prefer the Binokel term and explain it.

---

## 4. Core Terms

### 4.1 Game

A **Game** is one complete Binokel match from start to finish.

A game includes:
- the participating players,
- the selected rule set,
- a sequence of rounds,
- the current standings,
- a final outcome.

**Use in code/docs:** `Game`

**Do not confuse with:**
- a single round,
- a single hand,
- a generic app session.

---

### 4.2 Round

A **Round** is one scoring cycle within a game.

A round captures the scoring-relevant outcome of one played deal or one evaluated unit of play, depending on the selected Binokel rule interpretation.

A round may include:
- dealer information,
- active players,
- bidder / game maker,
- bid value,
- meld values,
- trick points,
- Mit points,
- special outcomes such as successful play, simple loss, double loss, or Tausender.

**Use in code/docs:** `Round`

**Do not confuse with:**
- a turn in the UI,
- a full game.

---

### 4.3 Player

A **Player** is one person participating in a game.

For MVP, a player is primarily a scoring participant. Persistent player profiles may be added later, but the domain term remains the same.

**Use in code/docs:** `Player`

**Do not confuse with:**
- a user account,
- an authenticated system user.

---

### 4.4 Dealer

The **Dealer** is the player who deals for a round.

In the currently documented 4-player interpretation, the dealer sits out during the round while the other three players are active.

**Use in code/docs:** `Dealer` or `dealer`

**Note:** This behavior belongs to the selected rule set and must not be assumed for every future variant.

---

### 4.5 Active Player

An **Active Player** is a player who participates directly in the current round.

In the currently documented 4-player interpretation:
- 3 players are active,
- 1 player is dealer and inactive for that round.

**Use in code/docs:** `Active Player`

---

### 4.6 Rule Set

A **Rule Set** is the explicit scoring and gameplay interpretation used for a game.

It defines, for example:
- player mode,
- scoring rules,
- bidding consequences,
- end conditions,
- special cases,
- variant-specific terminology.

**Use in code/docs:** `Rule Set`

**Important:** Rules must not be hidden in scattered conditionals; they belong conceptually to a rule set.

---

### 4.7 Score Entry

A **Score Entry** is the structured input recorded for a round and a player.

It contains the scoring-relevant values needed to evaluate and display the round result.

Depending on the rule set, a score entry may contain:
- meld points,
- trick points,
- Mit points,
- penalty values,
- star markers,
- explanatory status information.

**Use in code/docs:** `ScoreEntry`

**Do not confuse with:**
- cumulative standing,
- raw UI form state.

---

### 4.8 Meld

A **Meld** is a declared card combination that awards points according to the rule set.

Examples from the documented rules include:
- Paar,
- Trumpf-Paar,
- Binokel,
- Familie,
- Rundlauf,
- Doppelter Binokel.

**Use in code/docs:** `Meld`

**Related term:** `Meld Points`

---

### 4.9 Meld Points

**Meld Points** are the points awarded for valid melds in a round.

In the existing scoring examples, this is the **M** column.

**Use in code/docs:** `Meld Points`

**Important:** Whether meld points count may depend on round outcome rules, such as the stitch obligation or special loss scenarios.

---

### 4.10 Trick Points

**Trick Points** are the points earned from tricks during play.

In the existing scoring examples, this is the **S** column.

**Use in code/docs:** `Trick Points`

**Do not confuse with:**
- meld points,
- cumulative total score.

---

### 4.11 Mit Points

**Mit Points** are bonus points awarded to opponents in certain loss scenarios of the game maker.

In the documented rules, this is the **Mit** column and is currently described as `+30` in simple and double loss scenarios for the opponents.

**Use in code/docs:** `Mit Points`

**Important:** This is a domain-specific term and should not be translated into a vague generic label such as `bonus` without preserving its Binokel meaning.

---

### 4.12 Standing

The **Standing** is the cumulative score state of a player within an ongoing or completed game.

It reflects the running total after each round.

In the documented table example, this is the **STAND** row.

**Use in code/docs:** `Standing`

**Do not confuse with:**
- a single round result,
- ranking across many games.

---

### 4.13 Final Result

The **Final Result** is the persisted outcome of a completed game.

It includes at least:
- the final standings,
- the winner or winning condition,
- the rule set used,
- the completed sequence of rounds.

**Use in code/docs:** `Final Result`

---

### 4.14 Bid

A **Bid** is the announced value a player commits to achieve as game maker.

The documented rules also use the terms:
- `gereizt bis`,
- `Reizwert`.

For English domain documentation, the preferred general term is **Bid**. For German-facing rule documentation and UI, `Reizwert` may be retained where it is clearer to target users.

**Use in code/docs:** `Bid`

**Synonym mapping:**
- `Reizwert` → `Bid`
- `gereizt bis` → `Bid`

---

### 4.15 Game Maker

The **Game Maker** is the player who wins the bidding and must fulfill the bid.

In German rule terminology, this is close to the role of the player who `spielt`.

**Use in code/docs:** `Game Maker`

**Possible German synonym in documentation:** `Spielmacher`

---

### 4.16 Successful Game

A **Successful Game** means the game maker reaches the required target and wins the round according to the rule set.

In this outcome:
- the game maker scores the actual round result,
- opponents score according to their eligible points,
- no Mit points are awarded.

**Use in code/docs:** `Successful Game`

---

### 4.17 Simple Loss

A **Simple Loss** is the scenario where the game maker gives up the game before the first trick after seeing the Dapp.

In the documented German rules, this corresponds to **einfaches Abgehen**.

**Use in code/docs:** `Simple Loss`

**German synonym mapping:**
- `einfaches Abgehen` → `Simple Loss`

---

### 4.18 Double Loss

A **Double Loss** is the scenario where the game maker plays the round but fails to reach the bid.

In the documented German rules, this corresponds to **doppeltes Abgehen**.

**Use in code/docs:** `Double Loss`

**German synonym mapping:**
- `doppeltes Abgehen` → `Double Loss`

---

### 4.19 Tausender

A **Tausender** is a special announced game outcome defined by the selected rule set.

In the currently documented version:
- normal point scoring is frozen,
- no meld points are counted,
- no trick points are counted,
- no Mit points are counted,
- a star is awarded depending on success or failure.

**Use in code/docs:** `Tausender`

Because this is a highly domain-specific term, it should remain untranslated unless a later product decision introduces a user-facing alias.

---

### 4.20 Star

A **Star** is a non-numeric success marker awarded in the Tausender scenario.

In the documented rules, this is shown as `★`.

**Use in code/docs:** `Star`

**Important:** A star is not the same as score points and must not be modeled as normal round score.

---

### 4.21 Stitch Obligation

The **Stitch Obligation** is the rule that a player must win at least one trick for meld points to count.

In the documented rules:
- normally, a player with zero tricks loses their meld points,
- in game-maker loss scenarios, opponents may keep their meld points even with zero tricks.

**Use in code/docs:** `Stitch Obligation`

**German synonym mapping:**
- `Stich-Zwang` → `Stitch Obligation`

---

### 4.22 Game Status

The **Game Status** describes the lifecycle state of a game.

Initial candidate values:
- `planned`
- `active`
- `completed`
- `cancelled`

**Use in code/docs:** `Game Status`

---

### 4.23 Round Outcome

The **Round Outcome** is the classified result type of a round.

Initial candidate values based on current documentation:
- `successful_game`
- `simple_loss`
- `double_loss`
- `tausender_success`
- `tausender_failure`

**Use in code/docs:** `Round Outcome`

This helps separate business meaning from raw numeric values.

---

## 5. Preferred Term Mappings

The project may use German terms in source material and player-facing wording, but implementation and shared engineering documents should prefer stable mappings.

| Source / informal term | Preferred project term |
| --- | --- |
| Match | Game |
| Session | Game, only if it truly means a play session |
| Spiel | Game |
| Runde | Round |
| Anschreiben | Score Tracking / Score Entry depending on context |
| Spielmacher | Game Maker |
| Gereizt bis | Bid |
| Reizwert | Bid |
| M | Meld Points |
| S | Trick Points |
| Mit | Mit Points |
| Stand | Standing |
| Abgehen einfach | Simple Loss |
| Abgehen doppelt | Double Loss |
| Stich-Zwang | Stitch Obligation |

---

## 6. Terms to Avoid or Use Carefully

### 6.1 Session

Use **Session** carefully.

In software, session can mean:
- browser session,
- login session,
- application runtime session,
- game session.

For the domain, prefer:
- **Game** for a full match,
- **Round** for a scoring cycle.

---

### 6.2 Score
n
Use **Score** only when the context is clear.

It may otherwise refer to:
- round result,
- cumulative standing,
- points from a meld,
- points from tricks,
- final result.

Prefer the more precise term when possible:
- Meld Points
- Trick Points
- Standing
- Final Result
- Score Entry

---

### 6.3 User

Avoid **User** as a synonym for **Player** unless the feature truly concerns authentication or application identity.

A player is a domain role. A user account is a technical/application concept.

---

## 7. Initial Candidate Enumerations

These are not final implementation details, but they are useful vocabulary anchors.

### 7.1 Game Status

- planned
- active
- completed
- cancelled

### 7.2 Round Outcome

- successful_game
- simple_loss
- double_loss
- tausender_success
- tausender_failure

### 7.3 Participant Role in Round

- dealer
- active_player
- game_maker

---

## 8. Open Vocabulary Questions

The following terms still require joint clarification before implementation hardens them:

1. Should the MVP vocabulary be primarily English in code and documentation, while preserving German terms in rule annexes?
2. Is `Game Maker` the best long-term English term, or should `Declarer` / `Bid Winner` be preferred?
3. Should `Stitch Obligation` remain the preferred English term, or is there a better wording closer to common card-game language?
4. Should `Mit Points` remain untranslated because it is domain-familiar, or should a more descriptive English term be introduced?
5. Do we need explicit vocabulary for teams in MVP, or is individual scoring the only V1 target?

---

## 9. Usage Rule

Before introducing a new business term in:
- code,
- tests,
- Gherkin,
- UI labels,
- architecture documents,

check whether the concept already exists in this document.

If not, add or clarify the term here first when the concept is central to the domain.

# Bytecraft World 0.4.0: audit and corrected game loop

The 0.3.1 World screens were interactive mockups wired to unconditional state
mutations. This was the root cause, not a missing animation or a button label.
The existing Python course already used answer validators; World bypassed them.

## Findings and changes

| Defect in 0.3.1 | Corrected behavior |
| --- | --- |
| Expedition advanced from a button, with identical code five times | Five distinct authored problems; submitted answer must match the active task; 5/5 opens project |
| Boss lost HP on every tap, four hits versus a five-task caption | Four distinct vulnerabilities; 25 HP per validated answer; project completion required |
| Project checklist was freely toggleable, including prechecked steps | Four sequential verified components; cannot skip or uncheck; completion actually unlocks boss |
| Ghost record decreased by a fabricated 17 seconds per tap | Stopwatch measures from question display through correct submission; no fabricated leaderboard |
| Rival awarded a win on tap; displayed invented win rate | Verified answer earns a win; next task changes; explicitly described as authored local opponent |
| Guild added eight tasks without solving anything | Each solved task contributes an amount determined by team level; 160 completes the local project with a one-time bonus |
| Training reduced invented percentages without an exercise | Real mistake counts, topic-specific questions; wrong +1, correct training -1, floored at zero |
| Infinite mode allowed solving at zero lives and manual failure | Real answers; mistakes deduct a life/reset series; record and task cursor survive; zero lives blocks domain submission |
| Fake starting streak, records, XP, achievements | New accounts start at zero, five buildings at level 1, and three starting gems |
| City upgrades had no gameplay effect | Office: coins; Python: XP; R&D: clean XP; servers: lives; team: contribution. XP gates building levels, max 5 |
| Season threshold only checked in UI; overflow discarded | Domain enforces 1000 XP and subtracts exactly 1000; actual rewards described |
| Replaying a course level repeatedly paid World rewards | Persisted per-course/per-level reward keys; first verified completion only |
| Fast taps/storage writes could race | Serialized read-modify-write; persisted result before visible reward; stale challenge cursor rejected |
| Profile reset cleared only course progress | Confirmed reset clears World state and reward history too, with an explicit confirmation text |
| No explanation of the economy or quest dependencies | Rules and concrete deltas shown in each mode; story goal and economy described in hub |

## Rules

- Story: restore API (5 tasks) → calculator (4 components) → Bug Lord (4 vulnerabilities).
- Correct answers alone advance a task cursor. Empty answers change nothing.
- An incorrect answer adds an unresolved topic mistake; it never pays or unlocks.
- After any mistake on a task, its base XP reward is halved (rounded down), and the clean R&D bonus is not granted. Coins and previously completed story stages are not confiscated.
- Infinite failure additionally loses a life and resets the current series. The next problem follows total solved count, not series length, so failure cannot restart easy reward farming.
- Repeatable tasks cycle through conditions, loops, indexing, types and functions; parameters change every step. Loop range and function multiplier grow every five solved problems. Training stays within the selected topic.
- Ghost uses a personal fastest solved-problem time; tasks change, so this is not a difficulty-normalized or multiplayer ranking. No live AI or backend multiplayer is implied.
- Season XP is accumulated from verified World answers, first course completions and expedition chest. Buildings no longer award XP merely for spending coins.
- Daily streak uses actual local calendar days with correct solutions, once per day.

## Migration

Schema 1 included unvalidated and demo-filled World stats. Schema 2 resets only
those World quest flags, records, mistake profile, XP, streak and season progress.
Course progress, currency and purchased buildings are retained (building levels
clamped to 1–5). A dismissible explanation appears in the hub. Migration is
persisted once, never reapplied to schema 2 progress.

## Validation

- Independent CPython execution of exported questions: all 13 story tasks and
  450 generated problems (including 250 topic-specific training tasks).
- Regression tests cover empty/wrong/stale submissions, all story gates,
  boss completion, changing repeatable questions, zero-life guard, actual ghost
  time, topic training, guild completion, economy, season overflow and streaks.
- Controller tests cover 12 simultaneous duplicate submissions, process restart,
  storage failure/retry, legacy migration and course replay reward prevention.
- Phone widget tests cover empty submit, wrong/correct/next flow, choice selection,
  all modes at 320 px, and unlocked project and boss tasks.
- CI also runs the existing course validation, Pyodide checks, analyzer, full
  Flutter suite, release APK build/signature/identity checks and emulator smoke.

This fixes the audited progression bypasses. It does not claim arbitrary-code
execution on World questions: these are explicit output/fill questions with
authored answers, independently checked with CPython. The existing Python
playground continues to execute code through Pyodide.

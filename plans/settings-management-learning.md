# Learnings — `settings-management` / T3 (campaign `exp-settings-roi`)

## 1. Test where the bug lives, not where the code is convenient to call

**Rule.** When a value crosses a process boundary, a cache, or a serialisation,
the test has to cross it too. An in-process round trip measures the cache.

**Why.** The guard that a global boolean preference survives as a boolean passed
with the coercion deleted. Measured why:

| read | value | type |
|---|---|---|
| same process | `False` | `bool` |
| **fresh process** | `'false'` | `str` |

QSettings hands back the typed value it cached; a new process reading the Ini
file off disk gets the text. And `bool('false')` is `True` — so a scientist who
turns plotting off, closes the launcher and reopens it, gets plotting back on.
The defect exists *only* across the restart, and the test never left the
process, so it could not see it.

This is the same class T2 was rejected for — a string that is truthy where a
boolean was meant — arriving through a different door. Knowing the class did not
help; standing in the wrong process did the damage.

**How to apply.** Two tests, not one: a subprocess that proves the on-disk form
really is what you think, and an in-process test that forces that form and pins
the handler. The first stops the second from being written against an imagined
hazard; the second is the one that reds when the handler is removed.

## 2. Provenance has to be structural, or it is not provenance

**Rule.** If a resolver can return a bare value, someone will return one, and
the origin is gone at exactly the moment it matters.

**Why.** The whole point of the layer taxonomy is answering *which source won*.
That question only has an answer if it is impossible to produce a value without
one — hence `Resolved(value, source_layer, source_detail)` as the only return
type, and `resolve_all` producing the document and the provenance map from a
single walk.

The consequence for tests is sharper than it first looks: **every precedence
assertion keys on `source_layer`, never on the value.** Two layers holding the
same number is the ordinary case — an experiment file that agrees with the
built-in default — and a value-keyed assertion passes a swapped pair of layers
whenever the fixtures happen to coincide. One guard exists solely for that case:
two layers both holding `0.5`, asserting the winner is (a).

**How to apply.** Make the origin part of the type, not a parallel dict someone
maintains. And when a display shows the origin, have it read the same object the
value came from — a badge that re-derives "which layer won" is a second
implementation of the resolver, and the campaign has now paid three times for
two implementations of one answer.

## 3. A whitelist enforced on one door is not a whitelist

**Rule.** Count the ways into the restricted thing. Guard each, and give each
its own mutation.

**Why.** The user-global layer is reachable from `ResolutionContext.set_global`
(the model) and from `save_global_settings` (the dialog). Guarding only the
model would have left the dialog able to write `RB_Ymin` — a per-angle field
that describes one measurement — into a store that outranks every experiment
file. Both are guarded, and the mutate-once battery breaks them separately,
because a single test covering "the whitelist works" would have passed with
either door open.

Deriving the whitelist from FIELD_SPEC by group rather than listing names is the
other half: a new field is covered without anyone remembering, and per-angle and
runtime-owned fields are excluded by construction rather than by vigilance.

## 4. Catch the specific exception first when it subclasses the general one

**Rule.** `json.JSONDecodeError` is a `ValueError`. Ordering matters, and the
wrong order does not fail — it mislabels.

**Why.** Discovery catches `ValueError` for the settings-file helper's "no file
found", and `(OSError, json.JSONDecodeError)` for an unreadable file. With the
general clause first, a **malformed** settings file was reported as a *missing*
one. Nothing crashed; the status line just said something untrue, which for a
module whose entire job is explaining where values came from is the failure mode
that matters.

**How to apply.** When two except clauses could both match, put the specific one
first and say in a comment why the order is load-bearing — the next person to
tidy the clauses alphabetically needs to know.

## 5. A mechanism nothing calls is not a feature — it is a second muddle

**Rule.** Before a slug is done, name the line in the shipped application that
executes the thing you built. If there isn't one, the work is a precondition,
not a payoff.

**Why.** T3 v1 delivered a complete resolver — layers, provenance, discovery,
persistence, 42 green tests — with **zero production callers**. `set_resolution`
was reachable only from tests, so `self.provenance` stayed empty and every
badge rendered blank in the running launcher. The charter's complaint was that
settings arrived from an undefined muddle of sources; v1 left that muddle
running and added an unreached mechanism beside it. Strictly worse than nothing,
because the tests said it worked.

The plan is not a defence. It described an architecture in two pieces and I
built two pieces. Nothing in it said "and something must call this" — and
noticing that gap is the developer's job, not the plan's.

**How to apply.** For any new module, write the wiring test first: drive the
button, assert the observable effect. It fails immediately for the right reason
and cannot be satisfied by the module existing. "Is it called?" is a different
question from "does it work?", and only the first one is about shipping.

## 6. Extract the fix, or watch it recur in the next file

**Rule.** When a defect is fixed inside a private method, the fix is unavailable
to the next caller who needs it — and that caller will re-derive it, wrongly.

**Why.** Three instances, one shape:

- rendering a list: T2 fixed `str([50, 200])` → `"[50, 200]"` inside the
  settings tab's private `_as_text`. The global-settings dialog, written later,
  grew its own `str(value)`. Now `field_spec.render_value`, beside `coerce`.
- the atomic write: `SettingsDocument.save` had it; `save_resolution` grew a
  second copy that had drifted around the symlink refusal. Now
  `atomic_write_json`, imported by both.
- the up/down rule: the reduction and the autoreduction each had a copy, so the
  resolver wrote a **third** — `sorted(glob("template*.xml"))[0]`, which
  returned `template_down.xml` for an up-geometry run every time. Now
  `autoreduce_paths.select_by_geometry`, stdlib-only, derived by all three.

The last one is the clearest: the duplication existed because borrowing the rule
meant importing Mantid to make a filename decision. **A fix that is expensive to
reuse gets copied.** Extraction is not tidying; it is what makes the fix hold.

## 7. A derived rule still needs someone to read what it derived

**Rule.** Deriving membership from a property prevents drift. It does not make
the membership correct.

**Why.** `GLOBAL_WHITELIST` is derived from FIELD_SPEC by group, chosen
precisely so a new field could not be forgotten. The derivation swept in the
instrument-geometry group — `IncidentTheta`, `mmpix`, `dSampDet`, `dMod`,
`xi_ref`, `dS1Samp`, `nx`, `ny` — whose documented defaults read *"unset reads
it from the instrument settings / the PV."* They are **measurements**. A stored
personal preference outranking one means identical UI and identical experiment
file producing **different reduced data**, silently.

The elegance of the rule concealed the wrongness of its output, and I did not
print the list and read it. The human's decision — exclude the group, and put
(a) below the experiment file — is recorded as a named exclusion with its
reason, not as an absent group, because an exclusion nobody can see is one the
next derivation will undo.

**How to apply.** After writing a derivation, enumerate what it produced and
read every entry aloud against the question the rule is supposed to answer.
Here that question was *"is this something a person should carry between
experiments?"* — and eight entries answer no.

## 8. Guard every site of a behaviour, and prove each one separately

**Rule.** When a behaviour has several call sites, a guard on one of them proves
one of them. Record a mutation per **site**, not per behaviour.

**Why.** This was the most productive cluster of the whole slug, and every
instance had the same shape — a property that looked covered because *a* test
covered *a* site:

- discovery wrapped two of its three filesystem touches. `is_dir()` **succeeds**
  on a `chmod 000` share, so the tested guard never fired, while the unguarded
  `exists()` beneath `select_by_geometry` raised straight out of the slot. The
  module's headline promise — never take the launcher down when the mount is
  unavailable — was silently not delivered, with a green suite.
- the whitelist was pinned by one exemplar per group, so a hand-list of **six**
  survived against a real **twenty**.
- the angle-removal test asserted the column header *before* the removal, so
  deleting the re-attribution was green; `add_angle` had no test at all.

The fix for the first is worth separating from the test: push the guard into
**one** helper every step calls. Wrapping each site individually would have been
three copies of one rule, and the third is always the one that gets forgotten —
which is exactly how it happened the first time.

**How to apply.** Count the call sites before writing the guard. Then break each
one in turn: if two sites share a test, that test is proving one of them.

## 9. A shim tests the site you already thought about

**Rule.** Prefer injecting the real failure over monkeypatching the function you
expect to fail.

**Why.** The "unreachable mount" guard was tested by monkeypatching
`Path.is_dir` to raise. That could only ever exercise the site already wrapped in
a `try` — the shim *was* the hypothesis. A real `chmod 000` directory found the
truth instead: `is_dir()` returns True on it, and the failure surfaces two calls
later, in the site nobody had guarded.

The same distinction settled a smaller one: QSettings returns a cached typed
value in-process and the on-disk string in a fresh one, so an in-process
round-trip tests the cache. Both are the same lesson — **the shim reproduces
your model, the real thing reproduces the world.** Where a real injection is
cheap (a mode bit, a subprocess), it is worth more than the mock.

## 10. Two clauses guarded a field that does not exist — say so

**Rule.** When a defensive clause cannot be reached by any current input, test it
on a synthetic input and write down that it is defending a future.

**Why.** The whitelist predicate has five clauses. Two — `type == "path"` and
`runtime_owned` — turned out to be unreachable: every such field also sits
outside the included groups, so the group clause excludes it first, and deleting
either specific clause left the counter-example test green. The honest options
were to delete them as dead code or to isolate them, and deleting would have
removed the protection that keeps a *future* field added to an included group
out of the layer that outranks a dataset guess.

So they are tested on synthetic `Field` objects, with the reason stated in the
test. A clause guarding a future is worth keeping and worth pinning; what is not
acceptable is a clause that looks tested and is not.

## 11. A promise narrowed is a promise kept

**Rule.** When a guarantee cannot be delivered in full, narrow the words and name
the residual, rather than leaving the broad claim standing.

**Why.** The discovery docstring said "degrades, never raises". `/SNS` is FUSE,
and a stalled mount **blocks in D-state** — it does not raise, so `except OSError`
and the slot guard were both irrelevant to the failure most likely to occur.
Measured: 2.00 s blocked, zero timer ticks. The work moved to a worker thread,
and the docstring now says "never raises — it can still block", with the caller's
obligation spelled out.

The same move appears twice more in this slug: layer (d) is *declared and
honoured but not populated*, said in the docstring, a constant and a test; and
`LAYER_ORDER`'s partial scope ((e)/(f) are not mappings) is stated rather than
left to be discovered. Each replaces a comfortable sentence with a true one.

## 12. Fixes compose, and the composition is nobody's cluster

**Rule.** After landing several fixes that touch one data path, ask what they do
*together*. Each was reviewed alone; the interaction was reviewed by no one.

**Why.** Three v3 fixes, each correct and each demanded by a reviewer:

1. **C8** wired the sidecar *read* side, so `provenance` could be seeded from a
   file on disk;
2. **C8** populated `ui_overrides` from recorded provenance, so pre-Resolve
   edits stopped being discarded;
3. **C5** re-recorded `Resolved(..., "b")` on angle add/remove, so a stale
   header stopped attributing a changed column to the experiment file.

Composed: a `"b"` written into a sidecar for a *previous* run — in a
group-writable `shared/autoreduce` — became this run's authority, and layer (b)
is gated by nothing. So instrument geometry, the group excluded from layer (a)
*precisely* because a preference must never override a measurement, outranked
the experiment file and the measurement, with nobody typing anything. An "Add
angle" click did the same for all 13 per-angle fields.

Nothing in any of the three is wrong. The defect lives between them, and it
defeated a decision a human had made two rounds earlier.

**How to apply.** The fix is one idea, not three patches: **authority is
something a person does in this session, not something a file claims.** Track it
at its source (`_session_edits`) rather than inferring it from a recorded
origin, and give a recorded-but-not-authoritative value its own marker so the
badge can stay truthful without granting power. More generally — when a review
cycle lands several fixes on one path, the next cycle's first question should be
what they now do together.

## 13. When you cannot make a failure safe, choose which failure

**Rule.** Some conditions have no clean handling. Pick the survivable one
deliberately, and write down why.

**Why.** v2 called discovery synchronously and a stalled `/SNS` froze the GUI.
v3 moved it to a worker — and closing the launcher with a resolve in flight
destroyed a running QThread: **exit 134**, in the exact stalled-mount case the
worker was added for. The freeze had been traded for a crash.

`wait()` is the reflex and it is wrong: waiting on a D-state read blocks exactly
as long as the freeze did. There is no third option where the thread stops
promptly, because the kernel will not let it. So the choice is between an abort
and a **leak**, and the leak wins on the merits: it ends with the process, while
an abort takes every other tab's unsaved state with it.

The worker is therefore unparented, held in one reference, and `closeEvent`
disconnects and lets go. The docstring says leak-not-abort and why.

**How to apply.** When both branches are bad, do not pick by which looks tidier
in code review. Ask what each costs the user at the moment it happens, and say
in the comment that the other option was considered — otherwise the next
reader "fixes" it back by adding the `wait()`.

## 14. A record only counts if someone else can check it

**Rule.** Evidence of thoroughness belongs in the repository, enumerated from
the code, not asserted in a commit message.

**Why.** The per-site granularity defect recurred in v2 and again in v3, and the
reason is not that I did not run the mutations — I did, and reported "28
mutations, no survivors". It is that the claim was **unauditable by
construction**: nothing said which 28, or where, or how the sites were counted.
Two reviewers independently could not verify it, so the defect that the count
was supposed to rule out survived twice more.

The ledger now lives at `plans/settings-management-mutation-ledger.md`, one row
per site, with the `grep -c` command that produced each count and the observed
result of each mutation — including the two that did *not* red first time,
because a list of only successes is the prose count wearing a table.

**How to apply.** For any claim of the form "I checked all N of these": commit
the enumeration, generate it mechanically, and record the failures alongside the
passes. If a reviewer cannot re-derive N, the number is decoration.

## 15. Close the class, not the doors

**Rule.** When the same defect arrives through a second route, stop patching
routes and state the property that must hold.

**Why.** Geometry outranking a measurement arrived twice: once through a sidecar
seeding `ui_overrides`, once through an "Add angle" click minting authority for
fields nobody typed. v4 closed both, correctly — and a third route would have
been a third fix, in a slug that had already spent two attempts on exactly this
shape.

The invariant states it once: *a field in an excluded group never resolves above
layer (e) from a **user-authority layer***, expressed over
`USER_AUTHORITY_LAYERS` rather than over `"a"` and `"b"` by name, so a layer
added later inherits the protection instead of needing its own patch. A
hypothetical fourth door now reds the invariant instead of shipping.

**How to apply.** Two instances of one defect is the signal. Ask what property
was violated, express it where the decision is made — here, inside the
resolution walk — and quantify it over the class rather than the members.

## 16. "Leak, don't abort" is not achieved by letting go

**Rule.** Releasing the last reference to a running Qt thread is what destroys
it. To leak deliberately, hold it.

**Why.** v4 chose the right trade and implemented its opposite. The reasoning —
a stalled worker should leak rather than abort, because a leak ends with the
process while an abort takes every other tab's unsaved state — was correct and
is preserved. But the implementation *dropped the reference*, and an unparented
QThread is owned by Python: releasing it deletes the C++ object, and deleting a
running QThread is precisely `QThread: Destroyed while thread is still running`,
then `abort()`. Measured: **exit -6**, on the stalled teardown the fix was for.

Parking the worker in a module-level list is what the decision actually
requires. And a parked worker that later finishes is reclaimed, because parking
is for one still blocked at teardown, not a permanent hold.

**How to apply.** When the intended behaviour is "do nothing and let it run",
check who owns the object. In PyQt, "do nothing" and "delete it" are the same
statement unless something keeps a reference.

## 17. A guard is only wired where the code runs

**Rule.** Put teardown on the object whose teardown actually fires, and pin the
wiring from a test that can reach it.

**Why.** Two instances in one cluster. v4's worker guard lived on the tab's
`closeEvent` — which does **not** fire when a tab inside a QTabWidget inside a
QMainWindow is destroyed, so the guard never ran on the path that quits the
application, which is exactly when a resolve is most likely in flight. And
`aboutToQuit` was connected inside `main()`, a function no test calls, so the
connection was unpinned; factoring it into `install_shutdown_hooks(app, window)`
let a test install the same wiring the application ships.

Both were invisible in-process: `exit -6` is not something an in-process
assertion can observe. A subprocess matrix over the real window — idle,
mid-resolve, stalled, repeated, after a completed resolve, and quit-by-signal —
is what made the exit code the thing under test.

**How to apply.** For lifecycle code, ask which object Qt actually tears down,
and whether the test can drive the path the user takes. If the answer needs a
process, spend the process.


## 18. Record an edit at the granularity the thing can change at

**Rule.** When you snapshot "what the user set", snapshot the unit that has a
stable identity — not an aggregate whose *index* can move underneath it.

**Why.** `_session_edits[name] = document.get(name)` froze all thirteen
per-angle arrays whole. The array's identity is positional: angle 2's value is
"the thing at index 1". Anything that changes the row count — loading a
different experiment, removing an angle — re-indexes every element, so the
frozen column no longer described the angles it was recorded against. Because
that column then arrived at layer (b), which outranks the experiment file, a
Load silently dropped the file's extra angle and a Remove resurrected the angle
just deleted — both badged "set for this run", so the screen confirmed the
wrong answer. The value was never wrong; the *index* was, and the snapshot had
frozen the wrong one of the two.

**How to apply.** Ask what makes the recorded thing findable again later. If the
answer is a position in a container someone else can resize, record the cell
(`{(name, row): value}`) and reassemble against the container as it stands at
use time. Copy it, too: a getter that hands back the live object makes the
record an alias, so the document rewrites its own provenance.

## 19. A mutation the correct code cannot be distinguished from is not a guard

**Rule.** When mutation-testing a *reindexing* operation, pick the case where
nothing else writes the slot under test — usually the boundary element.
Otherwise a neighbour's shift covers for the bug.

**Why.** The mutation "keep the removed row's own edit" survived a guard written
specifically for Remove-angle. With edits at rows 0, 1, 2 and row 0 removed, the
correct code drops row 0 and shifts 1→0, 2→1; the mutant keeps row 0 *and*
shifts 1→0 — which **overwrites** the stale entry. Both produce `{0:'b', 1:'c'}`.
The guard could not observe the behaviour it was named for, and only running the
mutation revealed it; reasoning about the code said it was covered.

**How to apply.** For any shift/compaction/renumbering, the discriminating
fixture removes the LAST recorded element — nothing shifts over its slot — and
then grows the container again so the stale index comes back into range. More
generally: a mutation that survives is information about the *test*, so never
retire it by widening the assertion until you can say which input distinguishes
the two programs.

## 20. A hand-maintained tuple beside an enumeration is fail-open

**Rule.** If a rule is expressed against a subset of an enumeration, derive the
subset from the enumeration. Declaring both by hand means adding a member
silently opts it out of the rule.

**Why.** `USER_AUTHORITY_LAYERS = ("a", "b")` sat beside
`LAYER_ORDER = ("b","c","d","a","e","f")`, and the geometry invariant — the
science decision that a personal preference must never override a measurement —
is expressed against that subset. A new layer (the deferred per-run badged
override is exactly one) would not appear in the subset, so the invariant would
not cover it, and nothing compared the two to say so. The extension defaulted to
*unprotected*, which is the wrong direction for a safety rule.

**How to apply.** Make one table the single source for each member's identity
and its classification, project the derived views off it, and add a test that
every member of the enumeration carries a classification. Then adding a member
without classifying it fails a test instead of quietly widening the hole. Check
the derived value is byte-identical to the literal it replaces, so the
refactor's correctness does not rest on the reader's memory.


## 21. An `if/elif` over a value's STATES must say what happens in none of them

**Rule.** When branching on what state a value is in — has a value / is a
container / is absent — an `if/elif` with no `else` does not "do nothing". It
*preserves whatever was already recorded*, which for a cache or a record is a
silent wrong answer rather than a no-op.

**Why.** v6 recorded a per-angle edit with
`if row is None: … elif isinstance(current, (list, tuple)) and 0 <= row < len(current): …`.
`set_angle_field` deliberately collapses an `optional_list` column back to
`None` when its last populated cell is cleared — that is the sanctioned "derive
it from the chopper ranges" state, protected on purpose. With `current is None`,
**both arms are False and the method neither records nor removes**, so cells
from earlier keystrokes survived describing a column that no longer existed. The
deleted value came back badged as the scientist's own, and
`new_reduction_from_template` forces `lam_range` from it, so `LAMBDA >= None`
kills the reduction. Rejected as B1′ (`d5733af`), confirmed five times.

This was the **third** consecutive recurrence in the same two functions:
`_session_edits` had to model three states — a value, a whole column, and
absent-`None` — and v4→v5 missed whole-column while v5→v6 missed absent-`None`.
Amendment 18 governs a value's *type*; `None`-as-a-real-value is a *state* the
type does not distinguish, which is why it kept escaping.

**How to apply.** Enumerate the states a value can occupy before writing the
branch, and write the `else` even when you believe it is unreachable — make it
remove the record or raise, never fall through. When a setter can *change the
shape* of the thing you are recording (a list collapsing to `None`), the
recorder has to handle that shape as a first-class case, not as a guard
condition that happens to be False.

## 22. Subtracting a feature removes tested behaviour that was merely adjacent

**Rule.** When a work order says "remove X", separate the behaviour that *is* X
from the behaviour that merely *lived inside* X. Deleting the second under cover
of the first removes tested behaviour with no finding and no discussion.

**Why.** Slug A removes the layer-(b) pre-run UI override, and the removal list
named `_record_edit` and "the 'set for this run' badge population". But
`_record_edit` did two separable things: it granted layer-(b) authority (the
feature) and it re-attributed the badge so the origin stopped naming a file that
no longer supplied the value (not the feature — it is NFR-8 provenance, which
the same acceptance bar requires be kept "intact"). Four tests pinned the second
independently, one parametrized across three widget types precisely because an
earlier attempt had silently deleted two of those paths. The re-attribution was
kept and relabelled `b*` — provably not layer (b): absent from `LAYER_ORDER`,
authority `"none"`, never entering `ui_overrides`.

**How to apply.** For each symbol on a removal list, ask what it does *besides*
the thing being removed, and check whether any test pins that separately — a
test that keeps passing is not evidence, since you are about to delete it too.
Where the two are genuinely entangled, say so in the commit and give the
reviewer the one-line revert, rather than making the call silently.


## 23. Assert on the handoff, not on a stand-in you happen to hold

**Rule.** A guard that checks "X is not populated" must read X **where the
consumer receives it**. Holding an object you believe will be the one passed on
is a guess about the call path, and the guess is what a future writer breaks.

**Why.** Slug A's guard against layer (b) coming back captured the
`ResolutionContext` returned by the discovery stub and asserted its
`ui_overrides` was empty. But the editor passes `result` into
`SettingsResolver(result)`, and a writer spelled `dataclasses.replace` —
the natural spelling for a frozen-ish dataclass — produces a **different
object**, leaving the captured one untouched. Measured across four writer
spellings against the original guard:

```
W1 dataclasses.replace        -> passed   (vacuous)
W2 attribute assignment       -> failed
W3 mutate the dict in place   -> failed
W4 fresh context at the call  -> passed   (vacuous)
```

It caught exactly the two spellings that mutate the instance already held, i.e.
the writer the author had pictured, and missed the two that do not. The
accompanying source-text assertion (`"result.ui_overrides" not in source`) was
worse than nothing: it made the coverage look doubled while matching only one
literal spelling. The guard's single job was the safe handoff to a later slug
that will reintroduce the layer deliberately — so "a future change will fail
here" being false is the whole failure.

**How to apply.** Capture at the boundary: wrap or subclass the consumer and
record what it is actually constructed with or called with. Then enumerate the
spellings a future writer could plausibly use — in-place mutation, attribute
assignment, `replace`, constructing a fresh instance at the call — and require
the guard to red on **all** of them before believing it. This is the
`_guarded_step` lesson (§8: guard every site and prove each separately) applied
to a single site with several ways in, and the shim lesson (§9: a shim tests the
site you already thought about) applied to the object graph rather than the code
path.

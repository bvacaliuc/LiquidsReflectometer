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

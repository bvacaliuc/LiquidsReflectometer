# Learnings — `settings-editor` / T2 (campaign `exp-settings-roi`)

## 1. A QTest gesture can still be an assumption

**Rule.** "Verify signals with `QTest`, not `.emit()`" is right but not
sufficient. A `QTest.mouseClick` at a coordinate you reasoned about is still a
claim about geometry. Measure the widget's actual hit region, or use a gesture
that has no geometry.

**Why.** The plan's rule against `.emit()` exists because emitting a signal
proves a slot is connected to a signal *you chose to fire*, not that Qt fires
it for the gesture a user makes. Obeying that rule, this slug's checkbox test
used `QTest.mouseClick(box, LeftButton, pos=box.rect().center())` — and failed.
Measured:

| state | widget rect | click area (`SE_CheckBoxClickRect`) |
|---|---|---|
| un-shown | 640 × 480 | `QRect(0, 233, 14, 14)` |
| shown, laid out | 174 × 15 | still the ~14 px indicator |

A text-less `QCheckBox` accepts clicks only inside its indicator, so the widget
centre misses it in both states. The test had smuggled a geometry assumption
back in under the shape of a real gesture — the same stated-vs-measured trap,
one level up, now living in the test written to prevent it.

`QTest.keyClick(box, Qt.Key_Space)` is a genuine activation gesture through the
same `toggled` path with no pixel dependence, and it works in both states.

**How to apply.** When a `QTest` gesture fails, do not reach for the next
plausible coordinate. Print the widget's rect and the style's sub-element rect
first; the answer is usually that the two disagree, and it usually means the
*widget* is wrong too (see §2). Prefer keyboard activation for checkboxes,
radio buttons and push buttons — it is a real user path and it does not encode
a layout.

## 2. A test that is awkward to write is often reporting a real defect

**Rule.** Before working around an uncooperative widget in a test, ask whether
the user would hit the same thing.

**Why.** The obvious fix here was to click the indicator's coordinates and move
on. But the measurement said something worse than "the test is fiddly": a form
layout had stretched a 14 px control to 174 px while only its leftmost 14 px
responded to clicks. Most of a visibly-wide checkbox was inert. A scientist
clicking the middle of it would conclude the control was broken, and no test
was going to tell us — the test was the only thing that noticed, and only by
failing for what looked like its own reason.

So the fix went into the widget (a `Fixed` size policy, making the clickable
area and the visible extent the same thing) as well as the test, with a
regression test asserting the click rect contains the widget centre.

**How to apply.** When a UI test needs an unnatural gesture to pass, write down
*why* the natural one fails. If the reason would also apply to a person, that
is a bug in the interface, not friction in the harness.

## 3. Prove a dead reference is dead before you honour it

**Rule.** A commented-out import, a TODO naming a module, a doc pointing at a
file — check the thing exists before designing around it.

**Why.** `new_launcher.py` carried `#from launcher.apps.json_settings_builder
import JSONSettingsBuilderTab`. It reads like a feature that was disabled and
might be revived, and a plan could reasonably have been written to "restore"
it. `git log --all -S json_settings_builder` finds only the comment: the module
never existed. So T2 was greenfield, not a restoration — which changes the
work, and changes which bugs are possible. The angle table in particular is new
code, so the active-row-as-hidden-input trap would be *introduced* here rather
than inherited, and the guard belongs in the design from line one instead of in
an audit of ported code.

**How to apply.** `git log --all -S <symbol>` costs seconds and settles it. And
when the reference really is dead, delete it in the change that supersedes it —
leaving it beside working code preserves the same false lead for the next
reader. The replacement here is asserted by a test on the live wiring rather
than by a comment.

## 4. Let the data model carry the invariant the class does not

**Rule.** Where a config object is a flat attribute bag with no validation,
the editing layer is where the shape gets enforced — and it must enforce the
shape the *consumer* actually accepts, not a tidier one.

**Why.** `NRReductionConfig` has 13 per-angle fields and nothing keeps them the
same length; a short array silently shifts every later angle's settings by one.
`add_angle` therefore mutates all 13 in one operation. But the mirror-image
mistake is just as easy: a validator demanding strict equal length everywhere
would reject configurations the reducer accepts, because it deliberately
broadcasts a single `method_per_run` entry to every angle
(`nr_reduction_calc.py:76-78`) and defaults an empty one to `meanTheta`
(`:41-42`). Two different rules, one for the authoring operation and one for
validation, both read off the reducer's own code.

The same distinction settled `LambdaMin`/`LambdaMax`. The plan called for
materialising them from `None` on the first `add_angle`. Left alone instead:
`None` means "derive from the chopper ranges" (`:381-383`), a valid
configuration rather than a missing value, and `[None, None]` would be a list
that reports a length but carries no values — which `web_report.py:547` indexes
and `:70-71` length-checks. They materialise only when a value is supplied, at
full length, and `validate()` names the angles still lacking one.

**How to apply.** Read the consumer before writing the validator. Detection
complete (every disagreement is reported), resolution minimal (the scientist
decides), and the exceptions documented with the line numbers that justify them
— so the next person can check the reasoning rather than trusting it.

## 5. A green gate says nothing about whether a slot can kill the process

**Rule.** For any GUI handler, ask what happens when it raises — not whether it
raises in the tests.

**Why.** T2 v1 passed 128 launcher and 145 reduction tests, and two independent
paths in it aborted the entire launcher. Under PyQt5 an unhandled exception in a
slot reaches `qFatal()`, which calls `abort()`: `EXIT=134`, and every other tab
loses its unsaved state. Neither path needed a hostile file:

- `set_angle_field` padded a `None` per-angle column but not a **short** one, and
  short columns are produced by the reducer's own sanctioned length-1
  `method_per_run`, by `normalize()` dropping `RBnum`, and by the editor's own
  save/reload round trip;
- `validate()` iterated whatever a settings file contained, so `{"tof_min": 5}`
  raised `TypeError` before anything could catch it.

The gate could not see either, because a test suite calls methods and a user
sends gestures.

**How to apply.** A tool that reads files it did not write must treat malformed
input as a *message*, never a crash. Give every slot a top-level guard that
reports into the UI; put the recovery work **inside** the `try`, not after it;
and catch broadly there — `except (ValueError, OSError)` expressed the right
intent and still let `TypeError` through. Then pair each guard with a test that
makes the slot raise on purpose.

## 6. Type dispatch in three places is a bug with a delay fuse

**Rule.** When the same "what type is this field" decision is made by widget
construction, by text-to-value coercion, and by validation, they will disagree —
and the disagreement is silent.

**Why.** `_build_editor`, `_coerce`, `refresh_scalars` and `_check_value` each
re-derived the type. `_coerce` handled only `"int"` and `"float"`; every
per-angle field is a `list[...]`, so **no cell was ever coerced**. `useBS` stored
the string `"False"` — truthy — and the reducer subtracted background for a
scientist who had switched it off. `_check_value` returned `""` for anything not
int or float, so `validate()` reported *No problems found* and the declared
bounds never ran. The saved file looked correctly authored.

The fix is not "coerce lists too". It is that `coerce()` and `check()` are pure
`(Field, value)` functions and belong **on `Field`**, in the Qt-free module —
one dispatch, which a resolution layer then reuses instead of writing a fourth.

**How to apply.** Count the places that switch on a type tag. More than one is a
refactor; the copies that disagree are the bug you have not found yet.

## 7. Never bool(text), and never let a domain be a hand-copy

Two specific traps, both from this cluster:

`bool("False")` is `True`. Any parse of user text into a boolean needs an
explicit accepted set (`{"true","1","yes",...}` / `{"false","0","no",...}`),
because the plausible-looking one-liner produces exactly the wrong answer for
the word a user is most likely to type.

And `useCalcTheta` was declared `bool` while the reducer accepts
`'detector_angle'`/`'sample_angle'` — so the editor rendered a checkbox that
could not express one of the two values and silently downgraded a loaded one.
The choice lists themselves were hand-copies of bare local lists inside the
reducer. Copies drift, and the drift here is invisible: the editor goes on
offering a value the reducer has stopped accepting.

**How to apply.** Put a domain in one module both sides import
(`reduction_domains.py`), and have the *enforcer* derive its checks from it —
then drift is structurally impossible instead of merely tested for. Where a
field is tri-state (falsy means "off"), model that explicitly rather than
letting the default look like a violation; and migrate a legacy spelling the
consumer still accepts instead of reporting it, or the panel cries wolf on a
file that works.

## 8. A mutation that stays green means the test is vacuous OR the mutation missed

**Rule.** When mutate-once does not red, diagnose which of the two it is before
touching anything.

**Why.** Sixteen mutations, one per guard; four stayed green. The instinct is
"four vacuous tests" — and acting on it would have meant rewriting sound tests.
Three were **bad mutations**: they aimed at code the test does not depend on.
The save mutation truncated after the payload was already built; the cry-wolf
mutation emptied a derived tuple that `_length_is_allowed` never consults; the
C5 mutation changed `allowed` without changing `type`. Re-aimed, all three red.

Two were genuinely vacuous, and both were testing the wrong *layer* or the wrong
*state*:

- the C5 model test round-tripped `'sample_angle'` and passed with the field
  declared `bool`, because the document stores what it is given and never reads
  the declaration. The bug was always in the view. The model can only pin the
  declaration — so it does, and the widget is pinned in the view suite.
- the cry-wolf test built its angles with `add_angle()`, which grows all 13
  columns, so the empty-array exemption it named was never reached. It now loads
  a file where those arrays are genuinely absent.

**And correcting the second surfaced a true positive I nearly silenced.** With
the arrays really absent, `validate()` also reported `BkgROI has 0 entries for 3
angles`. `BkgROI` is indexed per-angle by `web_report` and is *not* in the
reducer's auto-default list, so that report is correct — a 3-angle file without
it fails downstream. The test supplies `BkgROI` rather than adding an exemption
to make itself pass. The tempting move — widen the exemption until the test goes
green — is the tolerance-widening mistake from the sibling slug, wearing
different clothes.

**How to apply.** Treat a stubbornly-green mutation as a question, not a verdict:
*does this test actually execute the code I just broke?* Re-aim once. If it
reds, the test was fine. If it still passes, the test is measuring something
else — and check whether the state you had to construct to reach the code
reveals a defect of its own.

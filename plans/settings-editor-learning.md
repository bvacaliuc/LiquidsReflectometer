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
